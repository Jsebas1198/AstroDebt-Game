"""
GameState - Gestión del Estado del Juego
Mantiene el estado global del juego incluyendo recursos, progreso y condiciones de victoria/derrota
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class GameState:
    """
    Clase principal que mantiene todo el estado del juego
    
    Simplificación MVP: Un solo tipo de material genérico
    Oxígeno = Dinero (moneda del juego)
    Materiales = Trabajo (recurso para reparar y pagar préstamos)
    
    Atributos:
        oxygen: Nivel actual de oxígeno (moneda principal)
        materials: Cantidad de materiales genéricos
        repair_progress: Progreso de reparación de la nave (0-100)
        turn_number: Número del turno actual
        game_over: Estado del juego (True si terminó)
        victory: True si el jugador ganó
    """
    
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Recursos vitales (simplificado)
    oxygen: float = 100.0  # Oxígeno = Dinero
    max_oxygen: float = 100.0  # Límite máximo de oxígeno
    materials: int = 0  # Materiales genéricos = Trabajo
    max_materials: int = 999  # Límite de almacenamiento
    
    # Progreso del juego
    repair_progress: float = 0.0
    turn_number: int = 0
    current_phase: str = "intro"  # intro, main_game, minigame, end
    
    # Estado del juego
    game_over: bool = False
    victory: bool = False
    game_over_reason: str = ""
    
    # Costos por acción (incrementados para más desafío)
    oxygen_cost_mining: float = 12.0  # 12-15 consumo aleatorio
    oxygen_cost_repair: float = 12.0  # 12-15 consumo aleatorio
    oxygen_cost_per_turn: float = 1.0  # Costo base por turno
    
    # Sistema de prestamista
    prestamista_shown: bool = False  # Flag para mostrar prestamista solo una vez
    
    # Referencias a otros managers (se inicializan después)
    loan_manager = None
    resource_manager = None
    repair_system = None
    
    def __post_init__(self):
        """Inicializa el estado con valores de configuración"""
        if self.config:
            gameplay = self.config.get('gameplay', {})
            self.oxygen = gameplay.get('initial_oxygen', 100.0)
            self.max_oxygen = self.oxygen
            self.oxygen_cost_per_turn = gameplay.get('oxygen_consumption_per_turn', 2.0)
            
            # Materiales iniciales (simplificado)
            self.materials = 10  # Empezamos con algunos materiales
            
        logger.info(f"GameState inicializado: Oxígeno={self.oxygen}, Materiales={self.materials}")
    
    def update_oxygen(self, delta: float) -> bool:
        """
        Actualiza el nivel de oxígeno (moneda del juego)
        
        Args:
            delta: Cambio en el nivel de oxígeno (puede ser negativo)
            
        Returns:
            True si la operación fue exitosa
        """
        old_oxygen = self.oxygen
        self.oxygen = max(0, min(self.max_oxygen, self.oxygen + delta))
        
        if self.oxygen != old_oxygen:
            logger.info(f"Oxígeno actualizado: {old_oxygen:.1f} -> {self.oxygen:.1f}")
            
        # Verificar condición de game over
        if self.oxygen <= 0:
            self.trigger_game_over("oxygen_depleted")
            return False
            
        return True
    
    def add_materials(self, amount: int) -> int:
        """
        Añade materiales genéricos (representan trabajo/recursos)
        
        Args:
            amount: Cantidad a añadir
            
        Returns:
            Cantidad realmente añadida (puede ser menor por límite)
        """
        old_materials = self.materials
        added = min(amount, self.max_materials - self.materials)
        self.materials = min(self.materials + amount, self.max_materials)
        
        if added > 0:
            logger.info(f"Materiales añadidos: +{added} (Total: {self.materials})")
            
        return added
    
    def consume_materials(self, amount: int) -> bool:
        """
        Consume materiales genéricos
        
        Args:
            amount: Cantidad a consumir
            
        Returns:
            True si había suficientes materiales, False en caso contrario
        """
        if self.materials >= amount:
            self.materials -= amount
            logger.info(f"Materiales consumidos: -{amount} (Total: {self.materials})")
            return True
        else:
            logger.warning(f"Materiales insuficientes: Necesarios={amount}, Disponibles={self.materials}")
            return False
    
    def update_repair_progress(self, delta: float) -> None:
        """
        Actualiza el progreso de reparación
        
        Args:
            delta: Cambio en el progreso (0-100)
        """
        old_progress = self.repair_progress
        self.repair_progress = max(0, min(100, self.repair_progress + delta))
        
        if self.repair_progress != old_progress:
            logger.info(f"Progreso de reparación: {old_progress:.1f}% -> {self.repair_progress:.1f}%")
            
        # Verificar condición de victoria
        if self.repair_progress >= 100 and not self.victory:
            self.trigger_victory()
    
    def advance_turn(self) -> None:
        """
        Avanza un turno en el juego
        Sistema basado en acciones, no en tiempo real
        """
        self.turn_number += 1
        logger.info(f"=== Turno {self.turn_number} ===")
        
        # Consumir oxígeno por turno (costo de supervivencia)
        self.update_oxygen(-self.oxygen_cost_per_turn)
        
        # Procesar préstamos si existen
        if self.loan_manager:
            self.loan_manager.process_turn()
        
        # Verificar condiciones del juego
        self.check_game_over_conditions()
    
    def check_game_over_conditions(self) -> None:
        """Verifica las condiciones de game over y victoria"""
        # Game Over por oxígeno
        if self.oxygen <= 0:
            self.trigger_game_over("oxygen_depleted")
            return
            
        # Game Over por deudas impagables
        if self.loan_manager:
            total_debt = self.loan_manager.get_total_debt_in_materials()
            if total_debt > self.materials + 50:  # Margen de 50 materiales
                # Solo si el oxígeno es muy bajo y no puede recuperarse
                if self.oxygen < 20 and total_debt > self.materials + 100:
                    self.trigger_game_over("debt_overwhelming")
                    return
        
        # Victoria por reparación completa
        if self.repair_progress >= 100:
            self.trigger_victory()
    
    def trigger_game_over(self, reason: str) -> None:
        """Activa el estado de game over"""
        if not self.game_over:
            self.game_over = True
            self.game_over_reason = reason
            self.current_phase = "end"
            logger.info(f"GAME OVER: {reason}")
    
    def trigger_victory(self) -> None:
        """Activa el estado de victoria"""
        if not self.victory:
            self.victory = True
            self.current_phase = "end"
            logger.info("\u00a1VICTORIA! Nave reparada al 100%")
    
    def can_afford_action(self, action: str) -> bool:
        """
        Verifica si el jugador puede pagar el costo de una acción
        
        Args:
            action: Tipo de acción (mining, repair, etc.)
            
        Returns:
            True si tiene suficiente oxígeno
        """
        costs = {
            "mining": self.oxygen_cost_mining,
            "repair": self.oxygen_cost_repair,
            "explore": 1.0
        }
        cost = costs.get(action, 0)
        return self.oxygen >= cost
    
    def get_status_summary(self) -> Dict[str, Any]:
        """
        Obtiene un resumen del estado actual para el HUD
        
        Returns:
            Diccionario con información del estado
        """
        return {
            "oxygen": self.oxygen,
            "max_oxygen": self.max_oxygen,
            "materials": self.materials,
            "repair_progress": self.repair_progress,
            "turn": self.turn_number,
            "phase": self.current_phase,
            "game_over": self.game_over,
            "victory": self.victory
        }

