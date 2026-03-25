from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Transition:
    """Representa una transición entre dos estados."""

    source_id: str
    symbol: str
    target_id: str