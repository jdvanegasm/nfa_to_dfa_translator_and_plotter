from __future__ import annotations

from nfa_plotter.domain.automaton import Automaton
from nfa_plotter.domain.transition import Transition


class DFA(Automaton):
    """Representa un autómata finito determinista."""

    def add_transition(self, transition: Transition) -> None:
        """En un DFA no puede haber más de una transición por símbolo desde un estado."""
        existing_targets = self.get_transitions(transition.source_id, transition.symbol)
        if existing_targets:
            raise ValueError(
                f"El estado '{transition.source_id}' ya tiene transición con símbolo "
                f"'{transition.symbol}'."
            )

        super().add_transition(transition)