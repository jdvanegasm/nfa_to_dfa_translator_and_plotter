from nfa_plotter.algorithms import (
    EpsilonClosureService,
    MoveService,
    SubsetConstructionConverter,
)
from nfa_plotter.domain import NFA
from nfa_plotter.regex import RegexParser, ThompsonConstructor


def build_nfa(regex: str) -> NFA:
    parser = RegexParser()
    constructor = ThompsonConstructor()
    postfix = parser.to_postfix(regex)
    return constructor.build_from_postfix(postfix)


def test_epsilon_closure_returns_same_state_when_no_epsilon_edges() -> None:
    nfa = build_nfa("0")
    service = EpsilonClosureService()

    closure = service.compute(nfa, {"q0"})

    assert closure == {"q0"}


def test_move_returns_reachable_states_for_symbol() -> None:
    nfa = build_nfa("0")
    service = MoveService()

    result = service.compute(nfa, {"q0"}, "0")

    assert result == {"q1"}


def test_subset_construction_generates_valid_dfa() -> None:
    nfa = build_nfa("0|1")
    converter = SubsetConstructionConverter()

    result = converter.convert(nfa)
    dfa = result.dfa

    assert dfa.start_state_id == "K0"
    assert len(dfa.states) >= 2
    assert len(dfa.accepting_state_ids) >= 1

    for state_id in dfa.states:
        for symbol in dfa.alphabet:
            targets = dfa.get_transitions(state_id, symbol)
            assert len(targets) == 1


def test_subset_construction_marks_accepting_states() -> None:
    nfa = build_nfa("0")
    converter = SubsetConstructionConverter()

    result = converter.convert(nfa)

    accepting_subsets = {
        name: subset
        for name, subset in result.state_mapping.items()
        if name in result.dfa.accepting_state_ids
    }

    assert accepting_subsets
    assert any("q1" in subset for subset in accepting_subsets.values())