from __future__ import annotations


class RegexNormalizer:
    """Inserta de forma explícita el operador de concatenación interna '.'."""

    CONCATENATION = "."

    def insert_concatenation(self, regex: str) -> str:
        cleaned = "".join(regex.split())
        if not cleaned:
            return cleaned

        result: list[str] = []

        for index, current in enumerate(cleaned):
            result.append(current)

            if index == len(cleaned) - 1:
                continue

            next_char = cleaned[index + 1]

            if self._needs_concatenation(current, next_char):
                result.append(self.CONCATENATION)

        return "".join(result)

    @staticmethod
    def _needs_concatenation(left: str, right: str) -> bool:
        left_allows_concat = left in {"0", "1", ")", "*"}
        right_allows_concat = right in {"0", "1", "("}
        return left_allows_concat and right_allows_concat