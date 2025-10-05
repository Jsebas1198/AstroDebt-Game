"""
EventManager - Sistema de Eventos
Sistema de señales/observers para comunicación entre componentes del juego
"""

from typing import Callable, Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum, auto
import logging

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Tipos de eventos del juego"""
    # Eventos de estado
    OXYGEN_CHANGED = auto()
    MATERIALS_GAINED = auto()  # Simplificado para materiales genéricos
    MATERIALS_CONSUMED = auto()
    REPAIR_PROGRESS_CHANGED = auto()
    
    # Eventos de turnos
    TURN_STARTED = auto()
    TURN_ENDED = auto()
    ACTION_SELECTED = auto()
    
    # Eventos de préstamos
    LOAN_APPEARED = auto()  # Prestamista aparece
    LOAN_ACCEPTED = auto()  # Préstamo aceptado
    LOAN_REJECTED = auto()  # Préstamo rechazado
    LOAN_PAYMENT = auto()
    LOAN_OVERDUE = auto()  # Pago vencido
    LOAN_DEFAULTED = auto()
    PENALTY_APPLIED = auto()
    
    # Eventos de minijuegos
    MINIGAME_STARTED = auto()
    MINIGAME_COMPLETED = auto()
    MINIGAME_FAILED = auto()
    MATERIALS_GAINED_SUCCESS = auto()
    MATERIALS_GAINED_FAIL = auto()
    REPAIR_COMPLETED = auto()
    
    # Eventos de juego
    GAME_OVER = auto()
    VICTORY = auto()
    PHASE_CHANGED = auto()
    
    # Eventos de UI
    DIALOGUE_STARTED = auto()
    DIALOGUE_ENDED = auto()
    NOTIFICATION_SHOWN = auto()
    ALERT_OXYGEN = auto()
    ALERT_MATERIALS = auto()


@dataclass
class Event:
    """
    Clase que representa un evento del juego
    
    Atributos:
        event_type: Tipo de evento
        data: Datos adicionales del evento
        source: Origen del evento (opcional)
    """
    event_type: EventType
    data: Dict[str, Any] = None
    source: str = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}


class EventManager:
    """
    Gestor centralizado de eventos del juego
    Implementa el patrón Observer/PubSub
    
    Permite que diferentes partes del juego se comuniquen
    sin acoplamiento directo entre componentes
    
    Dependencias:
        - Ninguna (es un componente de bajo nivel)
    """
    
    def __init__(self):
        """Inicializa el gestor de eventos"""
        # Diccionario de suscriptores: {EventType: [callbacks]}
        self.subscribers: Dict[EventType, List[Callable]] = {}
        
        # Cola de eventos pendientes
        self.event_queue: List[Event] = []
        
        # Historial de eventos (para debugging/replay)
        self.event_history: List[Event] = []
        self.max_history_size = 100
        
        # Inicializar listas vacías para cada tipo de evento
        for event_type in EventType:
            self.subscribers[event_type] = []
    
    def subscribe(self, event_type: EventType, callback: Callable[[Event], None]) -> None:
        """
        Suscribe un callback a un tipo de evento
        
        Args:
            event_type: Tipo de evento a escuchar
            callback: Función a llamar cuando ocurra el evento
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        
        if callback not in self.subscribers[event_type]:
            self.subscribers[event_type].append(callback)
            logger.debug(f"Callback suscrito a {event_type.name}")
    
    def unsubscribe(self, event_type: EventType, callback: Callable) -> None:
        """
        Cancela la suscripción de un callback
        
        Args:
            event_type: Tipo de evento
            callback: Función a eliminar
        """
        if event_type in self.subscribers and callback in self.subscribers[event_type]:
            self.subscribers[event_type].remove(callback)
            logger.debug(f"Callback desuscrito de {event_type.name}")
    
    def emit(self, event: Event) -> None:
        """
        Emite un evento inmediatamente
        
        Args:
            event: Evento a emitir
        """
        logger.debug(f"Emitiendo evento: {event.event_type.name} - {event.data}")
        
        # Añadir al historial
        self.event_history.append(event)
        if len(self.event_history) > self.max_history_size:
            self.event_history.pop(0)
        
        # Llamar a todos los callbacks suscritos
        if event.event_type in self.subscribers:
            for callback in self.subscribers[event.event_type]:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"Error en callback para {event.event_type.name}: {e}")
    
    def queue_event(self, event: Event) -> None:
        """
        Añade un evento a la cola para procesamiento posterior
        
        Args:
            event: Evento a encolar
        """
        self.event_queue.append(event)
        logger.debug(f"Evento encolado: {event.event_type.name}")
    
    def process_queue(self) -> None:
        """Procesa todos los eventos en la cola"""
        while self.event_queue:
            event = self.event_queue.pop(0)
            self.emit(event)
    
    def clear_history(self) -> None:
        """Limpia el historial de eventos"""
        self.event_history.clear()
        logger.debug("Historial de eventos limpiado")
    
    def get_history(self, event_type: Optional[EventType] = None) -> List[Event]:
        """
        Obtiene el historial de eventos
        
        Args:
            event_type: Filtrar por tipo de evento (opcional)
            
        Returns:
            Lista de eventos del historial
        """
        if event_type is None:
            return self.event_history.copy()
        else:
            return [e for e in self.event_history if e.event_type == event_type]
    
    def emit_quick(self, event_type: EventType, data: Dict[str, Any] = None, source: str = None) -> None:
        """
        Método de conveniencia para emitir eventos rápidamente
        
        Args:
            event_type: Tipo de evento
            data: Datos del evento
            source: Origen del evento
        """
        event = Event(event_type, data or {}, source)
        self.emit(event)

