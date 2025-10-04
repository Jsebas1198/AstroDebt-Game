"""
Narrator - Sistema de Narrativa y Diálogos
Gestiona la presentación de texto narrativo y diálogos con personajes
"""

import pygame
from typing import List, Dict, Optional, Callable
from enum import Enum, auto


class DialogueType(Enum):
    """Tipos de diálogos"""
    NARRATIVE = auto()  # Narración del juego
    CHARACTER = auto()  # Diálogo de personaje
    SYSTEM = auto()  # Mensajes del sistema
    CHOICE = auto()  # Diálogo con opciones


class DialogueNode:
    """
    Representa un nodo de diálogo
    
    Atributos:
        text: Texto del diálogo
        speaker: Nombre del hablante (opcional)
        dialogue_type: Tipo de diálogo
        choices: Opciones de respuesta (si es CHOICE)
        on_complete: Callback al completar el diálogo
    """
    def __init__(
        self,
        text: str,
        speaker: Optional[str] = None,
        dialogue_type: DialogueType = DialogueType.NARRATIVE,
        choices: Optional[List[str]] = None,
        on_complete: Optional[Callable] = None
    ):
        self.text = text
        self.speaker = speaker
        self.dialogue_type = dialogue_type
        self.choices = choices or []
        self.on_complete = on_complete
        self.current_char = 0  # Para efecto de escritura
        self.is_complete = False


class Narrator:
    """
    Sistema de narrativa y diálogos del juego
    
    Responsabilidades:
        - Mostrar texto narrativo con efecto de escritura
        - Gestionar diálogos con personajes (acreedores, aliados)
        - Presentar opciones de diálogo al jugador
        - Mostrar tutoriales y tips
        - Crear atmósfera y contexto narrativo
    
    Dependencias:
        - pygame: Para renderizado de texto
        - engine.events.EventManager: Para emitir eventos de diálogo
    """
    
    def __init__(self, screen: pygame.Surface):
        """
        Inicializa el narrador
        
        Args:
            screen: Superficie de Pygame donde renderizar
        """
        self.screen = screen
        self.font = None
        self.speaker_font = None
        
        # Estado del diálogo
        self.current_dialogue: Optional[DialogueNode] = None
        self.dialogue_queue: List[DialogueNode] = []
        self.is_active = False
        self.text_speed = 50  # Caracteres por segundo
        self.time_since_last_char = 0.0
        
        # UI del diálogo
        self.dialogue_box_rect = pygame.Rect(50, 500, 1180, 170)
        self.dialogue_alpha = 0
        self.is_fading = False
        
        # Referencias
        self.event_manager = None
    
    def initialize(self) -> None:
        """Inicializa fuentes y recursos"""
        # TODO: Cargar fuentes
        # TODO: Preparar sprites de cuadros de diálogo
        pass
    
    def show_dialogue(self, dialogue: DialogueNode) -> None:
        """
        Muestra un diálogo inmediatamente
        
        Args:
            dialogue: Nodo de diálogo a mostrar
        """
        # TODO: Establecer current_dialogue
        # TODO: Resetear caracteres mostrados
        # TODO: Establecer is_active = True
        # TODO: Emitir evento DIALOGUE_STARTED
        pass
    
    def queue_dialogue(self, dialogue: DialogueNode) -> None:
        """
        Añade un diálogo a la cola
        
        Args:
            dialogue: Nodo de diálogo a encolar
        """
        # TODO: Añadir a dialogue_queue
        pass
    
    def show_narrative(self, text: str) -> None:
        """
        Muestra texto narrativo
        
        Args:
            text: Texto narrativo a mostrar
        """
        # TODO: Crear DialogueNode de tipo NARRATIVE
        # TODO: Llamar a show_dialogue()
        pass
    
    def show_character_dialogue(self, speaker: str, text: str) -> None:
        """
        Muestra diálogo de un personaje
        
        Args:
            speaker: Nombre del personaje
            text: Texto del diálogo
        """
        # TODO: Crear DialogueNode de tipo CHARACTER
        # TODO: Llamar a show_dialogue()
        pass
    
    def show_choice(self, text: str, choices: List[str], on_choice: Callable) -> None:
        """
        Muestra un diálogo con opciones
        
        Args:
            text: Texto del diálogo
            choices: Lista de opciones
            on_choice: Callback con la opción elegida
        """
        # TODO: Crear DialogueNode de tipo CHOICE
        # TODO: Configurar on_complete para manejar elección
        # TODO: Llamar a show_dialogue()
        pass
    
    def update(self, delta_time: float) -> None:
        """
        Actualiza el estado del narrador
        
        Args:
            delta_time: Tiempo transcurrido
        """
        # TODO: Actualizar efecto de escritura
        # TODO: Revelar más caracteres según text_speed
        # TODO: Procesar cola de diálogos
        # TODO: Actualizar animaciones de fade
        pass
    
    def render(self) -> None:
        """Renderiza el diálogo actual"""
        # TODO: Dibujar cuadro de diálogo con transparencia
        # TODO: Renderizar nombre del hablante (si aplica)
        # TODO: Renderizar texto con efecto de escritura
        # TODO: Renderizar opciones (si es CHOICE)
        # TODO: Renderizar indicador de continuar
        pass
    
    def handle_input(self, event: pygame.event.Event) -> None:
        """
        Procesa input del jugador en diálogos
        
        Args:
            event: Evento de Pygame
        """
        # TODO: Detectar Enter/Space para avanzar diálogo
        # TODO: Detectar clic del mouse
        # TODO: Procesar selección de opciones
        pass
    
    def advance_dialogue(self) -> None:
        """Avanza al siguiente diálogo o completa el actual"""
        # TODO: Si el texto no está completamente revelado, revelarlo todo
        # TODO: Si está completo, marcar como terminado
        # TODO: Llamar on_complete si existe
        # TODO: Procesar siguiente diálogo de la cola
        # TODO: Emitir evento DIALOGUE_ENDED si no hay más
        pass
    
    def skip_dialogue(self) -> None:
        """Salta el diálogo actual completamente"""
        # TODO: Vaciar dialogue_queue
        # TODO: Completar current_dialogue
        # TODO: Establecer is_active = False
        pass
    
    def close_dialogue(self) -> None:
        """Cierra el diálogo actual"""
        # TODO: Fade out del cuadro de diálogo
        # TODO: Establecer is_active = False
        # TODO: Limpiar current_dialogue
        pass
    
    def get_wrapped_text(self, text: str, max_width: int) -> List[str]:
        """
        Divide el texto en líneas según el ancho máximo
        
        Args:
            text: Texto a dividir
            max_width: Ancho máximo en píxeles
            
        Returns:
            Lista de líneas de texto
        """
        # TODO: Implementar word wrapping
        pass

