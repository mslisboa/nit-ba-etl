
# Fontes de Dados — ETL

## 1. Objetivo

Este documento descreve as fontes de dados previstas para alimentar o módulo de integração estadual dos NITs da Bahia.

O ETL utilizará diferentes fontes para obter informações sobre:

- NITs;
- Instituições/ICTs;
- Pesquisadores;
- Propriedade Intelectual;
- Municípios;
- Territórios de Identidade.

O principal desafio consiste em integrar informações provenientes de fontes distintas, que podem apresentar diferenças de formato, nomenclatura, identificadores, cobertura e período de referência.

Este documento deve ser atualizado sempre que uma fonte for efetivamente inspecionada e validada.

## 2. Inventário de fontes

| Categoria | Fonte principal | Situação |
|---|---|---|
| NITs | DATANIT | Identificada |
| NITs | Relatórios dos NITs | Aguardando obtenção e inspeção |
| Instituições/ICTs | Fontes institucionais | A definir e validar |
| Pesquisadores | Observatório/SIMCC | Identificada |
| Propriedade Intelectual | BADEPI | Identificada |
| Territórios de Identidade | Observatório/SIMCC | Identificada |

A utilização de IA é permitida como ferramenta auxiliar para descoberta e organização dos dados, não como fonte oficial.

## 3. Fonte: DATANIT

### 3.1 Finalidade

A DATANIT será utilizada como uma das principais referências para identificar os NITs existentes.

Na reunião de alinhamento do projeto, a DATANIT foi indicada como a referência mais atualizada disponível para o levantamento preliminar.

### 3.2 Informações esperadas

Investigar a disponibilidade de:

- Identificação do NIT;
- Nome;
- Instituição relacionada;
- Localização;
- Informações institucionais;
- Indicadores disponíveis;
- Período de referência;
- Identificador original.

Não presumir que todos esses campos existam na estrutura da base.

### 3.3 Procedimento

1. Obter a base ou publicação disponível.
2. Registrar a versão e a data de obtenção.
3. Inspecionar os arquivos e formatos.
4. Identificar os campos existentes.
5. Verificar o universo de NITs apresentado.
6. Comparar com o levantamento preliminar do projeto.
7. Identificar registros duplicados ou estruturas não reconhecidas.
8. Preparar os dados para transformação.

### 3.4 Cuidados

A DATANIT será utilizada como referência inicial, mas não deve ser considerada automaticamente um inventário definitivo de todas as estruturas de inovação existentes na Bahia.

Diferenças entre o universo da base e o levantamento institucional devem ser documentadas.

## 4. Fonte: Relatórios dos NITs

### 4.1 Finalidade

Os relatórios dos NITs serão utilizados para complementar e validar as informações obtidas na DATANIT.

Os relatórios podem apresentar dados referentes a diferentes anos.

### 4.2 Obtenção

Conforme encaminhamento da reunião de alinhamento, o professor responsável realizará contato inicial com as instituições para solicitar o envio dos relatórios.

O ETL deverá ser preparado para trabalhar com diferentes formatos e estruturas.

### 4.3 Informações a investigar

Verificar a existência de:

- Dados de identificação;
- Instituição relacionada;
- Município;
- Informações de atuação;
- Indicadores de propriedade intelectual;
- Informações sobre pesquisadores;
- Dados históricos;
- Outros indicadores relacionados às atividades do NIT.

### 4.4 Cuidados

Não presumir que os relatórios de todos os NITs possuem o mesmo formato.

Registrar:

- Instituição;
- NIT;
- Ano de referência;
- Data de obtenção;
- Nome do documento;
- Tipo de arquivo;
- Campos disponíveis.

Valores de anos diferentes devem permanecer identificados por seus respectivos períodos.

Não somar indicadores de períodos distintos sem verificar se representam períodos exclusivos ou acumulados.

## 5. Fonte: Fontes institucionais

### 5.1 Finalidade

As fontes institucionais serão utilizadas para identificar e complementar informações sobre as ICTs relacionadas ao módulo.

A fonte definitiva para o cadastro de instituições ainda precisa ser consolidada.

### 5.2 Informações esperadas

Investigar a disponibilidade de:

- Nome oficial;
- Sigla;
- Natureza;
- Tipo institucional;
- Site;
- Município;
- Identificadores institucionais;
- Unidades ou campi, quando disponíveis.

### 5.3 Procedimento

1. Identificar uma referência institucional confiável.
2. Inspecionar a estrutura dos dados.
3. Identificar códigos e identificadores.
4. Comparar registros com as instituições já identificadas nos NITs.
5. Normalizar nomenclaturas.
6. Registrar os vínculos validados.

### 5.4 VIP

A utilização do VIP para obter informações sobre estruturas de inovação e produção tecnológica ainda está em avaliação.

Essas informações não fazem parte do escopo atual do ETL.

Não implementar integração com o VIP para essa finalidade sem uma decisão posterior.

## 6. Fonte: Observatório/SIMCC — Pesquisadores

### 6.1 Finalidade

Utilizar dados do Observatório/SIMCC para identificar pesquisadores e seus vínculos institucionais.

### 6.2 Informações a investigar

Verificar a disponibilidade de:

- Identificador SIMCC;
- Nome;
- Identificador Lattes;
- ORCID;
- Área de atuação;
- Instituição relacionada;
- Unidade institucional;
- Grupo de pesquisa, caso disponível.

Não presumir a disponibilidade de todos os atributos.

### 6.3 Procedimento

1. Obter os arquivos ou dados disponibilizados pelo Observatório/SIMCC.
2. Inspecionar formatos e campos.
3. Identificar os registros de pesquisadores.
4. Verificar os identificadores disponíveis.
5. Identificar como os vínculos institucionais estão representados.
6. Normalizar informações.
7. Preparar os dados para carga.

### 6.4 Correspondência

A correspondência entre pesquisadores do SIMCC e pesquisadores mencionados na BADEPI deve utilizar identificadores confiáveis sempre que possível.

Não realizar associação definitiva utilizando somente o nome.

Quando não existir identificador suficiente, registrar a possível correspondência para validação.

### 6.5 Cobertura

Verificar quais instituições e pesquisadores estão efetivamente cobertos pela fonte.

Não presumir que o SIMCC represente todos os pesquisadores de todas as ICTs identificadas no projeto.

## 7. Fonte: BADEPI — Propriedade Intelectual

### 7.1 Finalidade

A BADEPI será utilizada como fonte principal dos registros de propriedade intelectual do módulo.

### 7.2 Modalidades

Investigar as modalidades efetivamente disponibilizadas na base, incluindo, quando existentes:

- Patentes de invenção;
- Modelos de utilidade;
- Programas de computador;
- Marcas;
- Desenhos industriais;
- Indicações geográficas;
- Outras modalidades.

A seleção definitiva deve respeitar os arquivos e os campos disponíveis.

### 7.3 Informações a investigar

Inspecionar:

- Identificador original;
- Título;
- Tipo de PI;
- Número do processo;
- Data de depósito;
- Data de publicação;
- Situação;
- Depositantes;
- Titulares;
- Inventores;
- Autores;
- Instituições relacionadas.

Não presumir que todos os campos estejam disponíveis para todas as modalidades.

### 7.4 Procedimento

1. Obter a versão da BADEPI utilizada.
2. Registrar a data de extração.
3. Inspecionar os arquivos.
4. Identificar as tabelas e relacionamentos.
5. Identificar os campos de identificação.
6. Padronizar as modalidades de PI.
7. Normalizar datas e identificadores.
8. Separar registros principais e participantes.
9. Relacionar instituições e pesquisadores quando houver correspondência confiável.
10. Carregar os registros validados.

### 7.5 Regras de correspondência

Um registro de PI pode envolver:

- Um ou mais titulares;
- Um ou mais depositantes;
- Um ou mais inventores;
- Um ou mais autores.

Não duplicar o registro de PI para representar seus participantes.

Utilizar as entidades associativas PI_INSTITUICAO e PI_PESQUISADOR.

Diferenciar os papéis dos participantes.

Não associar automaticamente uma PI ao NIT da instituição relacionada.

### 7.6 Limitações

Os registros da BADEPI podem apresentar identificadores ou nomenclaturas diferentes das fontes de pesquisadores e instituições.

A correspondência entre as fontes deve ser realizada com critérios explícitos.

Correspondências duvidosas devem ser mantidas para validação.

### 7.7 Escopo

Transferência de Tecnologia, contratos e licenciamentos estão fora do MVP.

Não desenvolver pipelines dessas categorias nesta versão.

## 8. Fonte: Observatório/SIMCC — Territórios de Identidade

### 8.1 Finalidade

Utilizar os dados territoriais disponíveis no Observatório/SIMCC para construir a referência geográfica do módulo.

### 8.2 Informações esperadas

Investigar:

- Identificador do município;
- Código IBGE;
- Nome do município;
- Nome do Território de Identidade;
- Código do território, quando disponível.

### 8.3 Procedimento

1. Obter os dados territoriais.
2. Identificar a estrutura de municípios.
3. Identificar a estrutura dos Territórios de Identidade.
4. Verificar os identificadores.
5. Normalizar nomes.
6. Validar o relacionamento município-território.
7. Preparar a carga das tabelas de referência.

### 8.4 Regras

Cada município deve estar associado a um Território de Identidade validado.

Utilizar o código IBGE como principal referência de correspondência municipal.

Não realizar atribuições territoriais apenas com base na semelhança dos nomes.

A relação territorial deve permitir que instituições e unidades institucionais sejam contextualizadas geograficamente.

## 9. IA como ferramenta auxiliar

A inteligência artificial poderá auxiliar nas atividades de descoberta e tratamento de informações.

Usos permitidos:

- Localizar informações institucionais;
- Identificar possíveis NITs;
- Extrair informações de documentos;
- Organizar dados preliminares;
- Sugerir correspondências;
- Auxiliar na normalização.

Restrições:

- Não considerar resultados da IA como fonte oficial;
- Não criar informações ausentes;
- Não confirmar relacionamentos sem evidência;
- Não carregar registros não verificados como dados definitivos;
- Não descartar registros com base exclusivamente em uma decisão automatizada.

Quando a IA sugerir uma correspondência, registrar a situação como pendente de validação, quando necessário.

## 10. Matriz de mapeamento das fontes

Para cada fonte, manter um registro contendo:

| Campo | Descrição |
|---|---|
| nome_fonte | Nome da origem |
| categoria | NIT, instituição, pesquisador, PI ou território |
| endereco | URL ou referência |
| formato | CSV, XLSX, PDF, JSON, API etc. |
| data_obtencao | Data de obtenção |
| periodo_referencia | Período coberto |
| identificadores | Chaves disponíveis |
| campos_disponiveis | Informações presentes |
| cobertura | Instituições ou registros abrangidos |
| limitacoes | Restrições e lacunas |
| situacao | Identificada, obtida, inspecionada ou validada |

## 11. Qualidade e procedência

Toda informação carregada deve preservar, sempre que possível:

- Fonte de origem;
- Identificador original;
- Data de extração;
- Período de referência;
- Lote de importação;
- Situação da validação.

Não converter ausência de dados em zero.

Não misturar informações históricas e atuais sem identificar seus respectivos períodos.

Não substituir registros válidos por informações menos confiáveis.

## 12. Pendências de validação

As seguintes questões permanecem abertas:

### DATANIT
- Qual versão será utilizada?
- Quais campos estão efetivamente disponíveis?
- Qual é a cobertura dos NITs baianos?

### Relatórios dos NITs
- Quais instituições enviarão os documentos?
- Quais formatos serão encontrados?
- Qual é o período de referência de cada relatório?
- Existe padronização entre os documentos?

### Instituições
- Qual será a fonte de referência definitiva?
- Quais identificadores poderão ser utilizados?
- Existem informações sobre campi e unidades?

### SIMCC
- Qual formato será disponibilizado?
- Quais identificadores existem?
- Como os vínculos institucionais são representados?
- Qual é a cobertura dos pesquisadores?

### BADEPI
- Qual versão será utilizada?
- Quais modalidades estarão disponíveis?
- Como estão representados titulares, depositantes, inventores e autores?
- Quais identificadores permitem integração?

### Territórios
- Qual arquivo será utilizado como referência?
- Existe código para os territórios?
- Os códigos IBGE estão disponíveis?
- Como serão tratados municípios com dados incompletos?

## 13. Evolução das fontes

Novas fontes poderão ser incorporadas futuramente.

Toda inclusão deve exigir:

1. Justificativa;
2. Identificação da categoria de informação;
3. Inspeção da estrutura;
4. Avaliação da confiabilidade;
5. Definição de identificadores;
6. Mapeamento dos campos;
7. Definição das transformações;
8. Definição das regras de carga;
9. Atualização da documentação.

Não implementar integrações futuras sem que sua utilização seja aprovada no escopo do projeto.
