"""Configuração de logging do ETL.

Usa o logging padrão da biblioteca, formatado para leitura via `docker logs`.
Pipeline executa como processo pontual (architecture.md §11), portanto não
haverá rotação de arquivos neste componente inicial.
"""

from __future__ import annotations

import logging

FORMAT = "%(asctime)s %(levelname)s %(name)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(level: str = "INFO") -> None:
    """Configura o logging raiz do processo ETL.

    Aceita níveis padrão da biblioteca (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    Níveis fora do padrão são mapeados para INFO, mantendo o processo executável.
    """
    numeric_level = logging.getLevelNamesMapping().get(level.upper(), logging.INFO)
    logging.basicConfig(level=numeric_level, format=FORMAT, datefmt=DATE_FORMAT)

    # Bibliotecas ruidosas em nível INFO exigem mais silêncio por padrão.
    logging.getLogger("psycopg").setLevel(max(numeric_level, logging.WARNING))
