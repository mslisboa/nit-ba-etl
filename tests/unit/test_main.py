"""Testes unitários da CLI (src.main) — sem banco, sem rede."""

from __future__ import annotations

import importlib

import pytest

from common.exceptions import ConfigurationError
from main import main


@pytest.fixture()
def clean_env(monkeypatch):
    """Remove variáveis de configuração do ambiente do processo."""
    for name in ("ETL_DATABASE_DSN", "ETL_LOG_LEVEL", "ETL_DATA_DIR"):
        monkeypatch.delenv(name, raising=False)
    # Garante que módulos reimportem config sem cache de ambiente alterado.
    import common.config

    importlib.reload(common.config)


def test_pipeline_inexistente_rejeitado(clean_env):
    with pytest.raises(SystemExit) as excinfo:
        main(["nao-existe"])
    assert excinfo.value.code == 2


def test_sem_dsn_codigo_de_configuracao(clean_env, capsys):
    """Fail-fast de configuração resulta em código 2 (README/§11)."""
    assert main(["demo"]) == 2
    saida = capsys.readouterr().err
    assert "ETL_DATABASE_DSN" in saida
