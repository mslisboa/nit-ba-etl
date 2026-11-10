"""Conexão ao PostgreSQL compartilhado com o backend.

O ETL utiliza credenciais próprias e de permissão limitada
(architecture.md §6.2). Nenhuma credencial é definida no código:
o DSN origina-se de ETL_DATABASE_DSN (ver common.config).

Responsabilidades:
- Fornecer uma conexão configurada;
- Garantir commit na conclusão e rollback em caso de falha
  (architecture.md §5.4 e §10).

Não é responsabilidade deste módulo criar, remover ou modificar
tabelas canônicas: elas pertencem ao backend (architecture.md §6).
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import psycopg
from psycopg import Connection
from psycopg.rows import dict_row

from .config import load_settings
from .exceptions import DatabaseError

logger = logging.getLogger(__name__)


def connect(dsn: str | None = None, timeout_seconds: int = 30) -> Connection:
    """Abre uma conexão ao PostgreSQL.

    - `dsn`: quando ausente, lê de ETL_DATABASE_DSN via load_settings();
    - `timeout_seconds`: limite de conexão (psycopg connect_timeout);
    - Linhas retornadas como dicionário (row_factory=dict_row);
    - Falhas de conexão são convertidas em DatabaseError do domínio
      do ETL, conforme a classificação de erros de architecture.md §10.
    """
    resolved_dsn = dsn if dsn is not None else load_settings().database_dsn
    try:
        conn = psycopg.connect(
            resolved_dsn,
            connect_timeout=timeout_seconds,
            row_factory=dict_row,
        )
    except psycopg.OperationalError as exc:
        logger.error("Falha ao conectar ao PostgreSQL: %s", exc)
        raise DatabaseError(f"Falha ao conectar ao PostgreSQL: {exc}") from exc
    logger.debug("Conexão aberta com o PostgreSQL")
    return conn


@contextmanager
def transaction(conn: Connection) -> Iterator[Connection]:
    """Contexto transacional: commit ao concluir, rollback em qualquer exceção.

    A exceção original é relançada após o rollback, preservando a causa
    para classificação em níveis superiores (architecture.md §10).
    """
    try:
        yield conn
        conn.commit()
        logger.debug("Transação concluída com commit")
    except Exception:
        conn.rollback()
        logger.warning("Transação revertida com rollback")
        raise


def execute_in_transaction(
    dsn: str | None, statements: list[tuple[str, dict[str, Any]]]
) -> None:
    """Executa uma lista de (SQL, params) dentro de uma única transação.

    Utilidade para operações idempotentes de infraestrutura do ETL
    (criação de schema/tabela de staging) em uma única transação.
    """
    with connect(dsn) as conn, transaction(conn):
        for statement, params in statements:
            conn.execute(statement, params)
