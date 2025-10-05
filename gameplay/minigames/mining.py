"""
Mineral Rush - Minijuego tipo Whack-a-Mole para recolección de minerales
El jugador debe hacer clic en los minerales que aparecen en las minas antes de que desaparezcan
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
        """
        Inicializa una mina
        
        Args:
            x: Posición X de la mina
            y: Posición Y de la mina
            mine_id: Identificador único de la mina
        """
        self.x = x
        self.y = y
        self.mine_id = mine_id
        
        # Estado de la mina
        self.is_occupied = False
        self.current_mineral: Optional['Mineral'] = None
        
        # Dimensiones visuales
        self.radius = 60
        self.hole_depth = 20
    
    def spawn_mineral(self, mineral_type: str, mineral_image: pygame.Surface) -> 'Mineral':
        """
        Genera un mineral en esta mina
        
        Args:
            mineral_type: Tipo de mineral ('copper', 'silver', 'gold')
            mineral_image: Imagen del mineral
            
        Returns:
            El mineral creado
        """
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
    
    def __init__(self, x: int, y: int, mineral_type: str, image: pygame.Surface):
        """
        Inicializa un mineral
        
        Args:
            x: Posición X base
            y: Posición Y base
            mineral_type: Tipo ('copper', 'silver', 'gold')
            image: Imagen del mineral
        """
        self.x = x
        self.y = y
        self.base_y = y
        self.mineral_type = mineral_type
        self.image = image
        
        # Valores según tipo
        self.values = {
            'copper': 1,
            'silver': 3,
            'gold': 5
        }
        self.value = self.values.get(mineral_type, 1)
        
        # Estado y animación
        self.lifetime = random.uniform(0.8, 1.5)  # Tiempo visible
        self.max_lifetime = self.lifetime
        self.is_alive = True
        self.was_clicked = False
        
        # Animación de aparición (salta)
        self.animation_phase = 0.0  # 0 a 1
        self.animation_speed = 3.0
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
            
            # Movimiento de salto (easing)
            progress = self.animation_phase
            ease = 1 - (1 - progress) ** 2  # Ease out cuadrático
            self.y = self.base_y - (self.pop_height * ease)
            
            # Escala durante aparición
            self.scale = 0.5 + (0.5 * ease)
        
        # Animación de desaparición
        elif self.lifetime < 0.3:
            fade_progress = self.lifetime / 0.3
            self.scale = 0.5 + (0.5 * fade_progress)
            
            # Hundirse de vuelta
            self.y = self.base_y - (self.pop_height * fade_progress)
        
        # Rotación sutil
        self.rotation = math.sin(pygame.time.get_ticks() * 0.001) * 5
    
    def draw(self, screen: pygame.Surface):
        """Dibuja el mineral"""
        if not self.is_alive or self.animation_phase < 0.1:
            return
        
        # Aplicar transformaciones
        scaled_width = int(self.image.get_width() * self.scale)
        scaled_height = int(self.image.get_height() * self.scale)
        
        if scaled_width > 0 and scaled_height > 0:
            scaled_image = pygame.transform.scale(self.image, (scaled_width, scaled_height))
            rotated_image = pygame.transform.rotate(scaled_image, self.rotation)
            
            # Dibujar con centro en la posición
            rect = rotated_image.get_rect()
            rect.center = (int(self.x), int(self.y))
            
            # Sombra del mineral
            shadow_surface = pygame.Surface((scaled_width, scaled_height // 2))
            shadow_surface.fill((0, 0, 0))
            shadow_surface.set_alpha(50)
            shadow_rect = shadow_surface.get_rect()
            shadow_rect.center = (int(self.x), int(self.base_y + 10))
            screen.blit(shadow_surface, shadow_rect)
            
            # Dibujar mineral
            screen.blit(rotated_image, rect)
    
    def is_clicked(self, mouse_pos: Tuple[int, int]) -> bool:
        """
        Verifica si el mineral fue clickeado
        
        Args:
            mouse_pos: Posición del mouse (x, y)
            
        Returns:
            True si fue clickeado
        """
        if not self.is_alive or self.was_clicked or self.animation_phase < 1.0:
            return False
        
        # Calcular distancia al centro del mineral
        dx = mouse_pos[0] - self.x
        dy = mouse_pos[1] - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        # Área de click basada en la imagen escalada
        click_radius = (self.image.get_width() * self.scale) / 2
        
        if distance <= click_radius:
            self.was_clicked = True
            self.is_alive = False
            return True
        
        return False


class Particle:
    """Partícula visual para efectos de recolección"""
    
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
        """Actualiza la partícula"""
        self.x += self.vx * delta_time
        self.y += self.vy * delta_time
        self.vy += 400 * delta_time  # Gravedad
        self.lifetime -= delta_time
    
    def draw(self, screen: pygame.Surface):
        """Dibuja la partícula"""
        if self.lifetime > 0:
            alpha = self.lifetime / self.max_lifetime
            size = int(self.size * alpha)
            if size > 0:
                pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)


class MineralRush(BaseMinigame):
    """
    Minijuego Mineral Rush - Whack-a-Mole con minerales
    
    El jugador debe hacer clic en los minerales que aparecen en las minas
    para recolectarlos antes de que desaparezcan
    """
    
    def __init__(self, screen_width: int = 1280, screen_height: int = 720):
        # IMPORTANTE: Inicializar mineral_images ANTES de super().__init__()
        # porque BaseMinigame.__init__() llama a load_assets()
        self.mineral_images = {}
        
        super().__init__(screen_width, screen_height)
        
        # Configuración del minijuego
        self.time_remaining = 35.0  # 35 segundos de juego
        self.materials_collected = 0
        self.materials_needed = 20  # Objetivo para éxito
        
        # Minas
        self.mines: List[Mine] = []
        self.num_mines = 9  # 3x3 grid
        self.create_mines()
        
        # Sistema de spawn de minerales
        self.spawn_timer = 0.0
        self.spawn_interval = random.uniform(0.5, 1.0)
        self.max_active_minerals = 3
        self.active_minerals_count = 0
        
        # Probabilidades de aparición
        self.spawn_probabilities = {
            'copper': 0.50,   # 50%
            'silver': 0.35,   # 35%
            'gold': 0.15      # 15%
        }
        
        # Sistema de combo
        self.combo = 0
        self.max_combo = 0
        self.combo_timer = 0.0
        self.combo_timeout = 1.5
        self.consecutive_gold = 0
        
        # Efectos visuales
        self.particles: List[Particle] = []
        self.flash_effect = 0.0
        
        # Dificultad progresiva
        self.difficulty_timer = 0.0
        self.difficulty_increase_interval = 10.0
        self.min_spawn_interval = 0.3
        
        # Fondo
        self.background = None
        
        logger.info("Mineral Rush minijuego inicializado")
    
    def load_assets(self):
        """Carga los assets del minijuego"""
        try:
            # Cargar fondo
            bg_path = os.path.join('data', 'assets', 'minigame_mining_bg.png')
            if os.path.exists(bg_path):
                self.background = pygame.image.load(bg_path)
                self.background = pygame.transform.scale(self.background,
                                                        (self.screen_width, self.screen_height))
                logger.info("Fondo de minería cargado")
            
            # Cargar imágenes de minerales
            mineral_files = {
                'copper': 'copper_mineral.png',
                'silver': 'silver_mineral.png',
                'gold': 'gold_mineral.png'
            }
            
            for mineral_type, filename in mineral_files.items():
                path = os.path.join('data', 'assets', filename)
                if os.path.exists(path):
                    image = pygame.image.load(path).convert_alpha()
                    # Escalar a tamaño apropiado para el juego
                    image = pygame.transform.scale(image, (60, 60))
                    self.mineral_images[mineral_type] = image
                    logger.info(f"Mineral {mineral_type} cargado")
                else:
                    logger.warning(f"No se encontró {filename}")
                    # Crear placeholder
                    self.mineral_images[mineral_type] = self._create_placeholder_mineral(mineral_type)
        
        except Exception as e:
            logger.error(f"Error cargando assets: {e}")
            # Crear placeholders para todos
            for mineral_type in ['copper', 'silver', 'gold']:
                self.mineral_images[mineral_type] = self._create_placeholder_mineral(mineral_type)
    
    def _create_placeholder_mineral(self, mineral_type: str) -> pygame.Surface:
        """Crea un mineral placeholder si no se encuentra la imagen"""
        colors = {
            'copper': (184, 115, 51),
            'silver': (192, 192, 192),
            'gold': (255, 215, 0)
        }
        
        surface = pygame.Surface((60, 60), pygame.SRCALPHA)
        color = colors.get(mineral_type, (128, 128, 128))
        pygame.draw.circle(surface, color, (30, 30), 25)
        pygame.draw.circle(surface, tuple(min(255, c + 50) for c in color), (30, 30), 20)
        pygame.draw.circle(surface, color, (30, 30), 15)
        
        return surface
    
    def create_mines(self):
        """Crea la cuadrícula de minas"""
        # Calcular distribución 3x3
        cols = 3
        rows = 3
        
        # Área de juego (dejar márgenes)
        play_area_width = self.screen_width - 200
        play_area_height = self.screen_height - 300
        start_x = 100
        start_y = 150
        
        spacing_x = play_area_width // cols
        spacing_y = play_area_height // rows
        
        mine_id = 0
        for row in range(rows):
            for col in range(cols):
                x = start_x + spacing_x * col + spacing_x // 2
                y = start_y + spacing_y * row + spacing_y // 2
                
                # Añadir variación aleatoria para que no se vea tan rígido
                x += random.randint(-20, 20)
                y += random.randint(-20, 20)
                
                mine = Mine(x, y, mine_id)
                self.mines.append(mine)
                mine_id += 1
    
    def handle_input(self, event: pygame.event.Event):
        """Maneja la entrada del usuario"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Click izquierdo
                mouse_pos = event.pos
                self.try_collect_mineral(mouse_pos)
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Salir del minijuego
                self.calculate_rewards(False)
                self.complete_minigame(False)
    
    def try_collect_mineral(self, mouse_pos: Tuple[int, int]):
        """
        Intenta recolectar un mineral en la posición del mouse
        
        Args:
            mouse_pos: Posición del click
        """
        collected = False
        
        # Verificar cada mina
        for mine in self.mines:
            if mine.is_occupied and mine.current_mineral:
                if mine.current_mineral.is_clicked(mouse_pos):
                    # Mineral recolectado
                    mineral = mine.current_mineral
                    value = mineral.value
                    
                    # Aplicar bonus de combo
                    combo_bonus = 0
                    if self.combo >= 3:
                        combo_bonus = int(value * 0.5)  # +50% con combo
                    
                    # Bonus por oro consecutivo
                    if mineral.mineral_type == 'gold':
                        self.consecutive_gold += 1
                        if self.consecutive_gold >= 2:
                            combo_bonus += 2
                    else:
                        self.consecutive_gold = 0
                    
                    total_value = value + combo_bonus
                    self.materials_collected += total_value
                    self.score += value * 10
                    
                    # Actualizar combo
                    self.combo += 1
                    self.max_combo = max(self.max_combo, self.combo)
                    self.combo_timer = self.combo_timeout
                    
                    # Efectos visuales
                    self.create_collection_effect(mineral.x, mineral.y, mineral.mineral_type)
                    self.flash_effect = 0.2
                    
                    # Limpiar mina
                    mine.clear()
                    self.active_minerals_count -= 1
                    
                    collected = True
                    logger.info(f"Mineral {mineral.mineral_type} recolectado: +{total_value} materiales")
                    break
        
        # Si no se recolectó nada, romper combo
        if not collected:
            if self.combo > 0:
                logger.info(f"Combo roto: {self.combo}")
            self.combo = 0
            self.consecutive_gold = 0
    
    def create_collection_effect(self, x: float, y: float, mineral_type: str):
        """
        Crea efecto de partículas al recolectar un mineral
        
        Args:
            x: Posición X
            y: Posición Y
            mineral_type: Tipo de mineral
        """
        colors = {
            'copper': (184, 115, 51),
            'silver': (192, 192, 192),
            'gold': (255, 215, 0)
        }
        
        color = colors.get(mineral_type, (255, 255, 255))
        
        # Crear partículas
        num_particles = 15 if mineral_type == 'gold' else 10
        for _ in range(num_particles):
            particle = Particle(x, y, color)
            self.particles.append(particle)
    
    def spawn_mineral(self):
        """Genera un nuevo mineral en una mina disponible"""
        # Verificar si hay minas disponibles
        available_mines = [m for m in self.mines if not m.is_occupied]
        
        if not available_mines or self.active_minerals_count >= self.max_active_minerals:
            return
        
        # Seleccionar mina aleatoria
        mine = random.choice(available_mines)
        
        # Seleccionar tipo de mineral según probabilidades
        rand = random.random()
        cumulative = 0
        mineral_type = 'copper'
        
        for m_type, probability in self.spawn_probabilities.items():
            cumulative += probability
            if rand <= cumulative:
                mineral_type = m_type
                break
        
        # Verificar que tengamos la imagen
        if mineral_type not in self.mineral_images:
            mineral_type = 'copper'
        
        # Crear mineral
        mineral = mine.spawn_mineral(mineral_type, self.mineral_images[mineral_type])
        self.active_minerals_count += 1
        
        logger.debug(f"Mineral {mineral_type} spawneado en mina {mine.mine_id}")
    
    def update(self, delta_time: float):
        """Actualiza la lógica del minijuego"""
        # Actualizar temporizador
        self.time_remaining -= delta_time
        
        # Verificar fin del juego
        if self.time_remaining <= 0:
            success = self.materials_collected >= self.materials_needed
            self.calculate_rewards(success)
            self.complete_minigame(success)
            return
        
        # Actualizar combo timer
        if self.combo > 0:
            self.combo_timer -= delta_time
            if self.combo_timer <= 0:
                logger.info(f"Combo expirado: {self.combo}")
                self.combo = 0
                self.consecutive_gold = 0
        
        # Actualizar dificultad progresiva
        self.difficulty_timer += delta_time
        if self.difficulty_timer >= self.difficulty_increase_interval:
            self.difficulty_timer = 0
            # Reducir intervalo de spawn (aumentar dificultad)
            self.spawn_interval = max(
                self.min_spawn_interval,
                self.spawn_interval - 0.1
            )
            logger.info(f"Dificultad aumentada: spawn_interval={self.spawn_interval:.2f}")
        
        # Sistema de spawn de minerales
        self.spawn_timer += delta_time
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self.spawn_interval = random.uniform(0.5, 1.0)
            self.spawn_mineral()
        
        # Actualizar minerales activos
        for mine in self.mines:
            if mine.is_occupied and mine.current_mineral:
                mine.current_mineral.update(delta_time)
                
                # Si el mineral murió naturalmente, limpiar mina
                if not mine.current_mineral.is_alive:
                    mine.clear()
                    self.active_minerals_count -= 1
        
        # Actualizar partículas
        for particle in self.particles[:]:
            particle.update(delta_time)
            if particle.lifetime <= 0:
                self.particles.remove(particle)
        
        # Actualizar flash effect
        if self.flash_effect > 0:
            self.flash_effect -= delta_time * 3
    
    def calculate_rewards(self, success: bool):
        """
        Calcula las recompensas del minijuego
        
        Args:
            success: Si el jugador tuvo éxito
        """
        if success:
            # Recompensa base: materiales recolectados
            self.reward_materials = self.materials_collected
            
            # Bonus por combo máximo
            if self.max_combo >= 5:
                bonus = int(self.reward_materials * 0.2)
                self.reward_materials += bonus
                logger.info(f"Bonus por combo: +{bonus} materiales")
        else:
            # Recompensa mínima: 25% de lo recolectado
            self.reward_materials = max(1, int(self.materials_collected * 0.25))
        
        logger.info(f"Recompensa final: {self.reward_materials} materiales")
    
    def render(self, screen: pygame.Surface):
        """Renderiza el minijuego"""
        # Limpiar pantalla o dibujar fondo
        if self.background:
            screen.blit(self.background, (0, 0))
        else:
            screen.fill((101, 67, 33))  # Color marrón tierra
        
        # Flash effect
        if self.flash_effect > 0:
            flash_surface = pygame.Surface((self.screen_width, self.screen_height))
            flash_surface.fill((255, 255, 150))
            flash_surface.set_alpha(int(self.flash_effect * 150))
            screen.blit(flash_surface, (0, 0))
        
        # Renderizar minas (agujeros)
        for mine in self.mines:
            mine.draw(screen)
        
        # Renderizar minerales
        for mine in self.mines:
            if mine.is_occupied and mine.current_mineral:
                mine.current_mineral.draw(screen)
        
        # Renderizar partículas
        for particle in self.particles:
            particle.draw(screen)
        
        # Renderizar UI
        self.render_ui(screen)
    
    def render_ui(self, screen: pygame.Surface):
        """Renderiza la interfaz del minijuego"""
        # Temporizador
        self.render_timer(screen, x=self.screen_width - 150, y=30)
        
        # Contador de materiales recolectados
        materials_text = f"Materiales: {self.materials_collected}"
        materials_color = (100, 255, 100) if self.materials_collected >= self.materials_needed else (255, 255, 255)
        materials_surface = self.font_normal.render(materials_text, True, materials_color)
        screen.blit(materials_surface, (50, 30))
        
        # Objetivo
        goal_text = f"Objetivo: {self.materials_needed}"
        goal_surface = self.font_small.render(goal_text, True, (200, 200, 200))
        screen.blit(goal_surface, (50, 60))
        
        # Combo indicator
        if self.combo > 0:
            combo_text = f"¡COMBO x{self.combo}!"
            combo_color = (255, 255, 100)
            if self.combo >= 5:
                combo_color = (255, 150, 50)
            if self.combo >= 10:
                combo_color = (255, 50, 50)
            
            combo_surface = self.font_large.render(combo_text, True, combo_color)
            combo_rect = combo_surface.get_rect()
            combo_rect.center = (self.screen_width // 2, 60)
            
            # Efecto de escala según combo
            scale = 1.0 + (min(self.combo, 10) * 0.05)
            scaled_width = int(combo_rect.width * scale)
            scaled_height = int(combo_rect.height * scale)
            scaled_surface = pygame.transform.scale(combo_surface, (scaled_width, scaled_height))
            scaled_rect = scaled_surface.get_rect()
            scaled_rect.center = combo_rect.center
            
            screen.blit(scaled_surface, scaled_rect)
        
        # Bonus de oro consecutivo
        if self.consecutive_gold >= 2:
            gold_bonus_text = f"¡ORO x{self.consecutive_gold}! +2 bonus"
            gold_surface = self.font_normal.render(gold_bonus_text, True, (255, 215, 0))
            gold_rect = gold_surface.get_rect()
            gold_rect.center = (self.screen_width // 2, 100)
            screen.blit(gold_surface, gold_rect)
        
        # Instrucciones
        instructions = [
            "Haz clic en los minerales antes de que desaparezcan",
            "Cobre: +1  |  Plata: +3  |  Oro: +5",
            "Combo de 3+ para bonus del 50%"
        ]
        self.render_instructions(screen, instructions)
        
        # Barra de progreso hacia el objetivo
        progress_bar_width = 300
        progress_bar_height = 20
        progress_bar_x = self.screen_width // 2 - progress_bar_width // 2
        progress_bar_y = self.screen_height - 180
        
        # Fondo de la barra
        pygame.draw.rect(screen, (50, 50, 50),
                        (progress_bar_x, progress_bar_y, progress_bar_width, progress_bar_height))
        
        # Progreso
        progress = min(1.0, self.materials_collected / self.materials_needed)
        fill_width = int(progress_bar_width * progress)
        
        # Color según progreso
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


# Alias para mantener compatibilidad
MiningMinigame = MineralRush