from __future__ import annotations

from collections import deque

from nfa_plotter.domain.state import State
from nfa_plotter.domain.transition import Transition


class Automaton:
    """Clase base para representar un autómata."""

    def __init__(self, alphabet: set[str] | None = None) -> None:
        self.alphabet: set[str] = alphabet or {"0", "1"}
        self.states: dict[str, State] = {}
        self.transitions: list[Transition] = []
        self.start_state_id: str | None = None
        self.accepting_state_ids: set[str] = set()

    def add_state(self, state: State) -> None:
        """Agrega un estado al autómata."""
        if state.id in self.states:
            raise ValueError(f"El estado '{state.id}' ya existe.")

        if state.is_start:
            if self.start_state_id is not None:
                raise ValueError("Ya existe un estado inicial definido.")
            self.start_state_id = state.id

        if state.is_accepting:
            self.accepting_state_ids.add(state.id)

        self.states[state.id] = state

    def _validate_symbol(self, symbol: str) -> None:
        """Valida que el símbolo pertenezca al alfabeto."""
        if symbol not in self.alphabet:
            raise ValueError(
                f"Símbolo inválido '{symbol}'. Debe pertenecer al alfabeto {self.alphabet}."
            )

    def add_transition(self, transition: Transition) -> None:
        """Agrega una transición al autómata."""
        if transition.source_id not in self.states:
            raise ValueError(f"El estado origen '{transition.source_id}' no existe.")

        if transition.target_id not in self.states:
            raise ValueError(f"El estado destino '{transition.target_id}' no existe.")

        self._validate_symbol(transition.symbol)
        self.transitions.append(transition)

    def get_transitions(self, state_id: str, symbol: str) -> list[str]:
        """Retorna los ids destino alcanzables desde state_id con symbol."""
        return [
            transition.target_id
            for transition in self.transitions
            if transition.source_id == state_id and transition.symbol == symbol
        ]

    def get_outgoing_transitions(self, state_id: str) -> list[Transition]:
        """Retorna todas las transiciones salientes de un estado."""
        return [
            transition
            for transition in self.transitions
            if transition.source_id == state_id
        ]

    def get_reachable_states(self) -> set[str]:
        """Calcula los estados alcanzables desde el estado inicial."""
        if self.start_state_id is None:
            return set()

        visited: set[str] = set()
        queue: deque[str] = deque([self.start_state_id])

        while queue:
            current = queue.popleft()

            if current in visited:
                continue

            visited.add(current)

            for transition in self.get_outgoing_transitions(current):
                if transition.target_id not in visited:
                    queue.append(transition.target_id)

        return visited