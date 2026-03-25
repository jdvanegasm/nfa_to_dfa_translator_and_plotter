from nfa_plotter.domain import NFA
from nfa_plotter.regex import RegexParser, ThompsonConstructor


def test_build_nfa_for_single_symbol() -> None:
    parser = RegexParser()
    constructor = ThompsonConstructor()

    postfix = parser.to_postfix("0")
    nfa = constructor.build_from_postfix(postfix)

    assert nfa.start_state_id == "q0"
    assert nfa.accepting_state_ids == {"q1"}
    assert len(nfa.states) == 2
    assert nfa.get_transitions("q0", "0") == ["q1"]


def test_build_nfa_for_union_contains_epsilon_transitions() -> None:
    parser = RegexParser()
    constructor = ThompsonConstructor()

    postfix = parser.to_postfix("0|1")
    nfa = constructor.build_from_postfix(postfix)

    epsilon_transitions = [
        transition
        for transition in nfa.transitions
        if transition.symbol == NFA.EPSILON
    ]

    assert len(nfa.states) == 6
    assert len(epsilon_transitions) == 4
    assert nfa.start_state_id is not None
    assert len(nfa.accepting_state_ids) == 1


def test_build_nfa_for_kleene_star_marks_single_start_and_accept() -> None:
    parser = RegexParser()
    constructor = ThompsonConstructor()

    postfix = parser.to_postfix("(0|1)*")
    nfa = constructor.build_from_postfix(postfix)

    start_states = [state for state in nfa.states.values() if state.is_start]
    accepting_states = [state for state in nfa.states.values() if state.is_accepting]

    assert len(start_states) == 1
    assert len(accepting_states) == 1
    assert nfa.start_state_id == start_states[0].id
    assert nfa.accepting_state_ids == {accepting_states[0].id}