"""Configuração do ETL via variáveis de ambiente.

Nenhum valor de credencial deve ser definido no código (AGENTS.md §5).
A configuração é lida no momento do uso a partir de variáveis de ambiente,
com falha rápida quando um valor obrigatório estiver ausente.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from .exceptions import ConfigurationError


# Caminhos de dados (architecture.md §4).
# Default relativo ao diretório de trabalho do processo: em
# desenvolvimento, a raiz do repositório; no container, /app (WORKDIR
# do Dockerfile). Sobrescrito por ETL_DATA_DIR quando necessário.
DATA_ROOT = Path.cwd() / "data"

DATA_RAW_DIR = DATA_ROOT / "raw"
DATA_STAGING_DIR = DATA_ROOT / "staging"
DATA_PROCESSED_DIR = DATA_ROOT / "processed"

# Variáveis de ambiente reconhecidas.
ENV_DATABASE_DSN = "ETL_DATABASE_DSN"
ENV_LOG_LEVEL = "ETL_LOG_LEVEL"
ENV_DATA_DIR = "ETL_DATA_DIR"

# Níveis de log aceitos.
VALID_LOG_LEVELS = frozenset({"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"})

DEFAULT_LOG_LEVEL = "INFO"


@dataclass(frozen=True)
class Settings:
    """Snapshot imutável da configuração de uma execução."""

    database_dsn: str
    log_level: str
    data_dir: Path


def get_database_dsn(env: dict[str, str] | None = None) -> str:
    """Retorna o DSN do PostgreSQL ou falha se não estiver definido."""
    source = env if env is not None else os.environ
    dsn = source.get(ENV_DATABASE_DSN, "").strip()
    if not dsn:
        raise ConfigurationError(
            f"Variável de ambiente {ENV_DATABASE_DSN} não definida ou vazia."
        )
    return dsn


def get_log_level(env: dict[str, str] | None = None) -> str:
    """Retorna o nível de log, validando valores aceitos."""
    source = env if env is not None else os.environ
    level = source.get(ENV_LOG_LEVEL, DEFAULT_LOG_LEVEL).strip().upper()
    if level not in VALID_LOG_LEVELS:
        raise ConfigurationError(
            f"{ENV_LOG_LEVEL} inválido: '{level}'. Aceitos: "
            f"{', '.join(sorted(VALID_LOG_LEVELS))}."
        )
    return level


def get_data_dir(env: dict[str, str] | None = None) -> Path:
    """Retorna o diretório base de dados, sobrescrito por ambiente quando definido.

    Default: `<diretório de trabalho>/data` — resolve à raiz do
    repositório em desenvolvimento e a /app/data no container
    (WORKDIR), onde o volume é montado pelo nit-ba-infra.
    """
    source = env if env is not None else os.environ
    override = source.get(ENV_DATA_DIR, "").strip()
    return Path(override).resolve() if override else Path.cwd() / "data"


def load_settings(env: dict[str, str] | None = None) -> Settings:
    """Carrega e valida a configuração da execução.

    Falha rápida: qualquer configuração obrigatória ausente ou inválida
    interrompe a execução antes de qualquer processamento.

    Aceita um dicionário para facilitar testes; por padrão lê os.environ.
    """
    return Settings(
        database_dsn=get_database_dsn(env),
        log_level=get_log_level(env),
        data_dir=get_data_dir(env),
    )
