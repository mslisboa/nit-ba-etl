"""CLI do ETL: execução pontual de um pipeline por nome (architecture.md §8).

Uso:
    python -m src.main <pipeline> [--ref-period YYYY]

O pipeline é identificado por um nome registrado em PIPELINES.
Não há orquestrador: cada execução é individual e independente.
O código de saída reflete a conclusão para uso em execução
containerizada (docker run-to-completion; architecture.md §11).
"""

from __future__ import annotations

import argparse
import logging
import sys

from common.config import load_settings
from common.exceptions import ETLError
from common.logging import setup_logging

logger = logging.getLogger(__name__)

# Registro de pipelines disponíveis (architecture.md §8: execução individual).
# O pipeline 'demo' é um stub de esqueleto e será substituído pela
# primeira fonte real (Territórios, conforme ordem combinada).
PIPELINES = {
    "demo": {"module": "pipelines.demo", "function": "run"},
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="nit-ba-etl",
        description="Execução de pipelines do ETL do módulo dos NITs da Bahia.",
    )
    parser.add_argument("pipeline", choices=sorted(PIPELINES), help="pipeline a executar")
    parser.add_argument(
        "--ref-period",
        default=None,
        help="período de referência dos dados (quando conhecido)",
    )
    args = parser.parse_args(argv)

    try:
        settings = load_settings()
    except ETLError as exc:
        print(f"[nit-ba-etl] configuração: {exc}", file=sys.stderr)
        return 2

    setup_logging(settings.log_level)
    logger.info("Executando pipeline '%s'", args.pipeline)

    spec = PIPELINES[args.pipeline]
    module = __import__(spec["module"], fromlist=[spec["function"]])
    run_fn = getattr(module, spec["function"])

    try:
        run_fn(ref_period=args.ref_period)
    except ETLError as exc:
        logger.error("Falha no pipeline '%s': %s", args.pipeline, exc)
        return 1
    except Exception:
        logger.exception("Erro inesperado no pipeline '%s'", args.pipeline)
        return 1

    logger.info("Pipeline '%s' concluído", args.pipeline)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
