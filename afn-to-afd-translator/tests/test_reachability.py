from nfa_plotter.algorithms import ReachabilityPruner
from nfa_plotter.domain import DFA, State, Transition


def test_reachability_pruner_removes_unreachable_state() -> None:
    dfa = DFA()
    dfa.add_state(State(id="K0", is_start=True))
    dfa.add_state(State(id="K1", is_accepting=True))
    dfa.add_state(State(id="K2"))

    dfa.add_transition(Transition(source_id="K0", symbol="0", target_id="K1"))
    dfa.add_transition(Transition(source_id="K0", symbol="1", target_id="K1"))
    dfa.add_transition(Transition(source_id="K1", symbol="0", target_id="K1"))
    dfa.add_transition(Transition(source_id="K1", symbol="1", target_id="K1"))

    pruner = ReachabilityPruner()
    pruned = pruner.prune(dfa)

    assert set(pruned.states.keys()) == {"K0", "K1"}
    assert "K2" not in pruned.states