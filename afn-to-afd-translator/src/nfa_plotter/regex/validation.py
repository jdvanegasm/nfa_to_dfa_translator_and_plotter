from __future__ import annotations

from dataclasses import dataclass


VALID_SYMBOLS = {"0", "1"}
VALID_OPERATORS = {"|", "*", "(", ")"}
VALID_TOKENS = VALID_SYMBOLS | VALID_OPERATORS


@dataclass(slots=True)
class ValidationResult:
    """Resultado de la validación de una expresión regular."""

    is_valid: bool
    errors: list[str]


class RegexValidator:
    """Valida expresiones regulares sobre el alfabeto {0,1}."""

    def validate(self, regex: str) -> ValidationResult:
        errors: list[str] = []
        cleaned = self._clean(regex)

        if not cleaned:
            return ValidationResult(
                is_valid=False,
                errors=["La expresión regular no puede estar vacía."],
            )

        invalid_chars = sorted({char for char in cleaned if char not in VALID_TOKENS})
        if invalid_chars:
            errors.append(
                "La expresión contiene caracteres inválidos: "
                + ", ".join(invalid_chars)
            )

        balance = 0
        previous: str | None = None

        for index, current in enumerate(cleaned):
            if current == "(":
                balance += 1
            elif current == ")":
                balance -= 1
                if balance < 0:
                    errors.append(
                        f"Paréntesis desbalanceados: ')' inesperado en posición {index}."
                    )
                    balance = 0

            if previous is None:
                if current in {"|", "*", ")"}:
                    errors.append(
                        f"La expresión no puede iniciar con '{current}' en posición {index}."
                    )
            else:
                self._validate_sequence(previous, current, index, errors)

            previous = current

        if balance != 0:
            errors.append("Los paréntesis no están balanceados.")

        if previous in {"|", "("}:
            errors.append("La expresión no puede terminar con un operador incompleto.")

        return ValidationResult(is_valid=not errors, errors=errors)

    @staticmethod
    def _clean(regex: str) -> str:
        """Elimina espacios en blanco."""
        return "".join(regex.split())

    @staticmethod
    def _validate_sequence(
        previous: str,
        current: str,
        index: int,
        errors: list[str],
    ) -> None:
        """Valida secuencias inválidas de tokens."""

        if previous == "|" and current in {"|", "*", ")"}:
            errors.append(
                f"Secuencia inválida '{previous}{current}' en posición {index - 1}."
            )

        if previous == "(" and current in {"|", "*", ")"}:
            errors.append(
                f"Contenido inválido después de '(' en posición {index}."
            )

        if previous == "*" and current == "*":
            errors.append(
                f"No se permite aplicar '*' consecutivamente en posición {index}."
            )

        if previous == "|" and current == ")":
            errors.append(
                f"No puede cerrarse un grupo inmediatamente después de '|' en posición {index}."
            )

        if previous == "(" and current == ")":
            errors.append(
                f"No se permiten paréntesis vacíos '()' en posición {index - 1}."
            )