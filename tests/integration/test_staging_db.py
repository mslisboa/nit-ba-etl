"""Testes de integração: PostgreSQL real obrigatório (architecture.md §12).

Executados apenas com ETL_DATABASE_DSN_TEST definido; caso contrário
são pulados automaticamente (tests/conftest.py). O banco de teste é
sempre um banco descartável — nenhum banco de desenvolvimento ou
produção é usado.
"""

from __future__ import annotations

import json
import uuid

import pytest

from common.database import connect, transaction
from common.exceptions import ConfigurationError
from load.staging import STAGING_SCHEMA, ensure_staging, setup_staging
from load.provenance import STATUS_COMPLETED, STATUS_FAILED, Batch

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def db(integration_dsn: str):
    """Conexão de teste com staging preparado; descarta ao final."""
    with connect(integration_dsn) as conn:
        setup_staging(conn)
        yield conn


class TestSetupStaging:
    def test_idempotencia(self, db):
        setup_staging(db)  # segunda chamada não altera nada
        rows = db.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = %s ORDER BY table_name",
            (STAGING_SCHEMA,),
        ).fetchall()
        names = {r["table_name"] for r in rows}
        assert names == {"import_batch", "raw_records"}

    def test_falha_sem_dsn(self):
        with pytest.raises((ConfigurationError, Exception)):
            ensure_staging()


class TestBatchProvenance:
    def test_ciclo_completo_persiste(self, db):
        batch = Batch(source_system="teste", ref_period="2026")
        batch.create(db)
        batch.insert_raw(db, json.dumps({"nome": "sintetico"}, ensure_ascii=False))
        batch.update_counts(db, extracted=1, transformed=1, loaded=1, rejected=0)
        batch.finish(db, status=STATUS_COMPLETED)

        row = db.execute(
            "SELECT status, records_extracted, records_loaded, records_rejected "
            "FROM staging.import_batch WHERE batch_id = %s",
            (batch.batch_id,),
        ).fetchone()
        assert row["status"] == "completed"
        assert (row["records_extracted"], row["records_loaded"]) == (1, 1)

    def test_registro_bruto_preservado(self, db):
        batch = Batch(source_system="teste")
        batch.create(db)
        bruto = {"campo": "valor original", "anonimizado": True}
        batch.insert_raw(db, json.dumps(bruto, ensure_ascii=False))
        row = db.execute(
            "SELECT payload FROM staging.raw_records WHERE batch_id = %s",
            (batch.batch_id,),
        ).fetchone()
        # psycopg decodifica JSONB para dict; texto preserved também é aceito.
        payload = row["payload"]
        if isinstance(payload, str):
            payload = json.loads(payload)
        assert payload == bruto

    def test_status_invalido_tratado_como_failed(self, db):
        batch = Batch(source_system="teste")
        batch.create(db)
        batch.finish(db, status="desconhecido", errors="x")
        row = db.execute(
            "SELECT status FROM staging.import_batch WHERE batch_id = %s",
            (batch.batch_id,),
        ).fetchone()
        assert row["status"] == STATUS_FAILED

    def test_rollback_reverte_insercoes(self, db):
        batch = Batch(source_system="teste")
        batch.create(db)
        with pytest.raises(RuntimeError):
            with transaction(db):
                batch.insert_raw(
                    db, json.dumps({"reversivel": True}, ensure_ascii=False)
                )
                raise RuntimeError("simulação de falha")
        n = db.execute(
            "SELECT count(*) AS n FROM staging.raw_records WHERE batch_id = %s",
            (batch.batch_id,),
        ).fetchone()["n"]
        assert n == 0

    def test_nenhum_lote_apagado(self, db):
        """Nova execução cria novo lote; histórico permanente (§9)."""
        antes = db.execute(
            "SELECT count(*) AS n FROM staging.import_batch"
        ).fetchone()["n"]
        b = Batch(source_system="teste")
        b.create(db)
        depois = db.execute(
            "SELECT count(*) AS n FROM staging.import_batch"
        ).fetchone()["n"]
        assert depois > antes

    def test_batch_id_e_uuid_valido(self, db):
        batch = Batch(source_system="teste")
        batch.create(db)
        row = db.execute(
            "SELECT batch_id FROM staging.import_batch WHERE batch_id = %s",
            (batch.batch_id,),
        ).fetchone()
        uuid.UUID(str(row["batch_id"]))  # lança se inválido
