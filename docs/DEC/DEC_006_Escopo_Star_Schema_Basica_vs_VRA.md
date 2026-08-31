---
documento: DEC-006
titulo: Escopo do star schema da Fase D — Básica satisfaz o KR4.1, VRA fica com capítulo próprio
versao: v1
status: aprovado
data: 2026-08-30
autor: Bruno Alexandre Serminaro
referencia: DEC-002, SPEC-002
escopo: projeto
---

# DEC-006 · Escopo do star schema: Básica satisfaz o KR4.1, VRA fica com capítulo próprio

> DEC de conteúdo: resolve o ponto em aberto identificado em
> `rascunho/plano_certificacao_snowpro.md §5` — o star schema da Fase D do
> `plano_objetos_snowflake.md` está desenhado para o schema `ANAC.BASICA`,
> mas o KR4.1 do OKR de carreira (`okr_carreira_estudo.md`,
> `20-azul-analista-dados`) lista "ANAC VRA → Snowflake → Power BI" como
> ação estratégica, e VRA hoje só tem download bruto implementado.

---

## 1. Contexto

O `plano_objetos_snowflake.md` (linha 11) fixa escopo em `ANAC.BASICA` desde
a origem; a Camada 3 (Fase D) desenha o star schema — Sequence, tabelas de
dimensão, Dynamic Table de fato — inteiramente sobre esse schema. O
`plano_expansao_multidataset.md` já previu que VRA e SIROS "ganham
capítulos equivalentes quando chegar a vez deles", e a matriz do
`SPEC-002 §4.1` confirma: VRA está "a implementar" nos dois caminhos
(Snowflake e SQLite), sem ingestão nem tratamento ainda.

O `okr_carreira_estudo.md` nomeia, na coluna "Ações-estratégicas" do
KR4.1, "ANAC VRA → Snowflake → Power BI". Mas o critério verificável do
próprio KR4.1 (coluna "Resultado-Chave") não nomeia dataset: **"Projeto 1
publicado: star schema com ≥1 fato + ≥4 dimensões, ≥6 measures DAX,
conectado ao Snowflake"**. A menção a VRA é o meio planejado, não o
critério de aceite.

Sem decidir isso agora, a Fase D corre risco de esperar a implementação
completa do pipeline VRA (download → ingestão → tratamento, trabalho ainda
não iniciado) antes de poder começar — o que atrasaria tanto o KR4.1
quanto o cronograma de estudo do SnowPro Core que depende da Fase D
(`rascunho/plano_certificacao_snowpro.md §6`, semanas 5-6).

## 2. Decisão

**Adotar Básica como o dataset que satisfaz o critério verificável do
KR4.1 (star schema ≥1 fato + ≥4 dimensões + ≥6 measures DAX, conectado ao
Snowflake), via a Fase D já desenhada em `plano_objetos_snowflake.md`.**
A ação estratégica do OKR muda de "ANAC VRA → Snowflake → Power BI" para
"ANAC Básica → Snowflake → Power BI"; o texto do `okr_carreira_estudo.md`
é responsabilidade do autor atualizar no repositório `serminaro-governance`
(fora do controle desta DEC, que é local a este projeto). VRA continua
"a implementar" conforme `SPEC-002 §4.1`/`plano_expansao_multidataset.md`,
sem prazo vinculado ao KR4.1.

## 3. Origem ou rastro

- `rascunho/plano_certificacao_snowpro.md §5`: nomeia o ponto em aberto e
  recomenda resolvê-lo como decisão explícita antes da Fase D começar.
- `okr_carreira_estudo.md` (linha ~85, `serminaro-governance/trabalho/
  contratos-trabalho/20-azul-analista-dados/okr/`): texto exato do KR4.1 —
  confirma que o critério verificável ("Resultado-Chave") não nomeia
  dataset; "ANAC VRA" aparece só na coluna "Ações-estratégicas".
- `plano_objetos_snowflake.md` linha 11 e Camada 3 (Fase D): escopo
  `ANAC.BASICA` já fixado desde a origem do documento.
- `SPEC-002 §4.1`: matriz dataset × caminho confirma VRA "a implementar"
  nos dois caminhos.
- `DEC-002 §6.2`: critério de sucesso incremental ("sucesso parcial, por
  dataset e por caminho, é sucesso real") — usado para justificar que
  satisfazer o KR4.1 com Básica não contorna o objetivo do projeto, é
  aplicação do mesmo critério já adotado.

## 4. Alternativas consideradas

### 4.1 Manter VRA como ação estratégica do KR4.1, esperar capítulo próprio

Não mexer no OKR; Fase D só começa quando VRA tiver pipeline completo
(download → ingestão → tratamento) implementado.

**Por que descartada.** Bloqueia a Fase D — e por extensão o cronograma de
estudo do SnowPro Core, que depende dela nas semanas 5-6
(`rascunho/plano_certificacao_snowpro.md §6`) — num trabalho substancial
ainda não agendado (pipeline VRA inteiro), sem necessidade: o critério
verificável do KR4.1 não exige VRA especificamente.

### 4.2 Adiar a decisão, deixar em aberto até a Fase D precisar decidir

Não decidir agora; resolver quando a Fase D efetivamente começar.

**Por que descartada.** É exatamente o padrão que o `rascunho/
plano_certificacao_snowpro.md §5` pede para não repetir ("recomendo
resolver isso como uma decisão explícita... antes da Fase D começar, não
silenciosamente"). Sem decisão registrada, a Fase D pode começar sobre a
base errada (ex.: desenhar dimensões pensando em granularidade de rota
doméstica/internacional do VRA) e precisar ser refeita.

### 4.3 Básica satisfaz o KR4.1, VRA fica com capítulo próprio (decisão atual)

**Adotada.** Usa o critério de sucesso incremental já fixado pelo
`DEC-002 §6.2`, libera a Fase D para começar imediatamente sobre a base já
desenhada, e não descarta VRA — só remove o acoplamento indevido entre um
KR de 12 meses e um pipeline que ainda não existe.

## 5. Consequências

### 5.1 Positivas

- Fase D pode começar sem esperar o pipeline VRA, destravando também o
  cronograma de estudo do SnowPro Core (`rascunho/
  plano_certificacao_snowpro.md §6`, semanas 5-6).
- KR4.1 continua sendo cumprido no seu critério literal — dataset nunca
  foi parte do "Resultado-Chave" verificável, só da ação estratégica.
- Aplica o critério de sucesso incremental do `DEC-002 §6.2` de forma
  consistente com o resto do projeto, em vez de criar exceção.

### 5.2 Negativas

- **A nuance original do OKR se perde**: se a intenção por trás de nomear
  especificamente VRA era praticar uma cadência de dado diferente (dado
  operacional voo-a-voo) ou uma granularidade de rota mais rica que a
  Básica, essa motivação não fica registrada nem testada por esta
  decisão — Básica já tem dimensões equivalentes (aeronave, aeroporto,
  empresa, tempo; Camada 3 do `plano_objetos_snowflake.md`), mas não é
  goal-for-goal o mesmo exercício.
- **Edição cross-repo**: a mudança de texto no `okr_carreira_estudo.md`
  vive em `serminaro-governance`, fora deste repositório — esta DEC
  registra a decisão, mas não a executa; a edição do OKR fica pendente,
  a cargo do autor.
- **Não resolve quando VRA de fato ganha pipeline completo** — permanece
  como estava no `plano_expansao_multidataset.md` e no `SPEC-002 §4.1`
  (C-04, provisório), sem novo prazo.

### 5.3 O que esta decisão não resolve

- Não decide o cronograma de implementação de VRA (download → ingestão →
  tratamento) — isso é `plano_expansao_multidataset.md`.
- Não altera `C-04` do `SPEC-002` (critério provisório de VRA).
- Não edita o `okr_carreira_estudo.md` em si — decisão registrada aqui,
  execução da edição cross-repo é ação separada do autor.

## 6. Critérios de reavaliação

Esta decisão deve ser revisitada se:

- VRA ganhar pipeline completo (download → ingestão → tratamento) antes da
  Fase D terminar — nesse caso, avaliar se vale estender o star schema
  para VRA também (como dataset adicional, não substituto de Básica).
- O autor concluir que a granularidade/cadência específica do VRA é
  pedagogicamente necessária para o objetivo do KR4.1 (não só o número de
  dimensões) — nesse caso, reverter para a alternativa 4.1.
- A edição do `okr_carreira_estudo.md` (fora deste repositório) não for
  feita, criando divergência prolongada entre o que o OKR diz e o que este
  projeto de fato entrega.

## 7. Histórico

| Data | Evento |
|---|---|
| 2026-08-30 | DEC-006 produzida em status `proposto`. Resolve o ponto em aberto do `rascunho/plano_certificacao_snowpro.md §5`: adota Básica como dataset que satisfaz o critério verificável do KR4.1, mantendo VRA com capítulo próprio sem prazo vinculado. Três alternativas avaliadas. Aguardando revisão do autor antes de aprovar — inclui a ação pendente de editar `okr_carreira_estudo.md` fora deste repositório. |
| 2026-08-31 | **Aprovada.** Revisão estrutural sem divergência: sete seções obrigatórias presentes (Contexto, Decisão, Origem, três Alternativas com veredito, Consequências com negativas, Critérios de reavaliação, Histórico), `referencia: SPEC-002` coerente. Autor revisou o resumo (quadro "Aprovações ANAC") e aprovou explicitamente. Ação de editar `okr_carreira_estudo.md` (fora deste repositório) permanece pendência do autor, não bloqueia esta aprovação. |

---

*Fim do documento.*
