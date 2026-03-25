from __future__ import annotations

from nfa_plotter.domain.automaton import Automaton


class NFA(Automaton):
    """Representa un autómata finito no determinista."""

    EPSILON = "ε"

    def _validate_symbol(self, symbol: str) -> None:
        """Permite símbolos del alfabeto o epsilon."""
        if symbol != self.EPSILON and symbol not in self.alphabet:
            raise ValueError(
                f"Símbolo inválido '{symbol}'. Debe pertenecer al alfabeto {self.alphabet} "
                f"o ser '{self.EPSILON}'."
            )

    def get_epsilon_transitions(self, state_id: str) -> list[str]:
        """Retorna los estados alcanzables por epsilon desde state_id."""
        return self.get_transitions(state_id, self.EPSILON)