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
        
        # Assets del HUD
        self.assets = {}
        
        # Posiciones de elementos del HUD
        self.oxygen_bar_pos = (20, 20)
        self.materials_pos = (20, 80)
        self.repair_bar_pos = (20, 140)
        self.turn_info_pos = (self.screen_width - 200, 20)
        self.action_menu_pos = (self.screen_width // 2 - 150, self.screen_height - 100)
    
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
        self.render_turn_info()
        
        # Renderizar información de deudas si hay préstamos activos
        if self.loan_manager and self.loan_manager.active_loans:
            self.render_debt_summary()
        
        # Renderizar menú de acciones si está en fase principal
        if self.game_state.current_phase == "main_game" and self.show_action_menu:
            self.render_action_menu()
        
        # Renderizar notificaciones
        self.render_notifications()
        
        # Renderizar paneles activos
        if self.show_inventory:
            self.render_inventory_panel()
        if self.show_debt_panel:
            self.render_debt_panel()
        if self.show_repair_panel:
            self.render_repair_panel()
    
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
            "[M] Minar Materiales (Costo: 2 Oxígeno)",
            "[R] Reparar Nave (Costo: 3 Ox + 5-10 Mat)"
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
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_i:
                self.toggle_inventory()
            elif event.key == pygame.K_d:
                self.toggle_debt_panel()
            elif event.key == pygame.K_p:
                self.toggle_repair_panel()
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

