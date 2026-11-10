"""Staging: infraestrutura intermediária do ETL (architecture.md §6.1).

O schema `staging` é responsabilidade do ETL e não deve ser consumido
diretamente pelo frontend. Tabelas canônicas permanecem sob contrato
com o backend (architecture.md §6.2) e não são criadas aqui.

Estrutura mínima adotada nesta fase (anterior à inspeção das fontes
reais — architecture.md §13):

    staging.import_batch — lotes de importação;
    staging.raw_records  — registros brutos por fonte/lote.

Ambas têm estrutura genérica: o registro original é preservado sem
modificações em JSONB (payload), e os metadados de procedência ficam
em colunas próprias. O refinamento por fonte ocorrerá após a inspeção
de DATANIT, relatórios, SIMCC e BADEPI, quando o mapeamento por fonte
(data-model.md §11) for realizado.

Idempotência: executar novamente as migrações não altera a estrutura
existente nem apaga histórico (architecture.md §5.4 e §9).
"""

from __future__ import annotations

import logging

from psycopg import Connection, sql

from common.database import connect, transaction
from common.exceptions import DatabaseError

logger = logging.getLogger(__name__)

STAGING_SCHEMA = "staging"

# Verificação de existência: CREATE SCHEMA IF NOT EXISTS exige privilégio
# CREATE no banco mesmo quando o schema já existe. O usuário do ETL tem
# permissões limitadas (§6.2), então a existência é verificada antes da
# criação, que só ocorre quando o schema realmente não existe.
SCHEMA_EXISTS_SQL = sql.SQL(
    "SELECT count(*) AS schema_count "
    "FROM information_schema.schemata WHERE schema_name = {}"
).format(sql.Literal(STAGING_SCHEMA))

# Lotes de importação: proveniência de cada execução (architecture.md §9).
IMPORT_BATCH_DDL = sql.SQL(
    """
    CREATE TABLE IF NOT EXISTS {}.import_batch (
        batch_id           UUID        PRIMARY KEY,
        source_system      TEXT        NOT NULL,
        started_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
        finished_at        TIMESTAMPTZ NULL,
        ref_period         TEXT        NULL,
        records_extracted  INTEGER     NOT NULL DEFAULT 0,
        records_transformed INTEGER    NOT NULL DEFAULT 0,
        records_loaded     INTEGER     NOT NULL DEFAULT 0,
        records_rejected   INTEGER     NOT NULL DEFAULT 0,
        status             TEXT        NOT NULL DEFAULT 'running',
        errors             TEXT        NULL
    )
    """
).format(sql.Identifier(STAGING_SCHEMA))

# Registros brutos: dado original preservado sem modificação (§5.1),
# com referência ao lote e à fonte. Chave única (batch, ordem).
RAW_RECORDS_DDL = sql.SQL(
    """
    CREATE TABLE IF NOT EXISTS {}.raw_records (
        id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        batch_id      UUID        NOT NULL,
        source_system TEXT        NOT NULL,
        ref_period    TEXT        NULL,
        payload       JSONB       NOT NULL,
        loaded_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
        UNIQUE (batch_id, id)
    )
    """
).format(sql.Identifier(STAGING_SCHEMA))

STAGING_STATEMENTS: list[sql.Composable] = (
    IMPORT_BATCH_DDL,
    RAW_RECORDS_DDL,
)


def setup_staging(conn: Connection) -> None:
    """Cria schema e tabelas de staging de forma idempotente.

    O schema é criado somente se inexistente, por verificação explícita
    (o usuário do ETL possui permissões limitadas — architecture.md §6.2
    e §6.1). As tabelas usam CREATE TABLE IF NOT EXISTS, que não exige
    privilégio adicional quando executadas pelo dono do schema. Falha
    em qualquer instrução reverte a operação completa e levanta
    DatabaseError para classificação pelo pipeline chamador (§5.4, §10).
    """
    try:
        with transaction(conn):
            schema_exists = conn.execute(SCHEMA_EXISTS_SQL).fetchone()[
                "schema_count"
            ] > 0
            if not schema_exists:
                # AUTHORIZATION CURRENT_USER garante que o schema fique
                # sob o mesmo dono do role conectado, independente do
                # provisioning do nit-ba-infra.
                conn.execute(
                    sql.SQL("CREATE SCHEMA {} AUTHORIZATION CURRENT_USER").format(
                        sql.Identifier(STAGING_SCHEMA)
                    )
                )
            for statement in STAGING_STATEMENTS:
                conn.execute(statement)
    except Exception as exc:
        logger.error("Falha ao preparar o staging: %s", exc)
        raise DatabaseError(f"Falha ao preparar o staging: {exc}") from exc


def ensure_staging(dsn: str | None = None) -> None:
    """Abre conexão e prepara o staging, encerrando a conexão na saída.

    Atalho para uso no início de um pipeline, quando a conexão ainda
    não foi aberta pelo chamador.
    """
    with connect(dsn) as conn:
        setup_staging(conn)
