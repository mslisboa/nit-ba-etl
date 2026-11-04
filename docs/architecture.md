
# Arquitetura do ETL

## 1. Visão geral

Este repositório contém os processos de Extração, Transformação e Carga (ETL) responsáveis pela integração das informações utilizadas no módulo estadual dos NITs da Bahia.

O ETL tem como finalidade obter dados de diferentes fontes, realizar o tratamento e a padronização necessários, validar os registros e carregá-los no banco de dados PostgreSQL compartilhado pelo sistema.

As fontes contempladas no MVP são:

- DATANIT e relatórios dos NITs;
- Fontes institucionais;
- Observatório/SIMCC;
- BADEPI;
- Dados territoriais disponibilizados pelo Observatório/SIMCC.

O ETL é um componente independente dos repositórios de frontend e backend.

## 2. Responsabilidades

O ETL é responsável por:

1. Extrair informações das fontes definidas.
2. Preservar os arquivos e dados originais.
3. Normalizar os dados.
4. Padronizar atributos e identificadores.
5. Identificar registros duplicados.
6. Identificar correspondências entre entidades de fontes diferentes.
7. Validar a integridade dos dados.
8. Carregar os registros no PostgreSQL.
9. Registrar a origem e o histórico das importações.
10. Disponibilizar mecanismos de reprocessamento.

O ETL não é responsável por:

- Implementar endpoints da API;
- Implementar regras de apresentação dos dados;
- Construir interfaces;
- Gerenciar usuários da aplicação;
- Controlar as migrações do schema canônico;
- Implementar funcionalidades de TT;
- Realizar operações administrativas dos NITs.

## 3. Arquitetura geral

O fluxo de processamento é:

Fontes de dados
    |
    v
EXTRACT
    |
    v
Dados brutos (RAW)
    |
    v
TRANSFORM
    |
    v
Dados normalizados
    |
    v
VALIDATE
    |
    v
Dados validados
    |
    v
LOAD
    |
    v
PostgreSQL

O PostgreSQL é compartilhado com o backend.

O backend é responsável pelo schema canônico e suas migrações.

O ETL é responsável pelas estruturas intermediárias e pela alimentação das tabelas canônicas, conforme os contratos estabelecidos com o backend.

## 4. Organização interna

A organização recomendada é:

etl/
|
├── src/
│   ├── extract/
│   │   ├── datanit/
│   │   ├── relatorios_nit/
│   │   ├── instituicoes/
│   │   ├── simcc/
│   │   ├── badepi/
│   │   └── territorios/
│   │
│   ├── transform/
│   │   ├── nit/
│   │   ├── instituicao/
│   │   ├── pesquisador/
│   │   ├── propriedade_intelectual/
│   │   └── territorial/
│   │
│   ├── validate/
│   │   ├── identifiers.py
│   │   ├── relationships.py
│   │   ├── duplicates.py
│   │   └── schemas.py
│   │
│   ├── load/
│   │   ├── staging.py
│   │   ├── canonical.py
│   │   └── provenance.py
│   │
│   ├── common/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── logging.py
│   │   └── exceptions.py
│   │
│   └── main.py
│
├── tests/
│
├── data/
│   ├── raw/
│   ├── staging/
│   └── processed/
│
├── docs/
│
├── Dockerfile
├── .dockerignore
├── .env.example
├── pyproject.toml
└── README.md

Esta estrutura é uma referência inicial e pode ser adaptada caso o repositório já possua uma organização estabelecida.

Não criar diretórios ou abstrações desnecessárias.

## 5. Etapas do processamento

### 5.1 Extract

Responsável por obter os dados das fontes.

Cada fonte deve possuir um processo de extração independente.

Exemplos:

- Extração dos registros da DATANIT;
- Leitura dos relatórios dos NITs;
- Obtenção dos dados institucionais;
- Leitura dos dados do SIMCC;
- Leitura dos arquivos da BADEPI;
- Obtenção dos dados dos municípios e Territórios de Identidade.

A extração deve preservar os dados originais, sem modificações.

Sempre registrar a origem, o arquivo utilizado, a data de extração e o período de referência, quando conhecido.

### 5.2 Transform

Responsável por transformar os dados extraídos em estruturas padronizadas.

As operações podem incluir:

- Normalização de textos;
- Tratamento de acentuação;
- Padronização de nomes;
- Normalização de datas;
- Padronização de identificadores;
- Conversão de tipos;
- Tratamento de valores nulos;
- Padronização de categorias;
- Identificação de duplicações;
- Correspondência entre registros.

Os dados originais não devem ser sobrescritos.

### 5.3 Validate

Responsável por verificar a consistência dos dados transformados.

As validações devem considerar:

- Campos obrigatórios;
- Formatos;
- Identificadores;
- Duplicações;
- Integridade referencial;
- Correspondência entre instituições;
- Correspondência entre pesquisadores;
- Relacionamentos de propriedade intelectual;
- Associação territorial.

Registros inconsistentes não devem ser carregados silenciosamente nas tabelas definitivas.

Quando necessário, devem ser encaminhados para uma estrutura de inconsistências ou revisão manual.

### 5.4 Load

Responsável por carregar os dados no PostgreSQL.

A carga deve contemplar:

- Inserção de novos registros;
- Atualização de registros existentes;
- Atualização de relacionamentos;
- Registro de procedência;
- Registro de execução;
- Tratamento de erros.

As operações devem ser idempotentes.

Executar novamente o mesmo pipeline não deve gerar duplicações.

## 6. PostgreSQL e integração com o backend

O PostgreSQL será compartilhado entre ETL e backend.

O backend é o proprietário do schema canônico e responsável pelas migrações das tabelas definitivas.

O ETL não deve criar, remover ou modificar tabelas canônicas sem que exista uma migração previamente definida e aprovada pelo backend.

### 6.1 Staging

O ETL poderá utilizar um schema `staging` para armazenar registros intermediários.

O staging deve permitir:

- Armazenamento temporário dos registros extraídos;
- Inspeção dos dados originais;
- Identificação de inconsistências;
- Comparação entre execuções;
- Preparação para a carga definitiva.

Os dados de staging não devem ser consumidos diretamente pelo frontend.

### 6.2 Carga canônica

O ETL deve carregar os registros no schema canônico conforme os contratos estabelecidos pelo backend.

A carga deve utilizar:

- Chaves de identificação confiáveis;
- Restrições de integridade existentes;
- Transações;
- Estratégias de UPSERT quando apropriado;
- Tratamento explícito de conflitos.

O ETL deve possuir credenciais próprias e permissões limitadas.

Não utilizar credenciais de administrador do PostgreSQL para os processos de carga.

## 7. Estratégia de identificação e correspondência

A integração de diferentes fontes exige mecanismos de correspondência entre entidades.

### Instituições

Priorizar identificadores institucionais confiáveis, além de nomes e siglas normalizados.

Considerar variações de nomenclatura.

Não associar automaticamente instituições somente pela semelhança dos nomes.

### Pesquisadores

Priorizar identificadores como:

- Identificador SIMCC;
- Identificador Lattes;
- ORCID.

Não associar pesquisadores exclusivamente pelo nome.

### Propriedade Intelectual

Priorizar:

- Identificador BADEPI;
- Número do processo;
- Modalidade da propriedade intelectual.

Distinguir titulares, depositantes, inventores e autores.

### Municípios

Utilizar preferencialmente o código IBGE.

### NITs

Utilizar os identificadores disponíveis na DATANIT e nos relatórios institucionais.

Quando a correspondência não puder ser estabelecida com segurança, manter o registro pendente de validação.

## 8. Execução dos pipelines

O ETL deve funcionar como processo independente, executado sob demanda.

Não deve existir dependência de sua execução para que o backend ou frontend iniciem.

Cada pipeline deve permitir:

- Execução individual;
- Registro de logs;
- Identificação da fonte;
- Registro da execução;
- Tratamento de exceções;
- Reprocessamento.

A preparação para execução agendada poderá ocorrer futuramente.

Não implementar inicialmente um orquestrador complexo sem necessidade.

## 9. Rastreabilidade e histórico

Toda execução deve registrar:

- Identificador da importação;
- Fonte;
- Data de início;
- Data de término;
- Período de referência;
- Quantidade de registros extraídos;
- Quantidade de registros transformados;
- Quantidade de registros carregados;
- Quantidade de registros rejeitados;
- Situação da execução;
- Erros encontrados.

Sempre que possível, manter a identificação do registro original na fonte.

Não apagar informações históricas de execução ao realizar uma nova carga.

## 10. Tratamento de erros

Erros devem ser classificados de acordo com sua natureza:

- Erros de leitura;
- Erros de formato;
- Erros de transformação;
- Erros de validação;
- Erros de correspondência;
- Erros de banco de dados;
- Erros de integração.

Um erro em determinado registro não deve necessariamente interromper todo o pipeline.

Quando possível, isolar registros inválidos e continuar o processamento dos registros válidos.

Entretanto, falhas que comprometam a integridade da carga devem interromper a operação e gerar rollback.

## 11. Docker

O ETL deve possuir seu próprio Dockerfile.

A execução conjunta dos serviços é controlada pelo repositório `nit-ba-infra`.

O container do ETL deve permitir execução pontual e não deve permanecer executando continuamente sem necessidade.

Os arquivos brutos devem permanecer fora da imagem Docker.

Utilizar variáveis de ambiente para configurações.

Não versionar arquivos `.env`.

## 12. Testes

Os pipelines devem possuir testes unitários e de integração.

Testar:

- Leitura das fontes;
- Transformações;
- Normalização;
- Identificação de duplicações;
- Correspondência;
- Validação;
- Integridade dos relacionamentos;
- Idempotência;
- Carga no PostgreSQL.

Não utilizar dados reais restritos em testes versionados.

Criar fixtures e datasets pequenos e anonimizados quando necessário.

## 13. Decisões pendentes

As seguintes questões dependem da inspeção das fontes reais:

- Formato e estrutura dos dados da DATANIT;
- Disponibilidade dos relatórios dos NITs;
- Fonte definitiva para informações institucionais;
- Cobertura e estrutura dos dados do SIMCC;
- Estrutura dos arquivos da BADEPI;
- Formato dos dados territoriais;
- Estratégia de correspondência entre identificadores;
- Frequência de atualização das fontes.

Não presumir que esses pontos já estejam resolvidos.

## 14. Princípio arquitetural

O ETL deve ser independente, modular, rastreável e reproduzível.

Seu principal objetivo é transformar informações dispersas em registros consistentes para o banco canônico do módulo.

A qualidade das correspondências e a confiabilidade dos dados são mais importantes que a quantidade de registros importados.
