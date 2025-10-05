"""
Repair - Sistema de Reparación de la Nave
Simplificado para MVP: Un solo progreso de reparación general
"""

from typing import Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)


class RepairSystem:
    """
    Sistema simplificado de reparación de la nave
    
    MVP: Un solo progreso de reparación general (0-100%)
    - Materiales necesarios: 5-10 por intento
    - Oxígeno necesario: 3 por intento
    - Objetivo: Llegar a 100% para ganar
    
    Responsabilidades:
        - Gestionar progreso de reparación
        - Validar recursos para reparar
        - Procesar resultados de minijuegos de reparación
    
    Dependencias:
        - gameplay.resources.ResourceManager: Para consumir materiales
        - engine.events.EventManager: Para emitir eventos de reparación
        - engine.state.GameState: Para actualizar progreso total
    """
    
    def __init__(self):
        """Inicializa el sistema de reparación"""
        # Referencias a otros componentes
        self.resource_manager = None
        self.event_manager = None
        self.game_state = None
        
        # Configuración de reparación
        self.materials_cost_min = 5
        self.materials_cost_max = 10
        self.oxygen_cost = 3.0
        self.repair_increment_success = 15.0  # +15% por éxito
        self.repair_increment_fail = 0.0      # 0% por fallo
        
        logger.info("RepairSystem inicializado (sistema simplificado)")


    def can_start_repair(self) -> bool:
        """
        Verifica si se puede iniciar una reparación
        
        Returns:
            True si hay suficientes recursos
        """
        if not self.game_state or not self.resource_manager:
            return False
        
        # Verificar oxígeno
        if self.game_state.oxygen < self.oxygen_cost:
            logger.warning(f"Oxígeno insuficiente para reparar: {self.game_state.oxygen:.1f} < {self.oxygen_cost}")
            return False
        
        # Verificar materiales mínimos
        if self.game_state.materials < self.materials_cost_min:
            logger.warning(f"Materiales insuficientes para reparar: {self.game_state.materials} < {self.materials_cost_min}")
            return False
        
        # Verificar si ya está completo
        if self.game_state.repair_progress >= 100:
            logger.info("La nave ya está completamente reparada")
            return False
        
        return True
    
    def process_repair_attempt(self, success: bool) -> Dict[str, Any]:
        """
        Procesa el resultado de un intento de reparación
        
        Args:
            success: Si el minijuego fue exitoso
            
        Returns:
            Diccionario con resultados de la reparación
        """
        if not self.game_state or not self.resource_manager:
            return {'success': False, 'message': 'Sistema no inicializado'}
        
        # Calcular costo de materiales según éxito
        if success:
            materials_cost = self.materials_cost_min  # Menos materiales si es exitoso
            repair_increment = self.repair_increment_success
        else:
            materials_cost = self.materials_cost_max  # Más materiales si falla
            repair_increment = self.repair_increment_fail
        
        # Consumir materiales
        if not self.resource_manager.consume_materials(materials_cost, "repair"):
            return {
                'success': False,
                'message': f'Materiales insuficientes: necesitas {materials_cost}'
            }
        
        # Actualizar progreso de reparación
        old_progress = self.game_state.repair_progress
        self.game_state.update_repair_progress(repair_increment)
        new_progress = self.game_state.repair_progress
        
        # Emitir evento de progreso
        if self.event_manager:
            from engine.events import EventType
            self.event_manager.emit_quick(
                EventType.REPAIR_PROGRESS_CHANGED,
                {
                    'old_progress': old_progress,
                    'new_progress': new_progress,
                    'increment': repair_increment,
                    'materials_used': materials_cost
                }
            )
            
            # Verificar si se completó la reparación
            if new_progress >= 100:
                self.event_manager.emit_quick(
                    EventType.REPAIR_COMPLETED,
                    {'message': '¡Nave completamente reparada!'}
                )
                self.event_manager.emit_quick(EventType.VICTORY)
        
        result = {
            'success': True,
            'repair_increment': repair_increment,
            'materials_used': materials_cost,
            'new_progress': new_progress,
            'is_complete': new_progress >= 100
        }
        
        if success:
            result['message'] = f'Reparación exitosa: +{repair_increment:.0f}% (Total: {new_progress:.0f}%)'
        else:
            result['message'] = f'Reparación fallida, pero gastaste {materials_cost} materiales'
        
        logger.info(result['message'])
        
        return result
    
    def get_repair_cost_estimate(self) -> Dict[str, Any]:
        """
        Obtiene una estimación del costo de reparación
        
        Returns:
            Diccionario con costos estimados
        """
        return {
            'oxygen_cost': self.oxygen_cost,
            'materials_min': self.materials_cost_min,
            'materials_max': self.materials_cost_max,
            'potential_progress': self.repair_increment_success
        }
    
    def get_repair_summary(self) -> Dict[str, Any]:
        """
        Obtiene un resumen del estado de reparación
        
        Returns:
            Diccionario con información de reparación
        """
        if not self.game_state:
            return {'progress': 0, 'is_complete': False}
        
        progress = self.game_state.repair_progress
        remaining = 100 - progress
        
        # Estimar intentos necesarios (asumiendo éxito)
        attempts_needed = 0
        if remaining > 0 and self.repair_increment_success > 0:
            attempts_needed = int(remaining / self.repair_increment_success) + 1
        
        # Estimar materiales necesarios (promedio)
        avg_materials = (self.materials_cost_min + self.materials_cost_max) / 2
        estimated_materials = int(attempts_needed * avg_materials)
        
        return {
            'progress': progress,
            'remaining': remaining,
            'is_complete': progress >= 100,
            'attempts_needed': attempts_needed,
            'estimated_materials': estimated_materials,
            'estimated_oxygen': attempts_needed * self.oxygen_cost
        }

