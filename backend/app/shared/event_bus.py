import logging
from functools import lru_cache
from typing import Callable

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class Event(BaseModel):
    """Base class for all domain events"""
    pass


class EventBus:
    """Simple in-memory event bus for publishing and subscribing to events"""
    def __init__(self):
        self._subscribers: dict[type[Event], list[Callable[[Event], None]]] = {}

    def subscribe(self, event_type: type[Event], handler: Callable[[Event], None]) -> None:
        """Subscribe a handler to an event type"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    def publish(self, event: Event) -> None:
        """Publish an event to all subscribed handlers"""
        event_type = type(event)
        logger.debug(f"Publishing {event_type.__name__}: {event}")
        if event_type in self._subscribers:
            for handler in self._subscribers[event_type]:
                handler(event)


@lru_cache
def get_event_bus() -> EventBus:
    return EventBus()
