# Plano: pipeline nativo Snowflake cobrindo os objetos do schema

> Objetivo: não é só carregar dado, é usar deliberadamente o maior número de
> objetos do Snowflake que tiver um papel real no pipeline ANAC, como veículo
> de estudo para o SnowPro Core e para o roadmap de engenharia de dados (ver
> `okr_bruno_azul`, `CARREIRA_estrategia_e_linkedin.md` em
> `serminaro-governance/trabalho`). Onde um objeto não tem encaixe honesto no
> problema, isso fica registrado como tal, não forçado só para preencher a
> lista.
>
> Escopo: schema `ANAC.BASICA`, warehouse `wh_anac`. Este documento é o plano;
> a implementação vira scripts novos em `scripts/`, numerados na sequência dos
> já existentes (`10_...` em diante).

---

## Estado atual (2026-08-01)

| Objeto | Nome | Papel hoje |
|---|---|---|
| Table | `BASICA_RAW` | Camada raw, 111 colunas TEXT, carga via `09_snowflake_copy_merge.sql` |
| View | `BASICA_TYPED` | Casts corretos, `partida_ts`/`chegada_ts`, `bloco_tempo_min` |
| API Integration | `ANAC_GITHUB_INTEGRATION` | Allowlist para o Git Repository |
| Git Repository | `learn_microdados_anac_dados` | Espelho do repositório, fonte de verdade versionada |
| Warehouse | `wh_anac` | Compute isolado deste domínio |

---

## Camadas propostas

### Camada 0 — Ingestão automatizada

| Objeto | Papel | Justificativa (não forçado) |
|---|---|---|
| **File Format** | `anac_basica_csv_ff`, nomeando o parsing (delimitador, encoding Latin-1) hoje implícito nos scripts | Formaliza o que já existe; elimina repetição da definição em cada `COPY INTO` |
| **Stage** | `anac_basica_stage`, interno, recebendo os `.txt` extraídos antes da carga | Já é usado de fato via `PUT`/`COPY INTO`; só nunca foi criado como objeto nomeado fora do script |
| **Pipe** | `anac_basica_pipe`, auto-ingest disparado por chegada de arquivo no stage | Encaixe real, não forçado: a ANAC publica **um arquivo por mês**, evento discreto, exatamente o padrão que Snowpipe resolve. Diferente do Snowpipe *Streaming* (linha a linha), que eu já descartei antes por não bater com a cadência mensal. |

### Camada 1 — Raw + captura de mudança

| Objeto | Papel |
|---|---|
| Table `BASICA_RAW` | Já existe, sem mudança de schema |
| **Stream** `basica_raw_stream` | Rastreia quais linhas chegaram desde a última leitura, para a camada seguinte processar só o incremento, não a tabela inteira |

### Camada 2 — Orquestração

| Objeto | Papel |
|---|---|
| **Procedure** `sp_merge_basica(mes_referencia)` | Encapsula a lógica hoje espalhada em `07/08/09`: `COPY INTO` + `MERGE` idempotente, parametrizada por mês |
| **Task** `task_ingest_basica` | Disparada pelo Pipe/Stream (`WHEN SYSTEM$STREAM_HAS_DATA(...)`), chama a Procedure |
| **Task** `task_refresh_marts` | Encadeada após `task_ingest_basica` (DAG de duas tasks), atualiza a camada dimensional da Camada 3 |

Este par Stream + Task + Procedure é a peça central: fecha o gancho de
orquestração/CI-CD discutido antes, tudo nativo, sem depender de Airflow.

### Camada 3 — Modelagem dimensional

| Objeto | Papel |
|---|---|
| **Sequence** `seq_dim_aeronave`, `seq_dim_aeroporto`, `seq_dim_empresa` | Chaves substitutas para as tabelas de dimensão do star schema (ver `GUIDE_002_datasets_e_projetos_portfolio.md`: fato voo + dimensões Companhia/Aeroporto/Data/Rota/Aeronave) |
| Table (dimensões) | `DIM_AERONAVE`, `DIM_AEROPORTO`, `DIM_EMPRESA`, `DIM_TEMPO`, populadas pela Procedure/Task acima |
| **Dynamic Table** `fato_voo_dt` | Substitui o padrão view-recalculada-toda-hora do `BASICA_TYPED` por uma tabela materializada com `TARGET_LAG` declarado, alimentando o fato de voo já com os casts e joins às dimensões |
| **Function** (Snowpark Python UDF) `f_categoriza_bloco_tempo` ou similar | Regra de negócio reutilizável (ex.: categorizar duração de voo, ou decodificar prefixo de matrícula de aeronave) chamável em SQL, mas escrita em Python — ponte com o horizonte de 6-24 meses (Snowpark) |

### Camada 4 — Consumo / semântica

| Objeto | Papel |
|---|---|
| **Semantic View** `sv_operacao_basica` | Mapeia o star schema para métricas de negócio (ASK, RPK, ATK, RTK, % pontualidade), o mesmo conceito de modelo do PL-300, mas declarado dentro do Snowflake, reutilizável por Cortex Analyst e potencialmente por BI externo |
| View `BASICA_TYPED` | Mantida como ponto de acesso ad hoc simples, não substituída, só deixa de ser a única camada de consumo |

### Camada 5 — Governança

| Objeto | Papel | Honestidade sobre escala |
|---|---|---|
| **Contact** | Associado à Task e à `BASICA_RAW`, indicando quem notificar em falha de carga | Em conta trial solo isso é exercício de sintaxe, não necessidade operacional real; documentado como tal, é o seu diferencial (governança) praticado em miniatura |
| **Cortex Search Service** *(opcional, stretch)* | Busca em linguagem natural sobre um **dicionário de dados** (nome de coluna → descrição, extraído da documentação oficial da ANAC), não sobre os dados de voo em si | Único jeito honesto de encaixar esse objeto: dado de voo é estruturado, não texto. Um dicionário de campos É texto. Sem esse corpus, não vale forçar o objeto só para aparecer na lista. |

---

## Objetos deliberadamente fora do plano

| Objeto | Motivo |
|---|---|
| **Interactive Table** | Incerteza minha sobre a definição exata/sobreposição com Hybrid Table (workload OLTP de baixa latência). Não bate com o padrão analítico em lote deste projeto de qualquer forma; confirmar na documentação antes de reconsiderar. |
| **Image Repository** | Depende de Snowpark Container Services, que é o horizonte de 18-36 meses (ML/otimização), não o momento atual. |

---

## Ordem de implementação sugerida

1. **Fase A** — File Format + Stage nomeados, substituindo o que hoje é implícito no script `09`.
2. **Fase B** — Procedure `sp_merge_basica` encapsulando a lógica de `COPY INTO` + `MERGE`.
3. **Fase C** — Stream + Task disparando a Procedure (fecha o pipeline nativo de ingestão).
4. **Fase D** — Sequence + tabelas de dimensão + Dynamic Table do fato (star schema).
5. **Fase E** — Function Snowpark para a primeira regra de negócio.
6. **Fase F** — Semantic View sobre o star schema.
7. **Fase G** (opcional) — Pipe com auto-ingest real (exige stage externo com notificação de evento do provedor de nuvem) e Contact.
8. **Fase H** (stretch, opcional) — Cortex Search Service sobre o dicionário de dados.

Cada fase vira um ou mais scripts `.sql`/`.py` numerados em `scripts/`, versionados
via o Git Repository já configurado na conta.

---

## Mapa objeto → domínio SnowPro Core

| Domínio do exame (aproximado, confirmar blueprint oficial) | Objetos praticados |
|---|---|
| Arquitetura da plataforma | Table, View, Dynamic Table, Warehouse |
| Carga e descarga de dados | Stage, File Format, Pipe, Stream |
| Transformação de dados | Task, Procedure, Function, Sequence |
| Proteção e compartilhamento de dados | Contact, API Integration, Git Repository |
