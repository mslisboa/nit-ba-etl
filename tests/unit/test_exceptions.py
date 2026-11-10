"""Testes unitários da hierarquia de exceções (architecture.md §10)."""

from __future__ import annotations

from common.exceptions import (
    DatabaseError,
    ETLError,
    ExtractionError,
    FormatError,
    MatchingError,
    TransformationError,
    ValidationError,
)


def test_todas_derivam_da_base_do_dominio():
    for exc in (
        DatabaseError,
        ExtractionError,
        FormatError,
        MatchingError,
        TransformationError,
        ValidationError,
    ):
        assert issubclass(exc, ETLError)


def test_mensagem_default_quando_nada_informado():
    # O default descreve a natureza do erro, sem exigir o nome da ferramenta.
    assert DatabaseError().args[0].strip() != ""


def test_mensagem_especifica_e_preservada():
    exc = FormatError("CSV malformado na linha 3")
    assert "linha 3" in str(exc)


def test_causa_original_preservada():
    cause = ValueError("causa raiz")
    exc = DatabaseError("falha no banco")  # noqa: SIM105
    try:
        raise cause
    except ValueError:
        exc.__cause__ = cause  # simula o raise ... from ...
    assert exc.__cause__ is cause
