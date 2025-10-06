"""
Renderer - Motor de Renderizado
Gestiona el renderizado de todos los elementos visuales del juego
"""

import pygame
import os
import math
import random
from typing import Optional, Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class Renderer:
    """
    Motor de renderizado principal del juego
    
    Responsabilidades:
        - Inicializar pantalla de Pygame
        - Renderizar fondo, nave, efectos
        - Gestionar capas de renderizado
        - Manejar transiciones y efectos visuales
    
    Dependencias:
        - pygame: Para gráficos
        - engine.state.GameState: Para obtener estado visual
    """
    
    def __init__(self, screen_width: int = 1280, screen_height: int = 720):
        """
        Inicializa el renderer
        
        Args:
            screen_width: Ancho de la pantalla
            screen_height: Alto de la pantalla
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen: Optional[pygame.Surface] = None
        
        # Capas de renderizado
        self.background_layer = None
        self.game_layer = None
        self.ui_layer = None
        self.effect_layer = None
        
        # Estado visual
        self.camera_offset = [0, 0]
        self.shake_intensity = 0.0
        self.shake_duration = 0.0
        
        # Assets del juego
        self.assets: Dict[str, pygame.Surface] = {}
        
        # Estrellas de fondo
        self.stars: List[Tuple[int, int, int]] = []
        
        # Animaciones
        self.ship_animation_time = 0.0
        self.intro_animation_time = 0.0
        self.intro_complete = False
        self.impact_shake_applied = False  # Para aplicar shake solo una vez
        
        # Animación de victoria (despegue hacia la Tierra)
        self.victory_animation_time = 0.0
        self.victory_animation_active = False
        self.show_return_home_button = False
        self.victory_animation_complete = False
        
        # Sistema de prestamista visual
        self.lender_visible = False
        self.lender_type = None  # 'zorvax', 'ktarr', 'consorcio'
        self.lender_animation_time = 0.0
        self.lender_waiting_for_input = False  # Esperando que jugador presione continuar
        
        # Modo testing: Mostrar todos los prestamistas
        self.show_all_lenders_testing = False
        
        # Referencias
        self.game_state = None
    
    def initialize(self, screen: pygame.Surface) -> None:
        """Inicializa el renderer con la pantalla
        
        Args:
            screen: Superficie de Pygame para renderizar
        """
        self.screen = screen
        
        # Crear capas
        self.background_layer = pygame.Surface((self.screen_width, self.screen_height))
        self.game_layer = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        self.ui_layer = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        self.effect_layer = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        
        # Cargar assets
        self._load_assets()
        
        # Generar estrellas de fondo
        self._generate_stars()
        
        logger.info("Renderer inicializado")
    
    def render_frame(self) -> None:
        """Renderiza un frame completo del juego principal"""
        if not self.screen:
            return
        
        # Limpiar capas
        self.game_layer.fill((0, 0, 0, 0))
        self.effect_layer.fill((0, 0, 0, 0))
        
        # Renderizar fondo
        self.render_background()
        
        # Renderizar elementos del juego EN ORDEN (fondo a frente)
        # 1. Primero el terreno/luna (al fondo)
        self.render_environment()
        # 2. Luego nave y jugador (sobre el terreno)
        self.render_ship()
        
        # Modo testing: Mostrar todos los prestamistas
        if self.show_all_lenders_testing:
            self.render_all_lenders_display()
        
        # Renderizar efectos
        self.render_effects()
        
        # NO aplicar shake durante el juego normal
        # El shake solo debe aplicarse durante la intro o eventos críticos
        offset_x, offset_y = 0, 0
        
        # Componer capas en pantalla SIN shake
        self.screen.blit(self.background_layer, (offset_x, offset_y))
        self.screen.blit(self.game_layer, (offset_x, offset_y))
        self.screen.blit(self.effect_layer, (0, 0))
        self.screen.blit(self.ui_layer, (0, 0))
        
        # Renderizar prestamista si está visible (sobre todo)
        if self.lender_visible:
            self.render_lender()
    
    def render_background(self) -> None:
        """Renderiza el fondo espacial con estrellas"""
        # Usar asset de fondo si está disponible
        if 'space_background' in self.assets:
            bg = self.assets['space_background']
            # Escalar para cubrir toda la pantalla
            bg_scaled = pygame.transform.scale(bg, (self.screen_width, self.screen_height))
            self.background_layer.blit(bg_scaled, (0, 0))
        else:
            # Fondo degradado de negro a azul oscuro
            for y in range(self.screen_height):
                color_value = int(20 * (1 - y / self.screen_height))
                color = (0, 0, color_value)
                pygame.draw.line(self.background_layer, color, (0, y), (self.screen_width, y))
        
        # Dibujar estrellas
        for star in self.stars:
            x, y, size = star
            brightness = random.randint(150, 255)
            pygame.draw.circle(self.background_layer, (brightness, brightness, brightness), (x, y), size)
    
    def render_ship(self) -> None:
        """Renderiza la nave espacial del jugador SOBRE la luna"""
        if 'blue_spaceship' not in self.assets:
            return
        
        ship = self.assets['blue_spaceship']
        
        # Posición de la nave SOBRE la luna
        ship_x = self.screen_width // 2 - 60
        # La luna está en screen_height - 50 (bottom), con altura ~150
        # Queremos que la nave esté sobre la luna
        base_moon_top = self.screen_height - 200  # Aproximadamente el top de la luna
        ship_y = base_moon_top - 30  # 30px sobre la superficie lunar
        
        # Aplicar efecto de daño según el progreso de reparación
        if self.game_state:
            repair_percent = self.game_state.repair_progress / 100.0
            
            # Tinte rojo para nave dañada
            if repair_percent < 0.5:
                ship_copy = ship.copy()
                # Aplicar tinte rojo
                red_overlay = pygame.Surface(ship.get_size(), pygame.SRCALPHA)
                red_overlay.fill((255, 0, 0, int(100 * (1 - repair_percent * 2))))
                ship_copy.blit(red_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                ship = ship_copy
            
            # Animación de flotación suave
            self.ship_animation_time += 0.02
            float_offset = math.sin(self.ship_animation_time) * 3
            ship_y += int(float_offset)
        
        # Dibujar nave inclinada (como si estuviera estrellada)
        ship_rotated = pygame.transform.rotate(ship, 8)  # Leve inclinación
        ship_rect = ship_rotated.get_rect()
        ship_rect.centerx = ship_x
        ship_rect.bottom = int(ship_y) + 50  # bottom en lugar de center para mejor posicionamiento
        self.game_layer.blit(ship_rotated, ship_rect)
        
        # Dibujar jugador cerca de la nave, SOBRE la luna
        if 'player' in self.assets:
            player = self.assets['player']
            player_rect = player.get_rect()
            player_rect.centerx = ship_x + 80
            player_rect.bottom = int(ship_y) + 70  # Al lado y un poco más abajo que la nave
            self.game_layer.blit(player, player_rect)
    
    def render_environment(self) -> None:
        """Renderiza el terreno lunar y elementos del entorno (CAPA DE FONDO)"""
        # Dibujar superficie lunar EN LA CAPA DE FONDO
        if 'landing_moon' in self.assets:
            moon = self.assets['landing_moon']
            moon_rect = moon.get_rect()
            moon_rect.bottom = self.screen_height - 50
            moon_rect.centerx = self.screen_width // 2
            self.game_layer.blit(moon, moon_rect)
        
        # Dibujar minerales decorativos SOBRE la luna (solo visual)
        mineral_assets = ['copper_mineral', 'silver_mineral', 'gold_mineral']
        # Posiciones relativas a la superficie de la luna
        base_y = self.screen_height - 150  # Un poco sobre la luna
        positions = [(300, base_y), 
                    (500, base_y - 10),
                    (700, base_y + 5)]
        
        for i, mineral_name in enumerate(mineral_assets):
            if mineral_name in self.assets and i < len(positions):
                mineral = self.assets[mineral_name]
                mineral_scaled = pygame.transform.scale(mineral, (30, 30))
                pos = positions[i]
                self.game_layer.blit(mineral_scaled, pos)
    
    def render_effects(self) -> None:
        """Renderiza efectos visuales"""
        # Efecto de partículas si el oxígeno es bajo
        if self.game_state and self.game_state.oxygen < 20:
            # Efecto de alerta visual
            alert_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            alert_surface.fill((255, 0, 0, 20))  # Tinte rojo semi-transparente
            self.effect_layer.blit(alert_surface, (0, 0))
            
            # Parpadeo de borde
            if int(pygame.time.get_ticks() / 500) % 2 == 0:
                pygame.draw.rect(self.effect_layer, (255, 0, 0), 
                               (0, 0, self.screen_width, self.screen_height), 3)
    
    def render_intro(self) -> None:
        """Renderiza la pantalla de introducción con animación mejorada"""
        if not self.screen:
            return
        
        # Crear superficie temporal para evitar problemas de shake
        intro_surface = pygame.Surface((self.screen_width, self.screen_height))
        
        # Renderizar fondo en la superficie temporal
        if 'space_background' in self.assets:
            bg = self.assets['space_background']
            bg_scaled = pygame.transform.scale(bg, (self.screen_width, self.screen_height))
            intro_surface.blit(bg_scaled, (0, 0))
        else:
            intro_surface.fill((10, 10, 30))
        
        # Animación de crash
        if not self.intro_complete:
            self.intro_animation_time += 0.016  # ~60fps
            
            # Fase 1: Nave entrando desde la derecha (0-2 segundos)
            if self.intro_animation_time < 2.0:
                # Título apareciendo
                title_font = pygame.font.Font(None, 72)
                title = "AstroDebt"
                alpha = min(255, int(self.intro_animation_time * 127))
                title_surface = title_font.render(title, True, (255, 255, 255))
                title_surface.set_alpha(alpha)
                title_rect = title_surface.get_rect()
                title_rect.centerx = self.screen_width // 2
                title_rect.y = 50
                intro_surface.blit(title_surface, title_rect)
                
                # Nave entrando
                if 'blue_spaceship' in self.assets:
                    ship = self.assets['blue_spaceship']
                    # Nave entra desde la derecha
                    ship_x = self.screen_width + 100 - (self.intro_animation_time * 400)
                    ship_y = 200 + (self.intro_animation_time * 150)
                    ship_rotation = -5 - (self.intro_animation_time * 5)
                    
                    ship_rotated = pygame.transform.rotate(ship, ship_rotation)
                    ship_rect = ship_rotated.get_rect()
                    ship_rect.center = (int(ship_x), int(ship_y))
                    intro_surface.blit(ship_rotated, ship_rect)
            
            # Fase 2: Impacto y nave estrellada (2-3 segundos)
            elif self.intro_animation_time < 3.0:
                time_in_phase = self.intro_animation_time - 2.0
                
                # Título fijo
                title_font = pygame.font.Font(None, 72)
                title = "AstroDebt"
                title_surface = title_font.render(title, True, (255, 255, 255))
                title_rect = title_surface.get_rect()
                title_rect.centerx = self.screen_width // 2
                title_rect.y = 50
                intro_surface.blit(title_surface, title_rect)
                
                # Luna en el suelo
                if 'landing_moon' in self.assets:
                    moon = self.assets['landing_moon']
                    moon_rect = moon.get_rect()
                    moon_rect.bottom = self.screen_height - 30
                    moon_rect.centerx = self.screen_width // 2
                    intro_surface.blit(moon, moon_rect)
                
                # Nave estrellada sobre la luna
                if 'blue_spaceship' in self.assets:
                    ship = self.assets['blue_spaceship']
                    ship_rotated = pygame.transform.rotate(ship, 15)  # Inclinada
                    ship_rect = ship_rotated.get_rect()
                    ship_rect.centerx = self.screen_width // 2 - 50
                    ship_rect.bottom = self.screen_height - 150  # SOBRE la luna
                    intro_surface.blit(ship_rotated, ship_rect)
                
                # Efecto de impacto (partículas simples)
                if time_in_phase < 0.5:
                    import random
                    for _ in range(10):
                        particle_x = (self.screen_width // 2 - 50) + random.randint(-30, 30)
                        particle_y = (self.screen_height - 150) + random.randint(-20, 20)
                        particle_size = random.randint(2, 5)
                        color = (255, random.randint(150, 255), random.randint(50, 150))
                        pygame.draw.circle(intro_surface, color, (particle_x, particle_y), particle_size)
                    
                    # Aplicar shake SOLO una vez al inicio del impacto
                    if not self.impact_shake_applied:
                        self.apply_screen_shake(0.8, 0.4)
                        self.impact_shake_applied = True
            
            # Fase 3: Astronauta aparece (3+ segundos)
            else:
                self.intro_complete = True
                time_in_phase = self.intro_animation_time - 3.0
                
                # Título fijo
                title_font = pygame.font.Font(None, 72)
                title = "AstroDebt"
                title_surface = title_font.render(title, True, (255, 255, 255))
                title_rect = title_surface.get_rect()
                title_rect.centerx = self.screen_width // 2
                title_rect.y = 50
                intro_surface.blit(title_surface, title_rect)
                
                # Luna
                if 'landing_moon' in self.assets:
                    moon = self.assets['landing_moon']
                    moon_rect = moon.get_rect()
                    moon_rect.bottom = self.screen_height - 30
                    moon_rect.centerx = self.screen_width // 2
                    intro_surface.blit(moon, moon_rect)
                
                # Nave estrellada SOBRE la luna
                if 'blue_spaceship' in self.assets:
                    ship = self.assets['blue_spaceship']
                    ship_rotated = pygame.transform.rotate(ship, 15)
                    ship_rect = ship_rotated.get_rect()
                    ship_rect.centerx = self.screen_width // 2 - 50
                    ship_rect.bottom = self.screen_height - 150  # SOBRE la luna
                    intro_surface.blit(ship_rotated, ship_rect)
                
                # Astronauta apareciendo SOBRE la luna
                if 'player' in self.assets:
                    player = self.assets['player']
                    # Astronauta baja desde la nave
                    player_y = max(self.screen_height - 120, self.screen_height - 200 + (time_in_phase * 80))
                    player_rect = player.get_rect()
                    player_rect.centerx = self.screen_width // 2 + 30
                    player_rect.bottom = int(player_y)
                    intro_surface.blit(player, player_rect)
        
        # Escena completa (después de la animación)
        else:
            # Fondo con título
            title_font = pygame.font.Font(None, 72)
            subtitle_font = pygame.font.Font(None, 32)
            
            title = "AstroDebt"
            subtitle = "Un juego educativo sobre gestión de recursos"
            
            title_surface = title_font.render(title, True, (255, 255, 255))
            subtitle_surface = subtitle_font.render(subtitle, True, (200, 200, 200))
            
            title_rect = title_surface.get_rect()
            title_rect.centerx = self.screen_width // 2
            title_rect.y = 50
            
            subtitle_rect = subtitle_surface.get_rect()
            subtitle_rect.centerx = self.screen_width // 2
            subtitle_rect.y = 120
            
            intro_surface.blit(title_surface, title_rect)
            intro_surface.blit(subtitle_surface, subtitle_rect)
            
            # Luna
            if 'landing_moon' in self.assets:
                moon = self.assets['landing_moon']
                moon_rect = moon.get_rect()
                moon_rect.bottom = self.screen_height - 30
                moon_rect.centerx = self.screen_width // 2
                intro_surface.blit(moon, moon_rect)
            
            # Nave estrellada SOBRE la luna
            if 'blue_spaceship' in self.assets:
                ship = self.assets['blue_spaceship']
                ship_rotated = pygame.transform.rotate(ship, 15)
                ship_rect = ship_rotated.get_rect()
                ship_rect.centerx = self.screen_width // 2 - 50
                ship_rect.bottom = self.screen_height - 150  # SOBRE la luna
                intro_surface.blit(ship_rotated, ship_rect)
            
            # Astronauta SOBRE la luna
            if 'player' in self.assets:
                player = self.assets['player']
                player_rect = player.get_rect()
                player_rect.centerx = self.screen_width // 2 + 30
                player_rect.bottom = self.screen_height - 120  # SOBRE la luna
                intro_surface.blit(player, player_rect)
            
            # Botón de inicio
            button_font = pygame.font.Font(None, 36)
            button_text = "[ESPACIO] Comenzar"
            button_surface = button_font.render(button_text, True, (255, 255, 100))
            button_rect = button_surface.get_rect()
            button_rect.centerx = self.screen_width // 2
            button_rect.bottom = self.screen_height - 50
            
            # Fondo del botón para mejor visibilidad
            button_bg = pygame.Surface((button_rect.width + 20, button_rect.height + 10))
            button_bg.fill((50, 50, 50))
            button_bg.set_alpha(200)
            button_bg_rect = button_bg.get_rect()
            button_bg_rect.center = button_rect.center
            intro_surface.blit(button_bg, button_bg_rect)
            intro_surface.blit(button_surface, button_rect)
        
        # Dibujar la superficie temporal en la pantalla principal (SIN shake)
        self.screen.blit(intro_surface, (0, 0))
    
    def render_end_screen(self) -> None:
        """Renderiza la pantalla final (victoria o derrota)"""
        if not self.screen or not self.game_state:
            return
        
        # Fondo oscuro
        self.screen.fill((10, 10, 20))
        
        title_font = pygame.font.Font(None, 72)
        text_font = pygame.font.Font(None, 36)
        small_font = pygame.font.Font(None, 24)
        
        if self.game_state.victory:
            # Usar animación de victoria
            self.render_victory_sequence()
            return
        
        # Pantalla de game over
        title = "GAME OVER"
        title_color = (255, 100, 100)
        
        reason_text = {
            "oxygen_depleted": "¡Te quedaste sin oxígeno!",
            "debt_overwhelming": "Las deudas te abrumaron.",
            "unknown": "No pudiste completar la misión."
        }
        
        reason = reason_text.get(self.game_state.game_over_reason, reason_text["unknown"])
        
        # Mensajes específicos según la razón
        if self.game_state.game_over_reason == "oxygen_depleted":
            messages = [
                reason,
                "",
                "💀 Sin oxígeno no hay vida...",
                "",
                f"Sobreviviste {self.game_state.turn_number} turnos.",
                f"Progreso de reparación: {self.game_state.repair_progress:.0f}%",
                f"Materiales recolectados: {self.game_state.materials}",
                "",
                "💡 Consejo: Gestiona tu oxígeno cuidadosamente.",
                "Puedes intercambiar materiales por oxígeno.",
                "¡Los préstamos pueden salvarte en emergencias!"
            ]
        else:
            messages = [
                reason,
                f"Sobreviviste {self.game_state.turn_number} turnos.",
                f"Progreso de reparación: {self.game_state.repair_progress:.0f}%",
                "",
                "Moraleja: Los préstamos pueden ayudar,",
                "pero deben manejarse con cuidado."
            ]
        
        # Renderizar título
        title_surface = title_font.render(title, True, title_color)
        title_rect = title_surface.get_rect()
        title_rect.centerx = self.screen_width // 2
        title_rect.centery = 150
        self.screen.blit(title_surface, title_rect)
        
        # Renderizar mensajes
        y = 250
        for i, message in enumerate(messages):
            if message:  # Skip empty lines
                # Color especial para el primer mensaje (razón de game over)
                if i == 0 and self.game_state.game_over_reason == "oxygen_depleted":
                    color = (255, 80, 80)  # Rojo brillante para oxígeno agotado
                    font_to_use = title_font if i == 0 else text_font
                else:
                    color = (255, 255, 255)
                    font_to_use = text_font
                
                msg_surface = font_to_use.render(message, True, color)
                msg_rect = msg_surface.get_rect()
                msg_rect.centerx = self.screen_width // 2
                msg_rect.centery = y
                self.screen.blit(msg_surface, msg_rect)
            y += 40 if i < 3 else 35  # Espaciado ajustado
        
        # Opción de reiniciar
        restart_text = "[ESPACIO] Jugar de nuevo    [ESC] Salir"
        restart_surface = small_font.render(restart_text, True, (255, 255, 100))
        restart_rect = restart_surface.get_rect()
        restart_rect.centerx = self.screen_width // 2
        restart_rect.bottom = self.screen_height - 50
        self.screen.blit(restart_surface, restart_rect)
    
    def apply_screen_shake(self, intensity: float, duration: float) -> None:
        """
        Aplica efecto de vibración de pantalla
        
        Args:
            intensity: Intensidad del shake (0.0 - 1.0)
            duration: Duración en segundos
        """
        self.shake_intensity = intensity
        self.shake_duration = duration
    
    def update(self, delta_time: float) -> None:
        """
        Actualiza animaciones y efectos
        
        Args:
            delta_time: Tiempo transcurrido
        """
        # Actualizar shake solo durante la intro
        if self.shake_duration > 0:
            self.shake_duration -= delta_time
            # Reducir intensidad gradualmente
            self.shake_intensity *= 0.9
            
            if self.shake_duration <= 0:
                self.shake_intensity = 0.0
                self.shake_duration = 0.0
    
    def reset_shake(self) -> None:
        """Resetea completamente el efecto de shake"""
        self.shake_intensity = 0.0
        self.shake_duration = 0.0
        self.camera_offset = [0, 0]
    
    def _load_assets(self) -> None:
        """Carga todos los assets del juego"""
        asset_files = {
            'space_background': 'space_background.png',
            'blue_spaceship': 'blue_spaceship.png',
            'player': 'player.png',
            'landing_moon': 'landing_moon.png',
            'start_button': 'start_button.png',
            'copper_mineral': 'copper_mineral.png',
            'silver_mineral': 'silver_mineral.png',
            'gold_mineral': 'gold_mineral.png',
            'zorvax_alien': 'zorvax_alien.png',
            'ktarr_alien': 'ktarr_alien.png',
            'alien': 'alien.png',
            'npc_helper': 'npc_helper.png'
        }
        
        for key, filename in asset_files.items():
            path = os.path.join('data', 'assets', filename)
            try:
                if os.path.exists(path):
                    image = pygame.image.load(path).convert_alpha()
                    
                    # Escalar assets según su tipo
                    if key == 'blue_spaceship':
                        image = pygame.transform.scale(image, (150, 100))
                    elif key == 'player':
                        image = pygame.transform.scale(image, (50, 70))
                    elif key == 'landing_moon':
                        image = pygame.transform.scale(image, (300, 150))
                    elif 'alien' in key or key == 'npc_helper':
                        image = pygame.transform.scale(image, (100, 120))
                    elif 'button' in key:
                        image = pygame.transform.scale(image, (200, 60))
                    
                    self.assets[key] = image
                    logger.debug(f"Asset cargado: {filename}")
            except Exception as e:
                logger.warning(f"No se pudo cargar asset {filename}: {e}")
    
    def _generate_stars(self) -> None:
        """Genera estrellas aleatorias para el fondo"""
        num_stars = 100
        for _ in range(num_stars):
            x = random.randint(0, self.screen_width)
            y = random.randint(0, self.screen_height)
            size = random.choice([1, 1, 1, 2])  # Más estrellas pequeñas
            self.stars.append((x, y, size))
    
    def render_victory_sequence(self) -> None:
        """Renderiza la secuencia animada de victoria con despegue hacia la Tierra"""
        title_font = pygame.font.Font(None, 72)
        text_font = pygame.font.Font(None, 36)
        small_font = pygame.font.Font(None, 24)
        
        # Renderizar fondo con espacio
        if 'space_background' in self.assets:
            bg = self.assets['space_background']
            bg_scaled = pygame.transform.scale(bg, (self.screen_width, self.screen_height))
            self.screen.blit(bg_scaled, (0, 0))
        else:
            self.screen.fill((10, 10, 30))
        
        # FASE 1: Mostrar botón "Volver a Casa" si la animación no ha comenzado
        if not self.victory_animation_active:
            # Luna en el suelo
            if 'landing_moon' in self.assets:
                moon = self.assets['landing_moon']
                moon_rect = moon.get_rect()
                moon_rect.bottom = self.screen_height - 30
                moon_rect.centerx = self.screen_width // 2
                self.screen.blit(moon, moon_rect)
            
            # Nave reparada sobre la luna
            if 'blue_spaceship' in self.assets:
                ship = self.assets['blue_spaceship']
                ship_rect = ship.get_rect()
                ship_rect.centerx = self.screen_width // 2 - 50
                ship_rect.bottom = self.screen_height - 150
                self.screen.blit(ship, ship_rect)
            
            # Título de victoria
            title = "¡NAVE REPARADA AL 100%!"
            title_surface = title_font.render(title, True, (100, 255, 100))
            title_rect = title_surface.get_rect()
            title_rect.centerx = self.screen_width // 2
            title_rect.y = 50
            self.screen.blit(title_surface, title_rect)
            
            # Estadísticas
            stats_y = 150
            stats = [
                f"Materiales recolectados: {self.game_state.materials}",
                f"Oxígeno restante: {self.game_state.oxygen:.0f}",
                f"Turnos jugados: {self.game_state.turn_number}"
            ]
            
            for stat in stats:
                stat_surface = text_font.render(stat, True, (255, 255, 255))
                stat_rect = stat_surface.get_rect()
                stat_rect.centerx = self.screen_width // 2
                stat_rect.y = stats_y
                self.screen.blit(stat_surface, stat_rect)
                stats_y += 40
            
            # Botón "Volver a Casa"
            button_text = "🚀 [ESPACIO] Volver a Casa 🌍"
            button_surface = title_font.render(button_text, True, (255, 215, 0))
            button_rect = button_surface.get_rect()
            button_rect.centerx = self.screen_width // 2
            button_rect.centery = self.screen_height // 2 + 50
            
            # Fondo del botón con efecto pulsante
            pulse = math.sin(pygame.time.get_ticks() * 0.003) * 10
            button_bg = pygame.Surface((button_rect.width + 40, button_rect.height + 20))
            button_bg.fill((50, 50, 100))
            button_bg.set_alpha(200)
            button_bg_rect = button_bg.get_rect()
            button_bg_rect.center = (button_rect.centerx, button_rect.centery + int(pulse))
            self.screen.blit(button_bg, button_bg_rect)
            
            button_rect.centery += int(pulse)
            self.screen.blit(button_surface, button_rect)
            
            # Instrucción adicional
            hint_text = "[ESC] para salir"
            hint_surface = small_font.render(hint_text, True, (200, 200, 200))
            hint_rect = hint_surface.get_rect()
            hint_rect.centerx = self.screen_width // 2
            hint_rect.bottom = self.screen_height - 30
            self.screen.blit(hint_surface, hint_rect)
            
            return
        
        # FASE 2: Animación de despegue hacia la Tierra
        if self.victory_animation_active and not self.victory_animation_complete:
            self.victory_animation_time += 0.016  # ~60fps
            
            # Duración total: 5 segundos
            animation_duration = 5.0
            progress = min(1.0, self.victory_animation_time / animation_duration)
            
            # Luna en el fondo
            if 'landing_moon' in self.assets:
                moon = self.assets['landing_moon']
                moon_rect = moon.get_rect()
                moon_rect.bottom = self.screen_height - 30
                moon_rect.centerx = self.screen_width // 2
                self.screen.blit(moon, moon_rect)
            
            # Calcular posición y escala de la nave
            start_x = self.screen_width // 2 - 50
            start_y = self.screen_height - 150
            
            # La Tierra está a la derecha del fondo
            end_x = self.screen_width - 150
            end_y = self.screen_height // 2 - 50
            
            # Interpolación suave (ease-out)
            ease_progress = 1 - (1 - progress) ** 3
            
            ship_x = start_x + (end_x - start_x) * ease_progress
            ship_y = start_y - ((start_y - end_y) * ease_progress)
            
            # Reducir tamaño progresivamente (perspectiva)
            scale = 1.0 - (progress * 0.7)  # De 100% a 30%
            
            # Nave con animación
            if 'blue_spaceship' in self.assets:
                ship = self.assets['blue_spaceship']
                
                # Rotación ligera hacia arriba y derecha
                rotation = -15 * progress
                ship_rotated = pygame.transform.rotate(ship, rotation)
                
                # Escalar
                new_width = int(ship_rotated.get_width() * scale)
                new_height = int(ship_rotated.get_height() * scale)
                
                if new_width > 0 and new_height > 0:
                    ship_scaled = pygame.transform.scale(ship_rotated, (new_width, new_height))
                    ship_rect = ship_scaled.get_rect()
                    ship_rect.center = (int(ship_x), int(ship_y))
                    self.screen.blit(ship_scaled, ship_rect)
                    
                    # Estela de la nave (efecto de propulsión)
                    if progress > 0.1:
                        trail_length = int(30 * progress)
                        trail_width = int(15 * scale)
                        
                        for i in range(trail_length):
                            offset = i * 3
                            trail_x = int(ship_x - offset * ease_progress)
                            trail_y = int(ship_y + offset * ease_progress * 0.5)
                            trail_size = max(1, trail_width - i)
                            
                            if trail_size > 0:
                                pygame.draw.circle(self.screen, (255, 150, 50), 
                                                 (trail_x, trail_y), trail_size)
            
            # Mensaje de viaje
            if progress < 0.8:
                travel_text = "Regresando a casa..."
                travel_surface = text_font.render(travel_text, True, (255, 255, 255))
                travel_rect = travel_surface.get_rect()
                travel_rect.centerx = self.screen_width // 2
                travel_rect.y = 50
                self.screen.blit(travel_surface, travel_rect)
            
            # Completar animación
            if progress >= 1.0:
                self.victory_animation_complete = True
                self.victory_animation_time = 0
            
            return
        
        # FASE 3: Mensaje final después de la animación
        if self.victory_animation_complete:
            # Fondo
            if 'space_background' in self.assets:
                bg = self.assets['space_background']
                bg_scaled = pygame.transform.scale(bg, (self.screen_width, self.screen_height))
                self.screen.blit(bg_scaled, (0, 0))
            else:
                self.screen.fill((10, 10, 30))
            
            # Título final
            title = "¡FELICIDADES!"
            title_surface = title_font.render(title, True, (100, 255, 100))
            title_rect = title_surface.get_rect()
            title_rect.centerx = self.screen_width // 2
            title_rect.y = 100
            self.screen.blit(title_surface, title_rect)
            
            # Mensaje final
            final_messages = [
                "Has reparado la nave y regresado a casa sano y salvo.",
                "",
                f"Materiales recolectados: {self.game_state.materials}",
                f"Oxígeno restante: {self.game_state.oxygen:.0f}",
                f"Turnos jugados: {self.game_state.turn_number}",
                "",
                "Moraleja: La gestión responsable de recursos",
                "y préstamos es clave para el éxito."
            ]
            
            y = 200
            for message in final_messages:
                if message:
                    msg_surface = text_font.render(message, True, (255, 255, 255))
                    msg_rect = msg_surface.get_rect()
                    msg_rect.centerx = self.screen_width // 2
                    msg_rect.y = y
                    self.screen.blit(msg_surface, msg_rect)
                y += 40
            
            # Opciones finales
            options_text = "[ESPACIO] Jugar de nuevo    [ESC] Salir"
            options_surface = small_font.render(options_text, True, (255, 255, 100))
            options_rect = options_surface.get_rect()
            options_rect.centerx = self.screen_width // 2
            options_rect.bottom = self.screen_height - 50
            self.screen.blit(options_surface, options_rect)
    
    def start_victory_animation(self) -> None:
        """Inicia la animación de victoria (despegue)"""
        self.victory_animation_active = True
        self.victory_animation_time = 0.0
        logger.info("Iniciando animación de victoria - despegue hacia la Tierra")
    
    def show_lender(self, lender_type: str) -> None:
        """
        Muestra un prestamista en la escena
        
        Args:
            lender_type: Tipo de prestamista ('zorvax', 'ktarr', 'consorcio')
        """
        self.lender_visible = True
        self.lender_type = lender_type
        self.lender_animation_time = 0.0
        self.lender_waiting_for_input = False
        logger.info(f"Prestamista {lender_type} apareciendo en escena")
    
    def update_lender(self, delta_time: float) -> None:
        """Actualiza la animación del prestamista"""
        if self.lender_visible:
            self.lender_animation_time += delta_time
            
            # Después de la animación de entrada (0.5s), esperar input del jugador
            if self.lender_animation_time >= 0.5:
                self.lender_waiting_for_input = True
    
    def dismiss_lender(self) -> None:
        """Oculta el prestamista cuando el jugador presiona continuar"""
        self.lender_visible = False
        self.lender_type = None
        self.lender_animation_time = 0.0
        self.lender_waiting_for_input = False
        logger.info("Prestamista desapareciendo de escena")
    
    def render_lender(self) -> None:
        """Renderiza el prestamista en la escena"""
        if not self.lender_type:
            return
        
        # Mapear tipo a asset
        asset_map = {
            'zorvax': 'zorvax_alien',
            'ktarr': 'ktarr_alien',
            'consorcio': 'alien'
        }
        
        asset_key = asset_map.get(self.lender_type, 'alien')
        
        if asset_key not in self.assets:
            logger.warning(f"Asset {asset_key} no encontrado para prestamista")
            return
        
        # Obtener imagen
        lender_image = self.assets[asset_key]
        
        # Animación de entrada (deslizar desde la derecha solo los primeros 0.5s)
        progress = min(1.0, self.lender_animation_time / 0.5)
        ease_progress = 1 - (1 - progress) ** 3  # Ease out
        
        # Posición: desde fuera de pantalla derecha hacia el centro-derecha
        start_x = self.screen_width + 100
        end_x = self.screen_width - 200
        lender_x = start_x - ((start_x - end_x) * ease_progress)
        lender_y = self.screen_height // 2
        
        # Renderizar imagen
        rect = lender_image.get_rect()
        rect.center = (int(lender_x), lender_y)
        
        # Fondo semi-transparente para destacar
        overlay = pygame.Surface((rect.width + 40, rect.height + 40))
        overlay.fill((20, 20, 40))
        overlay.set_alpha(180)
        overlay_rect = overlay.get_rect()
        overlay_rect.center = rect.center
        self.screen.blit(overlay, overlay_rect)
        
        # Dibujar prestamista
        self.screen.blit(lender_image, rect)
        
        # Texto identificador
        font_large = pygame.font.Font(None, 36)
        name_text = self.lender_type.upper()
        name_surface = font_large.render(name_text, True, (255, 215, 0))
        name_rect = name_surface.get_rect()
        name_rect.centerx = rect.centerx
        name_rect.top = rect.bottom + 10
        self.screen.blit(name_surface, name_rect)
        
        # Si está esperando input, mostrar instrucción parpadeante
        if self.lender_waiting_for_input:
            # Efecto parpadeante
            alpha = int((math.sin(self.lender_animation_time * 3) + 1) * 127.5)
            
            font_small = pygame.font.Font(None, 28)
            continue_text = "[ESPACIO] Continuar"
            continue_surface = font_small.render(continue_text, True, (255, 255, 255))
            continue_surface.set_alpha(alpha)
            
            continue_rect = continue_surface.get_rect()
            continue_rect.centerx = self.screen_width // 2
            continue_rect.bottom = self.screen_height - 50
            
            # Fondo para el texto
            bg_surface = pygame.Surface((continue_rect.width + 20, continue_rect.height + 10))
            bg_surface.fill((50, 50, 50))
            bg_surface.set_alpha(200)
            bg_rect = bg_surface.get_rect()
            bg_rect.center = continue_rect.center
            
            self.screen.blit(bg_surface, bg_rect)
            self.screen.blit(continue_surface, continue_rect)
    
    def render_all_lenders_display(self) -> None:
        """Renderiza los tres prestamistas en pantalla para testing"""
        # Definir los tres prestamistas y sus assets
        lenders = [
            {'type': 'zorvax', 'asset': 'zorvax_alien', 'name': 'ZORVAX'},
            {'type': 'ktarr', 'asset': 'ktarr_alien', 'name': "K'TARR"},
            {'type': 'consorcio', 'asset': 'alien', 'name': 'CONSORCIO'}
        ]
        
        # Calcular posiciones (distribuir horizontalmente)
        spacing = self.screen_width // 4
        base_y = self.screen_height // 2 + 100  # Más abajo para no obstruir la nave
        
        for i, lender in enumerate(lenders):
            asset_key = lender['asset']
            
            if asset_key not in self.assets:
                logger.warning(f"Asset {asset_key} no encontrado")
                continue
            
            # Obtener imagen
            lender_image = self.assets[asset_key]
            
            # Posición horizontal (izquierda, centro, derecha)
            lender_x = spacing * (i + 1)
            lender_y = base_y
            
            # Renderizar imagen
            rect = lender_image.get_rect()
            rect.center = (lender_x, lender_y)
            
            # Fondo semi-transparente
            overlay = pygame.Surface((rect.width + 20, rect.height + 20))
            overlay.fill((30, 30, 50))
            overlay.set_alpha(150)
            overlay_rect = overlay.get_rect()
            overlay_rect.center = rect.center
            self.game_layer.blit(overlay, overlay_rect)
            
            # Dibujar prestamista
            self.game_layer.blit(lender_image, rect)
            
            # Texto identificador
            font = pygame.font.Font(None, 32)
            name_surface = font.render(lender['name'], True, (255, 215, 0))
            name_rect = name_surface.get_rect()
            name_rect.centerx = rect.centerx
            name_rect.top = rect.bottom + 10
            self.game_layer.blit(name_surface, name_rect)
        
        # Texto superior indicando que es modo testing
        font_title = pygame.font.Font(None, 40)
        title_surface = font_title.render("🧪 MODO TESTING - PRESTAMISTAS", True, (255, 100, 100))
        title_rect = title_surface.get_rect()
        title_rect.centerx = self.screen_width // 2
        title_rect.top = 30
        
        # Fondo para el título
        bg = pygame.Surface((title_rect.width + 40, title_rect.height + 20))
        bg.fill((0, 0, 0))
        bg.set_alpha(200)
        bg_rect = bg.get_rect()
        bg_rect.center = title_rect.center
        
        self.game_layer.blit(bg, bg_rect)
        self.game_layer.blit(title_surface, title_rect)
    
    def reset_animations(self) -> None:
        """Resetea todas las animaciones del renderer"""
        # Animaciones de intro
        self.ship_animation_time = 0.0
        self.intro_animation_time = 0.0
        self.intro_complete = False
        self.impact_shake_applied = False
        
        # Animaciones de victoria
        self.victory_animation_time = 0.0
        self.victory_animation_active = False
        self.show_return_home_button = False
        self.victory_animation_complete = False
        
        # Prestamista
        self.lender_visible = False
        self.lender_type = None
        self.lender_animation_time = 0.0
        self.lender_waiting_for_input = False
        
        # Resetear shake
        self.reset_shake()
        
        logger.info("Animaciones del renderer reseteadas")

