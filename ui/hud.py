"""
HUD - Heads-Up Display
Interfaz de usuario que muestra información del juego
"""

import pygame
import os
from typing import Optional, Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


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
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # Fuentes
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
        self.show_action_menu = True
        
        # Modal de intercambio de materiales por oxígeno
        self.show_exchange_modal = False
        self.exchange_amount = 0
        self.exchange_slider_dragging = False
        
        # Assets del HUD
        self.assets = {}
        
        # Posiciones de elementos del HUD
        self.oxygen_bar_pos = (20, 20)
        self.materials_pos = (20, 80)
        self.repair_bar_pos = (20, 140)
        self.turn_info_pos = (self.screen_width - 200, 20)
        self.action_menu_pos = (self.screen_width // 2 - 175, self.screen_height - 140)
    
    def initialize(self) -> None:
        """Inicializa fuentes y recursos del HUD"""
        # Cargar fuentes
        try:
            self.large_font = pygame.font.Font(None, 36)
            self.font = pygame.font.Font(None, 24)
            self.small_font = pygame.font.Font(None, 18)
        except Exception as e:
            logger.error(f"Error cargando fuentes: {e}")
            # Fuentes por defecto
            self.large_font = pygame.font.SysFont('Arial', 36)
            self.font = pygame.font.SysFont('Arial', 24)
            self.small_font = pygame.font.SysFont('Arial', 18)
        
        # Cargar assets del HUD
        self._load_assets()
        logger.info("HUD inicializado")
    
    def render(self) -> None:
        """Renderiza todos los elementos del HUD"""
        if not self.game_state:
            return
        
        # Renderizar elementos principales del HUD
        self.render_oxygen_bar()
        self.render_resource_summary()
        self.render_repair_progress()
        self.render_exchange_button()
        self.render_turn_info()
        
        # Renderizar información de deudas si hay préstamos activos
        if self.loan_manager and self.loan_manager.active_loans:
            self.render_debt_summary()
        
        # Renderizar menú de acciones si está en fase principal
        if self.game_state.current_phase == "main_game" and self.show_action_menu:
            self.render_action_menu()
        
        # Renderizar notificaciones
        self.render_notifications()
        
        # Renderizar paneles activos SOLO si NO estamos en un minijuego
        if self.game_state.current_phase != "minigame":
            if self.show_inventory:
                self.render_inventory_panel()
            if self.show_debt_panel:
                self.render_debt_panel()
            if self.show_repair_panel:
                self.render_repair_panel()
        
        # Renderizar modal de intercambio (sobre todo lo demás)
        if self.show_exchange_modal:
            self.render_exchange_modal()
    
    def render_oxygen_bar(self) -> None:
        """Renderiza la barra de oxígeno"""
        if not self.game_state:
            return
        
        x, y = self.oxygen_bar_pos
        bar_width = 200
        bar_height = 30
        
        # Calcular porcentaje de oxígeno
        oxygen_percent = self.game_state.oxygen / self.game_state.max_oxygen
        
        # Determinar color según nivel
        if oxygen_percent > 0.5:
            color = (0, 255, 0)  # Verde
        elif oxygen_percent > 0.2:
            color = (255, 255, 0)  # Amarillo
        else:
            color = (255, 0, 0)  # Rojo
        
        # Dibujar fondo de la barra
        pygame.draw.rect(self.screen, (50, 50, 50), (x, y, bar_width, bar_height))
        
        # Dibujar barra de oxígeno
        fill_width = int(bar_width * oxygen_percent)
        if fill_width > 0:
            pygame.draw.rect(self.screen, color, (x, y, fill_width, bar_height))
        
        # Dibujar borde
        pygame.draw.rect(self.screen, (255, 255, 255), (x, y, bar_width, bar_height), 2)
        
        # Dibujar icono si está disponible
        if 'oxygen_bar' in self.assets:
            icon = self.assets['oxygen_bar']
            icon_rect = icon.get_rect()
            icon_rect.midleft = (x - 40, y + bar_height // 2)
            self.screen.blit(icon, icon_rect)
        
        # Dibujar texto
        text = f"Oxígeno: {self.game_state.oxygen:.0f}/{self.game_state.max_oxygen:.0f}"
        text_surface = self.font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.midleft = (x + bar_width + 10, y + bar_height // 2)
        self.screen.blit(text_surface, text_rect)
        
        # Mostrar alerta si el oxígeno es crítico
        if oxygen_percent <= 0.2 and 'alert_oxygen' in self.assets:
            alert = self.assets['alert_oxygen']
            alert_rect = alert.get_rect()
            alert_rect.midleft = (x + bar_width + 150, y + bar_height // 2)
            self.screen.blit(alert, alert_rect)
    
    def render_resource_summary(self) -> None:
        """Renderiza resumen de materiales (simplificado)"""
        if not self.game_state:
            return
        
        x, y = self.materials_pos
        
        # Dibujar icono si está disponible
        if 'materials_bar' in self.assets:
            icon = self.assets['materials_bar']
            icon_rect = icon.get_rect()
            icon_rect.topleft = (x, y)
            self.screen.blit(icon, icon_rect)
            x += icon_rect.width + 10
        
        # Dibujar cantidad de materiales
        materials_text = f"Materiales: {self.game_state.materials}"
        color = (255, 255, 255)
        
        # Color de advertencia si los materiales son bajos
        if self.game_state.materials < 5:
            color = (255, 100, 100)
            
            # Mostrar alerta si los materiales son críticos
            if self.game_state.materials == 0 and 'alert_materials' in self.assets:
                alert = self.assets['alert_materials']
                alert_rect = alert.get_rect()
                alert_rect.midleft = (x + 150, y + 15)
                self.screen.blit(alert, alert_rect)
        
        text_surface = self.font.render(materials_text, True, color)
        self.screen.blit(text_surface, (x, y))
    
    def render_repair_progress(self) -> None:
        """Renderiza el progreso de reparación de la nave"""
        if not self.game_state:
            return
        
        x, y = self.repair_bar_pos
        bar_width = 200
        bar_height = 30
        
        # Calcular porcentaje de reparación
        repair_percent = self.game_state.repair_progress / 100.0
        
        # Dibujar fondo de la barra
        pygame.draw.rect(self.screen, (50, 50, 50), (x, y, bar_width, bar_height))
        
        # Dibujar barra de progreso
        fill_width = int(bar_width * repair_percent)
        if fill_width > 0:
            # Color dorado para progreso de reparación
            pygame.draw.rect(self.screen, (255, 215, 0), (x, y, fill_width, bar_height))
        
        # Dibujar borde
        pygame.draw.rect(self.screen, (255, 255, 255), (x, y, bar_width, bar_height), 2)
        
        # Dibujar icono si está disponible
        if 'repair_bar' in self.assets:
            icon = self.assets['repair_bar']
            icon_rect = icon.get_rect()
            icon_rect.midleft = (x - 40, y + bar_height // 2)
            self.screen.blit(icon, icon_rect)
        
        # Dibujar texto con porcentaje
        text = f"Reparación: {self.game_state.repair_progress:.0f}%"
        text_surface = self.font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.midleft = (x + bar_width + 10, y + bar_height // 2)
        self.screen.blit(text_surface, text_rect)
        
        # Mostrar mensaje de victoria si está completo
        if self.game_state.repair_progress >= 100 and 'repair_msg' in self.assets:
            msg = self.assets['repair_msg']
            msg_rect = msg.get_rect()
            msg_rect.center = (self.screen_width // 2, self.screen_height // 2 - 100)
            self.screen.blit(msg, msg_rect)
    
    def render_exchange_button(self) -> None:
        """Renderiza el botón de intercambio de materiales por oxígeno"""
        if not self.game_state:
            return
        
        # Posición: justo debajo de la barra de reparación
        x, y = self.repair_bar_pos
        button_y = y + 45  # 45 píxeles debajo de la barra de reparación
        button_x = x
        button_width = 250
        button_height = 35
        
        # Determinar si el botón está habilitado
        is_enabled = (self.game_state.materials > 0 and 
                     self.game_state.oxygen < 100 and 
                     self.game_state.current_phase == "main_game")
        
        # Color del botón según estado
        if is_enabled:
            button_color = (50, 100, 150)  # Azul
            text_color = (255, 255, 255)
            border_color = (100, 150, 200)
        else:
            button_color = (60, 60, 60)  # Gris oscuro
            text_color = (120, 120, 120)
            border_color = (80, 80, 80)
        
        # Dibujar botón
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        pygame.draw.rect(self.screen, button_color, button_rect)
        pygame.draw.rect(self.screen, border_color, button_rect, 2)
        
        # Texto del botón
        button_text = "🪙 Conseguir Oxígeno [O]"
        text_surface = self.small_font.render(button_text, True, text_color)
        text_rect = text_surface.get_rect()
        text_rect.center = button_rect.center
        self.screen.blit(text_surface, text_rect)
        
        # Texto de ayuda debajo del botón (solo si está habilitado)
        if is_enabled:
            help_text = f"(Tienes {self.game_state.materials} materiales)"
            help_surface = self.small_font.render(help_text, True, (150, 150, 150))
            help_rect = help_surface.get_rect()
            help_rect.midleft = (button_x, button_y + button_height + 12)
            self.screen.blit(help_surface, help_rect)
        elif self.game_state.oxygen >= 100:
            help_text = "(Oxígeno al máximo)"
            help_surface = self.small_font.render(help_text, True, (100, 200, 100))
            help_rect = help_surface.get_rect()
            help_rect.midleft = (button_x, button_y + button_height + 12)
            self.screen.blit(help_surface, help_rect)
        elif self.game_state.materials <= 0:
            help_text = "(Sin materiales)"
            help_surface = self.small_font.render(help_text, True, (150, 150, 150))
            help_rect = help_surface.get_rect()
            help_rect.midleft = (button_x, button_y + button_height + 12)
            self.screen.blit(help_surface, help_rect)
    
    def render_debt_summary(self) -> None:
        """Renderiza resumen de deudas activas"""
        if not self.loan_manager:
            return
        
        x = 20
        y = 200
        
        # Título
        title = "Préstamos Activos:"
        title_surface = self.font.render(title, True, (255, 200, 100))
        self.screen.blit(title_surface, (x, y))
        y += 30
        
        # Listar préstamos activos (simplificado)
        total_debt = 0
        for i, loan in enumerate(self.loan_manager.active_loans[:3]):  # Máximo 3 visibles
            # Obtener información del préstamo
            creditor = loan.creditor_name
            debt_materials = int(loan.current_balance * 1.5)  # Conversión simplificada
            total_debt += debt_materials
            
            # Color según urgencia
            if loan.turns_until_due <= 2:
                color = (255, 100, 100)  # Rojo
            elif loan.turns_until_due <= 5:
                color = (255, 255, 100)  # Amarillo
            else:
                color = (200, 200, 200)  # Gris claro
            
            # Texto del préstamo
            loan_text = f"  {creditor}: {debt_materials} mat. (Turno {loan.turns_until_due})"
            text_surface = self.small_font.render(loan_text, True, color)
            self.screen.blit(text_surface, (x, y))
            y += 20
        
        # Mostrar deuda total
        if total_debt > 0:
            y += 10
            total_text = f"Total a pagar: {total_debt} materiales"
            color = (255, 100, 100) if total_debt > self.game_state.materials else (255, 255, 255)
            total_surface = self.font.render(total_text, True, color)
            self.screen.blit(total_surface, (x, y))
    
    def render_turn_info(self) -> None:
        """Renderiza información del turno actual"""
        if not self.game_state:
            return
        
        x, y = self.turn_info_pos
        
        # Mostrar turno
        turn_text = f"Turno: {self.game_state.turn_number}"
        text_surface = self.font.render(turn_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.topright = (x + 180, y)
        self.screen.blit(text_surface, text_rect)
        
        # Mostrar fase actual
        phase_text = f"Fase: {self.game_state.current_phase}"
        phase_surface = self.small_font.render(phase_text, True, (200, 200, 200))
        phase_rect = phase_surface.get_rect()
        phase_rect.topright = (x + 180, y + 25)
        self.screen.blit(phase_surface, phase_rect)
    
    def render_notifications(self) -> None:
        """Renderiza notificaciones flotantes"""
        y_offset = 300
        
        # Renderizar notificaciones activas
        for i, notification in enumerate(self.notifications[:5]):  # Máximo 5 notificaciones
            # Calcular opacidad basada en tiempo restante
            alpha = min(255, notification['time_remaining'] * 255 / notification['duration'])
            
            # Color según tipo
            colors = {
                'info': (255, 255, 255),
                'success': (100, 255, 100),
                'warning': (255, 255, 100),
                'error': (255, 100, 100)
            }
            color = colors.get(notification['type'], (255, 255, 255))
            
            # Crear superficie con transparencia
            text_surface = self.font.render(notification['message'], True, color)
            text_surface.set_alpha(int(alpha))
            
            # Posicionar y dibujar
            x = self.screen_width // 2 - text_surface.get_width() // 2
            y = y_offset + i * 35
            
            # Fondo semi-transparente
            bg_rect = pygame.Rect(x - 10, y - 5, text_surface.get_width() + 20, 30)
            pygame.draw.rect(self.screen, (0, 0, 0), bg_rect)
            pygame.draw.rect(self.screen, color, bg_rect, 1)
            
            self.screen.blit(text_surface, (x, y))
    
    def add_notification(self, message: str, notification_type: str = 'info', duration: float = 3.0) -> None:
        """
        Añade una notificación al HUD
        
        Args:
            message: Mensaje a mostrar
            notification_type: Tipo (info, warning, error, success)
            duration: Duración en segundos
        """
        notification = {
            'message': message,
            'type': notification_type,
            'duration': duration,
            'time_remaining': duration
        }
        self.notifications.insert(0, notification)
        logger.info(f"Notificación: {message}")
        
        # Limitar número de notificaciones
        if len(self.notifications) > 10:
            self.notifications = self.notifications[:10]
    
    def render_inventory_panel(self) -> None:
        """Renderiza el panel detallado de inventario (simplificado)"""
        # Panel de fondo
        panel_rect = pygame.Rect(100, 100, 400, 300)
        pygame.draw.rect(self.screen, (20, 20, 40), panel_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), panel_rect, 2)
        
        # Título
        title = "Inventario"
        title_surface = self.large_font.render(title, True, (255, 255, 255))
        title_rect = title_surface.get_rect()
        title_rect.centerx = panel_rect.centerx
        title_rect.top = panel_rect.top + 20
        self.screen.blit(title_surface, title_rect)
        
        # Contenido simplificado
        y = panel_rect.top + 80
        
        # Materiales
        materials_text = f"Materiales Genéricos: {self.game_state.materials}/{self.game_state.max_materials}"
        text_surface = self.font.render(materials_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.centerx = panel_rect.centerx
        text_rect.top = y
        self.screen.blit(text_surface, text_rect)
        
        y += 40
        info_text = "Los materiales se obtienen minando y se usan para:"
        info_surface = self.small_font.render(info_text, True, (200, 200, 200))
        info_rect = info_surface.get_rect()
        info_rect.centerx = panel_rect.centerx
        info_rect.top = y
        self.screen.blit(info_surface, info_rect)
        
        y += 30
        uses = [
            "- Reparar la nave (objetivo principal)",
            "- Pagar préstamos de oxígeno"
        ]
        for use in uses:
            use_surface = self.small_font.render(use, True, (180, 180, 180))
            use_rect = use_surface.get_rect()
            use_rect.left = panel_rect.left + 40
            use_rect.top = y
            self.screen.blit(use_surface, use_rect)
            y += 25
        
        # Botón de cerrar
        close_text = "[ESC] Cerrar"
        close_surface = self.small_font.render(close_text, True, (255, 255, 100))
        close_rect = close_surface.get_rect()
        close_rect.centerx = panel_rect.centerx
        close_rect.bottom = panel_rect.bottom - 20
        self.screen.blit(close_surface, close_rect)
    
    def render_debt_panel(self) -> None:
        """Renderiza el panel detallado de deudas"""
        if not self.loan_manager:
            return
        
        # Panel de fondo
        panel_rect = pygame.Rect(self.screen_width // 2 - 250, 100, 500, 400)
        pygame.draw.rect(self.screen, (40, 20, 20), panel_rect)
        pygame.draw.rect(self.screen, (255, 200, 100), panel_rect, 2)
        
        # Título
        title = "Préstamos Activos"
        title_surface = self.large_font.render(title, True, (255, 200, 100))
        title_rect = title_surface.get_rect()
        title_rect.centerx = panel_rect.centerx
        title_rect.top = panel_rect.top + 20
        self.screen.blit(title_surface, title_rect)
        
        # Listar préstamos
        y = panel_rect.top + 80
        
        if not self.loan_manager.active_loans:
            no_loans_text = "No tienes préstamos activos"
            text_surface = self.font.render(no_loans_text, True, (200, 200, 200))
            text_rect = text_surface.get_rect()
            text_rect.centerx = panel_rect.centerx
            text_rect.top = y
            self.screen.blit(text_surface, text_rect)
        else:
            for loan in self.loan_manager.active_loans:
                # Información del préstamo
                loan_info = [
                    f"Acreedor: {loan.creditor_name}",
                    f"Oxígeno prestado: {loan.principal:.0f}",
                    f"Materiales a pagar: {int(loan.current_balance * 1.5)}",
                    f"Turnos restantes: {loan.turns_until_due}",
                    f"Interés: {loan.interest_rate * 100:.0f}%"
                ]
                
                for info in loan_info:
                    text_surface = self.small_font.render(info, True, (255, 255, 255))
                    text_rect = text_surface.get_rect()
                    text_rect.left = panel_rect.left + 40
                    text_rect.top = y
                    self.screen.blit(text_surface, text_rect)
                    y += 20
                
                y += 20  # Espacio entre préstamos
        
        # Botón de cerrar
        close_text = "[ESC] Cerrar"
        close_surface = self.small_font.render(close_text, True, (255, 255, 100))
        close_rect = close_surface.get_rect()
        close_rect.centerx = panel_rect.centerx
        close_rect.bottom = panel_rect.bottom - 20
        self.screen.blit(close_surface, close_rect)
    
    def render_repair_panel(self) -> None:
        """Renderiza el panel detallado de reparación"""
        # Panel de fondo
        panel_rect = pygame.Rect(self.screen_width // 2 - 200, 150, 400, 300)
        pygame.draw.rect(self.screen, (20, 30, 40), panel_rect)
        pygame.draw.rect(self.screen, (100, 200, 255), panel_rect, 2)
        
        # Título
        title = "Estado de Reparación"
        title_surface = self.large_font.render(title, True, (100, 200, 255))
        title_rect = title_surface.get_rect()
        title_rect.centerx = panel_rect.centerx
        title_rect.top = panel_rect.top + 20
        self.screen.blit(title_surface, title_rect)
        
        # Progreso actual
        y = panel_rect.top + 80
        
        progress_text = f"Progreso Total: {self.game_state.repair_progress:.0f}%"
        text_surface = self.font.render(progress_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.centerx = panel_rect.centerx
        text_rect.top = y
        self.screen.blit(text_surface, text_rect)
        
        y += 40
        
        # Información sobre reparación
        info_lines = [
            "Para reparar la nave necesitas:",
            "- Materiales (5-10 por intento)",
            "- Oxígeno (3 por intento)",
            "",
            "Presiona [R] para iniciar reparación",
            "Objetivo: Alcanzar 100% para ganar"
        ]
        
        for line in info_lines:
            if line:
                line_surface = self.small_font.render(line, True, (200, 200, 200))
                line_rect = line_surface.get_rect()
                line_rect.centerx = panel_rect.centerx
                line_rect.top = y
                self.screen.blit(line_surface, line_rect)
            y += 25
        
        # Botón de cerrar
        close_text = "[ESC] Cerrar"
        close_surface = self.small_font.render(close_text, True, (255, 255, 100))
        close_rect = close_surface.get_rect()
        close_rect.centerx = panel_rect.centerx
        close_rect.bottom = panel_rect.bottom - 20
        self.screen.blit(close_surface, close_rect)
    
    def render_action_menu(self) -> None:
        """Renderiza el menú de acciones disponibles"""
        x, y = self.action_menu_pos
        
        # Fondo del menú
        menu_rect = pygame.Rect(x, y, 300, 80)
        pygame.draw.rect(self.screen, (30, 30, 50), menu_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), menu_rect, 2)
        
        # Título
        title = "Acciones Disponibles:"
        title_surface = self.font.render(title, True, (255, 255, 255))
        title_rect = title_surface.get_rect()
        title_rect.centerx = menu_rect.centerx
        title_rect.top = menu_rect.top + 10
        self.screen.blit(title_surface, title_rect)
        
        # Opciones
        actions = [
            "[M] Minar Materiales (Costo: 12-15 Oxígeno)",
            "[R] Reparar Nave (Costo: 12-15 Ox + 5-10 Mat)"
        ]
        
        y_offset = 35
        for action in actions:
            action_surface = self.small_font.render(action, True, (200, 200, 200))
            action_rect = action_surface.get_rect()
            action_rect.centerx = menu_rect.centerx
            action_rect.top = menu_rect.top + y_offset
            self.screen.blit(action_surface, action_rect)
            y_offset += 20
    
    def toggle_inventory(self) -> None:
        """Alterna la visibilidad del panel de inventario"""
        self.show_inventory = not self.show_inventory
        self.show_debt_panel = False
        self.show_repair_panel = False
    
    def toggle_debt_panel(self) -> None:
        """Alterna la visibilidad del panel de deudas"""
        self.show_debt_panel = not self.show_debt_panel
        self.show_inventory = False
        self.show_repair_panel = False
    
    def toggle_repair_panel(self) -> None:
        """Alterna la visibilidad del panel de reparación"""
        self.show_repair_panel = not self.show_repair_panel
        self.show_inventory = False
        self.show_debt_panel = False
    
    def close_all_panels(self) -> None:
        """Cierra todos los paneles activos"""
        self.show_inventory = False
        self.show_debt_panel = False
        self.show_repair_panel = False
    
    def open_exchange_modal(self) -> None:
        """Abre el modal de intercambio de materiales por oxígeno"""
        if not self.game_state:
            return
        
        # Verificar si el oxígeno ya está al máximo
        if self.game_state.oxygen >= 100:
            self.add_notification("Tu oxígeno ya está al 100% ✅", "info")
            return
        
        # Verificar si tiene materiales
        if self.game_state.materials <= 0:
            self.add_notification("No tienes materiales para vender ❌", "error")
            return
        
        if self.game_state.current_phase == "minigame":
            return
        
        self.show_exchange_modal = True
        self.exchange_amount = 0
        logger.info("Modal de intercambio abierto")
    
    def close_exchange_modal(self) -> None:
        """Cierra el modal de intercambio"""
        self.show_exchange_modal = False
        self.exchange_amount = 0
        self.exchange_slider_dragging = False
        logger.info("Modal de intercambio cerrado")
    
    def confirm_exchange(self) -> None:
        """Confirma el intercambio de materiales por oxígeno"""
        if not self.game_state or self.exchange_amount <= 0:
            return
        
        # Verificar si el oxígeno ya está al máximo
        if self.game_state.oxygen >= 100:
            self.add_notification("Tu oxígeno ya está al 100% ✅", "info")
            self.close_exchange_modal()
            return
        
        if self.exchange_amount > self.game_state.materials:
            self.add_notification("Cantidad no válida ❌", "error")
            return
        
        # Realizar el intercambio: 1 material = 5 oxígeno
        materials_to_sell = self.exchange_amount
        
        # Calcular oxígeno que se ganaría (1 material = 5 oxígeno)
        oxygen_gained = materials_to_sell * 5
        
        # Verificar que no se exceda el máximo de oxígeno
        oxygen_available = 100 - self.game_state.oxygen
        if oxygen_gained > oxygen_available:
            # Ajustar la cantidad para no exceder 100
            oxygen_gained = int(oxygen_available)
            # Calcular cuántos materiales se necesitan realmente
            materials_to_sell = (oxygen_gained + 4) // 5  # Redondear hacia arriba
            
            if materials_to_sell <= 0:
                self.add_notification("Tu oxígeno ya está al 100% ✅", "info")
                self.close_exchange_modal()
                return
        
        self.game_state.consume_materials(materials_to_sell)
        self.game_state.update_oxygen(float(oxygen_gained))
        
        self.add_notification(f"+{oxygen_gained:.1f} oxígeno conseguido 🫧", "success")
        logger.info(f"Intercambio realizado: {materials_to_sell} materiales por {oxygen_gained:.1f} oxígeno")
        
        self.close_exchange_modal()
    
    def update(self, delta_time: float) -> None:
        """
        Actualiza animaciones y timers del HUD
        
        Args:
            delta_time: Tiempo transcurrido
        """
        # Actualizar timers de notificaciones
        for notification in self.notifications[:]:
            notification['time_remaining'] -= delta_time
            if notification['time_remaining'] <= 0:
                self.notifications.remove(notification)
    
    def handle_input(self, event: pygame.event.Event) -> None:
        """
        Maneja input del usuario para el HUD
        
        Args:
            event: Evento de Pygame
        """
        # NO procesar inputs del HUD durante minijuegos
        if self.game_state and self.game_state.current_phase == "minigame":
            return
        
        # Manejar eventos del modal de intercambio si está activo
        if self.show_exchange_modal:
            self._handle_exchange_modal_input(event)
            return
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_i:
                self.toggle_inventory()
            elif event.key == pygame.K_d:
                self.toggle_debt_panel()
            elif event.key == pygame.K_p:
                self.toggle_repair_panel()
            elif event.key == pygame.K_o:
                # Abrir modal de intercambio
                self.open_exchange_modal()
            elif event.key == pygame.K_ESCAPE:
                # Cerrar todos los paneles
                self.show_inventory = False
                self.show_debt_panel = False
                self.show_repair_panel = False
    
    def _load_assets(self) -> None:
        """Carga los assets del HUD"""
        asset_files = {
            'oxygen_bar': 'oxygen_bar.png',
            'materials_bar': 'materials_bar.png',
            'repair_bar': 'repair_bar.png',
            'alert_oxygen': 'alert_oxygen.png',
            'alert_materials': 'alert_materials.png',
            'repair_msg': 'repair_msg.png'
        }
        
        for key, filename in asset_files.items():
            path = os.path.join('data', 'assets', filename)
            try:
                if os.path.exists(path):
                    image = pygame.image.load(path)
                    # Escalar iconos a tamaño apropiado
                    if 'alert' in key or 'bar' in key:
                        image = pygame.transform.scale(image, (32, 32))
                    elif 'msg' in key:
                        image = pygame.transform.scale(image, (300, 100))
                    self.assets[key] = image
                    logger.debug(f"Asset cargado: {filename}")
            except Exception as e:
                logger.warning(f"No se pudo cargar asset {filename}: {e}")
    
    def _calculate_max_materials_to_sell(self) -> int:
        """Calcula el máximo de materiales que se pueden vender sin exceder 100 de oxígeno"""
        if not self.game_state:
            return 0
        
        # Calcular cuánto oxígeno falta para llegar a 100
        oxygen_needed = 100 - self.game_state.oxygen
        
        # Calcular cuántos materiales se necesitan para ese oxígeno
        # 1 material = 5 oxígeno, entonces materiales = oxígeno / 5 (redondeado hacia arriba)
        max_materials_for_oxygen = (int(oxygen_needed) + 4) // 5
        
        # El máximo es el menor entre los materiales disponibles y los necesarios
        return min(self.game_state.materials, max_materials_for_oxygen)
    
    def _handle_exchange_modal_input(self, event: pygame.event.Event) -> None:
        """Maneja inputs dentro del modal de intercambio"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.close_exchange_modal()
            elif event.key == pygame.K_RETURN:
                self.confirm_exchange()
            elif event.key == pygame.K_LEFT:
                self.exchange_amount = max(0, self.exchange_amount - 1)
            elif event.key == pygame.K_RIGHT:
                if self.game_state:
                    max_materials = self._calculate_max_materials_to_sell()
                    self.exchange_amount = min(max_materials, self.exchange_amount + 1)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Click izquierdo
                self._handle_exchange_modal_click(event.pos)
        
        elif event.type == pygame.MOUSEMOTION:
            if self.exchange_slider_dragging:
                self._handle_slider_drag(event.pos)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.exchange_slider_dragging = False
    
    def _handle_exchange_modal_click(self, mouse_pos: Tuple[int, int]) -> None:
        """Maneja clicks dentro del modal"""
        # Calcular posiciones de los botones
        modal_rect = pygame.Rect(
            self.screen_width // 2 - 250,
            self.screen_height // 2 - 200,
            500,
            400
        )
        
        # Botón confirmar
        confirm_btn = pygame.Rect(
            modal_rect.centerx - 210,
            modal_rect.bottom - 60,
            200,
            50
        )
        
        # Botón cancelar
        cancel_btn = pygame.Rect(
            modal_rect.centerx + 10,
            modal_rect.bottom - 60,
            200,
            50
        )
        
        # Slider
        slider_rect = pygame.Rect(
            modal_rect.left + 50,
            modal_rect.centery - 20,
            modal_rect.width - 100,
            40
        )
        
        if confirm_btn.collidepoint(mouse_pos):
            self.confirm_exchange()
        elif cancel_btn.collidepoint(mouse_pos):
            self.close_exchange_modal()
        elif slider_rect.collidepoint(mouse_pos):
            self.exchange_slider_dragging = True
            self._handle_slider_drag(mouse_pos)
    
    def _handle_slider_drag(self, mouse_pos: Tuple[int, int]) -> None:
        """Maneja el arrastre del slider"""
        if not self.game_state:
            return
        
        modal_rect = pygame.Rect(
            self.screen_width // 2 - 250,
            self.screen_height // 2 - 200,
            500,
            400
        )
        
        slider_start_x = modal_rect.left + 50
        slider_width = modal_rect.width - 100
        
        # Calcular posición relativa en el slider
        relative_x = mouse_pos[0] - slider_start_x
        percentage = max(0.0, min(1.0, relative_x / slider_width))
        
        # Calcular el máximo de materiales que se pueden vender
        max_materials = self._calculate_max_materials_to_sell()
        
        self.exchange_amount = int(percentage * max_materials)
    
    def render_exchange_modal(self) -> None:
        """Renderiza el modal de intercambio de materiales por oxígeno"""
        if not self.game_state:
            return
        
        # Overlay semitransparente
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))
        
        # Ventana modal
        modal_rect = pygame.Rect(
            self.screen_width // 2 - 250,
            self.screen_height // 2 - 200,
            500,
            400
        )
        
        # Fondo del modal
        pygame.draw.rect(self.screen, (40, 50, 70), modal_rect)
        pygame.draw.rect(self.screen, (100, 150, 200), modal_rect, 3)
        
        # Título
        title_text = "Intercambiar materiales por oxígeno"
        title_surface = self.large_font.render(title_text, True, (255, 255, 255))
        title_rect = title_surface.get_rect()
        title_rect.centerx = modal_rect.centerx
        title_rect.top = modal_rect.top + 20
        self.screen.blit(title_surface, title_rect)
        
        # Materiales disponibles y máximo que se puede vender
        max_materials = self._calculate_max_materials_to_sell()
        materials_text = f"Materiales disponibles: {self.game_state.materials} (máx. vender: {max_materials})"
        materials_surface = self.font.render(materials_text, True, (200, 200, 255))
        materials_rect = materials_surface.get_rect()
        materials_rect.centerx = modal_rect.centerx
        materials_rect.top = title_rect.bottom + 30
        self.screen.blit(materials_surface, materials_rect)
        
        # Slider para seleccionar cantidad
        slider_y = modal_rect.centery - 20
        slider_rect = pygame.Rect(
            modal_rect.left + 50,
            slider_y,
            modal_rect.width - 100,
            40
        )
        
        # Fondo del slider
        pygame.draw.rect(self.screen, (60, 70, 90), slider_rect)
        pygame.draw.rect(self.screen, (150, 150, 150), slider_rect, 2)
        
        # Indicador del slider
        if max_materials > 0:
            slider_percentage = self.exchange_amount / max_materials
            indicator_x = slider_rect.left + int(slider_percentage * slider_rect.width)
            indicator_rect = pygame.Rect(indicator_x - 5, slider_rect.top - 5, 10, slider_rect.height + 10)
            pygame.draw.rect(self.screen, (100, 200, 255), indicator_rect)
        
        # Cantidad seleccionada
        amount_text = f"Cantidad a vender: {self.exchange_amount}"
        amount_surface = self.font.render(amount_text, True, (255, 255, 255))
        amount_rect = amount_surface.get_rect()
        amount_rect.centerx = modal_rect.centerx
        amount_rect.top = slider_rect.bottom + 20
        self.screen.blit(amount_surface, amount_rect)
        
        # Oxígeno a recibir (siempre números enteros)
        materials_actual = self.exchange_amount
        
        oxygen_to_receive = materials_actual * 5  # 1 material = 5 oxígeno
        
        # Verificar límite de oxígeno
        oxygen_available = 100 - self.game_state.oxygen
        if oxygen_to_receive > oxygen_available:
            oxygen_to_receive = int(oxygen_available)
        
        oxygen_text = f"Recibirás: {oxygen_to_receive} oxígeno"
        oxygen_surface = self.large_font.render(oxygen_text, True, (100, 255, 200))
        oxygen_rect = oxygen_surface.get_rect()
        oxygen_rect.centerx = modal_rect.centerx
        oxygen_rect.top = amount_rect.bottom + 15
        self.screen.blit(oxygen_surface, oxygen_rect)
        
        # Tasa de cambio
        rate_text = "(Tasa: 1 material = 5 oxígeno)"
        rate_surface = self.small_font.render(rate_text, True, (180, 180, 180))
        rate_rect = rate_surface.get_rect()
        rate_rect.centerx = modal_rect.centerx
        rate_rect.top = oxygen_rect.bottom + 5
        self.screen.blit(rate_surface, rate_rect)
        
        # Botones
        # Botón confirmar
        confirm_btn = pygame.Rect(
            modal_rect.centerx - 210,
            modal_rect.bottom - 60,
            200,
            50
        )
        confirm_color = (50, 200, 100) if self.exchange_amount > 0 else (100, 100, 100)
        pygame.draw.rect(self.screen, confirm_color, confirm_btn)
        pygame.draw.rect(self.screen, (255, 255, 255), confirm_btn, 2)
        
        confirm_text = "✅ Confirmar"
        confirm_surface = self.font.render(confirm_text, True, (255, 255, 255))
        confirm_text_rect = confirm_surface.get_rect()
        confirm_text_rect.center = confirm_btn.center
        self.screen.blit(confirm_surface, confirm_text_rect)
        
        # Botón cancelar
        cancel_btn = pygame.Rect(
            modal_rect.centerx + 10,
            modal_rect.bottom - 60,
            200,
            50
        )
        pygame.draw.rect(self.screen, (200, 50, 50), cancel_btn)
        pygame.draw.rect(self.screen, (255, 255, 255), cancel_btn, 2)
        
        cancel_text = "❌ Cancelar"
        cancel_surface = self.font.render(cancel_text, True, (255, 255, 255))
        cancel_text_rect = cancel_surface.get_rect()
        cancel_text_rect.center = cancel_btn.center
        self.screen.blit(cancel_surface, cancel_text_rect)
        
        # Instrucciones
        instructions = "[←/→] Ajustar cantidad | [ENTER] Confirmar | [ESC] Cancelar"
        inst_surface = self.small_font.render(instructions, True, (180, 180, 180))
        inst_rect = inst_surface.get_rect()
        inst_rect.centerx = modal_rect.centerx
        inst_rect.bottom = modal_rect.bottom - 10
        self.screen.blit(inst_surface, inst_rect)

