from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from nfa_plotter.algorithms.epsilon_closure import EpsilonClosureService
from nfa_plotter.algorithms.move import MoveService
from nfa_plotter.domain import DFA, NFA, State, Transition


@dataclass(slots=True)
class ConversionStep:
    """Representa un paso individual del método de subconjuntos."""

    source_state_name: str
    source_subset: frozenset[str]
    symbol: str
    move_result: frozenset[str]
    epsilon_closure_result: frozenset[str]
    target_state_name: str
    target_was_new: bool
    target_is_accepting: bool


@dataclass(slots=True)
class DFAConversionResult:
    """Resultado completo de la conversión AFN → AFD."""

    dfa: DFA
    steps: list[ConversionStep]
    state_mapping: dict[str, frozenset[str]]


class StateNameGenerator:
    """Genera nombres secuenciales K0, K1, K2... para estados del AFD."""

    def __init__(self) -> None:
        self._counter = 0

    def next_name(self) -> str:
        name = f"K{self._counter}"
        self._counter += 1
        return name

    def reset(self) -> None:
        self._counter = 0


class SubsetConstructionConverter:
    """Convierte un AFN en un AFD usando el método de subconjuntos."""

    def __init__(self) -> None:
        self.epsilon_closure_service = EpsilonClosureService()
        self.move_service = MoveService()
        self.name_generator = StateNameGenerator()

    def convert(self, nfa: NFA) -> DFAConversionResult:
        """Convierte el AFN dado a un AFD equivalente."""
        if nfa.start_state_id is None:
            raise ValueError("El AFN no tiene un estado inicial definido.")

        self.name_generator.reset()

        dfa = DFA(alphabet=set(nfa.alphabet))
        steps: list[ConversionStep] = []

        subset_to_name: dict[frozenset[str], str] = {}
        state_mapping: dict[str, frozenset[str]] = {}

        start_subset = frozenset(
            self.epsilon_closure_service.compute(nfa, {nfa.start_state_id})
        )
        start_state_name = self.name_generator.next_name()

        subset_to_name[start_subset] = start_state_name
        state_mapping[start_state_name] = start_subset

        dfa.add_state(
            State(
                id=start_state_name,
                is_start=True,
                is_accepting=self._is_accepting_subset(nfa, start_subset),
            )
        )

        queue: deque[frozenset[str]] = deque([start_subset])
        processed: set[frozenset[str]] = set()

        while queue:
            current_subset = queue.popleft()

            if current_subset in processed:
                continue

            processed.add(current_subset)
            current_state_name = subset_to_name[current_subset]

            for symbol in sorted(dfa.alphabet):
                move_result = frozenset(
                    self.move_service.compute(nfa, set(current_subset), symbol)
                )
                epsilon_closure_result = frozenset(
                    self.epsilon_closure_service.compute(nfa, set(move_result))
                )

                if epsilon_closure_result not in subset_to_name:
                    target_state_name = self.name_generator.next_name()
                    subset_to_name[epsilon_closure_result] = target_state_name
                    state_mapping[target_state_name] = epsilon_closure_result

                    dfa.add_state(
                        State(
                            id=target_state_name,
                            is_accepting=self._is_accepting_subset(
                                nfa, epsilon_closure_result
                            ),
                        )
                    )
                    queue.append(epsilon_closure_result)
                    target_was_new = True
                else:
                    target_state_name = subset_to_name[epsilon_closure_result]
                    target_was_new = False

                dfa.add_transition(
                    Transition(
                        source_id=current_state_name,
                        symbol=symbol,
                        target_id=target_state_name,
                    )
                )

                steps.append(
                    ConversionStep(
                        source_state_name=current_state_name,
                        source_subset=current_subset,
                        symbol=symbol,
                        move_result=move_result,
                        epsilon_closure_result=epsilon_closure_result,
                        target_state_name=target_state_name,
                        target_was_new=target_was_new,
                        target_is_accepting=self._is_accepting_subset(
                            nfa, epsilon_closure_result
                        ),
                    )
                )

        return DFAConversionResult(
            dfa=dfa,
            steps=steps,
            state_mapping=state_mapping,
        )

    @staticmethod
    def _is_accepting_subset(nfa: NFA, subset: frozenset[str]) -> bool:
        """Indica si el subconjunto contiene al menos un estado de aceptación del AFN."""
        return any(state_id in nfa.accepting_state_ids for state_id in subset)