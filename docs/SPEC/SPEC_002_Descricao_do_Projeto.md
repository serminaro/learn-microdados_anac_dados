---
documento: SPEC-002
titulo: Descrição do Projeto learn-microdados_anac_dados
versao: v1
status: aprovado
data: 2026-08-24
autor: Bruno Alexandre Serminaro
referencia: DEC-002, REP-001
escopo: projeto
---

# SPEC-002 · Descrição do Projeto learn-microdados_anac_dados

> Declara o que o projeto **learn-microdados_anac_dados** se compromete a
> entregar: propósito, audiência, escopo, decomposição do produto,
> critérios de sucesso, premissas e não-objetivos. É a peça contra a qual
> se afere se o projeto entregou o que prometeu, materializando o que o
> **DEC-002** fixou a partir do acúmulo do **REP-001**.

---

## 1. Propósito

Consolidar os microdados públicos de tráfego aéreo da ANAC — **Básica**,
**VRA** e **SIROS** — em dois caminhos de produção completos e igualmente
investidos (Snowflake em arquitetura medalhão; SQLite+Python), cobrindo
2010-presente onde a fonte permite, como veículo deliberado de estudo de
engenharia de dados (competência Snowflake/SnowPro Core, modelagem,
Python/SQL/Jupyter) e como peça de portfólio público.

---

## 2. Audiência

Papéis abstratos; atribuição de pessoa é matéria da futura SPEC-003
(ainda não escrita).

| Papel | Função frente a esta SPEC |
|---|---|
| **Autor** | Produz, decide, executa; responde pela aplicação dos critérios de sucesso. |
| **Par assistivo (IA de apoio)** | Apoia redação, pesquisa e implementação técnica, sem autoridade de aprovação — condição a confirmar formalmente na SPEC-003. |
| **Autor futuro** | Relê esta SPEC para retomar o projeto sabendo o que prometia entregar, sem depender da memória de uma sessão específica. |
| **Leitor do repositório** | Visitante do GitHub (incl. recrutador/par avaliando portfólio) que lê o `README.md` (BRIEF) e, se quiser profundidade, esta SPEC. |

Não há stakeholder externo com poder de decisão sobre o projeto: é
trabalho solo (REP-001 §1).

---

## 3. Escopo

### 3.1 O que o projeto entrega

Pipeline completo — **download bruto → ingestão → tratamento → camada
ouro → dashboard** — para os **3 datasets ANAC** (Básica, VRA, SIROS), nos
**2 caminhos de produção** (Snowflake medalhão; SQLite+Python), cobrindo
**2010-presente** onde a fonte permite:

1. **Download bruto** (`scripts/`), único e compartilhado pelos dois
   caminhos — não duplicado por engine (DEC-001 §6.6, REP-001 P2).
2. **Preparação comum** (`src/02_extract_validate.py`,
   `src/03_build_schema.py`) — extração, validação de consistência e
   geração de DDL, comuns aos dois caminhos.
3. **Ingestão específica de engine** (`src/ingestao_sqlite/`,
   `src/ingestao_snowflake/`, `sql/ingestao_sqlite/`,
   `sql/ingestao_snowflake/`) — carga em SQLite (um banco por dataset) e
   carga em Snowflake (stage/file format/MERGE), fisicamente separadas.
4. **Tratamento** (`sql/tratamento/`) — views tipadas, casts corretos, para
   as duas engines.
5. **Camada ouro** — star schema/métricas no Snowflake (Fases D-F do plano
   Snowflake, `docs/plano_objetos_snowflake.md`) e equivalente no caminho
   SQLite (a desenhar).
6. **Dashboard** — Power BI ou Looker Studio (caminho Snowflake); Streamlit
   (caminho SQLite).
7. **Documentação** sob `docs/` conforme SPEC-001: as peças de fundação, os
   dois planos técnicos pré-SERMI (`plano_objetos_snowflake.md`,
   `plano_expansao_multidataset.md`), e SPECs/DECs de conteúdo futuras.
8. **Jupyter Notebook** (`notebook/`) como ferramenta de exploração e
   tratamento comum aos dois caminhos, não um produto entregável por si só.

### 3.2 Fora de escopo

O projeto **não** se compromete a:

- **Processar o dataset Combinada.** Existe na mesma fonte que a Básica,
  nunca foi pedido (DEC-002 §6.1).
- **Reconstruir SIROS anterior a 2019-11.** A fonte não publica em lote
  antes disso — não é recorte de escopo, é limite real (REP-001 §5.1).
- **Usar linguagens de UDF/procedure nativas do Snowflake além de
  Python/Snowpark** (JavaScript, Java, Scala) — decisão do DEC-001 §6.6.
- **Integrar R a um dos dois pipelines de produção.** R fica como
  ferramenta complementar de análise, fora dos caminhos (DEC-001 §6.6).
- **Processar Básica/VRA além do corte de 2010**, mesmo a fonte tendo dado
  desde 2000 — escolha deliberada (DEC-002 §4.3), não limite técnico.

---

## 4. Decomposição do produto

O produto decompõe-se em duas dimensões que se cruzam: **datasets** (o que
é processado) e **caminhos** (como é processado). DEC-002 §6.4 já
descartou decompor só por caminho, pela diferença de cadência de origem
entre os datasets.

### 4.1 Matriz dataset × caminho

| | Caminho Snowflake (medalhão) | Caminho SQLite+Python |
|---|---|---|
| **Básica** | `sql/ingestao_snowflake/`, camadas raw→prata→ouro (Fases A-H, `docs/plano_objetos_snowflake.md`) | `sql/ingestao_sqlite/`, `src/ingestao_sqlite/`, banco `basica.sqlite` |
| **VRA** | A implementar, mesmo padrão de fases da Básica | A implementar |
| **SIROS** | A implementar; cadência diária reabre a Fase G (Pipe/Snowpipe) | A implementar; volume diário ainda não medido (REP-001 §5.2) |

### 4.2 Estrutura de pastas (código e dado)

```
scripts/                    download bruto, comum aos dois caminhos
src/                         preparação comum (extração, validação, schema)
  ingestao_sqlite/           carga específica SQLite
  ingestao_snowflake/        preparação específica para carga Snowflake
sql/
  ingestao_sqlite/            DDL raw SQLite
  ingestao_snowflake/         DDL raw Snowflake + DML de carga/orquestração
  tratamento/                  views tipadas, as duas engines
  analise/                     reservada, preparação analítica
notebook/                     exploração/tratamento, comum aos dois caminhos
r/                            análise complementar (a criar quando houver arquivo R)
db/                           bancos SQLite (um por dataset), gitignored
data/                         dado bruto/derivado, gitignored
```

Convenção de nomes de código-fonte (`TIPO_NNN_descricao_curta`,
BASH/SRC/DDL/DML/NOTE/R) é do DEC-001 §6.6, não desta SPEC.

---

## 5. Critérios de sucesso

Critério incremental (DEC-002 §6.2): sucesso parcial, por dataset e por
caminho, é sucesso real — não se exige a matriz completa para declarar
progresso. Critérios marcados **(provisório)** dependem de trabalho ainda
não iniciado e serão calibrados quando esse trabalho começar.

### 5.1 Básica estendida (dataset já em produção, extensão de escopo)

- **C-01** — `scripts/01_download.sh` baixa o intervalo 2010-01 até o mês
  mais recente disponível, sem falha, tratando exceções de nome de arquivo
  conhecidas (ex.: `basica202606.zip`).
- **C-02** — `src/02_extract_validate.py` confirma cabeçalho estável em
  todo o intervalo 2010-2026, ou documenta e localiza exatamente onde
  diverge. Resolve a hipótese candidata do REP-001 §5.2 (estabilidade de
  schema não testada) em achado confirmado ou achado refutado.
- **C-03** — Básica 2010-presente carregada e validada nos dois caminhos
  (SQLite e Snowflake), com contagem de linhas batendo entre os dois.

### 5.2 VRA e SIROS (datasets novos)

- **C-04** *(provisório)* — VRA: pipeline completo (download → ingestão →
  tratamento) funcional em ao menos um caminho, para um recorte inicial a
  definir quando o trabalho começar, antes de estender para 2010-presente.
- **C-05** *(provisório)* — SIROS: desenho de download diário implementado
  e testado para ao menos um mês completo, com volume real medido —
  resolve a hipótese candidata do REP-001 §5.2 sobre volume estimado.

### 5.3 Camada ouro e consumo

- **C-06** *(provisório)* — Camada ouro (star schema/métricas) existe para
  ao menos um dataset, em ao menos um caminho.
- **C-07** *(provisório)* — Dashboard (Streamlit, Power BI ou Looker
  Studio) existe para ao menos um dataset, alimentado pela camada ouro
  correspondente.

### 5.4 Critérios documentais e de portfólio

- **C-08** — As sete peças de fundação existem, aprovadas, e se
  referenciam mutuamente (SPEC-001 R-TAX-08).
- **C-09** — Cada decisão arquitetural não-trivial (ex.: D4/D7 do REP-001,
  organização de dado e separação de ingestão) tem DEC própria com rastro
  a artefato concreto, mesmo quando produzida depois desta SPEC.

---

## 6. Premissas e dependências

Herdadas do DEC-002 §6.5, mais as específicas desta SPEC:

- **Disponibilidade contínua da ANAC** nos padrões de URL testados em
  2026-08-24 — a fonte é de terceiro, pode mudar sem aviso.
- **Conta Snowflake trial ativa**, com crédito suficiente para o volume
  ampliado (16 anos de Básica/VRA a mais, SIROS diário desde 2019).
- **Volume do SIROS dentro do que o ambiente suporta** sem redesenho —
  premissa não testada até C-05.
- **Schema estável de Básica/VRA em 2010-2026** — premissa até C-02
  confirmar ou refutar.
- **Ambiente local configurado** (conda `pesquisa-azul`, Snowflake CLI)
  permanece disponível ao longo do trabalho.

Mudança em qualquer premissa dispara reavaliação desta SPEC (§10).

---

## 7. Não-objetivos

Distintos do fora de escopo (§3.2): não dizem respeito ao que o projeto
não entrega, mas a critérios contra os quais o projeto **se recusa a
otimizar**, mesmo dentro do que entrega.

- **Latência em tempo real não é objetivo.** Mesmo o SIROS, diário, é
  processado em lote — não há compromisso de streaming.
- **Uso multiusuário ou SLA de produção não são objetivo.** É portfólio
  solo, não sistema com garantia de disponibilidade a terceiros.
- **Exaustividade histórica não é objetivo.** Usar o máximo teórico da
  fonte (2000) foi deliberadamente descartado (DEC-002 §4.3) — mais
  histórico não é, por si, sinal de sucesso.
- **Paridade de ritmo entre os dois caminhos, incremento a incremento, não
  é objetivo.** "Igualmente investidos" (REP-001 D2) é compromisso de
  chegada, não exige que cada avanço mova os dois caminhos no mesmo passo
  — isso seria irreal para projeto solo e alimentaria o viés de
  romantização de escopo já nomeado (REP-001 §6).

---

## 8. Regras checáveis (R-FUN)

| ID | Regra | Onde verificar | Severidade |
|---|---|---|---|
| **R-FUN-01** | `scripts/01_download.sh` cobre o intervalo 2010-presente para Básica, sem falha registrada no log de download (C-01). | Execução do script + `_download_log.csv` | Alta |
| **R-FUN-02** | Relatório de `src/02_extract_validate.py` cobre 2010-2026 e confirma cabeçalho estável, ou aponta exatamente a divergência (C-02). | `_validation_report.json` | Alta |
| **R-FUN-03** | Contagem de linhas da Básica bate entre `basica.sqlite` e `BASICA_RAW` (Snowflake) para o intervalo 2010-presente (C-03). | `COUNT(*)` nas duas engines | Alta |
| **R-FUN-04** | Dataset Combinada não aparece em nenhum script de download ou ingestão (§3.2). | Inspeção de `scripts/`, `src/`, `sql/` | Média |
| **R-FUN-05** | Cada dataset com ingestão ativa tem scripts equivalentes em `src/ingestao_sqlite/` e `src/ingestao_snowflake/` (ou pendência registrada, se um caminho ainda não começou). | Listagem de `src/ingestao_*/` por dataset | Média |
| **R-FUN-06** | Decisão arquitetural não-trivial tem DEC com rastro a artefato concreto (C-09). | Cruzamento `docs/DEC/` × escolhas no código | Média |
| **R-FUN-07** | Para cada `C-NN` desta SPEC existe artefato ou método de verificação; critério sem verificação possível é ornamental e deve ser revisado. | Inspeção da §5 × estrutura real do repositório | Média |
| **R-FUN-08** | Esta SPEC referencia DEC-002 e REP-001 no frontmatter; DEC-002 aponta de volta para esta SPEC como a peça que materializa (rastro bidirecional). | Inspeção de `referencia:` cruzado | Baixa |

---

## 9. Limitações conhecidas

- Critérios C-04 a C-07 dependem de trabalho ainda não iniciado (VRA,
  SIROS, camada ouro, dashboard) — não há linha de base real para
  calibrar números exatos ainda, daí marcados **(provisório)**.
- Esta SPEC não resolve D4/D7 do REP-001 (organização de dado em SQLite,
  separação física de ingestão) — permanecem pendentes de uma DEC de
  conteúdo dedicada (`DEC-004+`, `SPEC-001 §9`), não formalizados aqui.
- Os critérios do caminho Snowflake (§4.1) têm mais detalhe que os do
  caminho SQLite nesta versão — reflete o que já existe (plano de fases
  A-H para Snowflake) mais do que uma hierarquia real entre os caminhos;
  será equalizado conforme o caminho SQLite avançar.
- Não fixa números-alvo (ex.: "processar N milhões de linhas") — os
  critérios de volume (C-05) são de medição, não de meta, porque a medição
  ainda não aconteceu.

---

## 10. Critérios de revisão

Revisitar esta SPEC quando:

- **C-02** (validação de schema 2010-2026) revelar quebra de cabeçalho que
  mude o recorte temporal viável.
- **C-05** (volume real do SIROS) invalidar a premissa de viabilidade do
  §6.
- **DEC-003/SPEC-003** fixarem papéis de forma que altere alguma premissa
  de audiência (§2) aqui assumida.
- A pendência D4/D7 do REP-001 for resolvida por uma DEC de conteúdo
  dedicada — pode adicionar critérios ou regras a esta SPEC.
- Qualquer critério `C-NN` se revelar não verificável na prática
  (R-FUN-07).

---

## 11. Histórico

| Data | Evento |
|---|---|
| 2026-08-24 | SPEC-002 v1 produzida em status `proposto`. Materializa o DEC-002 (aprovado): propósito, audiência, escopo (3 datasets, 2 caminhos, 2010-presente), decomposição em matriz dataset × caminho, 9 critérios de sucesso incrementais (4 provisórios), premissas, 4 não-objetivos, 8 regras `R-FUN-NN`. Aguarda aprovação do autor antes de seguir para DEC-003. |
| 2026-08-24 | **Aprovada.** Revisão contra o blueprint (`SPEC_002.json`) sem divergência: onze seções obrigatórias presentes, cada `C-NN` aponta artefato verificável ou método de medição, provisórios marcados como tais, cada `R-FUN-NN` com id/enunciado/onde-verificar/severidade. Segue para DEC-003. |

---

*Fim do documento.*
