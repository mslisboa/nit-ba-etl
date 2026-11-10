"""Procedência: registro de lotes de importação e proveniência (architecture.md §9).

Toda execução de pipeline deve registrar:
- Identificador da importação (batch_id);
- Fonte;
- Datas de início/fim;
- Período de referência;
- Quantidades extraídas/transformadas/carregadas/rejeitadas;
- Situação e erros.

O registro físico é feito em staging.import_batch (src.load.staging).
Quando o backend disponibilizar a tabela canônica LOTE_IMPORTACAO
(data-model.md §10), este módulo deverá ser revisado e sincronizado
com esse contrato — pendência documentada.
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from psycopg import Connection

logger = logging.getLogger(__name__)

# Situações previstas de um lote (architecture.md §9; sources.md §10).
STATUS_RUNNING = "running"
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"


class Batch:
    """Representa um lote de importação em andamento.

    Usado como objeto de rastreabilidade por um pipeline: cria o lote,
    atualiza contagens e encerra com status final. As contagens devem
    ser informadas explicitamente pelo pipeline; este módulo não
    calcula nada sobre os dados.
    """

    def __init__(self, source_system: str, ref_period: str | None = None) -> None:
        self.batch_id = str(uuid.uuid4())
        self.source_system = source_system
        self.ref_period = ref_period
        self.started_at = datetime.now(UTC)

    def create(self, conn: Connection) -> str:
        """Cria o registro do lote em staging.import_batch."""
        conn.execute(
            "INSERT INTO staging.import_batch "
            "(batch_id, source_system, ref_period, started_at, status) "
            "VALUES (%s, %s, %s, %s, %s)",
            (
                self.batch_id,
                self.source_system,
                self.ref_period,
                self.started_at,
                STATUS_RUNNING,
            ),
        )
        logger.info(
            "Lote %s inicia: fonte=%s periodo=%s",
            self.batch_id,
            self.source_system,
            self.ref_period or "nao informado",
        )
        return self.batch_id

    def update_counts(
        self,
        conn: Connection,
        *,
        extracted: int | None = None,
        transformed: int | None = None,
        loaded: int | None = None,
        rejected: int | None = None,
    ) -> None:
        """Atualiza contagens explicitamente informadas do lote."""
        sets = []
        params: list[Any] = []
        for field, value in (
            ("records_extracted", extracted),
            ("records_transformed", transformed),
            ("records_loaded", loaded),
            ("records_rejected", rejected),
        ):
            if value is not None:
                sets.append(f"{field} = %s")
                params.append(value)
        if not sets:
            return
        params.append(self.batch_id)
        conn.execute(
            f"UPDATE staging.import_batch SET {', '.join(sets)} WHERE batch_id = %s",
            params,
        )

    def finish(self, conn: Connection, *, status: str, errors: str | None = None) -> None:
        """Encerra o lote com a situação final e os erros, se existirem.

        Situações aceitas: 'completed' ou 'failed'. Histórico permanente
        — nenhum método remove lotes (architecture.md §9).
        """
        if status not in {STATUS_COMPLETED, STATUS_FAILED}:
            logger.warning(
                "Status '%s' fora do conjunto previsto; tratado como 'failed'.",
                status,
            )
            status = STATUS_FAILED
        conn.execute(
            "UPDATE staging.import_batch "
            "SET finished_at = now(), status = %s, errors = %s "
            "WHERE batch_id = %s",
            (status, errors, self.batch_id),
        )
        logger.info("Lote %s encerrado: %s", self.batch_id, status)

    def insert_raw(self, conn: Connection, payload: str, ref_period: str | None = None) -> None:
        """Insere um registro bruto no lote.

        O payload deve ser o dado original preservado sem modificação
        (architecture.md §5.1), enviado como string JSON válida.
        """
        conn.execute(
            "INSERT INTO staging.raw_records "
            "(batch_id, source_system, ref_period, payload) "
            "VALUES (%s, %s, %s, %s::jsonb)",
            (self.batch_id, self.source_system, ref_period or self.ref_period, payload),
        )
