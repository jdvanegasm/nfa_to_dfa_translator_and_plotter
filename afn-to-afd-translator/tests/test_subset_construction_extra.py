from nfa_plotter.algorithms import SubsetConstructionConverter
from nfa_plotter.regex import RegexParser, ThompsonConstructor


def build_nfa(regex: str):
    parser = RegexParser()
    constructor = ThompsonConstructor()
    postfix = parser.to_postfix(regex)
    return constructor.build_from_postfix(postfix)


def test_subset_construction_creates_sink_state_when_needed() -> None:
    nfa = build_nfa("0")
    converter = SubsetConstructionConverter()

    result = converter.convert(nfa)

    assert frozenset() in result.state_mapping.values()

    sink_names = [
        state_name
        for state_name, subset in result.state_mapping.items()
        if subset == frozenset()
    ]
    assert len(sink_names) == 1

    sink_name = sink_names[0]
    assert len(result.dfa.get_transitions(sink_name, "0")) == 1
    assert len(result.dfa.get_transitions(sink_name, "1")) == 1