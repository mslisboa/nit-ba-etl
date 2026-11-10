"""Configuração dos testes.

Convenções (architecture.md §12):
- Fixtures pequenas, sintéticas e anonimizadas, versionadas;
- Nenhum dado real restrito nos testes;
- Testes de banco de dados são marcados como 'integration' e
  exigem a variável ETL_DATABASE_DSN_TEST; sem ela, são pulados.
"""

from __future__ import annotations

import os

import pytest

# DSN para testes de integração; os testes são pulados quando ausente.
INTEGRATION_DSN_ENV = "ETL_DATABASE_DSN_TEST"


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "integration: requer PostgreSQL disponível")


def _integration_dsn() -> str | None:
    return os.environ.get(INTEGRATION_DSN_ENV, "").strip() or None


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Pula testes de integração quando o DSN de teste não está definido."""
    if _integration_dsn():
        return
    skip_marker = pytest.mark.skip(
        reason=f"define {INTEGRATION_DSN_ENV} (PostgreSQL de teste) para rodar"
    )
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_marker)


@pytest.fixture(scope="session")
def integration_dsn() -> str:
    """DSN do PostgreSQL de teste para testes marcados como integration.

    Falha explicitamente se usado sem a variável definida (não deve
    ocorrer: os itens são pulados antes).
    """
    dsn = _integration_dsn()
    if not dsn:
        pytest.skip(f"{INTEGRATION_DSN_ENV} não definido")
    return dsn
