from __future__ import annotations

from nfa_plotter.domain import DFA, State, Transition


class ReachabilityPruner:
    """Elimina estados inaccesibles de un DFA."""

    def prune(self, dfa: DFA) -> DFA:
        """Retorna un nuevo DFA que contiene solo estados alcanzables."""
        reachable_state_ids = dfa.get_reachable_states()
        pruned_dfa = DFA(alphabet=set(dfa.alphabet))

        for state_id in sorted(reachable_state_ids):
            original_state = dfa.states[state_id]
            pruned_dfa.add_state(
                State(
                    id=original_state.id,
                    is_start=original_state.is_start,
                    is_accepting=original_state.is_accepting,
                )
            )

        for transition in dfa.transitions:
            if (
                transition.source_id in reachable_state_ids
                and transition.target_id in reachable_state_ids
            ):
                pruned_dfa.add_transition(
                    Transition(
                        source_id=transition.source_id,
                        symbol=transition.symbol,
                        target_id=transition.target_id,
                    )
                )

        return pruned_dfa