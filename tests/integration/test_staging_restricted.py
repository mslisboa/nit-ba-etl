"""Testes de integração do permissionamento limitado do schema staging.

Reproduz o permissionamento real do Compose (architecture.md §6.2):
o usuário do ETL é dono do schema staging mas NÃO possui CREATE no
banco — o banco tem outro dono e o schema é provisionado pelo init
script do nit-ba-infra. Garante que setup_staging não emita comando
que exija privilégio de banco quando o schema já existe.

Requer ETL_DATABASE_DSN_TEST (usuário administrador de teste, usado
exclusivamente para provisionar o cenário descartável).
"""

from __future__ import annotations

import pytest
from psycopg import sql
from psycopg import Connection
from psycopg.conninfo import conninfo_to_dict, make_conninfo

from common.database import connect
from common.exceptions import DatabaseError
from load.staging import STAGING_SCHEMA, setup_staging

pytestmark = pytest.mark.integration

ROLE = "nitba_etl_test"
PASSWORD = "test"
DATABASE = "nitba_etl_perm_test"
OTHER_SCHEMA = "outro_schema_teste"


@pytest.fixture(scope="class")
def restricted(integration_dsn: str) -> dict[str, str]:
    """Provisiona o cenário limitado e devolve os DSNs de conexão.

    - role do ETL: apenas LOGIN — sem CREATE no banco;
    - banco descartável com dono separado (o administrador);
    - schema staging pré-criado e ownado pelo role do ETL, papel do
      init script do nit-ba-infra.
    """
    base = conninfo_to_dict(integration_dsn)
    admin_dsn = make_conninfo(**base)
    role_dsn = make_conninfo(
        **{**base, "user": ROLE, "password": PASSWORD, "dbname": DATABASE}
    )
    admin_newdb_dsn = make_conninfo(**{**base, "dbname": DATABASE})

    with Connection.connect(admin_dsn, autocommit=True) as admin:
        admin.execute(
            sql.SQL("DROP DATABASE IF EXISTS {} WITH (FORCE)").format(sql.Identifier(DATABASE))
        )
        admin.execute(
            sql.SQL("DROP ROLE IF EXISTS {}").format(sql.Identifier(ROLE))
        )
        admin.execute(
            sql.SQL("CREATE ROLE {} LOGIN PASSWORD {}").format(
                sql.Identifier(ROLE), sql.Literal(PASSWORD)
            )
        )
        # Owner default do banco é o usuário criador (o administrador).
        admin.execute(
            sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DATABASE))
        )
        with Connection.connect(admin_newdb_dsn) as newdb:
            newdb.execute(
                sql.SQL("CREATE SCHEMA {} AUTHORIZATION {}").format(
                    sql.Identifier(STAGING_SCHEMA), sql.Identifier(ROLE)
                )
            )

    try:
        yield {"role_dsn": role_dsn, "admin_dsn": admin_newdb_dsn}
    finally:
        with Connection.connect(admin_dsn, autocommit=True) as admin:
            admin.execute(
                sql.SQL("DROP DATABASE IF EXISTS {} WITH (FORCE)").format(sql.Identifier(DATABASE))
            )
            admin.execute(
                sql.SQL("DROP ROLE IF EXISTS {}").format(sql.Identifier(ROLE))
            )


class TestSetupStagingComPermissaoLimitada:
    def test_setup_funciona_sendo_dono_do_schema(self, restricted):
        """Usuário dono do schema, SEM CREATE no banco: setup completo."""
        with connect(restricted["role_dsn"]) as conn:
            # Sanity check (em conexão descartável separada — a falha
            # abortaria a transação da conexão principal): o role
            # realmente não pode criar schema no banco — erro de
            # privilégio do psycopg.
            from psycopg import errors as pg_errors

            with connect(restricted["role_dsn"]) as sanity, pytest.raises(
                pg_errors.InsufficientPrivilege
            ):
                sanity.execute(
                    sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(OTHER_SCHEMA))
                )
            setup_staging(conn)
            rows = conn.execute(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = %s ORDER BY table_name",
                (STAGING_SCHEMA,),
            ).fetchall()
            assert {r["table_name"] for r in rows} == {
                "import_batch",
                "raw_records",
            }
            # Segunda execução: idempotente, sem exigir privilégio novo.
            setup_staging(conn)

    def test_falha_quando_schema_nao_existe(self, restricted):
        """Sem o schema staging e sem CREATE no banco: falha explícita
        (DatabaseError), sem depender silenciosamente de um erro de
        privilégio. O provisioning do schema é papel do nit-ba-infra."""
        with connect(restricted["admin_dsn"]) as conn:
            conn.autocommit = True
            conn.execute(
                sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(STAGING_SCHEMA))
            )
        with pytest.raises(DatabaseError, match="staging"):
            with connect(restricted["role_dsn"]) as conn:
                setup_staging(conn)
