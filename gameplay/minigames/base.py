"""
Base Minigame - Clase base para todos los minijuegos
"""

import pygame
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class BaseMinigame(ABC):
    """
    Clase base abstracta para todos los minijuegos
    
    Proporciona la estructura común y métodos que todos los minijuegos deben implementar
    """
    
    def __init__(self, screen_width: int = 1280, screen_height: int = 720):
        """
        Inicializa el minijuego base
        
        Args:
            screen_width: Ancho de la pantalla
            screen_height: Alto de la pantalla
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Estado del minijuego
        self.is_complete = False
        self.success = False
        self.score = 0
        self.time_remaining = 30.0  # Tiempo por defecto
        
        # Recursos y recompensas
        self.reward_materials = 0
        self.reward_repair = 0
        
        # Fuentes
        self.font_large = None
        self.font_normal = None
        self.font_small = None
        
        # Superficie de renderizado
        self.surface = pygame.Surface((screen_width, screen_height))
        
        # Inicializar fuentes
        self._init_fonts()
        
        # Cargar assets específicos del minijuego
        self.assets = {}
        self.load_assets()
    
    def _init_fonts(self):
        """Inicializa las fuentes del minijuego"""
        try:
            self.font_large = pygame.font.Font(None, 48)
            self.font_normal = pygame.font.Font(None, 32)
            self.font_small = pygame.font.Font(None, 24)
        except:
            self.font_large = pygame.font.SysFont('Arial', 48)
            self.font_normal = pygame.font.SysFont('Arial', 32)
            self.font_small = pygame.font.SysFont('Arial', 24)
    
    @abstractmethod
    def load_assets(self) -> None:
        """Carga los assets específicos del minijuego"""
        pass
    
    @abstractmethod
    def handle_input(self, event: pygame.event.Event) -> None:
        """
        Maneja la entrada del usuario
        
        Args:
            event: Evento de Pygame
        """
        pass
    
    @abstractmethod
    def update(self, delta_time: float) -> None:
        """
        Actualiza la lógica del minijuego
        
        Args:
            delta_time: Tiempo transcurrido desde el último frame
        """
        pass
    
    @abstractmethod
    def render(self, screen: pygame.Surface) -> None:
        """
        Renderiza el minijuego
        
        Args:
            screen: Superficie donde renderizar
        """
        pass
    
    def complete_minigame(self, success: bool) -> None:
        """
        Marca el minijuego como completado
        
        Args:
            success: Si el jugador tuvo éxito o no
        """
        self.is_complete = True
        self.success = success
        
        # Calcular recompensas según el éxito
        if success:
            logger.info(f"Minijuego completado con éxito. Score: {self.score}")
        else:
            logger.info(f"Minijuego fallado. Score: {self.score}")
    
    def get_results(self) -> Dict[str, Any]:
        """
        Obtiene los resultados del minijuego
        
        Returns:
            Diccionario con los resultados
        """
        return {
            'success': self.success,
            'score': self.score,
            'reward_materials': self.reward_materials,
            'reward_repair': self.reward_repair,
            'time_remaining': self.time_remaining
        }
    
    def render_timer(self, screen: pygame.Surface, x: int = None, y: int = None) -> None:
        """
        Renderiza el temporizador del minijuego
        
        Args:
            screen: Superficie donde renderizar
            x: Posición X (por defecto centrado)
            y: Posición Y (por defecto arriba)
        """
        if x is None:
            x = self.screen_width // 2
        if y is None:
            y = 30
        
        # Color según tiempo restante
        if self.time_remaining > 10:
            color = (255, 255, 255)
        elif self.time_remaining > 5:
            color = (255, 255, 100)
        else:
            color = (255, 100, 100)
        
        time_text = f"Tiempo: {self.time_remaining:.1f}s"
        text_surface = self.font_normal.render(time_text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        screen.blit(text_surface, text_rect)
    
    def render_score(self, screen: pygame.Surface, x: int = None, y: int = None) -> None:
        """
        Renderiza el puntaje del minijuego
        
        Args:
            screen: Superficie donde renderizar
            x: Posición X (por defecto izquierda)
            y: Posición Y (por defecto arriba)
        """
        if x is None:
            x = 50
        if y is None:
            y = 30
        
        score_text = f"Puntos: {self.score}"
        text_surface = self.font_normal.render(score_text, True, (255, 255, 255))
        screen.blit(text_surface, (x, y))
    
    def render_instructions(self, screen: pygame.Surface, instructions: list, 
                           x: int = None, y: int = None) -> None:
        """
        Renderiza las instrucciones del minijuego
        
        Args:
            screen: Superficie donde renderizar
            instructions: Lista de líneas de instrucciones
            x: Posición X (por defecto centrado)
            y: Posición Y inicial
        """
        if x is None:
            x = self.screen_width // 2
        if y is None:
            y = self.screen_height - 100
        
        for i, instruction in enumerate(instructions):
            text_surface = self.font_small.render(instruction, True, (200, 200, 200))
            text_rect = text_surface.get_rect()
            text_rect.center = (x, y + i * 25)
            screen.blit(text_surface, text_rect)
