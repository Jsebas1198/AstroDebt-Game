"""
Resources - Sistema de Recolección de Recursos
Simplificado para MVP: Un solo tipo de material genérico
Materiales = Trabajo (concepto educativo)
"""

from typing import Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)


class ResourceManager:
    """
    Gestor simplificado de recursos del juego
    
    MVP: Un solo tipo de material genérico
    - Materiales representan "trabajo" en el concepto educativo
    - Se obtienen minando (trabajando)
    - Se usan para reparar la nave y pagar préstamos
    
    Responsabilidades:
        - Gestionar recolección de materiales
        - Validar y procesar consumo de materiales
        - Sincronizar con GameState
    
    Dependencias:
        - engine.events.EventManager: Para emitir eventos de recursos
        - engine.state.GameState: Para actualizar el estado del juego
    """
    
    def __init__(self):
        """Inicializa el gestor de recursos"""
        # Referencias a otros componentes
        self.event_manager = None
        self.game_state = None
        
        # Configuración de recompensas
        self.mining_reward_success = 10  # Materiales por minería exitosa
        self.mining_reward_fail = 2      # Materiales por minería fallida
        
        logger.info("ResourceManager inicializado (sistema simplificado)")


    def collect_materials(self, amount: int, source: str = "mining") -> int:
        """
        Recolecta materiales genéricos (desde minijuegos)
        
        Args:
            amount: Cantidad recolectada
            source: Origen de los materiales (mining, scavenging, etc.)
            
        Returns:
            Cantidad realmente añadida
        """
        if not self.game_state:
            logger.error("GameState no conectado a ResourceManager")
            return 0
        
        # Añadir materiales al GameState
        added = self.game_state.add_materials(amount)
        
        if added > 0 and self.event_manager:
            # Emitir evento de materiales ganados
            from engine.events import EventType
            self.event_manager.emit_quick(
                EventType.MATERIALS_GAINED,
                {"amount": added, "source": source, "total": self.game_state.materials}
            )
            
            # Verificar si hay alerta por materiales bajos
            if self.game_state.materials < 5:
                self.event_manager.emit_quick(EventType.ALERT_MATERIALS)
        
        return added
    
    def consume_materials(self, amount: int, purpose: str = "repair") -> bool:
        """
        Consume materiales genéricos
        
        Args:
            amount: Cantidad a consumir
            purpose: Propósito del consumo (repair, loan_payment, etc.)
            
        Returns:
            True si se pudieron consumir los materiales
        """
        if not self.game_state:
            logger.error("GameState no conectado a ResourceManager")
            return False
        
        # Intentar consumir del GameState
        success = self.game_state.consume_materials(amount)
        
        if success and self.event_manager:
            # Emitir evento de materiales consumidos
            from engine.events import EventType
            self.event_manager.emit_quick(
                EventType.MATERIALS_CONSUMED,
                {"amount": amount, "purpose": purpose, "remaining": self.game_state.materials}
            )
        
        return success
    
    def has_materials(self, amount: int) -> bool:
        """
        Verifica si hay suficientes materiales
        
        Args:
            amount: Cantidad requerida
            
        Returns:
            True si hay suficientes materiales
        """
        if not self.game_state:
            return False
        return self.game_state.materials >= amount
    
    def get_materials_count(self) -> int:
        """
        Obtiene la cantidad actual de materiales
        
        Returns:
            Cantidad de materiales disponibles
        """
        if not self.game_state:
            return 0
        return self.game_state.materials
    
    def process_mining_result(self, success: bool) -> int:
        """
        Procesa el resultado de un minijuego de minería
        
        Args:
            success: Si el minijuego fue exitoso
            
        Returns:
            Cantidad de materiales obtenidos
        """
        amount = self.mining_reward_success if success else self.mining_reward_fail
        
        # Recolectar materiales
        added = self.collect_materials(amount, "mining")
        
        # Emitir evento específico del resultado
        if self.event_manager:
            from engine.events import EventType
            event_type = EventType.MATERIALS_GAINED_SUCCESS if success else EventType.MATERIALS_GAINED_FAIL
            self.event_manager.emit_quick(
                event_type,
                {"amount": added, "total": self.game_state.materials if self.game_state else 0}
            )
        
        logger.info(f"Minería {'exitosa' if success else 'fallida'}: +{added} materiales")
        return added
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Obtiene un resumen del estado de recursos
        
        Returns:
            Diccionario con información de recursos
        """
        if not self.game_state:
            return {"materials": 0, "max_materials": 999}
        
        return {
            "materials": self.game_state.materials,
            "max_materials": self.game_state.max_materials,
            "is_low": self.game_state.materials < 5,
            "is_critical": self.game_state.materials == 0
        }

