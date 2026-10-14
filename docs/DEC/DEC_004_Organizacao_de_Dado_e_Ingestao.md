---
documento: DEC-004
titulo: Organização de dado em SQLite e separação física de ingestão por engine
versao: v2
status: aprovado
data: 2026-10-14
autor: Bruno Alexandre Serminaro
referencia: REP-001, SPEC-002
escopo: projeto
---

# DEC-004 · Organização de dado e ingestão

> DEC de conteúdo, retroativa: formaliza D4 e D7 do REP-001 — um banco
> SQLite por dataset e separação física de ingestão SQLite/Snowflake —
> decisões técnicas já implementadas no repositório desde 2026-08-24, sem
> DEC própria até este momento. Produzida por achado do `gov-check`
> (`AUDIT-001`, R-FUN-06), no padrão de "DEC retroativa de regularização"
> que a própria taxonomia prevê (DEC-META-014 §2.5).

---

## 1. Contexto

O REP-001 (§4) registrou D4 (um banco SQLite por dataset, convenção de
nomenclatura por prefixo) e D7 (ingestão SQLite e Snowflake fisicamente
separadas) como decisões já tomadas na sessão de 2026-08-24, mas de
natureza diferente de D1-D3: são arquitetura técnica de dado, não escopo
do produto. Por isso o próprio REP-001 já apontava que não deveriam entrar
no DEC-002 (que fecha as escolhas de escopo/critério de sucesso do
SPEC-002), e sim numa DEC de conteúdo dedicada — sem fixar quando.

O `gov-check` (`AUDIT-001`, 2026-08-25) confrontou a regra R-FUN-06 do
SPEC-002 ("decisão arquitetural não-trivial tem DEC com rastro a artefato
concreto") contra o estado real e encontrou a lacuna: `sql/ingestao_sqlite/`,
`sql/ingestao_snowflake/`, `src/ingestao_sqlite/`, `src/ingestao_snowflake/`
já existem e estão em uso (commit `f7f116e`, 2026-08-24), mas nenhuma DEC
os registra. O autor escolheu fechar a lacuna agora (caminho "2b" da
auditoria), em vez de manter como pendência registrada.

---

## 2. Decisão

**Adotar formalmente a organização de dado já implementada: um banco
SQLite por dataset, e ingestão SQLite/Snowflake fisicamente separadas em
`src/`/`sql/`, com download bruto e preparação comum permanecendo únicos.**

---

## 3. Origem ou rastro

- `REP-001 §4` (D4, D7): texto original das duas decisões, tomadas em
  2026-08-24.
- `docs/plano_expansao_multidataset.md §4`: análise das três alternativas
  de organização de SQLite (banco único, banco por dataset, banco por
  dataset por camada), com a recomendação B já registrada ali.
- Commit `f7f116e` (2026-08-24, "Reorganiza pipeline por papel e engine,
  expande plano para 3 datasets ANAC"): estado real do repositório onde
  D4/D7 já estão implementados.
- `gov-check AUDIT-001` (2026-08-25): achado R-FUN-06 que motivou fechar
  esta lacuna agora.

---

## 4. Alternativas consideradas

### 4.1 Organização do SQLite: um banco único com tabelas prefixadas

`anac.sqlite` com `basica_raw`, `vra_raw`, `siros_raw`, etc.

**Por que descartada.** JOIN entre datasets sem `ATTACH DATABASE`, mas um
arquivo só cresce muito — SIROS sozinho, diário desde 2019, tem potencial
de dezenas de milhões de linhas (hipótese candidata, REP-001 §5.2) — e um
dataset problemático (corrupção, bug de carga) arrisca o banco inteiro
(`docs/plano_expansao_multidataset.md §4`).

### 4.2 Organização do SQLite: um banco por dataset por camada

Separar também raw de ouro dentro de cada dataset, espelhando o medalhão
do Snowflake.

**Por que descartada.** Overhead desnecessário no volume atual — mais
arquivos para gerenciar, mais um nível de indireção, sem que o volume de
cada camada individual justifique ainda a separação.

### 4.3 Ingestão: manter Básica/VRA/SIROS num só `src/`/`sql/` sem separação por engine

Não separar fisicamente a ingestão SQLite da ingestão Snowflake; manter os
scripts de carga juntos, diferenciados só pelo nome do arquivo.

**Por que descartada.** Pedido explícito do autor (sessão de 2026-08-24):
"os script de ingestão SQLite e snowflake quero que fiquem separados e
identificados". Manter junto dificulta localizar rapidamente o que é
específico de cada caminho de produção, justamente quando os dois caminhos
passaram a ser igualmente investidos (D2).

### 4.4 Um banco por dataset + ingestão fisicamente separada por engine (decisão atual)

`db/anac_basica.sqlite`, `db/anac_vra.sqlite`, `db/anac_siros.sqlite`
(com `ATTACH DATABASE` para cruzar); `src/ingestao_sqlite/`,
`src/ingestao_snowflake/`, `sql/ingestao_sqlite/`, `sql/ingestao_snowflake/`
para o que é específico de cada engine, com download bruto (`scripts/`) e
preparação comum (`src/SRC_001_basica_extract_validate.py`,
`src/SRC_002_basica_build_schema.py`, os antigos `src/02` e `src/03`
renomeados pela `DEC-005`) permanecendo únicos.

**Adotada.** Já implementada e em uso desde 2026-08-24; esta DEC só fecha
o rastro que faltava, sem mudar o estado real do repositório.

---

## 5. Consequências

### 5.1 Positivas

- Fecha o achado R-FUN-06 do `gov-check AUDIT-001`: decisão arquitetural
  não-trivial passa a ter DEC com rastro.
- Isolamento por dataset reduz o risco de um dataset problemático (volume,
  corrupção) afetar os outros.
- Localização rápida do que é específico de cada engine, sem navegar
  scripts misturados.

### 5.2 Negativas

- **Cruzar dados entre datasets exige `ATTACH DATABASE`** nas queries —
  não é JOIN direto como seria num banco único. Aceito: o ganho de
  isolamento supera o custo de sintaxe extra, mas é custo real, não zero.
- **Mais pastas para gerenciar** (`src/ingestao_sqlite/`,
  `src/ingestao_snowflake/`, espelho em `sql/`) do que uma estrutura
  plana teria. Aceito como o preço da identificação clara pedida pelo
  autor.
- **Esta DEC é retroativa**: registra uma decisão já em produção, não uma
  decisão prévia à implementação — ordem invertida em relação ao padrão
  decisão-primeiro que o resto da fundação seguiu. Aceito porque a
  DEC-META-014 §2.5 prevê exatamente esse caso (regularização por
  oportunidade), mas é honesto reconhecer que não é o fluxo ideal.

### 5.3 O que esta decisão não resolve

- **Não decide a convenção de nome de arquivo** dentro de cada pasta — já
  é o DEC-001 §6.6 (`TIPO_NNN_descricao_curta`, prospectiva).
- **Não decide como VRA e SIROS são carregados.** A estrutura de pastas
  os recebeu sem ajuste em 2026-08-31; a carga em si é a `DEC-008`.
- **Não decide as camadas dentro de cada banco.** Elas nasceram depois,
  como views silver (`sql/tratamento/`, `DEC-008`) e tabelas curated
  (`sql/curated_deep/`, `DEC-007` e `SPEC-012`), dentro dos bancos por
  dataset. Isso é compatível com o descarte da alternativa 4.2, que
  separava camada em arquivo próprio, não em objeto dentro do mesmo banco.
- **Não revisita a alternativa C** (banco por dataset por camada) — fica
  disponível como critério de reavaliação (§6) se o volume crescer o
  bastante para justificar.

---

## 6. Critérios de reavaliação

Esta decisão deve ser revisitada se:

- Cruzar dados entre datasets (via `ATTACH DATABASE`) virar operação
  frequente o bastante para que o custo de sintaxe supere o benefício do
  isolamento — sinal para reconsiderar a alternativa 4.1. Estado em
  2026-10-14: um uso, em `sql/curated_deep/DDL_004` (block time, Básica ×
  VRA).
- O volume real de algum dataset justificar separar também por camada —
  sinal para reconsiderar a alternativa 4.2. Estado em 2026-10-14: SIROS,
  que o REP-001 §5.2 apontava como o maior risco, ficou em 10.677.382
  linhas e 4,9 GB (`SPEC-010`); o maior banco é a Básica, com 19,7 GB.
- A convenção de pastas se mostrar confusa na prática ao adicionar VRA ou
  SIROS.

---

## 7. Histórico

| Data | Evento |
|---|---|
| 2026-08-25 | DEC-004 produzida em status `proposto`, retroativa: formaliza D4 e D7 do REP-001 (2026-08-24), já implementados no repositório (commit `f7f116e`). Origem: achado R-FUN-06 do `gov-check AUDIT-001`, resolvido pelo autor via caminho "2b" (produzir a DEC agora). Quatro alternativas avaliadas. Aguardando revisão do autor antes de aprovar. |
| 2026-10-14 | **v2, fatos atualizados, decisão inalterada.** Dívida M3 do `AUDIT-002`. Nomes dos bancos (`db/anac_<dataset>.sqlite`) e dos scripts de preparação (renomeados pela `DEC-005`) corrigidos no §4.4; §5.3 deixa de dizer que VRA e SIROS não têm scripts (têm desde a `DEC-008`) e passa a registrar que as camadas silver e curated nasceram dentro dos bancos por dataset; §6 recebe o estado medido dos dois critérios de reavaliação (um uso de `ATTACH`; volumes reais). Nenhuma alternativa, escolha ou critério muda. |
| 2026-10-14 | **Aprovada pelo autor** (Bruno Alexandre Serminaro), na v2. Fecha a dívida M3 do `AUDIT-002`: a `DEC-008`, aprovada, deixa de se apoiar numa DEC em proposta. A IA de apoio redigiu a v2 e não aprova (`SPEC-003 §3.2`). |

---

*Fim do documento.*
