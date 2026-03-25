from __future__ import annotations

from nfa_plotter.regex.normalization import RegexNormalizer


class RegexParser:
    """Convierte expresiones regulares infijas a postfix."""

    PRECEDENCE: dict[str, int] = {
        "|": 1,
        ".": 2,
    }

    def __init__(self) -> None:
        self.normalizer = RegexNormalizer()

    def to_postfix(self, regex: str) -> list[str]:
        normalized = self.normalizer.insert_concatenation(regex)

        output: list[str] = []
        operators: list[str] = []

        for token in normalized:
            if token in {"0", "1"}:
                output.append(token)
            elif token == "*":
                output.append(token)
            elif token == "(":
                operators.append(token)
            elif token == ")":
                while operators and operators[-1] != "(":
                    output.append(operators.pop())

                if not operators:
                    raise ValueError("Paréntesis desbalanceados durante el parseo.")

                operators.pop()
            elif token in {"|", "."}:
                while (
                    operators
                    and operators[-1] != "("
                    and self.PRECEDENCE[operators[-1]] >= self.PRECEDENCE[token]
                ):
                    output.append(operators.pop())

                operators.append(token)
            else:
                raise ValueError(f"Token inesperado '{token}'.")

        while operators:
            operator = operators.pop()
            if operator == "(":
                raise ValueError("Paréntesis desbalanceados durante el parseo.")
            output.append(operator)

        return output