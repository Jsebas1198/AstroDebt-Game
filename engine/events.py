"""
EventManager - Sistema de Eventos
Sistema de señales/observers para comunicación entre componentes del juego
"""

from typing import Callable, Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum, auto


class EventType(Enum):
    """Tipos de eventos del juego"""
    # Eventos de estado
    OXYGEN_CHANGED = auto()
    MATERIAL_COLLECTED = auto()
    MATERIAL_CONSUMED = auto()
    REPAIR_PROGRESS_CHANGED = auto()
    
    # Eventos de turnos
    TURN_STARTED = auto()
    TURN_ENDED = auto()
    
    # Eventos de préstamos
    LOAN_TAKEN = auto()
    LOAN_PAYMENT = auto()
    LOAN_DEFAULTED = auto()
    INTEREST_ACCRUED = auto()
    
    # Eventos de minijuegos
    MINIGAME_STARTED = auto()
    MINIGAME_COMPLETED = auto()
    MINIGAME_FAILED = auto()
    
    # Eventos de juego
    GAME_OVER = auto()
    VICTORY = auto()
    PHASE_CHANGED = auto()
    
    # Eventos de UI
    DIALOGUE_STARTED = auto()
    DIALOGUE_ENDED = auto()


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
    
    def subscribe(self, event_type: EventType, callback: Callable[[Event], None]) -> None:
        """
        Suscribe un callback a un tipo de evento
        
        Args:
            event_type: Tipo de evento a escuchar
            callback: Función a llamar cuando ocurra el evento
        """
        # TODO: Añadir callback a la lista de suscriptores
        pass
    
    def unsubscribe(self, event_type: EventType, callback: Callable) -> None:
        """
        Cancela la suscripción de un callback
        
        Args:
            event_type: Tipo de evento
            callback: Función a eliminar
        """
        # TODO: Eliminar callback de la lista de suscriptores
        pass
    
    def emit(self, event: Event) -> None:
        """
        Emite un evento inmediatamente
        
        Args:
            event: Evento a emitir
        """
        # TODO: Llamar a todos los callbacks suscritos
        # TODO: Añadir al historial
        pass
    
    def queue_event(self, event: Event) -> None:
        """
        Añade un evento a la cola para procesamiento posterior
        
        Args:
            event: Evento a encolar
        """
        # TODO: Añadir evento a event_queue
        pass
    
    def process_queue(self) -> None:
        """Procesa todos los eventos en la cola"""
        # TODO: Iterar sobre event_queue
        # TODO: Emitir cada evento con emit()
        # TODO: Limpiar la cola
        pass
    
    def clear_history(self) -> None:
        """Limpia el historial de eventos"""
        # TODO: Vaciar event_history
        pass
    
    def get_history(self, event_type: Optional[EventType] = None) -> List[Event]:
        """
        Obtiene el historial de eventos
        
        Args:
            event_type: Filtrar por tipo de evento (opcional)
            
        Returns:
            Lista de eventos del historial
        """
        # TODO: Devolver historial filtrado o completo
        pass

