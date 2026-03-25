from __future__ import annotations

from nfa_plotter.algorithms import DFAConversionResult


class SubsetTableFormatter:
    """Construye filas legibles para mostrar el paso a paso del método de subconjuntos."""

    HEADERS = [
        "Estado DFA",
        "Subconjunto AFN",
        "Símbolo",
        "move",
        "cerradura-ε",
        "Destino",
        "Nuevo",
        "Aceptación",
    ]

    def build_rows(self, result: DFAConversionResult) -> list[list[str]]:
        """Retorna las filas de la tabla a partir de los pasos de conversión."""
        rows: list[list[str]] = []

        for step in result.steps:
            rows.append(
                [
                    step.source_state_name,
                    self._format_subset(step.source_subset),
                    step.symbol,
                    self._format_subset(step.move_result),
                    self._format_subset(step.epsilon_closure_result),
                    step.target_state_name,
                    "Sí" if step.target_was_new else "No",
                    "Sí" if step.target_is_accepting else "No",
                ]
            )

        return rows

    @staticmethod
    def _format_subset(subset: frozenset[str]) -> str:
        if not subset:
            return "∅"
        return "{" + ", ".join(sorted(subset)) + "}"