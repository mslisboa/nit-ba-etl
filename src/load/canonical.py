"""Carga canônica: stub documentado (architecture.md §6.2).

O schema canônico é de responsabilidade do backend (`nit-ba-backend`),
com migrações próprias. O ETL não deve criar, remover ou modificar
tabelas canônicas sem migração previamente aprovada (architecture.md
§6; AGENTS.md §4).

Os contratos da carga definitiva ainda não foram definidos com o
backend:
- nomes das tabelas canônicas e colunas;
- chaves de identificação para UPSERT por entidade;
- permissões do usuário do ETL;
- tratamento de conflitos e idempotência.

Este módulo permanece como ponto de extensão. Até o fechamento dos
contratos, qualquer tentativa de carga canônica é bloqueada.
"""

from __future__ import annotations

from common.exceptions import DatabaseError

_CANONICAL_LOAD_BLOCKED = (
    "Carga canônica ainda não disponível: nomes de tabelas, chaves de "
    "UPSERT e permissões dependem de acordo com o repositório "
    "nit-ba-backend (architecture.md §6.2). Registros permanecem em "
    "staging até então."
)


def load_canonical() -> None:
    """Ponto de entrada previsto para a carga canônica.

    Stub de bloqueio: enquanto os contratos com o backend não
    estiverem estabelecidos, levanta DatabaseError imediatamente,
    impedindo qualquer carga definitiva acidental.
    """
    raise DatabaseError(_CANONICAL_LOAD_BLOCKED)
