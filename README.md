# nit-ba-etl

ETL do módulo de integração estadual dos NITs da Bahia, componente do Observatório de CT&I da Bahia.

Obtém dados de fontes distintas (DATANIT, relatórios dos NITs, fontes institucionais, Observatório/SIMCC, BADEPI, dados territoriais), realiza tratamento e padronização, valida e carrega no PostgreSQL compartilhado com o backend.

- Escopo detalhado: [AGENTS.md](AGENTS.md)
- Arquitetura: [docs/architecture.md](docs/architecture.md)
- Modelo de dados: [docs/data-model.md](docs/data-model.md)
- Fontes de dados: [docs/sources.md](docs/sources.md)

## Status atual

Esqueleto mínimo do repositório, destinado à configuração da orquestração no `nit-ba-infra`.

- ✅ Configuração, logging, exceções (architecture.md §10)
- ✅ Conexão ao PostgreSQL com transação/rollback
- ✅ Schema de staging (`staging.import_batch`, `staging.raw_records`)
- ✅ Procedência por lote de importação
- ✅ Pipeline stub de demonstração (`demo`)
- ✅ Dockerfile para execução pontual
- 🚫 Carga canônica: **bloqueada** até fechamento dos contratos com o `nit-ba-backend`

## Estrutura

```
src/
├── common/        # config, database, logging, exceptions
├── extract/       # extração por fonte (vazio — estrutura inicial)
├── transform/     # transformação por entidade (vazio)
├── validate/      # validação (vazio)
├── load/          # staging, canonical, provenance
├── pipelines/     # pipelines executáveis (demo apenas)
└── main.py        # CLI: python -m src.main <pipeline>
```

## Desenvolvimento

Requisitos: Python 3.12+ e PostgreSQL acessível.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt    # runtime + dev
# ou, apenas runtime:
.venv/bin/pip install -r requirements.txt && \
.venv/bin/pip install --no-deps -e .

cp .env.example .env   # ajuste ETL_DATABASE_DSN
```

A fonte única de dependências é `requirements.txt` (runtime) e `requirements-dev.txt` (dev). O `pyproject.toml` permanece apenas para empacotamento e configuração do pytest.

Execução de um pipeline a partir da raiz do repositório:

```bash
ETL_DATABASE_DSN="postgresql://etl:senha@localhost:5432/nitba" \
.venv/bin/python -m src.main demo
```

O pipeline `demo` lê um CSV sintético em `data/raw/demo/` e exercita o ciclo extract → transform → validate → load (staging). É um stub para validação da infraestrutura e será substituído pela primeira fonte real (Territórios, conforme ordem de implementação combinada).

## Configuração

| Variável | Obrigatória | Descrição |
|---|---|---|
| `ETL_DATABASE_DSN` | sim | DSN do PostgreSQL com usuário do ETL e permissões limitadas |
| `ETL_LOG_LEVEL` | não | `DEBUG`/`INFO`/`WARNING`/`ERROR`/`CRITICAL` (default `INFO`) |
| `ETL_DATA_DIR` | não | Base de dados; default `<cwd>/data` (`/app/data` no container) |

## Docker

```bash
docker build -t nit-ba-etl .
docker run --rm \
  -e ETL_DATABASE_DSN="postgresql://etl:senha@host:5432/nitba" \
  -v ./data:/app/data \
  nit-ba-etl demo --ref-period 2026
```

Execução pontual (run-to-completion), sem serviço contínuo (architecture.md §11). Arquivos brutos **não entram na imagem**; são montados como volume pelo `nit-ba-infra`.

### Parâmetros de orquestração (para o nit-ba-infra)

- Serviço: execução de pipeline por `docker run`, sem restart contínuo;
- `ENTRYPOINT`: `python -m src.main`; argumentos: `<pipeline> [--ref-period AAAA]`;
- Códigos de saída: `0` sucesso; `1` falha de pipeline; `2` falha de configuração;
- Volumes: `/app/data` (raw/externos);
- Rede: mesma rede do serviço PostgreSQL do módulo;

## Testes

```bash
.venv/bin/pytest
```

Os testes não usam dados reais restritos; fixtures são sintéticas e anonimizadas (architecture.md §12).

- Unitários (28): executam sem banco e sem rede — `pytest` por padrão;
- Integração (8): exigem PostgreSQL de teste e são **pulados** por default; para executá-los:

```bash
ETL_DATABASE_DSN_TEST="postgresql://etl:senha@localhost:5432/etl_teste" .venv/bin/pytest -m integration
```

## Pendências (ver docs/)

- Fonte institucional definitiva a definir;
- Contratos de carga canônica com o `nit-ba-backend` (tabelas canônicas, chaves de UPSERT, permissões);
- Estrutura real das fontes (DATANIT, SIMCC, BADEPI, relatórios, territórios) a inspecionar;
- Sincronização de `staging.import_batch` com a tabela canônica `LOTE_IMPORTACAO`.
