"""
Narrator - Sistema de Narrativa y Diálogos
Simplificado para MVP: Mensajes educativos y guía del jugador
"""

import pygame
import os
from typing import List, Dict, Optional, Callable, Any
from enum import Enum, auto
import logging

logger = logging.getLogger(__name__)


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
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # Fuentes
        self.font = None
        self.speaker_font = None
        self.small_font = None
        
        # Estado del diálogo
        self.current_dialogue: Optional[DialogueNode] = None
        self.dialogue_queue: List[DialogueNode] = []
        self.is_active = False
        self.text_speed = 50  # Caracteres por segundo
        self.time_since_last_char = 0.0
        
        # UI del diálogo
        # Dejar espacio a la izquierda para el NPC helper (80px imagen + 20px margen = 100px extra)
        self.dialogue_box_rect = pygame.Rect(150, self.screen_height - 200, self.screen_width - 200, 150)
        self.dialogue_alpha = 255
        self.is_fading = False
        
        # Assets
        self.helper_image = None
        
        # Referencias
        self.event_manager = None
        
        # Mensajes contextuales para eventos
        self.contextual_messages = {
            'materials_success': [
                "🪨 ¡Buen trabajo! Conseguimos materiales valiosos.",
                "⛏️ ¡Excelente minería! Los materiales serán útiles.",
                "💎 ¡Qué suerte! Encontraste materiales de calidad."
            ],
            'materials_fail': [
                "😔 No fue tu mejor intento, pero algo es algo.",
                "🤷 Al menos conseguiste algunos materiales.",
                "💪 No te rindas, la próxima vez será mejor."
            ],
            'repair_success': [
                "🔧 ¡Excelente! La nave está más estable.",
                "⚙️ ¡Buen trabajo! La reparación fue exitosa.",
                "🛠️ ¡Perfecto! Cada reparación nos acerca a casa."
            ],
            'oxygen_low': [
                "⚠️ Cuidado, tu oxígeno está crítico.",
                "🫧 ¡Alerta! Necesitas oxígeno pronto.",
                "😰 El oxígeno se agota, considera un préstamo."
            ],
            'materials_low': [
                "⚙️ Necesitas más materiales para reparar la nave.",
                "🪨 Sin materiales no podrás avanzar.",
                "⛏️ Es hora de minar más recursos."
            ]
        }
    
    def initialize(self) -> None:
        """Inicializa fuentes y recursos"""
        # Cargar fuentes
        try:
            self.speaker_font = pygame.font.Font(None, 28)
            self.font = pygame.font.Font(None, 22)
            self.small_font = pygame.font.Font(None, 18)
        except Exception as e:
            logger.error(f"Error cargando fuentes: {e}")
            self.speaker_font = pygame.font.SysFont('Arial', 28)
            self.font = pygame.font.SysFont('Arial', 22)
            self.small_font = pygame.font.SysFont('Arial', 18)
        
        # Cargar imagen del helper
        helper_path = os.path.join('data', 'assets', 'npc_helper.png')
        try:
            if os.path.exists(helper_path):
                self.helper_image = pygame.image.load(helper_path).convert_alpha()
                self.helper_image = pygame.transform.scale(self.helper_image, (80, 100))
                logger.debug("Helper image cargada")
        except Exception as e:
            logger.warning(f"No se pudo cargar helper image: {e}")
        
        # Configurar suscripciones a eventos
        self._setup_event_subscriptions()
        
        logger.info("Narrator inicializado")
    
    def show_dialogue(self, dialogue: DialogueNode) -> None:
        """
        Muestra un diálogo inmediatamente
        
        Args:
            dialogue: Nodo de diálogo a mostrar
        """
        self.current_dialogue = dialogue
        self.current_dialogue.current_char = 0
        self.is_active = True
        self.time_since_last_char = 0.0
        
        # Emitir evento
        if self.event_manager:
            from engine.events import EventType
            self.event_manager.emit_quick(EventType.DIALOGUE_STARTED, {'speaker': dialogue.speaker})
        
        logger.debug(f"Mostrando diálogo: {dialogue.text[:50]}...")
    
    def queue_dialogue(self, dialogue: DialogueNode) -> None:
        """
        Añade un diálogo a la cola
        
        Args:
            dialogue: Nodo de diálogo a encolar
        """
        self.dialogue_queue.append(dialogue)
        
        # Si no hay diálogo activo, mostrar el siguiente
        if not self.is_active and self.dialogue_queue:
            self.show_dialogue(self.dialogue_queue.pop(0))
    
    def show_narrative(self, text: str) -> None:
        """
        Muestra texto narrativo educativo
        
        Args:
            text: Texto narrativo a mostrar
        """
        dialogue = DialogueNode(
            text=text,
            speaker="Guía",
            dialogue_type=DialogueType.NARRATIVE
        )
        self.show_dialogue(dialogue)
    
    def show_character_dialogue(self, speaker: str, text: str) -> None:
        """
        Muestra diálogo de un personaje (prestamista)
        
        Args:
            speaker: Nombre del personaje
            text: Texto del diálogo
        """
        dialogue = DialogueNode(
            text=text,
            speaker=speaker,
            dialogue_type=DialogueType.CHARACTER
        )
        self.show_dialogue(dialogue)
    
    def show_loan_offer(self, creditor: str, amount: float, materials_to_pay: int) -> None:
        """
        Muestra una oferta de préstamo educativa
        
        Args:
            creditor: Nombre del prestamista
            amount: Cantidad de oxígeno ofrecido
            materials_to_pay: Materiales a devolver
        """
        text = (
            f"{creditor} te ofrece {amount:.0f} de oxígeno. "
            f"Deberás devolver {materials_to_pay} materiales. "
            f"Recuerda: El oxígeno es tu moneda, los materiales representan tu trabajo. "
            f"[A] Aceptar  [R] Rechazar"
        )
        
        dialogue = DialogueNode(
            text=text,
            speaker=creditor,
            dialogue_type=DialogueType.CHOICE,
            choices=["Aceptar préstamo", "Rechazar préstamo"]
        )
        self.show_dialogue(dialogue)
    
    def update(self, delta_time: float) -> None:
        """
        Actualiza el estado del narrador
        
        Args:
            delta_time: Tiempo transcurrido
        """
        if not self.is_active or not self.current_dialogue:
            return
        
        # Actualizar efecto de escritura
        if not self.current_dialogue.is_complete:
            self.time_since_last_char += delta_time
            
            # Calcular cuántos caracteres revelar
            chars_to_reveal = int(self.time_since_last_char * self.text_speed)
            if chars_to_reveal > 0:
                self.current_dialogue.current_char = min(
                    self.current_dialogue.current_char + chars_to_reveal,
                    len(self.current_dialogue.text)
                )
                self.time_since_last_char = 0.0
                
                # Verificar si se completó el texto
                if self.current_dialogue.current_char >= len(self.current_dialogue.text):
                    self.current_dialogue.is_complete = True
    
    def render(self) -> None:
        """Renderiza el diálogo actual"""
        if not self.is_active or not self.current_dialogue:
            return
        
        # Dibujar cuadro de diálogo
        dialogue_surface = pygame.Surface((self.dialogue_box_rect.width, self.dialogue_box_rect.height))
        dialogue_surface.set_alpha(self.dialogue_alpha)
        dialogue_surface.fill((20, 20, 40))
        
        # Borde del cuadro
        pygame.draw.rect(dialogue_surface, (100, 100, 200), dialogue_surface.get_rect(), 3)
        
        self.screen.blit(dialogue_surface, self.dialogue_box_rect)
        
        # Renderizar helper image si está disponible
        if self.helper_image and self.current_dialogue.dialogue_type == DialogueType.NARRATIVE:
            helper_rect = self.helper_image.get_rect()
            # Posicionar el helper completamente visible a la izquierda del cuadro de diálogo
            # Con margen de 20px desde el borde izquierdo de la pantalla
            helper_rect.bottomleft = (20, self.dialogue_box_rect.bottom)
            self.screen.blit(self.helper_image, helper_rect)
        
        # Renderizar nombre del hablante
        if self.current_dialogue.speaker:
            speaker_surface = self.speaker_font.render(
                self.current_dialogue.speaker,
                True,
                (255, 200, 100)
            )
            speaker_rect = speaker_surface.get_rect()
            speaker_rect.topleft = (self.dialogue_box_rect.left + 20, self.dialogue_box_rect.top + 10)
            self.screen.blit(speaker_surface, speaker_rect)
        
        # Renderizar texto con efecto de escritura
        visible_text = self.current_dialogue.text[:self.current_dialogue.current_char]
        
        # Dividir texto en líneas
        lines = self._wrap_text(visible_text, self.dialogue_box_rect.width - 40)
        
        y_offset = 45 if self.current_dialogue.speaker else 20
        for line in lines[:4]:  # Máximo 4 líneas
            text_surface = self.font.render(line, True, (255, 255, 255))
            text_rect = text_surface.get_rect()
            text_rect.topleft = (self.dialogue_box_rect.left + 20, self.dialogue_box_rect.top + y_offset)
            self.screen.blit(text_surface, text_rect)
            y_offset += 25
        
        # Renderizar opciones si es CHOICE
        if self.current_dialogue.dialogue_type == DialogueType.CHOICE and self.current_dialogue.is_complete:
            if self.current_dialogue.choices:
                choice_y = self.dialogue_box_rect.bottom - 30
                for i, choice in enumerate(self.current_dialogue.choices[:2]):
                    choice_text = f"[{i+1}] {choice}"
                    choice_surface = self.small_font.render(choice_text, True, (255, 255, 100))
                    choice_rect = choice_surface.get_rect()
                    choice_rect.left = self.dialogue_box_rect.left + 20 + (i * 200)
                    choice_rect.centery = choice_y
                    self.screen.blit(choice_surface, choice_rect)
        
        # Indicador de continuar
        if self.current_dialogue.is_complete and self.current_dialogue.dialogue_type != DialogueType.CHOICE:
            continue_text = "[ESPACIO] Continuar"
            continue_surface = self.small_font.render(continue_text, True, (200, 200, 200))
            continue_rect = continue_surface.get_rect()
            continue_rect.bottomright = (self.dialogue_box_rect.right - 20, self.dialogue_box_rect.bottom - 10)
            self.screen.blit(continue_surface, continue_rect)
    
    def handle_input(self, event: pygame.event.Event) -> None:
        """
        Procesa input del jugador en diálogos
        
        Args:
            event: Evento de Pygame
        """
        if not self.is_active or not self.current_dialogue:
            return
        
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                if self.current_dialogue.dialogue_type != DialogueType.CHOICE:
                    self.advance_dialogue()
            
            # Manejar opciones de préstamo
            elif self.current_dialogue.dialogue_type == DialogueType.CHOICE:
                if event.key == pygame.K_a or event.key == pygame.K_1:
                    # Aceptar préstamo
                    if self.current_dialogue.on_complete:
                        self.current_dialogue.on_complete(0)
                    self.close_dialogue()
                elif event.key == pygame.K_r or event.key == pygame.K_2:
                    # Rechazar préstamo
                    if self.current_dialogue.on_complete:
                        self.current_dialogue.on_complete(1)
                    self.close_dialogue()
            
            # Saltar texto
            elif event.key == pygame.K_ESCAPE:
                if not self.current_dialogue.is_complete:
                    self.current_dialogue.current_char = len(self.current_dialogue.text)
                    self.current_dialogue.is_complete = True
                else:
                    self.skip_dialogue()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Click izquierdo
                if not self.current_dialogue.is_complete:
                    # Completar texto instantáneamente
                    self.current_dialogue.current_char = len(self.current_dialogue.text)
                    self.current_dialogue.is_complete = True
                else:
                    self.advance_dialogue()
    
    def advance_dialogue(self) -> None:
        """Avanza al siguiente diálogo o completa el actual"""
        if not self.current_dialogue:
            return
        
        if not self.current_dialogue.is_complete:
            # Revelar todo el texto
            self.current_dialogue.current_char = len(self.current_dialogue.text)
            self.current_dialogue.is_complete = True
        else:
            # Llamar callback si existe
            if self.current_dialogue.on_complete:
                self.current_dialogue.on_complete()
            
            # Procesar siguiente diálogo de la cola
            if self.dialogue_queue:
                self.show_dialogue(self.dialogue_queue.pop(0))
            else:
                self.close_dialogue()
    
    def skip_dialogue(self) -> None:
        """Salta el diálogo actual completamente"""
        self.dialogue_queue.clear()
        if self.current_dialogue and self.current_dialogue.on_complete:
            self.current_dialogue.on_complete()
        self.close_dialogue()
    
    def close_dialogue(self) -> None:
        """Cierra el diálogo actual"""
        self.is_active = False
        self.current_dialogue = None
        
        # Emitir evento
        if self.event_manager:
            from engine.events import EventType
            self.event_manager.emit_quick(EventType.DIALOGUE_ENDED)
        
        logger.debug("Diálogo cerrado")
    
    def _wrap_text(self, text: str, max_width: int) -> List[str]:
        """
        Divide el texto en líneas según el ancho máximo
        
        Args:
            text: Texto a dividir
            max_width: Ancho máximo en píxeles
            
        Returns:
            Lista de líneas de texto
        """
        if not self.font:
            return [text]
        
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            text_width = self.font.size(test_line)[0]
            
            if text_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def _setup_event_subscriptions(self) -> None:
        """Configura las suscripciones a eventos"""
        if not self.event_manager:
            return
        
        from engine.events import EventType
        
        # Suscribir a eventos de minijuegos
        self.event_manager.subscribe(EventType.MATERIALS_GAINED_SUCCESS, self._on_materials_success)
        self.event_manager.subscribe(EventType.MATERIALS_GAINED_FAIL, self._on_materials_fail)
        self.event_manager.subscribe(EventType.REPAIR_COMPLETED, self._on_repair_completed)
        self.event_manager.subscribe(EventType.ALERT_OXYGEN, self._on_alert_oxygen)
        self.event_manager.subscribe(EventType.ALERT_MATERIALS, self._on_alert_materials)
    
    def _on_materials_success(self, event) -> None:
        """Maneja el evento de éxito en minería"""
        import random
        message = random.choice(self.contextual_messages['materials_success'])
        self.show_quick_message(message, duration=3.0)
    
    def _on_materials_fail(self, event) -> None:
        """Maneja el evento de fallo en minería"""
        import random
        message = random.choice(self.contextual_messages['materials_fail'])
        self.show_quick_message(message, duration=3.0)
    
    def _on_repair_completed(self, event) -> None:
        """Maneja el evento de reparación completada"""
        import random
        message = random.choice(self.contextual_messages['repair_success'])
        self.show_quick_message(message, duration=3.0)
    
    def _on_alert_oxygen(self, event) -> None:
        """Maneja la alerta de oxígeno bajo"""
        import random
        message = random.choice(self.contextual_messages['oxygen_low'])
        self.show_quick_message(message, duration=4.0)
    
    def _on_alert_materials(self, event) -> None:
        """Maneja la alerta de materiales bajos"""
        import random
        message = random.choice(self.contextual_messages['materials_low'])
        self.show_quick_message(message, duration=3.5)
    
    def show_educational_tip(self, tip_type: str) -> None:
        """
        Muestra un consejo educativo según el contexto
        
        Args:
            tip_type: Tipo de consejo (oxygen_low, debt_high, etc.)
        """
        tips = {
            'oxygen_low': (
                "Tu oxígeno está bajo. Considera tomar un préstamo, "
                "pero recuerda: deberás devolver materiales (trabajo) para pagarlo."
            ),
            'debt_high': (
                "Tu deuda es alta. Prioriza minar materiales para pagar "
                "antes de que venzan los plazos."
            ),
            'materials_low': (
                "Tienes pocos materiales. Mina más antes de intentar "
                "reparaciones costosas."
            ),
            'repair_progress': (
                "Cada reparación exitosa te acerca a la victoria. "
                "Balancea tus recursos entre reparar y pagar deudas."
            ),
            'loan_offer': (
                "Un prestamista apareció. Evalúa si realmente necesitas "
                "el oxígeno y si podrás pagar los materiales a tiempo."
            )
        }
        
        tip = tips.get(tip_type)
        if tip:
            self.show_narrative(tip)

