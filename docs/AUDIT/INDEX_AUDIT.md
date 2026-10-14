# Índice de AUDITs — learn-microdados_anac_dados

Registro de todas as auditorias de coerência do projeto. AUDIT é isento de
DEC prévia (DEC-META-014 §2.4) e gerado pela skill `gov-check`. É o freio
compensatório da operação solo (SPEC-003 §8) — cadência mínima por marco,
piso trimestral (SPEC-003 §7).

| Nº | Título | Data | Resultado | Descrição curta |
|---|---|---|---|---|
| [AUDIT-001](AUDIT_001_pos_fundacao.md) | Auditoria de coerência pós-fundação | 2026-08-25 | 17 Conforme / 5 Divergência / 3 N/A, 0 Crítica | Primeira rodada, disparada pelo fechamento da fundação. Gerou `DEC-004` (retroativa) e correção no `REP-001` (Histórico). |
| [AUDIT-002](AUDIT_002_pos_merge_linhas_a2_a6.md) | Auditoria de coerência após a incorporação das linhas a2 a a6 à main | 2026-10-14 | 20 Conforme / 3 Divergência / 1 N/A / 2 não verificadas, 0 Crítica | Voluntária, após o merge do PR #1. Corrigiu `versao:` em quatro peças e o §8 da SPEC-003; registrou quatro dívidas (a6 sem DEC, DEC-004, `pesquisa-azul`, log da Básica). |

**Próxima auditoria prevista**: por marco (fase B do plano Snowflake, ou
qualquer fase do plano de expansão), ou até **2027-01-14** (piso
trimestral contado do AUDIT-002), o que vier primeiro.
