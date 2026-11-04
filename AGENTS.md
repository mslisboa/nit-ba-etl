
# AGENTS.md

## 1. Contexto

Este repositório faz parte do sistema de integração
estadual dos NITs da Bahia, integrado ao Observatório
de CT&I da Bahia.

O projeto busca integrar informações sobre:

- NITs;
- Instituições/ICTs;
- Pesquisadores;
- Propriedade Intelectual;
- Municípios e Territórios de Identidade.

O escopo territorial é exclusivamente a Bahia.

## 2. Escopo do MVP

O MVP contempla:

- NITs;
- Instituições/ICTs;
- Pesquisadores;
- Propriedade Intelectual;
- Territórios de Identidade.

Não implementar nesta versão:

- Transferência de Tecnologia;
- PROFNIT;
- Incubadoras e parques;
- Anúncios e eventos;
- Vitrine tecnológica;
- Gestão individual dos NITs.

## 3. Regras fundamentais

- Cada NIT está relacionado a exatamente uma instituição.
- Cada instituição pode possuir no máximo um NIT.
- Uma instituição pode existir sem NIT identificado.
- Pesquisadores podem ter múltiplos vínculos institucionais.
- Uma PI pode envolver múltiplas instituições e pesquisadores.
- Não associar automaticamente uma PI ao NIT de uma instituição.
- Municípios devem ser relacionados aos Territórios de Identidade.
- Priorizar identificadores oficiais nas integrações.
- Não criar relacionamentos sem evidência suficiente.
- Preservar fonte e período de referência dos dados.
- Não converter dados ausentes em zero.

## 4. Arquitetura geral

- Banco: PostgreSQL.
- Backend: Python + FastAPI.
- Frontend: Next.js.
- ETL: Python.
- Infraestrutura: Docker e Docker Compose.

O projeto possui quatro repositórios independentes.

Respeitar a responsabilidade de cada componente
e seus contratos de integração.

## 5. Regras de desenvolvimento

- Inspecionar o código existente antes de modificá-lo.
- Respeitar os padrões já adotados no repositório.
- Trabalhar incrementalmente.
- Evitar duplicações e abstrações desnecessárias.
- Não adicionar dependências sem necessidade.
- Implementar e executar testes pertinentes.
- Não armazenar credenciais no código.
- Manter documentação atualizada.
- Não modificar contratos compartilhados sem avaliar
  o impacto nos outros repositórios.

## 6. Documentação sob demanda

IMPORTANTE:

Não leia todos os documentos de referência no início
de cada tarefa.

Identifique quais documentos são relevantes para
a tarefa atual e leia somente esses documentos.

As referências abaixo indicam documentação que deve
ser carregada quando necessária.

Consulte a documentação utilizando a ferramenta Read.

- Arquitetura: @docs/architecture.md
- Modelo de dados: @docs/data-model.md
- Desenvolvimento: @docs/development.md

Consulte também os documentos específicos do
componente quando a tarefa exigir.

Após carregar um documento, siga suas orientações.

Se houver conflito entre documentação e código
existente, investigue antes de modificar.

## 7. Validação

Ao concluir uma tarefa, informe:

- O que foi implementado;
- Arquivos modificados;
- Decisões tomadas;
- Testes executados;
- Resultados;
- Pendências.
