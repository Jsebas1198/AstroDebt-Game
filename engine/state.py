"""
GameState - Gestión del Estado del Juego
Mantiene el estado global del juego incluyendo recursos, progreso y condiciones de victoria/derrota
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class GameState:
    """
    Clase principal que mantiene todo el estado del juego
    
    Atributos:
        oxygen: Nivel actual de oxígeno (0-100)
        materials: Diccionario de materiales recolectados {tipo: cantidad}
        repair_progress: Progreso de reparación de la nave (0-100)
        turn_number: Número del turno actual
        time_elapsed: Tiempo transcurrido en segundos
        game_over: Estado del juego (True si terminó)
        victory: True si el jugador ganó
    
    Dependencias:
        - finance.loan_manager.LoanManager: Para gestionar préstamos activos
        - gameplay.resources: Para gestionar inventario de recursos
    """
    
    # Recursos vitales
    oxygen: float = 100.0
    materials: Dict[str, int] = field(default_factory=dict)
    
    # Progreso del juego
    repair_progress: float = 0.0
    turn_number: int = 0
    time_elapsed: float = 0.0
    
    # Estado del juego
    game_over: bool = False
    victory: bool = False
    
    # Referencias a otros managers (se inicializan después)
    loan_manager = None
    
    def __post_init__(self):
        """Inicializa los materiales básicos"""
        # TODO: Cargar materiales iniciales desde configuración
        if not self.materials:
            self.materials = {
                'metal': 0,
                'circuits': 0,
                'fuel': 0,
                'rare_minerals': 0
            }
    
    def update_oxygen(self, delta: float) -> None:
        """
        Actualiza el nivel de oxígeno
        
        Args:
            delta: Cambio en el nivel de oxígeno (puede ser negativo)
        """
        # TODO: Implementar lógica de actualización de oxígeno
        # TODO: Verificar game over si oxígeno <= 0
        pass
    
    def add_material(self, material_type: str, amount: int) -> None:
        """
        Añade materiales al inventario
        
        Args:
            material_type: Tipo de material
            amount: Cantidad a añadir
        """
        # TODO: Implementar lógica de añadir materiales
        pass
    
    def consume_material(self, material_type: str, amount: int) -> bool:
        """
        Consume materiales del inventario
        
        Args:
            material_type: Tipo de material
            amount: Cantidad a consumir
            
        Returns:
            True si había suficientes materiales, False en caso contrario
        """
        # TODO: Implementar lógica de consumo de materiales
        pass
    
    def update_repair_progress(self, delta: float) -> None:
        """
        Actualiza el progreso de reparación
        
        Args:
            delta: Cambio en el progreso (0-100)
        """
        # TODO: Implementar lógica de actualización de progreso
        # TODO: Verificar victoria si repair_progress >= 100
        pass
    
    def advance_turn(self) -> None:
        """Avanza un turno en el juego"""
        # TODO: Incrementar turn_number
        # TODO: Aplicar efectos de fin de turno (consumo de oxígeno, intereses, etc.)
        pass
    
    def check_game_over_conditions(self) -> None:
        """Verifica las condiciones de game over"""
        # TODO: Verificar oxígeno, deuda impagable, etc.
        pass
    
    def save_state(self) -> Dict:
        """
        Serializa el estado del juego para guardado
        
        Returns:
            Diccionario con el estado del juego
        """
        # TODO: Implementar serialización del estado
        pass
    
    @classmethod
    def load_state(cls, state_dict: Dict) -> 'GameState':
        """
        Carga el estado del juego desde un diccionario
        
        Args:
            state_dict: Diccionario con el estado guardado
            
        Returns:
            Nueva instancia de GameState
        """
        # TODO: Implementar deserialización del estado
        pass

