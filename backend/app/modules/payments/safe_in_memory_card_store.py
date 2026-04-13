import uuid
from dataclasses import dataclass
from functools import lru_cache
from typing import Optional


@dataclass
class CardData:
    """Card data stored for a payment"""

    card_number: str
    cvv: str
    expiry_date: str


class SafeInMemoryCardStore:
    """Simple in-memory store for card data indexed by payment ID"""

    def __init__(self):
        self._store: dict[uuid.UUID, CardData] = {}

    def store(self, payment_id: uuid.UUID, card_data: CardData) -> None:
        """Store card data for a payment"""
        self._store[payment_id] = card_data

    def get(self, payment_id: uuid.UUID) -> Optional[CardData]:
        """Retrieve card data for a payment"""
        return self._store.get(payment_id)

    def remove(self, payment_id: uuid.UUID) -> None:
        """Remove card data for a payment (security best practice)"""
        self._store.pop(payment_id, None)

    def exists(self, payment_id: uuid.UUID) -> bool:
        """Check if card data exists for a payment"""
        return payment_id in self._store


@lru_cache
def get_card_store() -> SafeInMemoryCardStore:
    """Get the global card store instance"""
    return SafeInMemoryCardStore()
