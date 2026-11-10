"""Testes unitários de common.config (sem banco, sem rede)."""

from __future__ import annotations

import pytest

from common.config import (
    ENV_DATA_DIR,
    ENV_DATABASE_DSN,
    ENV_LOG_LEVEL,
    get_data_dir,
    get_log_level,
    get_database_dsn,
    load_settings,
)
from common.exceptions import ConfigurationError


class TestGetDatabaseDsn:
    def test_dsn_ausente_falha_rapida(self):
        with pytest.raises(ConfigurationError, match="ETL_DATABASE_DSN"):
            get_database_dsn({})

    def test_dsn_vazio_falha_rapida(self):
        with pytest.raises(ConfigurationError):
            get_database_dsn({ENV_DATABASE_DSN: "   "})

    def test_dsn_definido_retorna_valor(self):
        dsn = "postgresql://etl:test@localhost:5432/etl"
        assert get_database_dsn({ENV_DATABASE_DSN: dsn}) == dsn


class TestGetLogLevel:
    def test_default_info(self):
        assert get_log_level({}) == "INFO"

    def test_nivel_minusculo_normalizado(self):
        assert get_log_level({ENV_LOG_LEVEL: "debug"}) == "DEBUG"

    def test_nivel_invalido_rejeitado(self):
        with pytest.raises(ConfigurationError, match="ETL_LOG_LEVEL"):
            get_log_level({ENV_LOG_LEVEL: "verbose"})


class TestGetDataDir:
    def test_default_relativo_ao_cwd(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        assert get_data_dir({}) == tmp_path / "data"

    def test_override_ambiente(self):
        custom = get_data_dir({ENV_DATA_DIR: "/tmp/opencode/etldata"})
        assert custom.name == "etldata"


class TestLoadSettings:
    def test_carga_completa(self):
        settings = load_settings(
            {
                ENV_DATABASE_DSN: "postgresql://x",
                ENV_LOG_LEVEL: "warning",
            }
        )
        assert settings.database_dsn == "postgresql://x"
        assert settings.log_level == "WARNING"

    def test_sem_dsn_levanta_erro(self):
        with pytest.raises(ConfigurationError):
            load_settings({})
