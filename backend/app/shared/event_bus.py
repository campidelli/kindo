from typing import Any, Callable

from pydantic import BaseModel


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
        if event_type in self._subscribers:
            for handler in self._subscribers[event_type]:
                handler(event)


# Global event bus instance
event_bus = EventBus()
