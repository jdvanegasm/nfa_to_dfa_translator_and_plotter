from __future__ import annotations

from collections import deque

from nfa_plotter.domain import NFA


class EpsilonClosureService:
    """Calcula la cerradura epsilon de un conjunto de estados."""

    def compute(self, nfa: NFA, state_ids: set[str]) -> set[str]:
        """Retorna la cerradura-ε del conjunto de estados dado."""
        closure = set(state_ids)
        queue: deque[str] = deque(state_ids)

        while queue:
            current_state_id = queue.popleft()

            for target_state_id in nfa.get_epsilon_transitions(current_state_id):
                if target_state_id not in closure:
                    closure.add(target_state_id)
                    queue.append(target_state_id)

        return closure