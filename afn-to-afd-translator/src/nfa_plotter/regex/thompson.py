from __future__ import annotations

from dataclasses import dataclass

from nfa_plotter.domain import NFA, State, Transition


@dataclass(slots=True)
class NFAFragment:
    """Fragmento temporal usado por el algoritmo de Thompson."""

    start_state_id: str
    accept_state_id: str


class ThompsonConstructor:
    """Construye un AFN a partir de una expresión postfix usando Thompson."""

    def __init__(self) -> None:
        self._state_counter = 0

    def build_from_postfix(self, tokens: list[str]) -> NFA:
        """Construye un AFN desde una lista de tokens postfix."""
        if not tokens:
            raise ValueError("No se puede construir un AFN a partir de una expresión vacía.")

        self._reset()
        nfa = NFA()
        stack: list[NFAFragment] = []

        for token in tokens:
            if token in {"0", "1"}:
                stack.append(self._build_symbol_fragment(token, nfa))
            elif token == ".":
                self._require_stack_size(stack, 2, token)
                right = stack.pop()
                left = stack.pop()
                stack.append(self._concatenate(left, right, nfa))
            elif token == "|":
                self._require_stack_size(stack, 2, token)
                right = stack.pop()
                left = stack.pop()
                stack.append(self._union(left, right, nfa))
            elif token == "*":
                self._require_stack_size(stack, 1, token)
                fragment = stack.pop()
                stack.append(self._kleene_star(fragment, nfa))
            else:
                raise ValueError(f"Token postfix no soportado: '{token}'.")

        if len(stack) != 1:
            raise ValueError(
                "La expresión postfix es inválida: no fue posible reducirla a un único AFN."
            )

        final_fragment = stack.pop()
        self._mark_start_and_accept(nfa, final_fragment)
        return nfa

    def _reset(self) -> None:
        """Reinicia el contador interno de estados."""
        self._state_counter = 0

    def _new_state(self, nfa: NFA) -> str:
        """Crea un nuevo estado y retorna su id."""
        state_id = f"q{self._state_counter}"
        self._state_counter += 1
        nfa.add_state(State(id=state_id))
        return state_id

    def _build_symbol_fragment(self, symbol: str, nfa: NFA) -> NFAFragment:
        """Construye un fragmento básico para un símbolo."""
        start_state_id = self._new_state(nfa)
        accept_state_id = self._new_state(nfa)

        nfa.add_transition(
            Transition(
                source_id=start_state_id,
                symbol=symbol,
                target_id=accept_state_id,
            )
        )

        return NFAFragment(
            start_state_id=start_state_id,
            accept_state_id=accept_state_id,
        )

    def _concatenate(
        self,
        left: NFAFragment,
        right: NFAFragment,
        nfa: NFA,
    ) -> NFAFragment:
        """Concatena dos fragmentos."""
        nfa.add_transition(
            Transition(
                source_id=left.accept_state_id,
                symbol=NFA.EPSILON,
                target_id=right.start_state_id,
            )
        )

        return NFAFragment(
            start_state_id=left.start_state_id,
            accept_state_id=right.accept_state_id,
        )

    def _union(
        self,
        left: NFAFragment,
        right: NFAFragment,
        nfa: NFA,
    ) -> NFAFragment:
        """Aplica la operación de unión entre dos fragmentos."""
        start_state_id = self._new_state(nfa)
        accept_state_id = self._new_state(nfa)

        nfa.add_transition(
            Transition(start_state_id, NFA.EPSILON, left.start_state_id)
        )
        nfa.add_transition(
            Transition(start_state_id, NFA.EPSILON, right.start_state_id)
        )
        nfa.add_transition(
            Transition(left.accept_state_id, NFA.EPSILON, accept_state_id)
        )
        nfa.add_transition(
            Transition(right.accept_state_id, NFA.EPSILON, accept_state_id)
        )

        return NFAFragment(
            start_state_id=start_state_id,
            accept_state_id=accept_state_id,
        )

    def _kleene_star(self, fragment: NFAFragment, nfa: NFA) -> NFAFragment:
        """Aplica estrella de Kleene a un fragmento."""
        start_state_id = self._new_state(nfa)
        accept_state_id = self._new_state(nfa)

        nfa.add_transition(
            Transition(start_state_id, NFA.EPSILON, fragment.start_state_id)
        )
        nfa.add_transition(
            Transition(start_state_id, NFA.EPSILON, accept_state_id)
        )
        nfa.add_transition(
            Transition(fragment.accept_state_id, NFA.EPSILON, fragment.start_state_id)
        )
        nfa.add_transition(
            Transition(fragment.accept_state_id, NFA.EPSILON, accept_state_id)
        )

        return NFAFragment(
            start_state_id=start_state_id,
            accept_state_id=accept_state_id,
        )

    @staticmethod
    def _require_stack_size(
        stack: list[NFAFragment],
        required_size: int,
        operator: str,
    ) -> None:
        """Valida que la pila tenga suficientes operandos."""
        if len(stack) < required_size:
            raise ValueError(
                f"La expresión postfix es inválida para el operador '{operator}'."
            )

    @staticmethod
    def _mark_start_and_accept(nfa: NFA, fragment: NFAFragment) -> None:
        """Marca los estados inicial y de aceptación del AFN final."""
        start_state = nfa.states[fragment.start_state_id]
        accept_state = nfa.states[fragment.accept_state_id]

        start_state.is_start = True
        accept_state.is_accepting = True

        nfa.start_state_id = start_state.id
        nfa.accepting_state_ids = {accept_state.id}