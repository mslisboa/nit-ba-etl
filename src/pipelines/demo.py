"""Pipeline stub: demonstração de ponta a ponta do esqueleto.

Exercita as quatro etapas previstas (architecture.md §5) com um CSV
de amostra anonimizado, SEM qualquer fonte real:

    extract   -> leitura em data/raw/demo/*.csv
    transform -> normalização leve de campos
    validate  -> separação válidos/inválidos
    load      -> carga em staging.raw_records + procedência

Este pipeline permanece no esqueleto apenas para validar a
infraestrutura (conexão, staging, provenance, logging, CLI) e como
modelo de organização dos pipelines reais. Será substituído pela
primeira fonte real conforme a ordem combinada (Territórios).

Observações de projeto:
- O dado bruto é preservado no payload sem modificação (§5.1);
- Registros inválidos são isolados e contabilizados, sem interromper
  o processamento dos válidos (§10);
- O staging mantém histórico por lote (§9): nova execução gera novo
  lote, sem alterar os anteriores. Idempotência estrita é requisito
  da carga canônica (§5.4), não do staging bruto.
"""

from __future__ import annotations

import csv
import json
import logging
from pathlib import Path

from common.config import get_data_dir
from common.exceptions import FormatError

logger = logging.getLogger(__name__)

# Campos mínimos da amostra (fixture de teste anonimizada).
REQUIRED_FIELDS = ("nome", "sigla")


def _find_input_file(data_dir: Path) -> Path:
    """Localiza o CSV de entrada da fonte demo."""
    candidate_dir = data_dir / "raw" / "demo"
    if not candidate_dir.is_dir():
        raise FormatError(
            f"Diretório de entrada ausente: {candidate_dir}. "
            "Inclua um arquivo CSV em data/raw/demo/."
        )
    candidates = sorted(candidate_dir.glob("*.csv"))
    if not candidates:
        raise FormatError(f"Nenhum arquivo CSV encontrado em {candidate_dir}.")
    if len(candidates) > 1:
        raise FormatError(
            f"Múltiplos CSVs em {candidate_dir} ({len(candidates)}). "
            "Cada execução deve ler exatamente um arquivo."
        )
    return candidates[0]


def extract(input_file: Path) -> list[dict[str, str]]:
    """Etapa 1 — extração: lê o CSV preservando o conteúdo original (§5.1)."""
    logger.info("Extraindo de %s", input_file)
    try:
        with input_file.open(newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
    except OSError as exc:
        raise FormatError(f"Falha de leitura em {input_file}: {exc}") from exc
    logger.info("Extraídos %d registros", len(rows))
    return rows


def transform(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Etapa 2 — transformação: normalização leve dos campos
    (remoção de espaços nas bordas; §5.2)."""
    normalized = [
        {key: (value or "").strip() for key, value in row.items()} for row in rows
    ]
    logger.info("Transformados %d registros", len(normalized))
    return normalized


def validate(
    rows: list[dict[str, str]],
) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    """Etapa 3 — validação: separa registros válidos e inválidos (§5.3).

    Retorna (transformados_válidos, transformados_inválidos, originais).
    Registros reprovados continuam no fluxo apenas como contagem de
    rejeição, nunca como carga silenciosa (§5.3).
    """
    valid: list[dict[str, str]] = []
    invalid: list[dict[str, str]] = []
    for row in rows:
        if all(row.get(field) for field in REQUIRED_FIELDS):
            valid.append(row)
        else:
            invalid.append(row)
    logger.info("Validados: %d válidos, %d rejeitados", len(valid), len(invalid))
    return valid, invalid, rows


def run(ref_period: str | None = None) -> dict[str, object]:
    """Executa o pipeline demo de ponta a ponta.

    Conecta ao banco, garante o staging, registra um lote e encerra
    com status final. Falha qualquer exceção não tratada reverte a
    carga e encerra o lote como 'failed' com os erros persistidos
    (§10).
    """
    from load.provenance import STATUS_COMPLETED, STATUS_FAILED, Batch
    from common.database import connect, transaction
    from load.staging import ensure_staging

    data_dir = get_data_dir()
    input_file = _find_input_file(data_dir)

    originals = extract(input_file)
    normalized = transform(originals)
    valid, invalid, _ = validate(normalized)

    ensure_staging()

    with connect() as conn:
        batch = Batch(source_system="demo", ref_period=ref_period)
        batch.create(conn)
        try:
            with transaction(conn):
                # O payload preservado em staging é o DADO ORIGINAL,
                # sem modificação; a transformação não sobrescreve a
                # origem (§5.2).
                for row in originals:
                    batch.insert_raw(conn, json.dumps(row, ensure_ascii=False))
                batch.update_counts(
                    conn,
                    extracted=len(originals),
                    transformed=len(normalized),
                    loaded=len(valid),
                    rejected=len(invalid),
                )
            batch.finish(conn, status=STATUS_COMPLETED)
        except Exception as exc:
            batch.finish(conn, status=STATUS_FAILED, errors=str(exc))
            raise

    summary = {
        "batch_id": batch.batch_id,
        "input_file": str(input_file),
        "extracted": len(originals),
        "transformed": len(normalized),
        "loaded": len(valid),
        "rejected": len(invalid),
    }
    logger.info("Pipeline demo concluído: %s", summary)
    return summary
