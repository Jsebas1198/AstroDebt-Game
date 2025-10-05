"""
Oxygen Rescue - Minijuego de rescate del marciano para obtener oxígeno
"""

import pygame
import math
import random
from typing import List, Tuple, Optional
from .base import BaseMinigame
import logging
import os

logger = logging.getLogger(__name__)


class Projectile:
    """Representa un proyectil (del jugador o enemigo)"""
    
    def __init__(self, x: float, y: float, vx: float, vy: float, is_player: bool = True):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.is_player = is_player
        self.radius = 8 if is_player else 10
        self.color = (255, 150, 50) if is_player else (100, 150, 255)
        self.active = True
    
    def update(self, delta_time: float):
        """Actualiza la posición del proyectil"""
        self.x += self.vx * delta_time
        self.y += self.vy * delta_time
    
    def draw(self, screen: pygame.Surface):
        """Dibuja el proyectil"""
        if self.active:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
            # Efecto de brillo
            pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), self.radius // 2)


class Enemy:
    """Representa un enemigo"""
    
    def __init__(self, spawn_side: str, screen_width: int, screen_height: int, image_path: str):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.spawn_side = spawn_side
        
        # Configurar posición inicial según el lado
        if spawn_side == "left":
            self.x = -50
            self.y = random.randint(100, screen_height - 100)
            self.target_x = random.randint(150, 250)
            self.vx = 100
        elif spawn_side == "right":
            self.x = screen_width + 50
            self.y = random.randint(100, screen_height - 100)
            self.target_x = random.randint(screen_width - 250, screen_width - 150)
            self.vx = -100
        else:  # top
            self.x = random.randint(100, screen_width - 100)
            self.y = -50
            self.target_x = self.x
            self.target_y = random.randint(100, 200)
            self.vx = 0
            self.vy = 100
        
        self.target_y = self.y if spawn_side in ["left", "right"] else self.target_y
        self.vy = 0 if spawn_side in ["left", "right"] else self.vy
        
        # Propiedades del enemigo
        self.max_health = 3
        self.health = self.max_health
        self.width = 60
        self.height = 60
        self.shoot_cooldown = 0
        self.shoot_interval = random.uniform(1.0, 1.5)
        self.active = True
        self.entering = True  # Estado de entrada a la pantalla
        
        # Cargar imagen
        self.image = None
        try:
            if os.path.exists(image_path):
                self.image = pygame.image.load(image_path)
                self.image = pygame.transform.scale(self.image, (self.width, self.height))
        except Exception as e:
            logger.warning(f"No se pudo cargar imagen del enemigo: {e}")
    
    def update(self, delta_time: float, player_x: float, player_y: float) -> Optional[Projectile]:
        """
        Actualiza el enemigo y retorna un proyectil si dispara
        """
        # Movimiento de entrada
        if self.entering:
            if self.spawn_side == "left":
                self.x += self.vx * delta_time
                if self.x >= self.target_x:
                    self.x = self.target_x
                    self.entering = False
            elif self.spawn_side == "right":
                self.x += self.vx * delta_time
                if self.x <= self.target_x:
                    self.x = self.target_x
                    self.entering = False
            else:  # top
                self.y += self.vy * delta_time
                if self.y >= self.target_y:
                    self.y = self.target_y
                    self.entering = False
        else:
            # Movimiento suave arriba/abajo cuando está en posición
            if self.spawn_side in ["left", "right"]:
                self.y += math.sin(pygame.time.get_ticks() * 0.001) * 50 * delta_time
        
        # Actualizar cooldown de disparo
        self.shoot_cooldown -= delta_time
        
        # Disparar si puede
        if self.shoot_cooldown <= 0 and not self.entering:
            self.shoot_cooldown = self.shoot_interval
            
            # Calcular dirección hacia el jugador
            dx = player_x - self.x
            dy = player_y - self.y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance > 0:
                # Normalizar y aplicar velocidad
                projectile_speed = 300
                vx = (dx / distance) * projectile_speed
                vy = (dy / distance) * projectile_speed
                
                return Projectile(self.x, self.y, vx, vy, is_player=False)
        
        return None
    
    def take_damage(self, damage: int = 1):
        """Aplica daño al enemigo"""
        self.health -= damage
        if self.health <= 0:
            self.active = False
    
    def draw(self, screen: pygame.Surface):
        """Dibuja el enemigo"""
        if not self.active:
            return
        
        # Dibujar enemigo
        if self.image:
            screen.blit(self.image, (self.x - self.width // 2, self.y - self.height // 2))
        else:
            # Fallback: dibujar un rectángulo
            color = (200, 50, 50)
            pygame.draw.rect(screen, color, 
                           (self.x - self.width // 2, self.y - self.height // 2, 
                            self.width, self.height))
        
        # Dibujar barra de vida
        bar_width = 50
        bar_height = 6
        bar_x = self.x - bar_width // 2
        bar_y = self.y - self.height // 2 - 15
        
        # Fondo de la barra
        pygame.draw.rect(screen, (50, 50, 50), 
                        (bar_x, bar_y, bar_width, bar_height))
        
        # Vida actual
        health_percentage = self.health / self.max_health
        health_color = (0, 200, 0) if health_percentage > 0.5 else (200, 200, 0) if health_percentage > 0.25 else (200, 0, 0)
        pygame.draw.rect(screen, health_color,
                        (bar_x, bar_y, int(bar_width * health_percentage), bar_height))
        
        # Borde de la barra
        pygame.draw.rect(screen, (100, 100, 100),
                        (bar_x, bar_y, bar_width, bar_height), 1)


class Player:
    """Representa al jugador"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Posición inicial (centro-abajo)
        self.x = screen_width // 2
        self.y = screen_height - 100
        
        # Propiedades
        self.width = 50
        self.height = 50
        self.speed = 400
        self.max_health = 5
        self.health = self.max_health
        self.angle = 0  # Ángulo de rotación hacia el cursor
        
        # Imagen
        self.image = None
        self.original_image = None
        try:
            image_path = os.path.join('data', 'assets', 'player_weapon.png')
            if os.path.exists(image_path):
                self.original_image = pygame.image.load(image_path)
                self.original_image = pygame.transform.scale(self.original_image, (self.width, self.height))
                self.image = self.original_image.copy()
        except Exception as e:
            logger.warning(f"No se pudo cargar imagen del jugador: {e}")
    
    def update(self, delta_time: float, keys: pygame.key.ScancodeWrapper, mouse_x: int, mouse_y: int):
        """Actualiza el jugador"""
        # Movimiento con WASD
        dx = 0
        dy = 0
        
        if keys[pygame.K_w]:
            dy = -self.speed * delta_time
        if keys[pygame.K_s]:
            dy = self.speed * delta_time
        if keys[pygame.K_a]:
            dx = -self.speed * delta_time
        if keys[pygame.K_d]:
            dx = self.speed * delta_time
        
        # Aplicar movimiento con límites
        self.x = max(self.width // 2, min(self.screen_width - self.width // 2, self.x + dx))
        self.y = max(self.height // 2, min(self.screen_height - self.height // 2, self.y + dy))
        
        # Calcular ángulo hacia el cursor
        angle_rad = math.atan2(mouse_y - self.y, mouse_x - self.x)
        self.angle = math.degrees(angle_rad)
        
        # Rotar imagen si existe
        if self.original_image:
            self.image = pygame.transform.rotate(self.original_image, -self.angle - 90)
    
    def shoot(self, mouse_x: int, mouse_y: int) -> Projectile:
        """Crea un proyectil hacia la posición del mouse"""
        dx = mouse_x - self.x
        dy = mouse_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            projectile_speed = 600
            vx = (dx / distance) * projectile_speed
            vy = (dy / distance) * projectile_speed
            return Projectile(self.x, self.y, vx, vy, is_player=True)
        
        return Projectile(self.x, self.y, 0, -projectile_speed, is_player=True)
    
    def take_damage(self, damage: int = 1):
        """Aplica daño al jugador"""
        self.health = max(0, self.health - damage)
    
    def draw(self, screen: pygame.Surface, mouse_x: int, mouse_y: int):
        """Dibuja el jugador"""
        # Dibujar jugador
        if self.image:
            # Centrar la imagen rotada
            rect = self.image.get_rect(center=(self.x, self.y))
            screen.blit(self.image, rect)
        else:
            # Fallback: dibujar un triángulo
            color = (100, 150, 255)
            points = [
                (self.x, self.y - self.height // 2),
                (self.x - self.width // 2, self.y + self.height // 2),
                (self.x + self.width // 2, self.y + self.height // 2)
            ]
            pygame.draw.polygon(screen, color, points)
        
        # Dibujar flecha indicadora de dirección
        arrow_length = 40
        angle_rad = math.atan2(mouse_y - self.y, mouse_x - self.x)
        arrow_end_x = self.x + math.cos(angle_rad) * arrow_length
        arrow_end_y = self.y + math.sin(angle_rad) * arrow_length
        
        # Línea principal de la flecha
        pygame.draw.line(screen, (255, 255, 100), (self.x, self.y), 
                        (arrow_end_x, arrow_end_y), 3)
        
        # Punta de la flecha
        arrow_angle1 = angle_rad + 2.5
        arrow_angle2 = angle_rad - 2.5
        arrow_size = 10
        
        point1 = (arrow_end_x - math.cos(arrow_angle1) * arrow_size,
                 arrow_end_y - math.sin(arrow_angle1) * arrow_size)
        point2 = (arrow_end_x - math.cos(arrow_angle2) * arrow_size,
                 arrow_end_y - math.sin(arrow_angle2) * arrow_size)
        
        pygame.draw.polygon(screen, (255, 255, 100), 
                          [(arrow_end_x, arrow_end_y), point1, point2])
        
        # Dibujar barra de vida
        bar_width = 60
        bar_height = 8
        bar_x = self.x - bar_width // 2
        bar_y = self.y - self.height // 2 - 20
        
        # Fondo de la barra
        pygame.draw.rect(screen, (50, 50, 50), 
                        (bar_x, bar_y, bar_width, bar_height))
        
        # Vida actual
        health_percentage = self.health / self.max_health
        health_color = (0, 200, 0) if health_percentage > 0.5 else (200, 200, 0) if health_percentage > 0.25 else (200, 0, 0)
        pygame.draw.rect(screen, health_color,
                        (bar_x, bar_y, int(bar_width * health_percentage), bar_height))
        
        # Borde de la barra
        pygame.draw.rect(screen, (150, 150, 150),
                        (bar_x, bar_y, bar_width, bar_height), 2)


class OxygenRescueMinigame(BaseMinigame):
    """
    Minijuego de rescate del marciano
    
    El jugador debe derrotar a todos los enemigos para rescatar al marciano
    y obtener +10 de oxígeno
    """
    
    def __init__(self, screen_width: int = 1280, screen_height: int = 720):
        super().__init__(screen_width, screen_height)
        
        # No usar tiempo límite para este minijuego
        self.time_remaining = -1  # Sin límite de tiempo
        
        # Jugador
        self.player = Player(screen_width, screen_height)
        
        # Enemigos
        self.enemies: List[Enemy] = []
        self.spawn_enemies()
        
        # Proyectiles
        self.projectiles: List[Projectile] = []
        
        # Estado del mouse
        self.mouse_x = screen_width // 2
        self.mouse_y = screen_height // 2
        
        # Efectos visuales
        self.explosions = []
        self.screen_flash = 0
        
        # Recompensa fija
        self.reward_oxygen = 10
        
        # Fondo
        self.background = None
        
        logger.info("Oxygen Rescue minijuego inicializado")
    
    def load_assets(self):
        """Carga los assets del minijuego"""
        try:
            # Intentar cargar un fondo espacial
            bg_path = os.path.join('data', 'assets', 'space_background.png')
            if os.path.exists(bg_path):
                self.background = pygame.image.load(bg_path)
                self.background = pygame.transform.scale(self.background,
                                                        (self.screen_width, self.screen_height))
                logger.info("Fondo de rescate cargado")
        except Exception as e:
            logger.warning(f"No se pudo cargar el fondo: {e}")
    
    def spawn_enemies(self):
        """Crea los enemigos iniciales"""
        # 2 enemigos desde la izquierda
        for i in range(2):
            image_path = os.path.join('data', 'assets', 'seal_left.png')
            enemy = Enemy("left", self.screen_width, self.screen_height, image_path)
            enemy.y = 200 + i * 150  # Separar verticalmente
            self.enemies.append(enemy)
        
        # 2 enemigos desde la derecha
        for i in range(2):
            image_path = os.path.join('data', 'assets', 'seal_right.png')
            enemy = Enemy("right", self.screen_width, self.screen_height, image_path)
            enemy.y = 200 + i * 150  # Separar verticalmente
            self.enemies.append(enemy)
        
        # 1 enemigo desde arriba (aleatorio entre seal_left o seal_right)
        random_seal = random.choice(['seal_left.png', 'seal_right.png'])
        image_path = os.path.join('data', 'assets', random_seal)
        enemy = Enemy("top", self.screen_width, self.screen_height, image_path)
        self.enemies.append(enemy)
    
    def handle_input(self, event: pygame.event.Event):
        """Maneja la entrada del usuario"""
        if event.type == pygame.MOUSEMOTION:
            self.mouse_x, self.mouse_y = event.pos
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Click izquierdo
                # Disparar
                projectile = self.player.shoot(self.mouse_x, self.mouse_y)
                self.projectiles.append(projectile)
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Salir del minijuego (derrota)
                self.complete_minigame(False)
    
    def update(self, delta_time: float):
        """Actualiza la lógica del minijuego"""
        # Obtener estado de las teclas
        keys = pygame.key.get_pressed()
        
        # Actualizar jugador
        self.player.update(delta_time, keys, self.mouse_x, self.mouse_y)
        
        # Verificar si el jugador perdió
        if self.player.health <= 0:
            self.complete_minigame(False)
            return
        
        # Actualizar enemigos
        active_enemies = 0
        for enemy in self.enemies:
            if enemy.active:
                active_enemies += 1
                # Actualizar y verificar si dispara
                projectile = enemy.update(delta_time, self.player.x, self.player.y)
                if projectile:
                    self.projectiles.append(projectile)
        
        # Verificar victoria (todos los enemigos derrotados)
        if active_enemies == 0:
            self.success = True
            self.complete_minigame(True)
            return
        
        # Actualizar proyectiles
        for projectile in self.projectiles[:]:
            projectile.update(delta_time)
            
            # Eliminar proyectiles fuera de pantalla
            if (projectile.x < -50 or projectile.x > self.screen_width + 50 or
                projectile.y < -50 or projectile.y > self.screen_height + 50):
                projectile.active = False
                self.projectiles.remove(projectile)
                continue
            
            # Verificar colisiones
            if projectile.active:
                if projectile.is_player:
                    # Verificar colisión con enemigos
                    for enemy in self.enemies:
                        if enemy.active:
                            dist = math.sqrt((projectile.x - enemy.x)**2 + 
                                           (projectile.y - enemy.y)**2)
                            if dist < enemy.width // 2:
                                enemy.take_damage()
                                projectile.active = False
                                self.projectiles.remove(projectile)
                                
                                # Crear explosión si el enemigo murió
                                if not enemy.active:
                                    self.create_explosion(enemy.x, enemy.y)
                                    self.score += 100
                                break
                else:
                    # Verificar colisión con jugador
                    dist = math.sqrt((projectile.x - self.player.x)**2 + 
                                   (projectile.y - self.player.y)**2)
                    if dist < self.player.width // 2:
                        self.player.take_damage()
                        projectile.active = False
                        self.projectiles.remove(projectile)
                        self.screen_flash = 0.3
        
        # Actualizar explosiones
        for explosion in self.explosions[:]:
            explosion['lifetime'] -= delta_time
            explosion['radius'] += 100 * delta_time
            if explosion['lifetime'] <= 0:
                self.explosions.remove(explosion)
        
        # Actualizar flash de pantalla
        if self.screen_flash > 0:
            self.screen_flash -= delta_time
    
    def create_explosion(self, x: float, y: float):
        """Crea una explosión visual"""
        explosion = {
            'x': x,
            'y': y,
            'radius': 10,
            'lifetime': 0.5,
            'max_lifetime': 0.5
        }
        self.explosions.append(explosion)
    
    def render(self, screen: pygame.Surface):
        """Renderiza el minijuego"""
        # Limpiar pantalla o dibujar fondo
        if self.background:
            screen.blit(self.background, (0, 0))
        else:
            # Fondo degradado espacial
            for i in range(self.screen_height):
                color_value = int(10 + (i / self.screen_height) * 20)
                color = (color_value, color_value, color_value + 10)
                pygame.draw.line(screen, color, (0, i), (self.screen_width, i))
        
        # Dibujar explosiones (detrás de todo)
        for explosion in self.explosions:
            alpha = explosion['lifetime'] / explosion['max_lifetime']
            color = (255, int(200 * alpha), int(100 * alpha))
            if explosion['radius'] > 0:
                pygame.draw.circle(screen, color, 
                                 (int(explosion['x']), int(explosion['y'])), 
                                 int(explosion['radius']), 3)
        
        # Dibujar enemigos
        for enemy in self.enemies:
            if enemy.active:
                enemy.draw(screen)
        
        # Dibujar jugador
        self.player.draw(screen, self.mouse_x, self.mouse_y)
        
        # Dibujar proyectiles
        for projectile in self.projectiles:
            if projectile.active:
                projectile.draw(screen)
        
        # Flash de daño
        if self.screen_flash > 0:
            flash_surface = pygame.Surface((self.screen_width, self.screen_height))
            flash_surface.fill((255, 0, 0))
            flash_surface.set_alpha(int(self.screen_flash * 100))
            screen.blit(flash_surface, (0, 0))
        
        # Renderizar UI
        self.render_ui(screen)
    
    def render_ui(self, screen: pygame.Surface):
        """Renderiza la interfaz del minijuego"""
        # Título del minijuego
        title_text = "¡RESCATA AL MARCIANO!"
        title_surface = self.font_large.render(title_text, True, (255, 255, 100))
        title_rect = title_surface.get_rect()
        title_rect.center = (self.screen_width // 2, 40)
        screen.blit(title_surface, title_rect)
        
        # Contador de enemigos
        active_enemies = sum(1 for e in self.enemies if e.active)
        enemies_text = f"Enemigos: {active_enemies}/{len(self.enemies)}"
        enemies_color = (255, 100, 100) if active_enemies > 0 else (100, 255, 100)
        enemies_surface = self.font_normal.render(enemies_text, True, enemies_color)
        enemies_rect = enemies_surface.get_rect()
        enemies_rect.center = (self.screen_width // 2, 80)
        screen.blit(enemies_surface, enemies_rect)
        
        # Puntuación
        self.render_score(screen, x=50, y=50)
        
        # Estado del jugador
        health_text = f"Vida: {self.player.health}/{self.player.max_health}"
        health_color = (0, 255, 0) if self.player.health > 2 else (255, 255, 0) if self.player.health > 1 else (255, 0, 0)
        health_surface = self.font_normal.render(health_text, True, health_color)
        screen.blit(health_surface, (self.screen_width - 200, 50))
        
        # Recompensa potencial
        reward_text = f"Recompensa: +{self.reward_oxygen} Oxígeno"
        reward_surface = self.font_small.render(reward_text, True, (100, 200, 255))
        reward_rect = reward_surface.get_rect()
        reward_rect.center = (self.screen_width // 2, 120)
        screen.blit(reward_surface, reward_rect)
        
        # Instrucciones
        instructions = [
            "WASD: Mover | Click: Disparar",
            "Derrota a todos los enemigos para rescatar al marciano",
            "ESC: Abandonar misión"
        ]
        self.render_instructions(screen, instructions)
    
    def complete_minigame(self, success: bool):
        """Marca el minijuego como completado con mensaje específico"""
        self.is_complete = True
        self.success = success
        
        if success:
            logger.info(f"¡Marciano rescatado! +{self.reward_oxygen} de oxígeno")
        else:
            self.reward_oxygen = 0
            logger.info("El marciano no pudo ser rescatado")
    
    def get_results(self) -> dict:
        """Obtiene los resultados del minijuego"""
        return {
            'success': self.success,
            'score': self.score,
            'reward_materials': 0,  # Este minijuego no da materiales
            'reward_repair': 0,  # Este minijuego no repara
            'reward_oxygen': self.reward_oxygen  # Nueva recompensa de oxígeno
        }
