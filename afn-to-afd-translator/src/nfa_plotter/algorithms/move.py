from __future__ import annotations

from nfa_plotter.domain import NFA


class MoveService:
    """Calcula el movimiento de un conjunto de estados con un símbolo dado."""

    def compute(self, nfa: NFA, state_ids: set[str], symbol: str) -> set[str]:
        """Retorna el conjunto de estados alcanzables desde state_ids con symbol."""
        result: set[str] = set()

        for state_id in state_ids:
            result.update(nfa.get_transitions(state_id, symbol))

        return result