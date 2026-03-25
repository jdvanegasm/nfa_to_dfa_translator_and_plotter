from dataclasses import dataclass


@dataclass(slots=True)
class State:
    """Representa un estado de un autómata."""

    id: str
    is_start: bool = False
    is_accepting: bool = False