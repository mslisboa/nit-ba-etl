# Imagem do ETL do módulo estadual dos NITs da Bahia.
# Execução pontual (run-to-completion): `docker run ... nit-ba-etl <pipeline>`
# Não permanece executando continuamente (architecture.md §11).
# Os arquivos brutos de dados NÃO entram na imagem (§11); eles são
# montados como volume pelo nit-ba-infra.

FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# requirements.txt é a fonte única de dependências (opção A da
# organização do projeto); o código é instalado sem reprocessar
# dependências que já foram instaladas.
COPY pyproject.toml requirements.txt ./
COPY src ./src

RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir --no-deps .

# Executa como usuário sem privilégios.
RUN useradd --create-home etluser
USER etluser

# Comando padrão: executa um pipeline informado em runtime.
# O diretório /app/data é montado como volume pelo nit-ba-infra.
ENTRYPOINT ["python", "-m", "src.main"]
CMD ["--help"]
