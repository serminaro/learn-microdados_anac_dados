---
documento: AUDIT-001
titulo: Auditoria de coerência pós-fundação
versao: v1
status: aprovado
data: 2026-08-25
autor: Bruno Alexandre Serminaro
referencia: —
escopo: projeto
---

# AUDIT-001 · Auditoria de coerência pós-fundação

> Primeira rodada de `gov-check` do projeto, disparada pelo marco de
> fechamento da fundação de sete peças (DEC-META-014 §2.1). AUDIT é isento
> de DEC prévia (DEC-META-014 §2.4) — gerado pela skill, conforme
> SPEC-003 §7/§8 (cadência mínima por marco). É o freio compensatório da
> operação solo (SPEC-META-001 §7A.1) em ato.

---

## 1. Escopo auditado

- **Artefatos**: as sete peças da fundação (`docs/DEC/DEC_001-003`,
  `docs/SPEC/SPEC_001-003`, `docs/REP/REP_001`), mais o estado real do
  repositório (`scripts/`, `src/`, `sql/`) contra o que `SPEC-002`
  declara.
- **Regras confrontadas**: as 25 regras declaradas — `R-TAX-01..10`
  (`SPEC-001`), `R-FUN-01..08` (`SPEC-002`), `R-CON-01..07` (`SPEC-003`).
- **Método**: passada determinística (`gov-check/scripts/check_project.py`)
  para regras `auto` (frontmatter, nomenclatura, numeração, estrutura de
  pastas, presença e rastro das sete peças); passada semântica (leitura
  direta de cada SPEC contra o estado real) para as regras marcadas
  `semântica`.

---

## 2. Resultado por regra

| Regra | Severidade | Veredito | Evidência |
|---|---|---|---|
| R-TAX-01 | Alta | Conforme | Script: frontmatter completo em todos os `.md` tipados |
| R-TAX-02 | Alta | Conforme | Script: nomes conforme `TIPO_NNN_descricao_curta.md` |
| R-TAX-03 | Crítica | Conforme | Script: numeração sequencial sem reuso |
| R-TAX-04 | Média | Conforme | Script: todos os `status` em `{proposto, aprovado}` |
| R-TAX-05 | Alta | Conforme | Leitura: DEC-001/002/003 aprovadas têm as sete seções (headers conferidos) |
| R-TAX-06 | Média | Conforme | Leitura: SPEC-001→DEC-001; REP-001→DEC-001; SPEC-002→DEC-002,REP-001; SPEC-003→DEC-003,SPEC-002 |
| R-TAX-07 | Média | Conforme | Script: `INDEX_DEC.md` lista as quatro DECs presentes |
| R-TAX-08 | Crítica | Conforme | Script: sete peças presentes e referenciadas |
| R-TAX-09 | Alta | N/A | Nenhum documento `superseded` existe ainda |
| R-TAX-10 | Baixa | Conforme | Script: exceção documentada respeitada |
| R-FUN-01 | Alta | **Divergência (esperada)** | `scripts/01_download.sh` cobre só 2024-2026, não 2010-presente (C-01 ainda não atingido) |
| R-FUN-02 | Alta | **Divergência (esperada)** | Validação (`src/02_extract_validate.py`) cobre só 2024-2026 (C-02 ainda não atingido) |
| R-FUN-03 | Alta | **Divergência (esperada)** | Básica 2010-presente ainda não carregada em nenhuma engine (C-03 ainda não atingido) |
| R-FUN-04 | Média | Conforme | `grep -rl "Combinada" scripts/ src/ sql/` — nenhuma ocorrência |
| R-FUN-05 | Média | Conforme | Básica tem `ingestao_sqlite/`+`ingestao_snowflake/`; VRA/SIROS pendência já registrada (SPEC-002 §9) |
| R-FUN-06 | Média | **Divergência, resolvida nesta auditoria** | D4/D7 implementados sem DEC própria — corrigida via `DEC-004` |
| R-FUN-07 | Média | Conforme | Cada `C-NN` do SPEC-002 §5 aponta artefato/método verificável |
| R-FUN-08 | Baixa | Conforme | Script: rastro bidirecional SPEC-002 ↔ DEC-002 |
| R-CON-01 | Média | Conforme | SPEC-003 §3.1: todo papel com pessoa ou "não previsto" |
| R-CON-02 | Alta | **Divergência, resolvida nesta auditoria** | REP-001 aprovado sem Histórico de aprovação — corrigida (seção Histórico adicionada) |
| R-CON-03 | Alta | Conforme | Nenhum Histórico registra "aprovado por Claude"; Claude não consta em nenhuma tabela de papéis |
| R-CON-04 | Média | Conforme | Script: SPEC-002 e SPEC-003 referenciam-se mutuamente |
| R-CON-05 | Média | N/A | Nenhuma mudança de atribuição de papel ocorreu ainda |
| R-CON-06 | Alta | N/A (primeira rodada) | `docs/AUDIT/` não existia antes deste documento — esta rodada é o marco que o cria |
| R-CON-07 | Média | Conforme | Equivalente a R-TAX-06, mesma evidência |

**Resumo**: 17 Conforme, 5 Divergência (2 resolvidas nesta auditoria, 3
esperadas e já rastreadas em REP-001/SPEC-002), 3 N/A. Nenhuma Crítica.

---

## 3. Divergências e resolução

### 3.1 R-CON-02 — REP-001 aprovado sem registro de aprovação

**Caminho escolhido pelo autor: (b) corrigir o artefato.** Seção Histórico
adicionada ao `REP-001` (2026-08-25), registrando a aprovação original
(2026-08-24) e a correção retroativa, com o autor como aprovador.

### 3.2 R-FUN-06 — D4/D7 implementados sem DEC própria

**Caminho escolhido pelo autor: (b) produzir a DEC.** `DEC-004` produzida
(2026-08-25, status `proposto`), formalizando retroativamente a
organização de dado em SQLite e a separação física de ingestão por
engine, no padrão de "DEC retroativa de regularização" previsto pela
DEC-META-014 §2.5.

### 3.3 R-FUN-01/02/03 — Básica ainda não estendida para 2010

**Não é divergência de governança**: SPEC-002 declara critérios-alvo
(C-01/C-02/C-03), não estado já atingido; REP-001 §8 já registrava isso
como próximo passo. Nenhuma ação de correção de documento — é trabalho de
implementação pendente, já rastreado. Registrado aqui como confirmação, não
como achado novo.

---

## 4. Ressalvas

- A cadência de auditoria comprometida no SPEC-003 §7 (por marco, piso
  trimestral) começa a valer a partir desta rodada — não há histórico
  anterior contra o qual medir atraso (R-CON-06, N/A por ser a primeira).
- `DEC-004` está `proposto`, não `aprovado`, no momento desta auditoria —
  o achado R-FUN-06 está resolvido no sentido de ter DEC com rastro, mas a
  DEC em si ainda aguarda aprovação do autor.

---

## 5. Próxima auditoria

Gatilhos previstos (SPEC-003 §7): fechamento da fase B do plano Snowflake
(`docs/plano_objetos_snowflake.md`), fechamento de qualquer fase do plano
de expansão (`docs/plano_expansao_multidataset.md`, ex.: Básica estendida
a 2010 — quando C-01/C-02/C-03 deste AUDIT deixarem de ser Divergência),
ou, na ausência de marco, até **2026-11-25** (piso trimestral).

---

## 6. Histórico

| Data | Evento |
|---|---|
| 2026-08-25 | AUDIT-001 produzido, gerado pela skill `gov-check` sem DEC prévia (DEC-META-014 §2.4). 25 regras confrontadas, 5 divergências (2 resolvidas na própria sessão: REP-001 Histórico, DEC-004; 3 esperadas e já rastreadas). Primeiro exercício do freio compensatório da operação solo (SPEC-003 §8). |

---

*Fim do documento.*
