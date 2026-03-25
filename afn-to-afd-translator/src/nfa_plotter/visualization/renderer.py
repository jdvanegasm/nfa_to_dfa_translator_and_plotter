from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from graphviz import Digraph

from nfa_plotter.domain import Automaton


class AutomatonRenderer:
    """Genera una representación DOT y renderiza autómatas con Graphviz."""

    def to_dot(self, automaton: Automaton, title: str = "Automaton") -> str:
        """Retorna el código DOT del autómata."""
        return self._build_graph(automaton, title).source

    def render_png(self, automaton: Automaton, output_path: str | Path) -> str:
        """Renderiza el autómata como imagen PNG y retorna la ruta generada."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        graph = self._build_graph(automaton, title=path.stem)
        rendered_path = graph.render(
            filename=path.stem,
            directory=str(path.parent),
            cleanup=True,
        )
        return rendered_path

    def _build_graph(self, automaton: Automaton, title: str) -> Digraph:
        """Construye el grafo Graphviz a partir del autómata."""
        graph = Digraph(name=title, format="png")
        graph.attr(rankdir="LR")
        graph.attr(label=title, labelloc="t", fontsize="20")

        start_marker_id = "__start__"
        graph.node(start_marker_id, "", shape="none", width="0")

        for state_id in sorted(automaton.states):
            state = automaton.states[state_id]
            shape = "doublecircle" if state.is_accepting else "circle"
            graph.node(state.id, state.id, shape=shape)

        if automaton.start_state_id is not None:
            graph.edge(start_marker_id, automaton.start_state_id)

        transitions_by_pair: dict[tuple[str, str], list[str]] = defaultdict(list)
        for transition in automaton.transitions:
            transitions_by_pair[
                (transition.source_id, transition.target_id)
            ].append(transition.symbol)

        for (source_id, target_id), symbols in sorted(transitions_by_pair.items()):
            label = ", ".join(sorted(symbols, key=lambda value: (value != "ε", value)))
            graph.edge(source_id, target_id, label=label)

        return graph