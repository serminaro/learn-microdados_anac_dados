---
documento: DEC-008
titulo: Ingestão das 3 bases ANAC no caminho SQLite — padrão comum e detalhamento por SPEC
versao: v1
status: aprovado
data: 2026-08-31
autor: Bruno Alexandre Serminaro
referencia: DEC-004, SPEC-005, SPEC-006, SPEC-007
escopo: projeto
---

# DEC-008 · Ingestão das 3 bases ANAC (SQLite): padrão comum, detalhamento em três SPECs

> DEC de arquitetura: fixa o padrão de ingestão raw → typed, já provado
> na Básica, como modelo para VRA e SIROS no caminho **SQLite**
> (Snowflake fica para uma rodada futura, por pedido do autor), e decide
> que o detalhamento de cada base vira **SPEC própria** — autoriza
> `SPEC-008` (Básica, retroativa), `SPEC-009` (VRA, prospectiva) e
> `SPEC-010` (SIROS, prospectiva).

---

## 1. Contexto

A Básica já tem ingestão SQLite implementada e em produção: `basica_raw`
(carga bruta) → `basica_typed` (view tipada,
`sql/tratamento/DDL_001_basica_view_typed_sqlite.sql`). VRA e SIROS têm
só download bruto (`scripts/BASH_002_vra_download.sh`,
`BASH_003_siros_download.sh`) — nenhuma ingestão real, per `SPEC-002 §4.1`
(C-04/C-05, ambos provisórios).

Dois levantamentos novos, grounded em dado real já baixado
(`SPEC-006`, `SPEC-007`), mudam o que se sabe: VRA é estruturalmente
compatível com o padrão da Básica (12 colunas, voo-por-data, mesma
granularidade). SIROS **não é** — é registro de autorização de slot
(padrão semanal + janela de validade), sem data de voo individual
(`SPEC-007 §6`). Isso significa que "o mesmo padrão para as três" não
pode ser aplicado cegamente — precisa herdar essa diferença, não
escondê-la.

`DEC-004` já fixa a organização física (um banco SQLite por dataset,
`ATTACH DATABASE` para cruzar) — esta DEC não reabre isso, decide o que
acontece **dentro** de cada banco.

## 2. Decisão

Fixar, para o caminho SQLite:

**(a) Padrão raw → typed** como modelo para as três bases: uma tabela
`<dataset>_raw` com carga bruta fiel ao CSV de origem, uma view
`<dataset>_typed` com casts corretos — mesmo padrão que `basica_raw`/
`basica_typed` já seguem, mesma convenção de nome (`vra_raw`/`vra_typed`,
`siros_raw`/`siros_typed`).

**(b) Detalhamento de cada base vira SPEC própria**, autorizada por esta
DEC:
- `SPEC-008` · Ingestão SQLite — Básica (**retroativa**, documenta o que
  já existe).
- `SPEC-009` · Ingestão SQLite — VRA (**prospectiva**, referencia
  `SPEC-006`).
- `SPEC-010` · Ingestão SQLite — SIROS (**prospectiva**, referencia
  `SPEC-007`, herda o achado de granularidade sem resolvê-lo aqui).

**(c) Escopo só SQLite.** Snowflake (schemas `ANAC.VRA`, `ANAC.SIROS`,
mesma lógica) fica para uma DEC futura, por pedido explícito do autor —
não decidido, não descartado, só adiado.

**(d) SIROS é caso especial de grão, registrado, não resolvido.** O
padrão raw → typed vale para `siros_raw`/`siros_typed` como carga fiel
1:1 do CSV (uma linha do arquivo = uma linha na tabela). A eventual
expansão "autorização → voo por data" (`SPEC-007 §6`) é uma camada
**seguinte**, fora do escopo desta DEC e da `SPEC-010` — só entra em
pauta quando alguma pergunta de análise precisar dela.

## 3. Origem ou rastro

- `basica_raw`/`basica_typed`: padrão já implementado e em produção,
  modelo desta decisão.
- `DEC-004 §2/§4.4`: organização física (banco por dataset) — herdada,
  não reaberta.
- `SPEC-005`, `SPEC-006`, `SPEC-007`: levantamentos de coluna que dão a
  cada SPEC de ingestão futura sua base de schema.
- `SPEC-007 §6`: achado de que SIROS é autorização de slot, não
  voo-por-data — motivou a alternativa 4.3 (descartada) e a decisão (d).
- Pedido do autor nesta sessão (2026-08-31): DEC para as 3 bases, depois
  quebrar o detalhamento SQLite de cada uma em SPEC própria; Snowflake
  fica para depois.

## 4. Alternativas consideradas

### 4.1 Ingestão de VRA e SIROS sem padrão comum, cada uma desenhada do zero

Sem herdar o padrão raw→typed da Básica.

**Por que descartada.** Perde reuso de convenção já provada, risco de
inconsistência (nomes, camadas) entre as três bases sem motivo — a
Básica já mostrou que o padrão funciona.

### 4.2 Detalhar VRA e SIROS numa única SPEC, não três separadas

Uma SPEC de ingestão cobrindo os três datasets.

**Por que descartada.** Pedido explícito do autor de quebrar por base —
alinhado ao padrão que `SPEC-005`/`SPEC-006`/`SPEC-007` já seguem (uma
peça por dataset), e às estruturas de dado genuinamente diferentes
(SIROS em especial) que uma SPEC única esconderia atrás de uma falsa
uniformidade.

### 4.3 Resolver a expansão autorização→voo-por-data do SIROS já nesta DEC

Decidir agora como transformar o SIROS em voo-por-data.

**Por que descartada.** Informação insuficiente — `SPEC-007 §6` é achado
preliminar (amostra de 2 linhas), não base suficiente para desenhar uma
transformação real. Decidir agora seria decisão às pressas, o mesmo risco
que a `DEC-007 §4.7` já evitou para o padrão de junção Básica×VRA.

### 4.4 Escopo dual-path (SQLite + Snowflake) já nesta DEC

Estender a decisão aos dois caminhos de produção, como a `DEC-007` fez
depois de corrigir sua v1 Snowflake-only.

**Por que descartada, aqui.** Pedido explícito do autor de fazer SQLite
primeiro, Snowflake depois — ordem escolhida deliberadamente, diferente
do caso da `DEC-007` (onde o escopo único-caminho foi engano a corrigir,
não pedido). Não é o mesmo erro repetido, é sequenciamento pedido.

### 4.5 Padrão raw→typed comum, três SPECs de detalhamento, só SQLite agora (decisão atual)

**Adotada.** Reusa o que já funciona (Básica), respeita a diferença real
de grão do SIROS sem escondê-la, seguindo a ordem de trabalho que o autor
pediu.

## 5. Consequências

### 5.1 Positivas

- Reaproveita um padrão já provado (raw→typed da Básica) em vez de
  desenhar do zero para cada base.
- Três SPECs de detalhamento ficam com escopo claro e citável
  individualmente, sem misturar decisão de arquitetura de dataset com a
  de outro.
- A diferença de grão do SIROS fica registrada como decisão consciente
  (não escondida atrás de um padrão único forçado).

### 5.2 Negativas

- **Mais documentos para manter**: três SPECs em vez de uma, mais esta
  DEC — custo de manutenção maior que uma peça única, aceito pelo pedido
  explícito do autor.
- **SIROS fica com ingestão "raw fiel" que não resolve o problema real**
  (analisar por voo-por-data) — quem ler só `siros_raw`/`siros_typed` sem
  ler `SPEC-007 §6` pode não perceber que falta uma camada de
  transformação para usar o dado como voo individual.
- **Snowflake adiado** significa que, por um tempo, o caminho SQLite fica
  à frente do Snowflake para VRA/SIROS — tensão com "dois caminhos
  igualmente investidos" (`SPEC-002`), aceita como sequenciamento
  temporário, não permanente.

### 5.3 O que esta decisão não resolve

- Não decide a numeração exata dos scripts `DDL_NNN` por base — convenção
  já fixada no `DEC-001 §6.6`.
- Não resolve a expansão autorização→voo-por-data do SIROS — registrada,
  não decidida (§2.d).
- Não decide nada sobre o caminho Snowflake para VRA/SIROS — fica para
  DEC futura.
- Não formaliza os critérios de sucesso de cada ingestão — isso é
  conteúdo de `SPEC-008`/`009`/`010`.

## 6. Critérios de reavaliação

Esta decisão deve ser revisitada se:

- Alguma pergunta de análise passar a precisar do SIROS como voo-por-data
  — aciona a decisão adiada em §2.d, com base maior de amostra que
  `SPEC-007 §6`.
- O autor decidir iniciar o caminho Snowflake para VRA/SIROS — herda o
  mesmo padrão raw→typed, decisão análoga a esta, não necessariamente
  nova DEC se só estende o padrão já fixado aqui.
- A ingestão real de VRA revelar que a estrutura de `SPEC-006` não é
  estável entre meses/anos (premissa não testada lá).

## 7. Histórico

| Data | Evento |
|---|---|
| 2026-08-31 | DEC-008 v1 produzida em status `proposto`. Fixa padrão raw→typed para as 3 bases no caminho SQLite, autoriza `SPEC-008`/`009`/`010` como detalhamento por dataset, registra SIROS como caso especial de grão sem resolver a transformação. Cinco alternativas avaliadas. Aguardando aprovação do autor. |
| 2026-08-31 | **Aprovada.** Autor revisou o lote e aprovou explicitamente. |

---

*Fim do documento.*
