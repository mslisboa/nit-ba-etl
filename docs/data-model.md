
# Modelo de Dados — ETL

## 1. Objetivo

Este documento descreve o modelo conceitual de dados utilizado pelo módulo de integração estadual dos NITs da Bahia, com foco nas necessidades dos processos de ETL.

O objetivo é estabelecer as entidades, atributos, relacionamentos, cardinalidades e regras de integração que devem orientar a transformação e a carga dos dados no PostgreSQL.

Este documento representa o modelo de referência do projeto.

A implementação física das tabelas e suas migrações são responsabilidade do repositório `nit-ba-backend`.

O ETL deve respeitar os contratos definidos pelo backend.

## 2. Escopo do modelo

O modelo contempla as seguintes dimensões:

- NITs;
- Instituições/ICTs;
- Unidades institucionais;
- Pesquisadores;
- Propriedade Intelectual;
- Municípios;
- Territórios de Identidade;
- Fontes de dados;
- Lotes de importação.

Não fazem parte do modelo atual:

- Transferência de Tecnologia;
- Contratos e licenciamentos;
- PROFNIT;
- Estruturas de inovação além dos NITs;
- Incubadoras e parques tecnológicos;
- Equipe dos NITs;
- Anúncios e eventos.

Essas dimensões poderão ser incorporadas futuramente.

## 3. Entidades principais

### 3.1 NIT

Representa um Núcleo de Inovação Tecnológica identificado no estado da Bahia.

Atributos conceituais:

| Campo | Descrição |
|---|---|
| id_nit | Identificador interno |
| nome | Nome oficial |
| sigla | Sigla, quando existente |
| descricao | Descrição resumida |
| site | Site institucional |
| email | Contato institucional público |
| situacao | Situação do NIT |
| data_atualizacao | Data da última atualização |
| id_instituicao | Instituição relacionada |

Cada NIT deve estar associado a exatamente uma instituição.

A instituição correspondente deve ser identificada antes da carga definitiva.

Se não for possível identificar com segurança a instituição de um NIT, o registro deverá permanecer pendente de validação.

### 3.2 Instituição

Representa universidades, institutos, centros de pesquisa e outras ICTs relacionadas ao ecossistema de inovação da Bahia.

Atributos conceituais:

| Campo | Descrição |
|---|---|
| id_instituicao | Identificador interno |
| nome | Nome oficial |
| sigla | Sigla |
| natureza | Pública ou privada |
| tipo | Universidade, instituto, centro de pesquisa etc. |
| site | Site institucional |
| descricao | Descrição institucional |

Uma instituição pode existir no banco sem que um NIT tenha sido identificado.

Cada instituição poderá estar associada a, no máximo, um NIT no modelo atual.

### 3.3 Unidade Institucional

Representa campi, unidades de pesquisa e outras instalações vinculadas a uma instituição.

Atributos:

| Campo | Descrição |
|---|---|
| id_unidade | Identificador |
| id_instituicao | Instituição responsável |
| nome | Nome da unidade |
| tipo | Campus, unidade de pesquisa etc. |
| endereco | Endereço, quando disponível |
| id_municipio | Município de localização |

A inclusão dessa entidade depende da disponibilidade de dados suficientemente detalhados.

Não criar unidades fictícias para preencher lacunas.

### 3.4 Pesquisador

Representa pesquisadores identificados nas fontes do Observatório/SIMCC.

Atributos:

| Campo | Descrição |
|---|---|
| id_pesquisador | Identificador interno |
| nome | Nome completo |
| id_simcc | Identificador na fonte |
| id_lattes | Identificador Lattes, quando disponível |
| orcid | Identificador ORCID, quando disponível |
| area_atuacao | Área de atuação |

Não armazenar CPF ou outros dados pessoais desnecessários.

### 3.5 Propriedade Intelectual

Representa registros de propriedade intelectual provenientes principalmente da BADEPI.

Atributos:

| Campo | Descrição |
|---|---|
| id_pi | Identificador interno |
| titulo | Título do registro |
| tipo_pi | Modalidade da propriedade intelectual |
| numero_processo | Número do processo ou registro |
| data_deposito | Data do depósito |
| data_publicacao | Data de publicação |
| situacao | Situação do registro |
| descricao | Descrição, quando disponível |
| identificador_badepi | Identificador original da BADEPI |

As modalidades devem respeitar a classificação efetivamente fornecida pela fonte.

Possíveis categorias:

- Patente de invenção;
- Modelo de utilidade;
- Programa de computador;
- Marca;
- Desenho industrial;
- Indicação geográfica;
- Outras modalidades disponibilizadas pela BADEPI.

Não criar campos específicos sem antes inspecionar a estrutura real da fonte.

### 3.6 Município

Representa os municípios da Bahia.

Atributos:

| Campo | Descrição |
|---|---|
| id_municipio | Identificador interno |
| codigo_ibge | Código IBGE |
| nome | Nome do município |
| uf | Unidade federativa |

O código IBGE deve ser utilizado como identificador de integração sempre que disponível.

### 3.7 Território de Identidade

Representa os Territórios de Identidade da Bahia.

Atributos:

| Campo | Descrição |
|---|---|
| id_territorio | Identificador interno |
| nome | Nome do território |
| codigo | Código de referência, quando disponível |
| descricao | Descrição |

Cada município deve ser relacionado ao seu respectivo Território de Identidade conforme a referência territorial validada.

## 4. Entidades associativas

### 4.1 PESQUISADOR_INSTITUICAO

Resolve o relacionamento N:N entre pesquisadores e instituições.

Atributos:

| Campo | Descrição |
|---|---|
| id_vinculo | Identificador |
| id_pesquisador | Pesquisador |
| id_instituicao | Instituição |
| id_unidade | Unidade, quando identificada |
| tipo_vinculo | Tipo de vínculo |
| vinculo_principal | Indicador de vínculo principal, quando disponível |
| data_inicio | Início do vínculo |
| data_fim | Fim do vínculo |

Um pesquisador pode possuir vínculos com diferentes instituições.

Não presumir que todos os vínculos sejam atuais.

### 4.2 PI_INSTITUICAO

Resolve o relacionamento N:N entre propriedade intelectual e instituições.

Atributos:

| Campo | Descrição |
|---|---|
| id_pi_instituicao | Identificador |
| id_pi | Propriedade intelectual |
| id_instituicao | Instituição |
| papel | Papel da instituição no registro |

O papel deve preservar a classificação da fonte, quando disponível.

Exemplos:

- Depositante;
- Titular;
- Outro papel identificado.

Não confundir a instituição depositante com a instituição onde o pesquisador trabalha atualmente.

### 4.3 PI_PESQUISADOR

Resolve o relacionamento N:N entre propriedade intelectual e pesquisadores.

Atributos:

| Campo | Descrição |
|---|---|
| id_pi_pesquisador | Identificador |
| id_pi | Propriedade intelectual |
| id_pesquisador | Pesquisador |
| papel | Papel do pesquisador no registro |

Exemplos:

- Inventor;
- Autor;
- Criador;
- Outro papel identificado.

Não associar automaticamente uma pessoa a um registro de PI somente pela semelhança do nome.

### 4.4 NIT_PI

Relacionamento opcional entre NIT e propriedade intelectual.

Atributos:

| Campo | Descrição |
|---|---|
| id_nit_pi | Identificador |
| id_nit | NIT relacionado |
| id_pi | Propriedade intelectual |
| tipo_relacionamento | Natureza do relacionamento |
| fonte | Origem da informação |

A associação somente deve ser criada quando existir evidência de que o NIT gerenciou, acompanhou ou participou do processo relacionado à PI.

A simples associação entre uma PI e uma instituição não comprova a participação do NIT correspondente.

## 5. Cardinalidades

| Relacionamento | Cardinalidade |
|---|---|
| Instituição — NIT | 1:1 |
| Instituição — Unidade Institucional | 1:N |
| Município — Unidade Institucional | 1:N |
| Território — Município | 1:N |
| Instituição — Pesquisador | N:N |
| Instituição — PI | N:N |
| Pesquisador — PI | N:N |
| NIT — PI | N:N, opcional |

### 5.1 Regra NIT–Instituição

Esta regra é obrigatória:

- Cada NIT deve estar relacionado a exatamente uma instituição.
- Cada instituição pode estar relacionada a, no máximo, um NIT.
- Uma instituição sem NIT identificado pode permanecer cadastrada.

No banco:

NIT.id_instituicao deve ser:

- Foreign Key;
- NOT NULL;
- UNIQUE.

Não criar a entidade associativa NIT_INSTITUICAO.

Se a fonte apresentar um relacionamento incompatível, registrar a inconsistência e encaminhar para revisão.

Não descartar nem alterar silenciosamente os registros.

## 6. Modelo territorial

A associação territorial deve seguir a estrutura:

Território de Identidade
    -> Município
        -> Unidade Institucional
            -> Instituição

Quando uma unidade institucional não estiver disponível, poderá ser utilizada a localização da instituição, desde que essa localização seja conhecida e corretamente classificada.

Regras:

- Utilizar código IBGE para municípios.
- Não relacionar município a território apenas por semelhança textual.
- Não utilizar o município de uma sede como localização automática de todos os campi.
- Não presumir que o município institucional seja a residência de um pesquisador.
- Não atribuir o território de uma unidade a todas as unidades da instituição.

A PI poderá envolver instituições de diferentes territórios.

Indicadores territoriais devem explicitar os critérios de atribuição e evitar duplicações indevidas.

## 7. Identificação e integração de registros

### 7.1 Instituições

Priorizar:

- Identificadores oficiais;
- CNPJ, quando disponível e aplicável;
- Identificadores institucionais das fontes;
- Siglas;
- Nomes oficiais.

Variações textuais devem ser normalizadas.

Não considerar nomes como identificadores únicos.

### 7.2 Pesquisadores

Priorizar:

- id_simcc;
- id_lattes;
- orcid.

Nomes devem ser utilizados como informação complementar.

### 7.3 Propriedade Intelectual

Priorizar:

- identificador_badepi;
- numero_processo;
- tipo_pi.

A combinação de número de processo e modalidade poderá servir como critério adicional quando a fonte não fornecer identificador único confiável.

### 7.4 Municípios

Priorizar código IBGE.

### 7.5 NITs

Preservar os identificadores da DATANIT ou dos relatórios de origem.

A instituição relacionada deve ser identificada por correspondência validada.

## 8. Tratamento de duplicações

Os processos de ETL devem identificar registros repetidos.

A identificação deve utilizar os identificadores originais e regras específicas para cada entidade.

Não utilizar somente:

- Nome do NIT;
- Nome da instituição;
- Nome do pesquisador;
- Título da PI.

Para registros de PI com vários inventores ou instituições:

- Manter um registro principal na tabela de PI;
- Registrar os relacionamentos em tabelas associativas;
- Não duplicar o ativo de PI para cada participante.

## 9. Procedência dos registros

Todo registro importado deve preservar sua origem.

Dados de procedência:

- Fonte;
- Identificador original;
- Lote de importação;
- Data de extração;
- Período de referência;
- Situação da validação.

A implementação pode utilizar referências diretas ao lote de importação e à fonte no registro canônico.

Quando uma entidade puder ter múltiplas origens, avaliar uma estrutura de associação entre registros e fontes.

## 10. Fonte de Dados e Lote de Importação

### FONTE_DADOS

Representa as origens das informações.

Campos previstos:

- id_fonte;
- nome;
- categoria;
- endereco;
- descricao.

### LOTE_IMPORTACAO

Representa cada execução.

Campos previstos:

- id_importacao;
- id_fonte;
- data_execucao;
- periodo_referencia;
- arquivo_origem;
- situacao.

A estrutura física definitiva deve ser coordenada com o backend.

## 11. Dicionário de dados e contratos

O ETL deve documentar para cada fonte:

- Campo original;
- Campo de destino;
- Tipo original;
- Tipo de destino;
- Regra de transformação;
- Obrigatoriedade;
- Regra de validação;
- Identificador utilizado.

Não presumir que os campos da fonte correspondam diretamente aos atributos do modelo canônico.

O mapeamento deve ser baseado na inspeção dos arquivos reais.

## 12. Valores ausentes

Diferenciar:

- Zero: ausência confirmada pela fonte;
- Não informado: informação não apresentada;
- Não disponível: informação não obtida;
- Não aplicável: campo que não se aplica ao registro.

Não preencher valores ausentes com valores fictícios.

## 13. Limitações conhecidas

As seguintes informações dependem de validação:

- Identificadores disponíveis na DATANIT;
- Identificação institucional dos NITs;
- Correspondência de pesquisadores entre SIMCC e BADEPI;
- Representação de múltiplos titulares;
- Representação de múltiplos inventores;
- Disponibilidade de unidades institucionais;
- Padronização dos códigos territoriais;
- Campos efetivamente fornecidos pelas fontes.

## 14. Evolução do modelo

O modelo apresentado é a referência conceitual do MVP.

Mudanças nas cardinalidades ou entidades devem ser documentadas e justificadas.

O modelo lógico e físico devem acompanhar as características reais das fontes e os contratos definidos pelo backend.

Não implementar entidades ou atributos sem necessidade demonstrada.
