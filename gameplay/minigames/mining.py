"""
Mining Clicker - Minijuego de minería tipo clicker
"""

import pygame
import random
import os
import math
from typing import List, Dict, Any
from .base import BaseMinigame
import logging

logger = logging.getLogger(__name__)


class MiningParticle:
    """Partícula visual para efectos de minería"""
    
    def __init__(self, x: float, y: float, color: tuple):
        self.x = x
        self.y = y
        self.vx = random.uniform(-200, 200)
        self.vy = random.uniform(-300, -100)
        self.color = color
        self.lifetime = random.uniform(0.5, 1.0)
        self.max_lifetime = self.lifetime
        self.size = random.randint(2, 5)
    
    def update(self, delta_time: float):
        """Actualiza la partícula"""
        self.x += self.vx * delta_time
        self.y += self.vy * delta_time
        self.vy += 500 * delta_time  # Gravedad
        self.lifetime -= delta_time
    
    def draw(self, screen: pygame.Surface):
        """Dibuja la partícula"""
        if self.lifetime > 0:
            alpha = self.lifetime / self.max_lifetime
            size = int(self.size * alpha)
            if size > 0:
                pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)


class MiningMinigame(BaseMinigame):
    """
    Minijuego de minería tipo clicker
    
    El jugador debe hacer clic repetidamente en una roca para extraer minerales
    antes de que se acabe el tiempo
    """
    
    def __init__(self, screen_width: int = 1280, screen_height: int = 720):
        super().__init__(screen_width, screen_height)
        
        # Configuración del minijuego
        self.time_remaining = 20.0
        self.clicks_needed = 30
        self.clicks_done = 0
        
        # Posición y tamaño de la roca
        self.rock_x = screen_width // 2
        self.rock_y = screen_height // 2
        self.rock_base_size = 150
        self.rock_size = self.rock_base_size
        
        # Estado de la roca
        self.rock_health = 100
        self.rock_max_health = 100
        self.damage_per_click = 100 / self.clicks_needed
        
        # Minerales disponibles
        self.minerals = [
            {'name': 'Cobre', 'color': (184, 115, 51), 'value': 1},
            {'name': 'Plata', 'color': (192, 192, 192), 'value': 2},
            {'name': 'Oro', 'color': (255, 215, 0), 'value': 3}
        ]
        self.current_mineral = random.choice(self.minerals)
        
        # Efectos visuales
        self.particles: List[MiningParticle] = []
        self.shake_amount = 0
        self.shake_decay = 10
        
        # Control
        self.can_click = True
        self.click_cooldown = 0.0
        self.click_cooldown_time = 0.05
        
        # Combo system
        self.combo = 0
        self.combo_timer = 0.0
        self.combo_timeout = 1.0
        self.max_combo = 0
        
        # Animación
        self.rock_crack_level = 0  # 0-4 niveles de grietas
        
        # Fondo
        self.background = None
        
        logger.info("Mining Clicker minijuego inicializado")
    
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
            
            # Cargar iconos de minerales si existen
            mineral_assets = {
                'copper': os.path.join('data', 'assets', 'copper_mineral.png'),
                'silver': os.path.join('data', 'assets', 'silver_mineral.png'),
                'gold': os.path.join('data', 'assets', 'gold_mineral.png')
            }
            
            for key, path in mineral_assets.items():
                if os.path.exists(path):
                    self.assets[key] = pygame.image.load(path)
                    self.assets[key] = pygame.transform.scale(self.assets[key], (32, 32))
                    
        except Exception as e:
            logger.warning(f"No se pudo cargar assets: {e}")
    
    def handle_input(self, event: pygame.event.Event):
        """Maneja la entrada del usuario"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Click izquierdo
                mouse_x, mouse_y = event.pos
                # Verificar si el click está sobre la roca
                distance = math.sqrt((mouse_x - self.rock_x)**2 + (mouse_y - self.rock_y)**2)
                if distance <= self.rock_size and self.can_click:
                    self.mine_rock()
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Alternativa con teclado
                if self.can_click:
                    self.mine_rock()
            elif event.key == pygame.K_ESCAPE:
                # Salir del minijuego
                self.complete_minigame(False)
    
    def mine_rock(self):
        """Procesa un click de minería"""
        if self.can_click and self.rock_health > 0:
            # Aplicar daño a la roca
            self.rock_health -= self.damage_per_click * (1 + self.combo * 0.1)  # Bonus por combo
            self.clicks_done += 1
            
            # Actualizar combo
            self.combo += 1
            self.combo_timer = self.combo_timeout
            self.max_combo = max(self.max_combo, self.combo)
            
            # Añadir puntos
            self.score += 10 * (1 + self.combo // 5)
            
            # Efectos visuales
            self.create_particles()
            self.shake_amount = 10
            
            # Actualizar nivel de grietas
            health_percent = self.rock_health / self.rock_max_health
            if health_percent <= 0:
                self.rock_crack_level = 4
            elif health_percent <= 0.25:
                self.rock_crack_level = 3
            elif health_percent <= 0.5:
                self.rock_crack_level = 2
            elif health_percent <= 0.75:
                self.rock_crack_level = 1
            
            # Cooldown
            self.can_click = False
            self.click_cooldown = self.click_cooldown_time
            
            # Verificar si la roca fue destruida
            if self.rock_health <= 0:
                self.rock_destroyed()
    
    def rock_destroyed(self):
        """Maneja la destrucción de la roca"""
        # Crear explosión de partículas
        for _ in range(30):
            self.create_particles()
        
        # Resetear la roca con un nuevo mineral
        self.rock_health = self.rock_max_health
        self.rock_crack_level = 0
        self.current_mineral = random.choice(self.minerals)
        
        # Bonus de puntos
        self.score += 100 * self.current_mineral['value']
    
    def create_particles(self):
        """Crea partículas de mineral"""
        num_particles = random.randint(3, 8)
        for _ in range(num_particles):
            # Posición aleatoria cerca de la roca
            angle = random.uniform(0, 360)
            distance = random.uniform(0, self.rock_size * 0.7)
            x = self.rock_x + distance * math.cos(math.radians(angle))
            y = self.rock_y + distance * math.sin(math.radians(angle))
            
            # Color basado en el mineral actual
            particle = MiningParticle(x, y, self.current_mineral['color'])
            self.particles.append(particle)
    
    def update(self, delta_time: float):
        """Actualiza la lógica del minijuego"""
        # Actualizar temporizador
        self.time_remaining -= delta_time
        
        # Verificar condiciones de finalización
        if self.time_remaining <= 0:
            success = self.clicks_done >= self.clicks_needed
            self.calculate_rewards(success)
            self.complete_minigame(success)
            return
        
        if self.clicks_done >= self.clicks_needed:
            self.calculate_rewards(True)
            self.complete_minigame(True)
            return
        
        # Actualizar cooldown de click
        if not self.can_click:
            self.click_cooldown -= delta_time
            if self.click_cooldown <= 0:
                self.can_click = True
        
        # Actualizar combo
        if self.combo > 0:
            self.combo_timer -= delta_time
            if self.combo_timer <= 0:
                self.combo = 0
        
        # Actualizar shake
        if self.shake_amount > 0:
            self.shake_amount -= self.shake_decay * delta_time * 60
            self.shake_amount = max(0, self.shake_amount)
        
        # Actualizar partículas
        for particle in self.particles[:]:
            particle.update(delta_time)
            if particle.lifetime <= 0:
                self.particles.remove(particle)
        
        # Animación de la roca (pulso)
        pulse = math.sin(pygame.time.get_ticks() * 0.002) * 5
        self.rock_size = self.rock_base_size + pulse
    
    def calculate_rewards(self, success: bool):
        """Calcula las recompensas del minijuego"""
        if success:
            # Recompensa base
            self.reward_materials = random.randint(3, 8)
            # Bonus por combo máximo
            if self.max_combo >= 10:
                self.reward_materials += 2
            if self.max_combo >= 20:
                self.reward_materials += 3
        else:
            # Recompensa mínima
            self.reward_materials = 1
    
    def render(self, screen: pygame.Surface):
        """Renderiza el minijuego"""
        # Aplicar shake si es necesario
        shake_offset_x = 0
        shake_offset_y = 0
        if self.shake_amount > 0:
            shake_offset_x = random.randint(-int(self.shake_amount), int(self.shake_amount))
            shake_offset_y = random.randint(-int(self.shake_amount), int(self.shake_amount))
        
        # Crear superficie temporal para aplicar shake
        temp_surface = pygame.Surface((self.screen_width, self.screen_height))
        
        # Limpiar pantalla o dibujar fondo
        if self.background:
            temp_surface.blit(self.background, (0, 0))
        else:
            temp_surface.fill((101, 67, 33))  # Color marrón tierra
            
            # Dibujar patrón de cueva
            for i in range(0, self.screen_width, 50):
                for j in range(0, self.screen_height, 50):
                    if (i + j) % 100 == 0:
                        pygame.draw.circle(temp_surface, (81, 47, 13), (i, j), 20)
        
        # Renderizar la roca
        self.render_rock(temp_surface)
        
        # Renderizar partículas
        for particle in self.particles:
            particle.draw(temp_surface)
        
        # Aplicar shake
        screen.blit(temp_surface, (shake_offset_x, shake_offset_y))
        
        # Renderizar UI (sin shake)
        self.render_ui(screen)
    
    def render_rock(self, screen: pygame.Surface):
        """Renderiza la roca de mineral"""
        # Color base de la roca
        rock_color = (105, 105, 105)
        
        # Dibujar sombra
        shadow_offset = 10
        pygame.draw.ellipse(screen, (0, 0, 0, 128),
                           (self.rock_x - self.rock_size + shadow_offset,
                            self.rock_y - self.rock_size // 2 + shadow_offset,
                            self.rock_size * 2, self.rock_size))
        
        # Dibujar roca principal
        pygame.draw.ellipse(screen, rock_color,
                           (self.rock_x - self.rock_size,
                            self.rock_y - self.rock_size // 2,
                            self.rock_size * 2, self.rock_size))
        
        # Dibujar vetas de mineral
        vein_color = self.current_mineral['color']
        for i in range(3):
            angle = 120 * i + pygame.time.get_ticks() * 0.01
            x = self.rock_x + math.cos(math.radians(angle)) * self.rock_size * 0.5
            y = self.rock_y + math.sin(math.radians(angle)) * self.rock_size * 0.3
            pygame.draw.circle(screen, vein_color, (int(x), int(y)), 10)
        
        # Dibujar grietas según el daño
        if self.rock_crack_level > 0:
            crack_color = (50, 50, 50)
            for i in range(self.rock_crack_level):
                start_angle = random.randint(0, 360)
                start_x = self.rock_x + math.cos(math.radians(start_angle)) * self.rock_size * 0.3
                start_y = self.rock_y + math.sin(math.radians(start_angle)) * self.rock_size * 0.2
                end_angle = start_angle + random.randint(30, 90)
                end_x = self.rock_x + math.cos(math.radians(end_angle)) * self.rock_size * 0.7
                end_y = self.rock_y + math.sin(math.radians(end_angle)) * self.rock_size * 0.4
                pygame.draw.line(screen, crack_color,
                               (int(start_x), int(start_y)),
                               (int(end_x), int(end_y)), 2)
        
        # Dibujar barra de salud de la roca
        if self.rock_health < self.rock_max_health:
            bar_width = self.rock_size * 2
            bar_height = 10
            bar_x = self.rock_x - bar_width // 2
            bar_y = self.rock_y - self.rock_size - 20
            
            # Fondo de la barra
            pygame.draw.rect(screen, (50, 50, 50),
                           (bar_x, bar_y, bar_width, bar_height))
            
            # Barra de salud
            health_percent = self.rock_health / self.rock_max_health
            fill_width = int(bar_width * health_percent)
            pygame.draw.rect(screen, (255, 100, 100),
                           (bar_x, bar_y, fill_width, bar_height))
            
            # Borde
            pygame.draw.rect(screen, (255, 255, 255),
                           (bar_x, bar_y, bar_width, bar_height), 1)
    
    def render_ui(self, screen: pygame.Surface):
        """Renderiza la interfaz del minijuego"""
        # Renderizar temporizador
        self.render_timer(screen)
        
        # Renderizar puntuación
        self.render_score(screen)
        
        # Renderizar progreso
        progress_text = f"Clicks: {self.clicks_done}/{self.clicks_needed}"
        color = (100, 255, 100) if self.clicks_done >= self.clicks_needed else (255, 255, 255)
        text_surface = self.font_normal.render(progress_text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (self.screen_width // 2, 70)
        screen.blit(text_surface, text_rect)
        
        # Renderizar combo
        if self.combo > 0:
            combo_text = f"¡Combo x{self.combo}!"
            combo_color = (255, 255, 100) if self.combo < 10 else (255, 200, 0)
            if self.combo >= 20:
                combo_color = (255, 100, 100)
            
            combo_surface = self.font_large.render(combo_text, True, combo_color)
            combo_rect = combo_surface.get_rect()
            combo_rect.center = (self.screen_width // 2, 150)
            
            # Aplicar escala según el combo
            scale = 1 + (self.combo * 0.02)
            scaled_surface = pygame.transform.scale(combo_surface,
                                                   (int(combo_rect.width * scale),
                                                    int(combo_rect.height * scale)))
            scaled_rect = scaled_surface.get_rect()
            scaled_rect.center = combo_rect.center
            screen.blit(scaled_surface, scaled_rect)
        
        # Renderizar mineral actual
        mineral_text = f"Mineral: {self.current_mineral['name']}"
        mineral_surface = self.font_normal.render(mineral_text, True, self.current_mineral['color'])
        mineral_rect = mineral_surface.get_rect()
        mineral_rect.topleft = (50, 70)
        screen.blit(mineral_surface, mineral_rect)
        
        # Renderizar instrucciones
        instructions = [
            "Haz clic en la roca o presiona ESPACIO",
            f"Destruye la roca {self.clicks_needed} veces",
            "¡Mantén el combo para más puntos!"
        ]
        self.render_instructions(screen, instructions)