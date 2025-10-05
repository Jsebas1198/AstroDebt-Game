"""
Asteroid Shooter - Minijuego de disparar asteroides para obtener materiales
"""

import pygame
import random
import math
import os
from typing import List, Tuple
from .base import BaseMinigame
import logging

logger = logging.getLogger(__name__)


class Asteroid:
    """Representa un asteroide en el minijuego"""
    
    def __init__(self, x: float, y: float, size: int, speed: float):
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed
        self.angle = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-5, 5)
        self.color = random.choice([
            (139, 69, 19),   # Marrón
            (105, 105, 105), # Gris
            (169, 169, 169), # Gris claro
            (218, 165, 32)   # Dorado
        ])
        self.health = size // 20  # Asteroides más grandes requieren más disparos
        self.max_health = self.health
    
    def update(self, delta_time: float):
        """Actualiza la posición del asteroide"""
        self.y += self.speed * delta_time
        self.angle += self.rotation_speed
    
    def draw(self, screen: pygame.Surface):
        """Dibuja el asteroide"""
        # Dibujar asteroide como polígono irregular
        points = []
        num_points = 8
        for i in range(num_points):
            angle = (360 / num_points) * i + self.angle
            radius = self.size + random.randint(-5, 5)
            x = self.x + radius * math.cos(math.radians(angle))
            y = self.y + radius * math.sin(math.radians(angle))
            points.append((x, y))
        
        pygame.draw.polygon(screen, self.color, points)
        
        # Dibujar barra de salud si está dañado
        if self.health < self.max_health:
            bar_width = self.size * 2
            bar_height = 4
            bar_x = self.x - bar_width // 2
            bar_y = self.y - self.size - 10
            
            # Fondo de la barra
            pygame.draw.rect(screen, (50, 50, 50), 
                           (bar_x, bar_y, bar_width, bar_height))
            
            # Barra de salud
            health_percent = self.health / self.max_health
            fill_width = int(bar_width * health_percent)
            if health_percent > 0.5:
                color = (0, 255, 0)
            elif health_percent > 0.25:
                color = (255, 255, 0)
            else:
                color = (255, 0, 0)
            
            pygame.draw.rect(screen, color, 
                           (bar_x, bar_y, fill_width, bar_height))
    
    def hit(self, damage: int = 1) -> bool:
        """
        Daña el asteroide
        
        Returns:
            True si el asteroide fue destruido
        """
        self.health -= damage
        return self.health <= 0
    
    def get_rect(self) -> pygame.Rect:
        """Obtiene el rectángulo de colisión"""
        return pygame.Rect(self.x - self.size, self.y - self.size, 
                          self.size * 2, self.size * 2)


class Projectile:
    """Representa un proyectil disparado por el jugador"""
    
    def __init__(self, x: float, y: float, target_x: float, target_y: float):
        self.x = x
        self.y = y
        self.speed = 800
        
        # Calcular dirección hacia el objetivo
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            self.vx = (dx / distance) * self.speed
            self.vy = (dy / distance) * self.speed
        else:
            self.vx = 0
            self.vy = -self.speed
        
        self.alive = True
        self.radius = 5
    
    def update(self, delta_time: float):
        """Actualiza la posición del proyectil"""
        self.x += self.vx * delta_time
        self.y += self.vy * delta_time
        
        # Marcar como muerto si sale de la pantalla
        if self.x < -50 or self.x > 1330 or self.y < -50 or self.y > 770:
            self.alive = False
    
    def draw(self, screen: pygame.Surface):
        """Dibuja el proyectil"""
        pygame.draw.circle(screen, (255, 255, 100), (int(self.x), int(self.y)), self.radius)
        # Efecto de brillo
        pygame.draw.circle(screen, (255, 255, 200), (int(self.x), int(self.y)), self.radius - 2)
    
    def get_rect(self) -> pygame.Rect:
        """Obtiene el rectángulo de colisión"""
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                          self.radius * 2, self.radius * 2)


class AsteroidShooterMinigame(BaseMinigame):
    """
    Minijuego de disparar asteroides
    
    El jugador debe destruir asteroides que caen desde arriba
    usando un cañón controlado con el mouse o teclado
    """
    
    def __init__(self, screen_width: int = 1280, screen_height: int = 720):
        super().__init__(screen_width, screen_height)
        
        # Configuración del minijuego
        self.time_remaining = 30.0
        self.asteroids_destroyed = 0
        self.asteroids_needed = 5
        
        # Listas de objetos
        self.asteroids: List[Asteroid] = []
        self.projectiles: List[Projectile] = []
        
        # Posición del cañón (en la parte inferior)
        self.cannon_x = screen_width // 2
        self.cannon_y = screen_height - 100
        self.cannon_angle = -90  # Apuntando hacia arriba
        
        # Control
        self.mouse_control = True
        self.can_shoot = True
        self.shoot_cooldown = 0.0
        self.shoot_cooldown_time = 0.2
        
        # Generación de asteroides
        self.asteroid_spawn_timer = 0.0
        self.asteroid_spawn_rate = 2.0  # Segundos entre spawns
        
        # Fondo
        self.background = None
        
        # Efectos
        self.explosions = []
        
        logger.info("Asteroid Shooter minijuego inicializado")
    
    def load_assets(self):
        """Carga los assets del minijuego"""
        try:
            # Cargar fondo
            bg_path = os.path.join('data', 'assets', 'minigame_asteroid.png')
            if os.path.exists(bg_path):
                self.background = pygame.image.load(bg_path)
                self.background = pygame.transform.scale(self.background, 
                                                        (self.screen_width, self.screen_height))
                logger.info("Fondo de asteroide cargado")
        except Exception as e:
            logger.warning(f"No se pudo cargar el fondo: {e}")
    
    def handle_input(self, event: pygame.event.Event):
        """Maneja la entrada del usuario"""
        if event.type == pygame.MOUSEMOTION:
            # Actualizar posición del cañón con el mouse
            if self.mouse_control:
                mouse_x, mouse_y = event.pos
                # Calcular ángulo del cañón hacia el mouse
                dx = mouse_x - self.cannon_x
                dy = mouse_y - self.cannon_y
                self.cannon_angle = math.degrees(math.atan2(dy, dx))
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Click izquierdo
                self.shoot(event.pos[0], event.pos[1])
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Disparar hacia arriba si se usa el teclado
                target_x = self.cannon_x + math.cos(math.radians(self.cannon_angle)) * 100
                target_y = self.cannon_y + math.sin(math.radians(self.cannon_angle)) * 100
                self.shoot(target_x, target_y)
            elif event.key == pygame.K_LEFT:
                self.cannon_angle -= 10
                self.mouse_control = False
            elif event.key == pygame.K_RIGHT:
                self.cannon_angle += 10
                self.mouse_control = False
            elif event.key == pygame.K_ESCAPE:
                # Salir del minijuego (fallo)
                self.complete_minigame(False)
    
    def shoot(self, target_x: float, target_y: float):
        """Dispara un proyectil hacia la posición objetivo"""
        if self.can_shoot:
            projectile = Projectile(self.cannon_x, self.cannon_y, target_x, target_y)
            self.projectiles.append(projectile)
            self.can_shoot = False
            self.shoot_cooldown = self.shoot_cooldown_time
    
    def spawn_asteroid(self):
        """Genera un nuevo asteroide"""
        x = random.randint(50, self.screen_width - 50)
        y = -50
        size = random.randint(20, 40)
        speed = random.uniform(50, 150)
        
        asteroid = Asteroid(x, y, size, speed)
        self.asteroids.append(asteroid)
    
    def update(self, delta_time: float):
        """Actualiza la lógica del minijuego"""
        # Actualizar temporizador
        self.time_remaining -= delta_time
        
        # Verificar condiciones de finalización
        if self.time_remaining <= 0:
            # Se acabó el tiempo
            success = self.asteroids_destroyed >= self.asteroids_needed
            self.calculate_rewards(success)
            self.complete_minigame(success)
            return
        
        if self.asteroids_destroyed >= self.asteroids_needed:
            # Objetivo cumplido
            self.calculate_rewards(True)
            self.complete_minigame(True)
            return
        
        # Actualizar cooldown de disparo
        if not self.can_shoot:
            self.shoot_cooldown -= delta_time
            if self.shoot_cooldown <= 0:
                self.can_shoot = True
        
        # Generar asteroides
        self.asteroid_spawn_timer += delta_time
        if self.asteroid_spawn_timer >= self.asteroid_spawn_rate:
            self.spawn_asteroid()
            self.asteroid_spawn_timer = 0
            # Aumentar dificultad gradualmente
            self.asteroid_spawn_rate = max(0.5, self.asteroid_spawn_rate - 0.1)
        
        # Actualizar asteroides
        for asteroid in self.asteroids[:]:
            asteroid.update(delta_time)
            
            # Eliminar si sale de la pantalla
            if asteroid.y > self.screen_height + 100:
                self.asteroids.remove(asteroid)
        
        # Actualizar proyectiles
        for projectile in self.projectiles[:]:
            projectile.update(delta_time)
            
            if not projectile.alive:
                self.projectiles.remove(projectile)
                continue
            
            # Verificar colisiones con asteroides
            projectile_rect = projectile.get_rect()
            for asteroid in self.asteroids[:]:
                if projectile_rect.colliderect(asteroid.get_rect()):
                    # Impacto
                    if asteroid.hit():
                        # Asteroide destruido
                        self.asteroids_destroyed += 1
                        self.score += 100 * (asteroid.size // 10)
                        self.asteroids.remove(asteroid)
                        self.create_explosion(asteroid.x, asteroid.y, asteroid.size)
                    
                    # Eliminar proyectil
                    projectile.alive = False
                    break
        
        # Actualizar explosiones
        for explosion in self.explosions[:]:
            explosion['lifetime'] -= delta_time
            if explosion['lifetime'] <= 0:
                self.explosions.remove(explosion)
    
    def create_explosion(self, x: float, y: float, size: int):
        """Crea un efecto de explosión"""
        self.explosions.append({
            'x': x,
            'y': y,
            'size': size,
            'lifetime': 0.5,
            'max_lifetime': 0.5
        })
    
    def calculate_rewards(self, success: bool):
        """Calcula las recompensas del minijuego"""
        if success:
            # Recompensa base + bonus por asteroides extra
            self.reward_materials = random.randint(5, 10)
            bonus = min(5, self.asteroids_destroyed - self.asteroids_needed)
            self.reward_materials += bonus
        else:
            # Recompensa mínima por participar
            self.reward_materials = random.randint(1, 2)
    
    def render(self, screen: pygame.Surface):
        """Renderiza el minijuego"""
        # Limpiar pantalla o dibujar fondo
        if self.background:
            screen.blit(self.background, (0, 0))
        else:
            screen.fill((10, 10, 30))
            
            # Dibujar estrellas de fondo
            for _ in range(100):
                x = random.randint(0, self.screen_width)
                y = random.randint(0, self.screen_height)
                pygame.draw.circle(screen, (255, 255, 255), (x, y), 1)
        
        # Renderizar asteroides
        for asteroid in self.asteroids:
            asteroid.draw(screen)
        
        # Renderizar proyectiles
        for projectile in self.projectiles:
            projectile.draw(screen)
        
        # Renderizar explosiones
        for explosion in self.explosions:
            alpha = explosion['lifetime'] / explosion['max_lifetime']
            radius = explosion['size'] * (1 + (1 - alpha))
            color = (255, int(200 * alpha), int(100 * alpha))
            pygame.draw.circle(screen, color, 
                             (int(explosion['x']), int(explosion['y'])), 
                             int(radius), 2)
        
        # Renderizar cañón
        self.render_cannon(screen)
        
        # Renderizar UI
        self.render_ui(screen)
    
    def render_cannon(self, screen: pygame.Surface):
        """Renderiza el cañón del jugador"""
        # Base del cañón
        pygame.draw.circle(screen, (100, 100, 100), 
                         (self.cannon_x, self.cannon_y), 30)
        pygame.draw.circle(screen, (150, 150, 150), 
                         (self.cannon_x, self.cannon_y), 25)
        
        # Tubo del cañón
        cannon_length = 50
        end_x = self.cannon_x + cannon_length * math.cos(math.radians(self.cannon_angle))
        end_y = self.cannon_y + cannon_length * math.sin(math.radians(self.cannon_angle))
        
        pygame.draw.line(screen, (80, 80, 80), 
                        (self.cannon_x, self.cannon_y), 
                        (end_x, end_y), 10)
        pygame.draw.line(screen, (120, 120, 120), 
                        (self.cannon_x, self.cannon_y), 
                        (end_x, end_y), 6)
        
        # Indicador de recarga
        if not self.can_shoot:
            reload_percent = 1 - (self.shoot_cooldown / self.shoot_cooldown_time)
            bar_width = 60
            bar_height = 6
            bar_x = self.cannon_x - bar_width // 2
            bar_y = self.cannon_y + 40
            
            pygame.draw.rect(screen, (50, 50, 50), 
                           (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(screen, (255, 255, 0), 
                           (bar_x, bar_y, int(bar_width * reload_percent), bar_height))
    
    def render_ui(self, screen: pygame.Surface):
        """Renderiza la interfaz del minijuego"""
        # Renderizar temporizador
        self.render_timer(screen)
        
        # Renderizar puntuación
        self.render_score(screen)
        
        # Renderizar objetivo
        objective_text = f"Asteroides: {self.asteroids_destroyed}/{self.asteroids_needed}"
        color = (100, 255, 100) if self.asteroids_destroyed >= self.asteroids_needed else (255, 255, 255)
        text_surface = self.font_normal.render(objective_text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (self.screen_width // 2, 70)
        screen.blit(text_surface, text_rect)
        
        # Renderizar instrucciones
        instructions = [
            "Mueve el mouse para apuntar",
            "Click izquierdo o ESPACIO para disparar",
            "Destruye 5 asteroides antes de que se acabe el tiempo"
        ]
        self.render_instructions(screen, instructions)
