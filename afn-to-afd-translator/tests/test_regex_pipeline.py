from nfa_plotter.regex import RegexNormalizer, RegexParser, RegexValidator


def test_validator_accepts_valid_expression() -> None:
    validator = RegexValidator()
    result = validator.validate("(0|010)*")

    assert result.is_valid is True
    assert result.errors == []


def test_validator_rejects_invalid_expression() -> None:
    validator = RegexValidator()
    result = validator.validate("0||1")

    assert result.is_valid is False
    assert result.errors


def test_normalizer_inserts_explicit_concatenation() -> None:
    normalizer = RegexNormalizer()
    normalized = normalizer.insert_concatenation("(0|010)*")

    assert normalized == "(0|0.1.0)*"


def test_parser_generates_expected_postfix() -> None:
    parser = RegexParser()
    postfix = parser.to_postfix("(0|010)*")

    assert postfix == ["0", "0", "1", ".", "0", ".", "|", "*"]