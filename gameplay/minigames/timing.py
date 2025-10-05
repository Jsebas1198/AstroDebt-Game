"""
Timing Precision - Minijuego de precisión temporal para reparación
"""

import pygame
import random
import math
import os
from typing import List, Dict, Any
from .base import BaseMinigame
import logging

logger = logging.getLogger(__name__)


class TimingBar:
    """Representa una barra de timing individual"""
    
    def __init__(self, y_position: int, screen_width: int, speed: float = 200):
        self.y = y_position
        self.screen_width = screen_width
        self.speed = speed
        
        # Posición del indicador móvil
        self.indicator_x = 0
        self.direction = 1  # 1 = derecha, -1 = izquierda
        
        # Zona de éxito
        self.target_x = screen_width // 2
        self.target_width = 100
        self.perfect_width = 30  # Zona perfecta dentro del target
        
        # Estado
        self.active = True
        self.hit = False
        self.perfect_hit = False
        self.missed = False
        
        # Visual
        self.bar_height = 60
        self.flash_timer = 0
    
    def update(self, delta_time: float):
        """Actualiza la posición del indicador"""
        if self.active and not self.hit and not self.missed:
            # Mover el indicador
            self.indicator_x += self.speed * self.direction * delta_time
            
            # Rebotar en los bordes
            margin = 50
            if self.indicator_x <= margin:
                self.indicator_x = margin
                self.direction = 1
            elif self.indicator_x >= self.screen_width - margin:
                self.indicator_x = self.screen_width - margin
                self.direction = -1
        
        # Actualizar flash
        if self.flash_timer > 0:
            self.flash_timer -= delta_time
    
    def check_hit(self) -> str:
        """
        Verifica si el indicador está en la zona de éxito
        
        Returns:
            'perfect', 'good', o 'miss'
        """
        if not self.active or self.hit or self.missed:
            return 'miss'
        
        distance = abs(self.indicator_x - self.target_x)
        
        if distance <= self.perfect_width / 2:
            self.perfect_hit = True
            self.hit = True
            self.flash_timer = 0.5
            return 'perfect'
        elif distance <= self.target_width / 2:
            self.hit = True
            self.flash_timer = 0.3
            return 'good'
        else:
            self.missed = True
            self.flash_timer = 0.3
            return 'miss'
    
    def draw(self, screen: pygame.Surface):
        """Dibuja la barra de timing"""
        # Color de fondo de la barra
        bar_color = (50, 50, 50)
        if self.hit:
            if self.perfect_hit:
                bar_color = (0, 100, 0)
            else:
                bar_color = (0, 50, 100)
        elif self.missed:
            bar_color = (100, 0, 0)
        
        # Dibujar barra de fondo
        bar_rect = pygame.Rect(40, self.y - self.bar_height // 2,
                               self.screen_width - 80, self.bar_height)
        pygame.draw.rect(screen, bar_color, bar_rect)
        pygame.draw.rect(screen, (100, 100, 100), bar_rect, 2)
        
        # Dibujar zona de éxito
        target_rect = pygame.Rect(self.target_x - self.target_width // 2,
                                  self.y - self.bar_height // 2 + 5,
                                  self.target_width, self.bar_height - 10)
        
        target_color = (0, 200, 0) if not self.missed else (200, 0, 0)
        if self.flash_timer > 0 and self.hit:
            alpha = self.flash_timer * 2
            target_color = tuple(int(c + (255 - c) * alpha) for c in target_color)
        
        pygame.draw.rect(screen, target_color, target_rect)
        
        # Dibujar zona perfecta
        perfect_rect = pygame.Rect(self.target_x - self.perfect_width // 2,
                                   self.y - self.bar_height // 2 + 10,
                                   self.perfect_width, self.bar_height - 20)
        perfect_color = (255, 215, 0)  # Dorado
        pygame.draw.rect(screen, perfect_color, perfect_rect)
        
        # Dibujar indicador móvil
        if not self.hit and not self.missed:
            indicator_color = (255, 255, 255)
            indicator_width = 10
            indicator_rect = pygame.Rect(self.indicator_x - indicator_width // 2,
                                        self.y - self.bar_height // 2 - 5,
                                        indicator_width, self.bar_height + 10)
            pygame.draw.rect(screen, indicator_color, indicator_rect)
            
            # Efecto de brillo
            glow_rect = pygame.Rect(self.indicator_x - indicator_width // 2 - 2,
                                    self.y - self.bar_height // 2 - 7,
                                    indicator_width + 4, self.bar_height + 14)
            pygame.draw.rect(screen, (150, 150, 255), glow_rect, 2)


class TimingMinigame(BaseMinigame):
    """
    Minijuego de precisión temporal
    
    El jugador debe presionar espacio cuando el indicador esté en la zona verde
    Debe lograr 3 aciertos consecutivos para tener éxito
    """
    
    def __init__(self, screen_width: int = 1280, screen_height: int = 720):
        super().__init__(screen_width, screen_height)
        
        # Configuración del minijuego
        self.time_remaining = 30.0
        self.hits_needed = 3
        self.hits_done = 0
        self.perfect_hits = 0
        self.misses = 0
        
        # Barras de timing
        self.bars: List[TimingBar] = []
        self.current_bar_index = 0
        
        # Dificultad (DEBE estar antes de create_bars)
        self.base_speed = 200
        self.speed_increase = 50  # Aumenta con cada acierto
        
        # Crear las barras (después de inicializar base_speed)
        self.create_bars()
        
        # Efectos visuales
        self.success_particles = []
        self.fail_flash = 0
        
        # Fondo
        self.background = None
        
        logger.info("Timing Precision minijuego inicializado")
    
    def load_assets(self):
        """Carga los assets del minijuego"""
        try:
            # Cargar fondo
            bg_path = os.path.join('data', 'assets', 'minigame_timing_bg.png')
            if os.path.exists(bg_path):
                self.background = pygame.image.load(bg_path)
                self.background = pygame.transform.scale(self.background,
                                                        (self.screen_width, self.screen_height))
                logger.info("Fondo de timing cargado")
        except Exception as e:
            logger.warning(f"No se pudo cargar el fondo: {e}")
    
    def create_bars(self):
        """Crea las barras de timing"""
        # Posiciones Y para las barras
        y_positions = [
            self.screen_height // 2 - 100,
            self.screen_height // 2,
            self.screen_height // 2 + 100
        ]
        
        for i, y_pos in enumerate(y_positions):
            speed = self.base_speed + (i * self.speed_increase)
            bar = TimingBar(y_pos, self.screen_width, speed)
            # Solo la primera barra está activa inicialmente
            bar.active = (i == 0)
            self.bars.append(bar)
    
    def handle_input(self, event: pygame.event.Event):
        """Maneja la entrada del usuario"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.attempt_hit()
            elif event.key == pygame.K_ESCAPE:
                # Salir del minijuego
                self.complete_minigame(False)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Click izquierdo como alternativa
                self.attempt_hit()
    
    def attempt_hit(self):
        """Intenta hacer un hit en la barra actual"""
        if self.current_bar_index >= len(self.bars):
            return
        
        current_bar = self.bars[self.current_bar_index]
        result = current_bar.check_hit()
        
        if result == 'perfect':
            self.hits_done += 1
            self.perfect_hits += 1
            self.score += 100
            self.create_success_particles(current_bar.target_x, current_bar.y)
            logger.info("¡Hit perfecto!")
            
            # Pasar a la siguiente barra
            self.next_bar()
            
        elif result == 'good':
            self.hits_done += 1
            self.score += 50
            self.create_success_particles(current_bar.target_x, current_bar.y)
            logger.info("Hit bueno")
            
            # Pasar a la siguiente barra
            self.next_bar()
            
        else:  # miss
            self.misses += 1
            self.fail_flash = 0.5
            logger.info("Fallo")
            
            # Reiniciar desde la primera barra
            self.reset_bars()
    
    def next_bar(self):
        """Pasa a la siguiente barra"""
        self.current_bar_index += 1
        
        if self.current_bar_index >= len(self.bars):
            # Completó todas las barras
            self.calculate_rewards(True)
            self.complete_minigame(True)
        else:
            # Activar la siguiente barra
            self.bars[self.current_bar_index].active = True
    
    def reset_bars(self):
        """Reinicia todas las barras"""
        self.current_bar_index = 0
        self.hits_done = 0
        
        # Recrear las barras con mayor dificultad
        self.base_speed = min(400, self.base_speed + 20)
        self.bars.clear()
        self.create_bars()
    
    def create_success_particles(self, x: float, y: float):
        """Crea partículas de éxito"""
        for _ in range(20):
            particle = {
                'x': x,
                'y': y,
                'vx': random.uniform(-200, 200),
                'vy': random.uniform(-300, -100),
                'lifetime': 1.0,
                'color': random.choice([
                    (255, 255, 100),
                    (100, 255, 100),
                    (255, 200, 100)
                ])
            }
            self.success_particles.append(particle)
    
    def update(self, delta_time: float):
        """Actualiza la lógica del minijuego"""
        # Actualizar temporizador
        self.time_remaining -= delta_time
        
        # Verificar condiciones de finalización
        if self.time_remaining <= 0:
            # Se acabó el tiempo
            success = self.hits_done >= self.hits_needed
            self.calculate_rewards(success)
            self.complete_minigame(success)
            return
        
        # Actualizar barras
        for bar in self.bars:
            if bar.active:
                bar.update(delta_time)
        
        # Actualizar partículas
        for particle in self.success_particles[:]:
            particle['x'] += particle['vx'] * delta_time
            particle['y'] += particle['vy'] * delta_time
            particle['vy'] += 500 * delta_time  # Gravedad
            particle['lifetime'] -= delta_time
            
            if particle['lifetime'] <= 0:
                self.success_particles.remove(particle)
        
        # Actualizar flash de fallo
        if self.fail_flash > 0:
            self.fail_flash -= delta_time
    
    def calculate_rewards(self, success: bool):
        """Calcula las recompensas del minijuego"""
        if success:
            # Recompensa de reparación base
            self.reward_repair = random.randint(5, 15)
            
            # Bonus por hits perfectos
            if self.perfect_hits >= 3:
                self.reward_repair += 5
            
            # Penalización por muchos fallos
            if self.misses > 5:
                self.reward_repair = max(5, self.reward_repair - 3)
        else:
            # Sin reparación o daño menor
            if self.misses > 10:
                self.reward_repair = -2  # Daño a la nave
            else:
                self.reward_repair = 0
    
    def render(self, screen: pygame.Surface):
        """Renderiza el minijuego"""
        # Limpiar pantalla o dibujar fondo
        if self.background:
            screen.blit(self.background, (0, 0))
        else:
            # Fondo degradado
            for i in range(self.screen_height):
                color_value = int(20 + (i / self.screen_height) * 30)
                color = (color_value, color_value, color_value + 20)
                pygame.draw.line(screen, color, (0, i), (self.screen_width, i))
        
        # Flash de fallo
        if self.fail_flash > 0:
            flash_surface = pygame.Surface((self.screen_width, self.screen_height))
            flash_surface.fill((255, 0, 0))
            flash_surface.set_alpha(int(self.fail_flash * 100))
            screen.blit(flash_surface, (0, 0))
        
        # Renderizar barras
        for i, bar in enumerate(self.bars):
            bar.draw(screen)
            
            # Indicador de barra actual
            if i == self.current_bar_index and bar.active:
                arrow_x = 20
                arrow_y = bar.y
                points = [
                    (arrow_x, arrow_y),
                    (arrow_x - 15, arrow_y - 10),
                    (arrow_x - 15, arrow_y + 10)
                ]
                pygame.draw.polygon(screen, (255, 255, 0), points)
        
        # Renderizar partículas
        for particle in self.success_particles:
            alpha = particle['lifetime']
            size = int(5 * alpha)
            if size > 0:
                pygame.draw.circle(screen, particle['color'],
                                 (int(particle['x']), int(particle['y'])), size)
        
        # Renderizar UI
        self.render_ui(screen)
    
    def render_ui(self, screen: pygame.Surface):
        """Renderiza la interfaz del minijuego"""
        # Renderizar temporizador
        self.render_timer(screen)
        
        # Renderizar puntuación
        self.render_score(screen)
        
        # Renderizar progreso
        progress_text = f"Barras: {self.current_bar_index}/{len(self.bars)}"
        color = (100, 255, 100) if self.current_bar_index >= len(self.bars) else (255, 255, 255)
        text_surface = self.font_normal.render(progress_text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (self.screen_width // 2, 70)
        screen.blit(text_surface, text_rect)
        
        # Renderizar estadísticas
        stats_y = 100
        
        # Hits perfectos
        if self.perfect_hits > 0:
            perfect_text = f"Perfectos: {self.perfect_hits}"
            perfect_surface = self.font_small.render(perfect_text, True, (255, 215, 0))
            perfect_rect = perfect_surface.get_rect()
            perfect_rect.topleft = (50, stats_y)
            screen.blit(perfect_surface, perfect_rect)
        
        # Fallos
        if self.misses > 0:
            miss_text = f"Fallos: {self.misses}"
            miss_color = (255, 100, 100) if self.misses > 3 else (255, 200, 200)
            miss_surface = self.font_small.render(miss_text, True, miss_color)
            miss_rect = miss_surface.get_rect()
            miss_rect.topleft = (50, stats_y + 25)
            screen.blit(miss_surface, miss_rect)
        
        # Renderizar instrucciones
        instructions = [
            "Presiona ESPACIO cuando el indicador esté en la zona verde",
            "Zona dorada = Puntos extra",
            "Completa las 3 barras consecutivas para ganar"
        ]
        self.render_instructions(screen, instructions)