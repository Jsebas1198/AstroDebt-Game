"""
Wiring Puzzle - Minijuego de conexión de cables para reparación
"""

import pygame
import random
import math
import os
from typing import List, Dict, Tuple, Optional
from .base import BaseMinigame
import logging

logger = logging.getLogger(__name__)


class Wire:
    """Representa un cable en el puzzle"""
    
    def __init__(self, color: Tuple[int, int, int], start_pos: Tuple[int, int], 
                 end_pos: Tuple[int, int], wire_id: int):
        self.color = color
        self.wire_id = wire_id
        self.start_pos = start_pos  # Posición del conector izquierdo
        self.end_pos = end_pos  # Posición del conector derecho correcto
        
        # Estado del cable
        self.is_connected = False
        self.current_end_pos = None  # Posición actual del extremo del cable
        self.is_being_dragged = False
        
        # Puntos de control para curva de Bezier
        self.control_points = []
        
        # Radio del conector
        self.connector_radius = 15
    
    def start_drag(self, mouse_pos: Tuple[int, int]) -> bool:
        """
        Intenta iniciar el arrastre del cable
        
        Returns:
            True si se inició el arrastre
        """
        # Verificar si el mouse está sobre el conector de inicio
        distance = math.sqrt((mouse_pos[0] - self.start_pos[0])**2 + 
                           (mouse_pos[1] - self.start_pos[1])**2)
        
        if distance <= self.connector_radius * 1.5:
            self.is_being_dragged = True
            self.current_end_pos = mouse_pos
            self.is_connected = False
            return True
        
        # Si ya está conectado, verificar si se quiere desconectar
        if self.is_connected and self.current_end_pos:
            distance = math.sqrt((mouse_pos[0] - self.current_end_pos[0])**2 + 
                               (mouse_pos[1] - self.current_end_pos[1])**2)
            if distance <= self.connector_radius * 1.5:
                self.is_being_dragged = True
                self.is_connected = False
                return True
        
        return False
    
    def update_drag(self, mouse_pos: Tuple[int, int]):
        """Actualiza la posición durante el arrastre"""
        if self.is_being_dragged:
            self.current_end_pos = mouse_pos
            self.update_control_points()
    
    def end_drag(self, connectors: List[Tuple[int, int]]) -> bool:
        """
        Termina el arrastre y verifica conexión
        
        Args:
            connectors: Lista de posiciones de conectores derechos
            
        Returns:
            True si se conectó correctamente
        """
        if not self.is_being_dragged:
            return False
        
        self.is_being_dragged = False
        
        # Verificar si se conectó a algún conector
        for connector_pos in connectors:
            distance = math.sqrt((self.current_end_pos[0] - connector_pos[0])**2 + 
                               (self.current_end_pos[1] - connector_pos[1])**2)
            
            if distance <= self.connector_radius * 2:
                # Snap al conector
                self.current_end_pos = connector_pos
                
                # Verificar si es la conexión correcta
                if connector_pos == self.end_pos:
                    self.is_connected = True
                    self.update_control_points()
                    return True
                else:
                    # Conexión incorrecta - mantener conectado pero no es correcto
                    self.update_control_points()
                    return False
        
        # No se conectó a ningún conector - resetear
        self.current_end_pos = None
        return False
    
    def update_control_points(self):
        """Actualiza los puntos de control para la curva del cable"""
        if not self.current_end_pos:
            return
        
        # Calcular puntos de control para una curva suave
        mid_x = (self.start_pos[0] + self.current_end_pos[0]) / 2
        mid_y = (self.start_pos[1] + self.current_end_pos[1]) / 2
        
        # Añadir algo de curvatura
        sag = 30  # Cantidad de caída del cable
        self.control_points = [
            self.start_pos,
            (mid_x, mid_y + sag),
            self.current_end_pos
        ]
    
    def draw(self, screen: pygame.Surface):
        """Dibuja el cable"""
        # Dibujar conector de inicio
        pygame.draw.circle(screen, self.color, self.start_pos, self.connector_radius)
        pygame.draw.circle(screen, (255, 255, 255), self.start_pos, self.connector_radius, 2)
        
        # Dibujar el cable si tiene una posición final
        if self.current_end_pos:
            # Dibujar cable con múltiples segmentos para simular curva
            if len(self.control_points) >= 2:
                # Cable más grueso
                for i in range(len(self.control_points) - 1):
                    pygame.draw.line(screen, self.color, 
                                   self.control_points[i], 
                                   self.control_points[i + 1], 8)
                
                # Línea central más delgada para efecto
                for i in range(len(self.control_points) - 1):
                    lighter_color = tuple(min(255, c + 50) for c in self.color)
                    pygame.draw.line(screen, lighter_color, 
                                   self.control_points[i], 
                                   self.control_points[i + 1], 4)
            
            # Dibujar extremo del cable
            end_color = self.color if not self.is_being_dragged else (255, 255, 255)
            pygame.draw.circle(screen, end_color, self.current_end_pos, 10)


class WiringMinigame(BaseMinigame):
    """
    Minijuego de conexión de cables
    
    El jugador debe conectar cables de colores entre dos paneles
    Inspirado en el minijuego de Among Us
    """
    
    def __init__(self, screen_width: int = 1280, screen_height: int = 720):
        super().__init__(screen_width, screen_height)
        
        # Configuración del minijuego
        self.time_remaining = 45.0
        self.num_wires = 4
        
        # Colores disponibles para los cables
        self.wire_colors = [
            (255, 0, 0),     # Rojo
            (0, 0, 255),     # Azul
            (255, 255, 0),   # Amarillo
            (0, 255, 0),     # Verde
            (255, 0, 255),   # Magenta
            (0, 255, 255),   # Cian
        ]
        
        # Cables
        self.wires: List[Wire] = []
        self.left_connectors: List[Tuple[int, int]] = []
        self.right_connectors: List[Tuple[int, int]] = []
        
        # Cable siendo arrastrado
        self.dragging_wire: Optional[Wire] = None
        
        # Paneles
        self.left_panel_x = screen_width // 4
        self.right_panel_x = 3 * screen_width // 4
        self.panel_y = screen_height // 2
        self.panel_width = 150
        self.panel_height = 300
        
        # Crear el puzzle
        self.create_puzzle()
        
        # Efectos
        self.spark_effects = []
        self.completion_flash = 0
        
        # Fondo
        self.background = None
        
        logger.info("Wiring Puzzle minijuego inicializado")
    
    def load_assets(self):
        """Carga los assets del minijuego"""
        try:
            # Cargar fondo
            bg_path = os.path.join('data', 'assets', 'minigame_wiring_bg.png')
            if os.path.exists(bg_path):
                self.background = pygame.image.load(bg_path)
                self.background = pygame.transform.scale(self.background,
                                                        (self.screen_width, self.screen_height))
                logger.info("Fondo de wiring cargado")
        except Exception as e:
            logger.warning(f"No se pudo cargar el fondo: {e}")
    
    def create_puzzle(self):
        """Crea el puzzle de cables"""
        # Limpiar cables existentes
        self.wires.clear()
        self.left_connectors.clear()
        self.right_connectors.clear()
        
        # Seleccionar colores aleatorios para este puzzle
        selected_colors = random.sample(self.wire_colors, self.num_wires)
        
        # Crear posiciones de conectores
        spacing = self.panel_height / (self.num_wires + 1)
        
        for i in range(self.num_wires):
            y_pos = self.panel_y - self.panel_height // 2 + spacing * (i + 1)
            self.left_connectors.append((self.left_panel_x, int(y_pos)))
            self.right_connectors.append((self.right_panel_x, int(y_pos)))
        
        # Mezclar las posiciones del lado derecho
        right_positions = self.right_connectors.copy()
        random.shuffle(right_positions)
        
        # Crear cables
        for i, color in enumerate(selected_colors):
            wire = Wire(
                color=color,
                start_pos=self.left_connectors[i],
                end_pos=right_positions[i],
                wire_id=i
            )
            self.wires.append(wire)
    
    def handle_input(self, event: pygame.event.Event):
        """Maneja la entrada del usuario"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Click izquierdo
                mouse_pos = event.pos
                
                # Intentar iniciar arrastre en algún cable
                for wire in self.wires:
                    if wire.start_drag(mouse_pos):
                        self.dragging_wire = wire
                        break
        
        elif event.type == pygame.MOUSEMOTION:
            # Actualizar posición del cable siendo arrastrado
            if self.dragging_wire:
                self.dragging_wire.update_drag(event.pos)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.dragging_wire:
                # Terminar arrastre
                connected = self.dragging_wire.end_drag(self.right_connectors)
                
                if connected:
                    self.create_spark_effect(self.dragging_wire.current_end_pos)
                    self.check_completion()
                
                self.dragging_wire = None
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Salir del minijuego
                self.complete_minigame(False)
            elif event.key == pygame.K_r:
                # Resetear puzzle
                self.reset_puzzle()
    
    def reset_puzzle(self):
        """Resetea todos los cables"""
        for wire in self.wires:
            wire.is_connected = False
            wire.current_end_pos = None
            wire.is_being_dragged = False
    
    def check_completion(self):
        """Verifica si el puzzle está completo"""
        all_connected = all(wire.is_connected for wire in self.wires)
        
        if all_connected:
            self.score = 1000 + int(self.time_remaining * 10)
            self.completion_flash = 1.0
            self.calculate_rewards(True)
            
            # Retrasar un poco la finalización para mostrar el efecto
            pygame.time.wait(500)
            self.complete_minigame(True)
    
    def create_spark_effect(self, pos: Tuple[int, int]):
        """Crea un efecto de chispa"""
        for _ in range(10):
            spark = {
                'x': pos[0],
                'y': pos[1],
                'vx': random.uniform(-100, 100),
                'vy': random.uniform(-100, 100),
                'lifetime': 0.5,
                'color': (255, 255, random.randint(100, 255))
            }
            self.spark_effects.append(spark)
    
    def update(self, delta_time: float):
        """Actualiza la lógica del minijuego"""
        # Actualizar temporizador
        self.time_remaining -= delta_time
        
        # Verificar tiempo agotado
        if self.time_remaining <= 0:
            self.calculate_rewards(False)
            self.complete_minigame(False)
            return
        
        # Actualizar efectos de chispas
        for spark in self.spark_effects[:]:
            spark['x'] += spark['vx'] * delta_time
            spark['y'] += spark['vy'] * delta_time
            spark['lifetime'] -= delta_time
            
            if spark['lifetime'] <= 0:
                self.spark_effects.remove(spark)
        
        # Actualizar flash de completado
        if self.completion_flash > 0:
            self.completion_flash -= delta_time * 2
    
    def calculate_rewards(self, success: bool):
        """Calcula las recompensas del minijuego"""
        if success:
            # Recompensa de reparación base
            self.reward_repair = random.randint(10, 20)
            
            # Bonus por tiempo restante
            if self.time_remaining > 30:
                self.reward_repair += 5
            elif self.time_remaining > 20:
                self.reward_repair += 3
        else:
            # Penalización por fallo
            self.reward_repair = -2 if self.time_remaining <= 0 else 0
    
    def render(self, screen: pygame.Surface):
        """Renderiza el minijuego"""
        # Limpiar pantalla o dibujar fondo
        if self.background:
            screen.blit(self.background, (0, 0))
        else:
            screen.fill((20, 20, 40))
            
            # Dibujar patrón de circuitos de fondo
            grid_color = (30, 30, 60)
            for x in range(0, self.screen_width, 50):
                pygame.draw.line(screen, grid_color, (x, 0), (x, self.screen_height), 1)
            for y in range(0, self.screen_height, 50):
                pygame.draw.line(screen, grid_color, (0, y), (self.screen_width, y), 1)
        
        # Flash de completado
        if self.completion_flash > 0:
            flash_surface = pygame.Surface((self.screen_width, self.screen_height))
            flash_surface.fill((100, 255, 100))
            flash_surface.set_alpha(int(self.completion_flash * 100))
            screen.blit(flash_surface, (0, 0))
        
        # Renderizar paneles
        self.render_panels(screen)
        
        # Renderizar conectores del lado derecho primero (destinos)
        for i, pos in enumerate(self.right_connectors):
            # Encontrar el cable que debe conectarse aquí
            target_wire = None
            for wire in self.wires:
                if wire.end_pos == pos:
                    target_wire = wire
                    break
            
            if target_wire:
                # Dibujar conector con el color del cable objetivo
                pygame.draw.circle(screen, target_wire.color, pos, 15)
                pygame.draw.circle(screen, (255, 255, 255), pos, 15, 2)
                
                # Indicador si está correctamente conectado
                if target_wire.is_connected:
                    pygame.draw.circle(screen, (0, 255, 0), pos, 20, 3)
        
        # Renderizar cables
        for wire in self.wires:
            wire.draw(screen)
        
        # Renderizar chispas
        for spark in self.spark_effects:
            alpha = spark['lifetime'] * 2
            size = int(3 * alpha)
            if size > 0:
                pygame.draw.circle(screen, spark['color'],
                                 (int(spark['x']), int(spark['y'])), size)
        
        # Renderizar UI
        self.render_ui(screen)
    
    def render_panels(self, screen: pygame.Surface):
        """Renderiza los paneles de conexión"""
        # Panel izquierdo
        left_rect = pygame.Rect(
            self.left_panel_x - self.panel_width // 2,
            self.panel_y - self.panel_height // 2,
            self.panel_width,
            self.panel_height
        )
        pygame.draw.rect(screen, (60, 60, 80), left_rect)
        pygame.draw.rect(screen, (100, 100, 120), left_rect, 3)
        
        # Panel derecho
        right_rect = pygame.Rect(
            self.right_panel_x - self.panel_width // 2,
            self.panel_y - self.panel_height // 2,
            self.panel_width,
            self.panel_height
        )
        pygame.draw.rect(screen, (60, 60, 80), right_rect)
        pygame.draw.rect(screen, (100, 100, 120), right_rect, 3)
        
        # Etiquetas
        left_text = self.font_small.render("ENTRADA", True, (200, 200, 200))
        left_text_rect = left_text.get_rect()
        left_text_rect.center = (self.left_panel_x, self.panel_y - self.panel_height // 2 - 20)
        screen.blit(left_text, left_text_rect)
        
        right_text = self.font_small.render("SALIDA", True, (200, 200, 200))
        right_text_rect = right_text.get_rect()
        right_text_rect.center = (self.right_panel_x, self.panel_y - self.panel_height // 2 - 20)
        screen.blit(right_text, right_text_rect)
    
    def render_ui(self, screen: pygame.Surface):
        """Renderiza la interfaz del minijuego"""
        # Renderizar temporizador
        self.render_timer(screen)
        
        # Renderizar puntuación
        self.render_score(screen)
        
        # Renderizar progreso
        connected_count = sum(1 for wire in self.wires if wire.is_connected)
        progress_text = f"Cables conectados: {connected_count}/{self.num_wires}"
        color = (100, 255, 100) if connected_count == self.num_wires else (255, 255, 255)
        text_surface = self.font_normal.render(progress_text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (self.screen_width // 2, 70)
        screen.blit(text_surface, text_rect)
        
        # Renderizar instrucciones
        instructions = [
            "Arrastra los cables desde la izquierda hasta el conector del mismo color a la derecha",
            "Conecta todos los cables correctamente",
            "[R] para reiniciar el puzzle"
        ]
        self.render_instructions(screen, instructions)