"""Hierarquia de exceções do ETL.

A classificação segue as categorias definidas em architecture.md §10:
- Erros de leitura;
- Erros de formato;
- Erros de transformação;
- Erros de validação;
- Erros de correspondência;
- Erros de banco de dados;
- Erros de configuração e integração.

Um erro em um registro não deve interromper o pipeline quando possível;
falhas que comprometem a integridade da carga devem interromper com rollback.
"""

from __future__ import annotations


class ETLError(Exception):
    """Base para todos os erros de domínio do ETL."""

    default_message = "Erro do ETL."

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.default_message)


class ConfigurationError(ETLError):
    """Erro de configuração ou integração (architecture.md §10, item 7)."""

    default_message = "Configuração inválida ou ausente."


class ExtractionError(ETLError):
    """Erro de leitura da fonte (architecture.md §10, item 1)."""

    default_message = "Falha na extração da fonte."


class FormatError(ETLError):
    """Erro de formato (architecture.md §10, item 2)."""

    default_message = "Formato de dados inválido ou não reconhecido."


class TransformationError(ETLError):
    """Erro de transformação (architecture.md §10, item 3)."""

    default_message = "Falha na transformação dos dados."


class ValidationError(ETLError):
    """Erro de validação (architecture.md §10, item 4).

    Não confundir com registros rejeitados na validação: a rejeição de um
    registro é um resultado de processamento; este erro indica falha na
    etapa de validação em si.
    """

    default_message = "Falha na validação dos dados."


class MatchingError(ETLError):
    """Erro de correspondência entre fontes (architecture.md §10, item 5)."""

    default_message = "Falha na correspondência entre registros de fontes distintas."


class DatabaseError(ETLError):
    """Erro de banco de dados do domínio do ETL (architecture.md §10, item 6)."""

    default_message = "Falha na operação de banco de dados."
