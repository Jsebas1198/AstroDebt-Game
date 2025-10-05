"""
Mineral Rush - Minijuego tipo Whack-a-Mole para recolección de minerales
El jugador debe hacer clic en los minerales que aparecen en las minas antes de que desaparezcan

Mecánica:
- Máximo 7 materiales a recolectar
- Valores: Cobre (0.05), Plata (0.1), Oro (0.2)
- Sistema de combos con multiplicadores ×2, ×3, ×5
- Duración: 20 segundos
- Cada golpe suma su valor redondeado a entero
"""

import pygame
import random
import math
import os
from typing import List, Dict, Tuple, Optional
from .base import BaseMinigame
import logging

logger = logging.getLogger(__name__)


class Mine:
    """Representa una mina donde pueden aparecer minerales"""
    
    def __init__(self, x: int, y: int, mine_id: int):
        self.x = x
        self.y = y
        self.mine_id = mine_id
        self.is_occupied = False
        self.current_mineral: Optional['Mineral'] = None
        self.radius = 60
        self.hole_depth = 20
    
    def spawn_mineral(self, mineral_type: str, mineral_image: pygame.Surface) -> 'Mineral':
        """Genera un mineral en esta mina"""
        self.is_occupied = True
        self.current_mineral = Mineral(self.x, self.y, mineral_type, mineral_image)
        return self.current_mineral
    
    def clear(self):
        """Limpia el mineral de la mina"""
        self.is_occupied = False
        self.current_mineral = None
    
    def draw(self, screen: pygame.Surface):
        """Dibuja la mina"""
        # Sombra del agujero
        pygame.draw.ellipse(screen, (20, 20, 20),
                          (self.x - self.radius, self.y - self.radius // 2,
                           self.radius * 2, self.radius))
        
        # Borde del agujero
        pygame.draw.ellipse(screen, (80, 50, 30),
                          (self.x - self.radius - 5, self.y - self.radius // 2 - 5,
                           self.radius * 2 + 10, self.radius + 10), 5)
        
        # Interior del agujero (más oscuro)
        pygame.draw.ellipse(screen, (30, 20, 10),
                          (self.x - self.radius + 5, self.y - self.radius // 2 + 5,
                           self.radius * 2 - 10, self.radius - 10))


class Mineral:
    """Representa un mineral que aparece en una mina"""
    
    # Valores base balanceados para dificultad
    # Con round(), necesitas combos para que cuenten
    BASE_VALUES = {
        'copper': 0.4,   # Necesita combo ×2 para sumar 1 (0.4×2=0.8→1)
        'silver': 0.5,   # Con combo ×2 suma 1 (0.5×2=1.0→1)
        'gold': 0.6      # Con combo ×2 suma 1 (0.6×2=1.2→1)
    }
    
    def __init__(self, x: int, y: int, mineral_type: str, image: pygame.Surface):
        self.x = x
        self.y = y
        self.base_y = y
        self.mineral_type = mineral_type
        self.image = image
        
        # Valor base del mineral
        self.base_value = self.BASE_VALUES.get(mineral_type, 0.05)
        
        # Estado y animación
        self.lifetime = 1.0  # ~1s visible según especificación
        self.max_lifetime = self.lifetime
        self.is_alive = True
        self.was_clicked = False
        
        # Animación de aparición
        self.animation_phase = 0.0
        self.animation_speed = 4.0
        self.pop_height = 40
        
        # Escala y rotación
        self.scale = 1.0
        self.rotation = 0
    
    def update(self, delta_time: float):
        """Actualiza el estado del mineral"""
        if not self.is_alive:
            return
        
        # Actualizar tiempo de vida
        self.lifetime -= delta_time
        if self.lifetime <= 0:
            self.is_alive = False
            return
        
        # Animación de aparición
        if self.animation_phase < 1.0:
            self.animation_phase = min(1.0, self.animation_phase + delta_time * self.animation_speed)
            progress = self.animation_phase
            ease = 1 - (1 - progress) ** 2
            self.y = self.base_y - (self.pop_height * ease)
            self.scale = 0.5 + (0.5 * ease)
        
        # Animación de desaparición
        elif self.lifetime < 0.3:
            fade_progress = self.lifetime / 0.3
            self.scale = 0.5 + (0.5 * fade_progress)
            self.y = self.base_y - (self.pop_height * fade_progress)
        
        # Rotación sutil
        self.rotation = math.sin(pygame.time.get_ticks() * 0.002) * 5
    
    def draw(self, screen: pygame.Surface):
        """Dibuja el mineral"""
        if not self.is_alive or self.animation_phase < 0.1:
            return
        
        scaled_width = int(self.image.get_width() * self.scale)
        scaled_height = int(self.image.get_height() * self.scale)
        
        if scaled_width > 0 and scaled_height > 0:
            scaled_image = pygame.transform.scale(self.image, (scaled_width, scaled_height))
            rotated_image = pygame.transform.rotate(scaled_image, self.rotation)
            
            rect = rotated_image.get_rect()
            rect.center = (int(self.x), int(self.y))
            
            # Sombra
            shadow_surface = pygame.Surface((scaled_width, scaled_height // 2))
            shadow_surface.fill((0, 0, 0))
            shadow_surface.set_alpha(50)
            shadow_rect = shadow_surface.get_rect()
            shadow_rect.center = (int(self.x), int(self.base_y + 10))
            screen.blit(shadow_surface, shadow_rect)
            
            screen.blit(rotated_image, rect)
    
    def is_clicked(self, mouse_pos: Tuple[int, int]) -> bool:
        """Verifica si el mineral fue clickeado"""
        if not self.is_alive or self.was_clicked or self.animation_phase < 1.0:
            return False
        
        dx = mouse_pos[0] - self.x
        dy = mouse_pos[1] - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        click_radius = (self.image.get_width() * self.scale) / 2
        
        if distance <= click_radius:
            self.was_clicked = True
            self.is_alive = False
            return True
        
        return False


class Particle:
    """Partícula visual para efectos"""
    
    def __init__(self, x: float, y: float, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.vx = random.uniform(-150, 150)
        self.vy = random.uniform(-200, -50)
        self.color = color
        self.lifetime = random.uniform(0.3, 0.6)
        self.max_lifetime = self.lifetime
        self.size = random.randint(3, 6)
    
    def update(self, delta_time: float):
        self.x += self.vx * delta_time
        self.y += self.vy * delta_time
        self.vy += 400 * delta_time
        self.lifetime -= delta_time
    
    def draw(self, screen: pygame.Surface):
        if self.lifetime > 0:
            alpha = self.lifetime / self.max_lifetime
            size = int(self.size * alpha)
            if size > 0:
                pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)


class MineralRush(BaseMinigame):
    """
    Minijuego Mineral Rush - Whack-a-Mole con minerales
    
    Especificaciones:
    - Máximo 7 materiales (enteros)
    - Duración: 20 segundos
    - Valores: Cobre (0.05), Plata (0.1), Oro (0.2)
    - Combos: ×2, ×3, ×5 por golpes consecutivos
    - Cada golpe suma su valor redondeado
    """
    
    def __init__(self, screen_width: int = 1280, screen_height: int = 720):
        # IMPORTANTE: Inicializar antes de super().__init__()
        self.mineral_images = {}
        
        super().__init__(screen_width, screen_height)
        
        # Configuración del minijuego
        self.time_remaining = 10.0  # 10 segundos (desafiante)
        self.materials_collected = 0  # Entero, máximo 7
        self.max_materials = 7  # Límite máximo
        
        # Minas (3x3 grid = 9 minas)
        self.mines: List[Mine] = []
        self.num_mines = 9
        self.create_mines()
        
        # Sistema de spawn
        self.spawn_timer = 0.0
        self.spawn_interval = 0.8
        self.max_active_minerals = 3
        self.active_minerals_count = 0
        
        # Probabilidades de aparición (balanceado para dificultad)
        self.spawn_probabilities = {
            'copper': 0.50,   # 50% - frecuente pero poco valor
            'silver': 0.30,   # 30% - intermedio
            'gold': 0.20      # 20% - menos raro, más necesario
        }
        
        # Sistema de combo
        self.combo = 0
        self.combo_timer = 0.0
        self.combo_timeout = 1.0  # <1s entre golpes para mantener combo
        self.last_hit_time = 0.0
        
        # Multiplicadores de combo
        self.combo_multipliers = {
            0: 1,  # Sin combo
            1: 1,  # 1 golpe
            2: 2,  # 2 golpes: ×2
            3: 2,  # 3 golpes: ×2
            4: 3,  # 4 golpes: ×3
            5: 3,  # 5 golpes: ×3
        }
        # 6+ golpes: ×5
        
        # Efectos visuales
        self.particles: List[Particle] = []
        self.flash_effect = 0.0
        
        # Fondo
        self.background = None
        
        logger.info("Mineral Rush inicializado (Max: 7 materiales, 10s - DESAFIANTE)")
    
    def load_assets(self):
        """Carga los assets del minijuego"""
        try:
            # Cargar fondo
            bg_path = os.path.join('data', 'assets', 'minigame_mining_bg.png')
            if os.path.exists(bg_path):
                self.background = pygame.image.load(bg_path)
                self.background = pygame.transform.scale(self.background,
                                                        (self.screen_width, self.screen_height))
            
            # Cargar minerales
            mineral_files = {
                'copper': 'copper_mineral.png',
                'silver': 'silver_mineral.png',
                'gold': 'gold_mineral.png'
            }
            
            for mineral_type, filename in mineral_files.items():
                path = os.path.join('data', 'assets', filename)
                if os.path.exists(path):
                    image = pygame.image.load(path).convert_alpha()
                    image = pygame.transform.scale(image, (60, 60))
                    self.mineral_images[mineral_type] = image
                else:
                    self.mineral_images[mineral_type] = self._create_placeholder_mineral(mineral_type)
        
        except Exception as e:
            logger.error(f"Error cargando assets: {e}")
            for mineral_type in ['copper', 'silver', 'gold']:
                self.mineral_images[mineral_type] = self._create_placeholder_mineral(mineral_type)
    
    def _create_placeholder_mineral(self, mineral_type: str) -> pygame.Surface:
        """Crea placeholder si no hay imagen"""
        colors = {
            'copper': (184, 115, 51),
            'silver': (192, 192, 192),
            'gold': (255, 215, 0)
        }
        
        surface = pygame.Surface((60, 60), pygame.SRCALPHA)
        color = colors.get(mineral_type, (128, 128, 128))
        pygame.draw.circle(surface, color, (30, 30), 25)
        pygame.draw.circle(surface, tuple(min(255, c + 50) for c in color), (30, 30), 20)
        
        return surface
    
    def create_mines(self):
        """Crea la cuadrícula 3x3 de minas"""
        cols, rows = 3, 3
        play_area_width = self.screen_width - 200
        play_area_height = self.screen_height - 300
        start_x, start_y = 100, 150
        
        spacing_x = play_area_width // cols
        spacing_y = play_area_height // rows
        
        mine_id = 0
        for row in range(rows):
            for col in range(cols):
                x = start_x + spacing_x * col + spacing_x // 2
                y = start_y + spacing_y * row + spacing_y // 2
                x += random.randint(-20, 20)
                y += random.randint(-20, 20)
                
                self.mines.append(Mine(x, y, mine_id))
                mine_id += 1
    
    def get_combo_multiplier(self) -> int:
        """Obtiene el multiplicador según el combo actual"""
        if self.combo >= 6:
            return 5  # ×5 para 6+ golpes
        return self.combo_multipliers.get(self.combo, 1)
    
    def handle_input(self, event: pygame.event.Event):
        """Maneja la entrada del usuario"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.try_collect_mineral(event.pos)
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.calculate_rewards(False)
                self.complete_minigame(False)
    
    def try_collect_mineral(self, mouse_pos: Tuple[int, int]):
        """Intenta recolectar un mineral"""
        collected = False
        current_time = pygame.time.get_ticks() / 1000.0
        
        for mine in self.mines:
            if mine.is_occupied and mine.current_mineral:
                if mine.current_mineral.is_clicked(mouse_pos):
                    mineral = mine.current_mineral
                    
                    # Verificar combo timing
                    time_since_last_hit = current_time - self.last_hit_time
                    if time_since_last_hit <= self.combo_timeout and self.combo > 0:
                        self.combo += 1
                    else:
                        self.combo = 1
                    
                    self.last_hit_time = current_time
                    self.combo_timer = self.combo_timeout
                    
                    # Calcular valor con multiplicador
                    base_value = mineral.base_value
                    multiplier = self.get_combo_multiplier()
                    value_with_combo = base_value * multiplier
                    
                    # Redondear (necesitas combos para que cuenten)
                    materials_gained = round(value_with_combo)
                    
                    # Asegurar que no se supere el máximo de 7
                    if self.materials_collected + materials_gained > self.max_materials:
                        materials_gained = self.max_materials - self.materials_collected
                    
                    self.materials_collected += materials_gained
                    self.score += materials_gained * 100
                    
                    # Efectos visuales
                    self.create_collection_effect(mineral.x, mineral.y, mineral.mineral_type)
                    self.flash_effect = 0.15
                    
                    # Limpiar mina
                    mine.clear()
                    self.active_minerals_count -= 1
                    
                    collected = True
                    logger.info(f"{mineral.mineral_type.upper()} golpeado: "
                              f"{base_value:.2f} × {multiplier} = {value_with_combo:.2f} "
                              f"→ {materials_gained} mat. | Combo: {self.combo} | "
                              f"Total: {self.materials_collected}/7")
                    
                    # Verificar victoria anticipada
                    if self.materials_collected >= self.max_materials:
                        logger.info("¡7 materiales alcanzados! Victoria anticipada")
                        self.calculate_rewards(True)
                        self.complete_minigame(True)
                        return
                    
                    break
        
        # Si falló el golpe, romper combo
        if not collected and self.combo > 0:
            logger.info(f"Combo roto: {self.combo}")
            self.combo = 0
    
    def create_collection_effect(self, x: float, y: float, mineral_type: str):
        """Crea efecto de partículas"""
        colors = {
            'copper': (184, 115, 51),
            'silver': (192, 192, 192),
            'gold': (255, 215, 0)
        }
        
        color = colors.get(mineral_type, (255, 255, 255))
        num_particles = 15 if mineral_type == 'gold' else 10
        
        for _ in range(num_particles):
            self.particles.append(Particle(x, y, color))
    
    def spawn_mineral(self):
        """Genera un nuevo mineral"""
        available_mines = [m for m in self.mines if not m.is_occupied]
        
        if not available_mines or self.active_minerals_count >= self.max_active_minerals:
            return
        
        mine = random.choice(available_mines)
        
        # Seleccionar tipo según probabilidades
        rand = random.random()
        cumulative = 0
        mineral_type = 'copper'
        
        for m_type, probability in self.spawn_probabilities.items():
            cumulative += probability
            if rand <= cumulative:
                mineral_type = m_type
                break
        
        mine.spawn_mineral(mineral_type, self.mineral_images[mineral_type])
        self.active_minerals_count += 1
    
    def update(self, delta_time: float):
        """Actualiza la lógica del minijuego"""
        self.time_remaining -= delta_time
        
        # Verificar fin del tiempo
        if self.time_remaining <= 0:
            # Éxito solo si alcanzó 7 materiales
            success = (self.materials_collected >= self.max_materials)
            self.calculate_rewards(success)
            self.complete_minigame(success)
            logger.info(f"Minijuego terminado por tiempo. Materiales: {self.materials_collected}/7. Éxito: {success}")
            return
        
        # Actualizar combo timer
        if self.combo > 0:
            self.combo_timer -= delta_time
            if self.combo_timer <= 0:
                self.combo = 0
        
        # Sistema de spawn
        self.spawn_timer += delta_time
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self.spawn_interval = random.uniform(0.6, 1.0)
            self.spawn_mineral()
        
        # Actualizar minerales
        for mine in self.mines:
            if mine.is_occupied and mine.current_mineral:
                mine.current_mineral.update(delta_time)
                if not mine.current_mineral.is_alive:
                    mine.clear()
                    self.active_minerals_count -= 1
        
        # Actualizar partículas
        for particle in self.particles[:]:
            particle.update(delta_time)
            if particle.lifetime <= 0:
                self.particles.remove(particle)
        
        # Actualizar flash
        if self.flash_effect > 0:
            self.flash_effect -= delta_time * 3
    
    def calculate_rewards(self, success: bool):
        """
        Calcula las recompensas del minijuego
        
        El jugador SIEMPRE recibe los materiales que recolectó (0-7)
        Success determina si dispara MATERIALS_GAINED_SUCCESS o MATERIALS_GAINED_FAIL
        
        Args:
            success: True si alcanzó 7 materiales, False en caso contrario
        """
        # El jugador SIEMPRE recibe lo que recolectó
        self.reward_materials = self.materials_collected
        
        if success:
            logger.info(f"¡ÉXITO! Alcanzaste {self.reward_materials} materiales (objetivo: {self.max_materials})")
        else:
            logger.info(f"FALLO: Solo recolectaste {self.reward_materials}/{self.max_materials} materiales")
        
        # Actualizar score
        self.score = self.materials_collected * 100
    
    def render(self, screen: pygame.Surface):
        """Renderiza el minijuego"""
        # Fondo
        if self.background:
            screen.blit(self.background, (0, 0))
        else:
            screen.fill((101, 67, 33))
        
        # Flash effect
        if self.flash_effect > 0:
            flash_surface = pygame.Surface((self.screen_width, self.screen_height))
            flash_surface.fill((255, 255, 150))
            flash_surface.set_alpha(int(self.flash_effect * 150))
            screen.blit(flash_surface, (0, 0))
        
        # Minas
        for mine in self.mines:
            mine.draw(screen)
        
        # Minerales
        for mine in self.mines:
            if mine.is_occupied and mine.current_mineral:
                mine.current_mineral.draw(screen)
        
        # Partículas
        for particle in self.particles:
            particle.draw(screen)
        
        # UI
        self.render_ui(screen)
    
    def render_ui(self, screen: pygame.Surface):
        """Renderiza la interfaz"""
        # Temporizador
        self.render_timer(screen, x=self.screen_width - 150, y=30)
        
        # Materiales recolectados
        materials_text = f"Materiales: {self.materials_collected} / {self.max_materials}"
        materials_color = (100, 255, 100) if self.materials_collected >= self.max_materials else (255, 255, 255)
        materials_surface = self.font_normal.render(materials_text, True, materials_color)
        screen.blit(materials_surface, (50, 30))
        
        # Combo indicator
        if self.combo > 1:
            multiplier = self.get_combo_multiplier()
            combo_text = f"COMBO ×{multiplier}!"
            
            # Color según multiplicador
            if multiplier >= 5:
                combo_color = (255, 50, 50)
            elif multiplier >= 3:
                combo_color = (255, 150, 50)
            else:
                combo_color = (255, 255, 100)
            
            combo_surface = self.font_large.render(combo_text, True, combo_color)
            combo_rect = combo_surface.get_rect()
            combo_rect.center = (self.screen_width // 2, 60)
            screen.blit(combo_surface, combo_rect)
        
        # Instrucciones
        instructions = [
            "¡Haz clic en los minerales! Mantén combos para sumar materiales",
            "Sin combo: 0 materiales | Combo ×2: 1 material | Combo ×3+: 1-2 materiales",
            "¡Solo 10 segundos! Apunta a 7 materiales - ¡Es difícil!"
        ]
        self.render_instructions(screen, instructions)
        
        # Barra de progreso
        progress_bar_width = 300
        progress_bar_height = 25
        progress_bar_x = self.screen_width // 2 - progress_bar_width // 2
        progress_bar_y = self.screen_height - 180
        
        # Fondo
        pygame.draw.rect(screen, (50, 50, 50),
                        (progress_bar_x, progress_bar_y, progress_bar_width, progress_bar_height))
        
        # Progreso
        progress = min(1.0, self.materials_collected / self.max_materials)
        fill_width = int(progress_bar_width * progress)
        
        if progress >= 1.0:
            color = (100, 255, 100)
        elif progress >= 0.7:
            color = (255, 255, 100)
        else:
            color = (255, 150, 150)
        
        if fill_width > 0:
            pygame.draw.rect(screen, color,
                           (progress_bar_x, progress_bar_y, fill_width, progress_bar_height))
        
        # Borde
        pygame.draw.rect(screen, (255, 255, 255),
                        (progress_bar_x, progress_bar_y, progress_bar_width, progress_bar_height), 2)


# Alias para compatibilidad
MiningMinigame = MineralRush
