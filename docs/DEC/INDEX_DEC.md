# Índice de DECs — learn-microdados_anac_dados

Registro de todas as decisões do projeto. Numeração local, sequencial,
**nunca reutilizada**. Convenção e estrutura em SPEC-META-001 §7 e §10
(`serminaro-governance/_meta/SPEC/SPEC_META_001_Taxonomia_SERMI.md`) — o
SPEC-001 deste projeto, quando produzido, passa a ser a referência local.

## DECs ativas (status `aprovado`)

| Nº | Título | Data | Descrição curta |
|---|---|---|---|
| [DEC-001](DEC_001_Fundacao_sob_SERMI.md) | Fundação do projeto sob a governança documental SERMI | 2026-08-24 | Funda o projeto sob a taxonomia de sete peças (DEC-META-014), escopo local, seis tipos de documento, `docs/<TIPO>/`. Fixa também a convenção `TIPO_NNN` para código-fonte (§6.6). |
| [DEC-002](DEC_002_Decisoes_de_Descricao.md) | Decisões de descrição | 2026-08-24 | Fixa recorte de escopo (3 datasets, 2 caminhos, corte 2010), critério de sucesso incremental e não-objetivos, a partir do acúmulo de REP-001/SPEC-001. |
| [DEC-003](DEC_003_Decisao_de_Participacao.md) | Decisão de participação | 2026-08-24 | Fixa operação solo (Autor/Gestor/Diretor acumulados), Claude como par assistivo sem autoridade de aprovação, e cadência mínima de auditoria por marco (piso trimestral). |
| [DEC-005](DEC_005_Renomeacao_em_Lote_TIPO_NNN.md) | Renomeação em lote para TIPO_NNN | 2026-08-26 | Autoriza a exceção que o DEC-001 §6.6 deixou explicitamente em aberto: renomeia em lote `scripts/01_download.sh`, `src/02_...`, `sql/07_...` etc. para `TIPO_NNN_descricao_curta`, motivada pela expansão para 3 datasets. Supersede pontual do DEC-001 §6.6 (só o trecho sobre retroatividade). |

## DECs em proposta (status `proposto`)

| Nº | Título | Data | Descrição curta |
|---|---|---|---|
| [DEC-004](DEC_004_Organizacao_de_Dado_e_Ingestao.md) | Organização de dado e ingestão | 2026-08-25 | DEC retroativa de regularização: formaliza D4/D7 do REP-001 (banco por dataset, separação física SQLite/Snowflake), já implementados desde 2026-08-24. Origem: achado R-FUN-06 do `gov-check AUDIT-001`. Aguardando revisão do autor. |

## DECs previstas (de conteúdo, a materializar)

| Nº | Título previsto | Tópico |
|---|---|---|

_(nenhuma no momento)_

## DECs superseded

| Nº | Título | Substituída por |
|---|---|---|

_(nenhuma)_

## DECs descartadas

| Nº | Título | Motivo |
|---|---|---|

_(nenhuma)_

## Relação SPEC × DEC supersedente

| SPEC | DEC que a modifica | O que muda |
|---|---|---|

_(nenhuma ainda)_

---

> **Nota de fundação (2026-08-24).** O projeto adota a fundação de sete
> peças em ordem decisão-primeiro (DEC-META-014): DEC-001 → SPEC-001 →
> REP-001 → DEC-002 → SPEC-002 → DEC-003 → SPEC-003. DEC-001, SPEC-001,
> REP-001, DEC-002, SPEC-002 e DEC-003 estão **aprovados** (2026-08-24).
> **SPEC-003 segue em `proposto`**, aguardando revisão do autor — falta
> só ela para a fundação de sete peças estar completa. Material de
> trabalho da fundação (contexto bruto, blueprints) em `rascunho/`, na
> raiz do repositório.
>
> **Nota de auditoria (2026-08-25).** Primeira rodada de `gov-check`
> (`docs/AUDIT/AUDIT_001_pos_fundacao.md`) gerou `DEC-004` (retroativa,
> formaliza D4/D7 do REP-001) e uma correção no REP-001 (Histórico
> adicionado). DEC-004 está em `proposto`.
