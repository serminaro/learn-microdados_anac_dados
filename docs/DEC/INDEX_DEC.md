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
| [DEC-006](DEC_006_Escopo_Star_Schema_Basica_vs_VRA.md) | Escopo do star schema: Básica satisfaz o KR4.1, VRA fica com capítulo próprio | 2026-08-31 | Resolve o ponto em aberto do `GUIDE-001 §5`: adota Básica (Fase D já desenhada) para o KR4.1 do OKR de carreira, sem bloquear a Fase D à espera do pipeline VRA. Edição pendente do `okr_carreira_estudo.md` (fora deste repositório) fica com o autor, não bloqueia a decisão. |
| [DEC-007](DEC_007_Arquitetura_Perguntas_Analise_Deep_Dive.md) | Arquitetura para as Perguntas de Análise: Trusted_Essencial + Curated Deep Dive (GOL, Azul), genérica e dual-path | 2026-08-31 | Fixa camada `trusted_essencial` (29 colunas) e duas `curated` fixas por concorrente (GOL, Azul), janela 2021-01-01+, de forma agnóstica de engine (Snowflake e SQLite+Python). Seis perguntas: destinos/rota/mercado, distribuição da frota, comportamento do tempo de solo, caracterização das bases (hub/off-hub), etapa média (duração+distância+velocidade inferida), block time (bloqueada até o VRA, padrão de junção cross-dataset já registrado, §2.g). |
| [DEC-008](DEC_008_Ingestao_das_3_Bases_SQLite.md) | Ingestão das 3 bases ANAC no caminho SQLite | 2026-08-31 | Fixa padrão raw→silver (renomeado de "typed", já provado na Básica e no VRA) para as 3 bases no caminho SQLite; autoriza SPEC-008/009/010 como detalhamento por dataset; registra SIROS como caso especial de grão (autorização de slot, não voo-por-data) sem resolver a transformação. Snowflake fica para depois. |
| [DEC-009](DEC_009_Dimensao_Aerodromo_em_Basica_SQLite.md) | Dimensão de aeródromo (localização e fuso horário) como tabela auxiliar em anac_basica.sqlite | 2026-08-31 | DEC retroativa: formaliza `dim_airport_location_time_zone` (858 aeródromos, sem colunas de horário de verão), carregada em `anac_basica.sqlite`, como exceção pontual ao isolamento por dataset do `DEC-004`. |

## DECs em proposta (status `proposto`)

| Nº | Título | Data | Descrição curta |
|---|---|---|---|
| [DEC-004](DEC_004_Organizacao_de_Dado_e_Ingestao.md) | Organização de dado e ingestão | 2026-08-25 | DEC retroativa de regularização: formaliza D4/D7 do REP-001 (banco por dataset, separação física SQLite/Snowflake), já implementados desde 2026-08-24. Origem: achado R-FUN-06 do `gov-check AUDIT-001`. Aguardando revisão do autor. |
| [DEC-010](DEC_010_Relatorios_Derivados_no_Repositorio.md) | Relatórios derivados (IMRaD e Minto) versionados em `relatorios/`, fora da estrutura da SPEC-001 §5 | 2026-09-04 | Cria `relatorios/` na raiz para os geradores do relatório IMRaD e do comunicado Minto do deep dive GOL/Azul, trazidos de `learn-imrad-mintos` (repositório sem git). A pasta não é peça SERMI: sem frontmatter, sem numeração `TIPO_NNN`, regida pela convenção de código do DEC-001 §6.6. O guia de escrita das duas peças vira `GUIDE-005`. Duplicação deliberada das figuras de `analise/`, para manter cada gerador autocontido, com um `PROCEDENCIA_FIGURAS.md` por versão impedindo divergência silenciosa. *(v2, 2026-09-05: os geradores passam a viver sob uma pasta por versão, `relatorios/report_microdados_vN/`.)* |

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
> só ela para a fundação de sete peças estar completa. Os blueprints da
> fundação vivem em `docs/assets/blueprints/` (movidos de `rascunho/` em
> 2026-09-06); o contexto bruto que os acompanhava foi absorvido pelas
> próprias peças e removido, conforme registrado no Histórico da DEC-001.
>
> **Nota de auditoria (2026-08-25).** Primeira rodada de `gov-check`
> (`docs/AUDIT/AUDIT_001_pos_fundacao.md`) gerou `DEC-004` (retroativa,
> formaliza D4/D7 do REP-001) e uma correção no REP-001 (Histórico
> adicionado). DEC-004 está em `proposto`.
