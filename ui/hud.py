"""
HUD - Heads-Up Display
Interfaz de usuario que muestra información del juego
"""

import pygame
from typing import Optional, Dict, List


class HUD:
    """
    Heads-Up Display del juego
    
    Responsabilidades:
        - Mostrar nivel de oxígeno
        - Mostrar recursos e inventario
        - Mostrar progreso de reparación
        - Mostrar información de préstamos
        - Mostrar notificaciones y alertas
        - Mostrar menús contextuales
    
    Dependencias:
        - pygame: Para renderizado de UI
        - engine.state.GameState: Para obtener información a mostrar
        - finance.loan_manager.LoanManager: Para mostrar deudas
        - gameplay.resources.ResourceManager: Para mostrar inventario
    """
    
    def __init__(self, screen: pygame.Surface):
        """
        Inicializa el HUD
        
        Args:
            screen: Superficie de Pygame donde renderizar
        """
        self.screen = screen
        self.font = None
        self.large_font = None
        self.small_font = None
        
        # Referencias a componentes
        self.game_state = None
        self.loan_manager = None
        self.resource_manager = None
        
        # Estado del HUD
        self.notifications: List[Dict] = []
        self.show_inventory = False
        self.show_debt_panel = False
        self.show_repair_panel = False
    
    def initialize(self) -> None:
        """Inicializa fuentes y recursos del HUD"""
        # TODO: Cargar fuentes
        # TODO: Preparar iconos y sprites de UI
        pass
    
    def render(self) -> None:
        """Renderiza todos los elementos del HUD"""
        # TODO: Renderizar barra de oxígeno
        # TODO: Renderizar inventario resumido
        # TODO: Renderizar progreso de reparación
        # TODO: Renderizar información de deuda
        # TODO: Renderizar notificaciones
        # TODO: Renderizar paneles activos
        pass
    
    def render_oxygen_bar(self) -> None:
        """Renderiza la barra de oxígeno"""
        # TODO: Obtener nivel de oxígeno del GameState
        # TODO: Dibujar barra con color según nivel (verde, amarillo, rojo)
        # TODO: Añadir icono y texto
        pass
    
    def render_resource_summary(self) -> None:
        """Renderiza resumen de recursos principales"""
        # TODO: Obtener recursos del ResourceManager
        # TODO: Dibujar iconos y cantidades
        # TODO: Resaltar recursos críticos
        pass
    
    def render_repair_progress(self) -> None:
        """Renderiza el progreso de reparación de la nave"""
        # TODO: Obtener progreso del GameState
        # TODO: Dibujar barra de progreso
        # TODO: Mostrar porcentaje
        pass
    
    def render_debt_summary(self) -> None:
        """Renderiza resumen de deudas activas"""
        # TODO: Obtener deudas del LoanManager
        # TODO: Mostrar deuda total
        # TODO: Alertar si hay pagos pendientes
        # TODO: Usar colores de advertencia si es crítico
        pass
    
    def render_turn_info(self) -> None:
        """Renderiza información del turno actual"""
        # TODO: Mostrar número de turno
        # TODO: Mostrar tiempo transcurrido
        pass
    
    def render_notifications(self) -> None:
        """Renderiza notificaciones flotantes"""
        # TODO: Iterar sobre self.notifications
        # TODO: Dibujar cada notificación con fade out
        # TODO: Eliminar notificaciones expiradas
        pass
    
    def add_notification(self, message: str, notification_type: str = 'info', duration: float = 3.0) -> None:
        """
        Añade una notificación al HUD
        
        Args:
            message: Mensaje a mostrar
            notification_type: Tipo (info, warning, error, success)
            duration: Duración en segundos
        """
        # TODO: Crear diccionario de notificación
        # TODO: Añadir a self.notifications
        pass
    
    def render_inventory_panel(self) -> None:
        """Renderiza el panel detallado de inventario"""
        # TODO: Dibujar panel de fondo
        # TODO: Listar todos los recursos con iconos
        # TODO: Mostrar cantidades y límites
        pass
    
    def render_debt_panel(self) -> None:
        """Renderiza el panel detallado de deudas"""
        # TODO: Dibujar panel de fondo
        # TODO: Listar todos los préstamos activos
        # TODO: Mostrar detalles: acreedor, balance, tasa, plazo
        # TODO: Opciones de pago
        pass
    
    def render_repair_panel(self) -> None:
        """Renderiza el panel detallado de reparación"""
        # TODO: Dibujar panel de fondo
        # TODO: Listar componentes de la nave
        # TODO: Mostrar estado de cada componente
        # TODO: Mostrar recursos necesarios
        pass
    
    def toggle_inventory(self) -> None:
        """Alterna la visibilidad del panel de inventario"""
        # TODO: Invertir show_inventory
        pass
    
    def toggle_debt_panel(self) -> None:
        """Alterna la visibilidad del panel de deudas"""
        # TODO: Invertir show_debt_panel
        pass
    
    def toggle_repair_panel(self) -> None:
        """Alterna la visibilidad del panel de reparación"""
        # TODO: Invertir show_repair_panel
        pass
    
    def update(self, delta_time: float) -> None:
        """
        Actualiza animaciones y timers del HUD
        
        Args:
            delta_time: Tiempo transcurrido
        """
        # TODO: Actualizar animaciones
        # TODO: Actualizar timers de notificaciones
        pass

