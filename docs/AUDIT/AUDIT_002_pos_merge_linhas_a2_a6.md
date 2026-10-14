---
documento: AUDIT-002
titulo: Auditoria de coerência após a incorporação das linhas a2 a a6 à main
versao: v1
status: aprovado
data: 2026-10-14
autor: Bruno Alexandre Serminaro
referencia: —
escopo: projeto
---

# AUDIT-002 · Auditoria de coerência após a incorporação das linhas a2 a a6

> Segunda rodada registrada de `gov-check`, pedida pelo autor logo após o
> merge do PR #1 na `main` (`4ebf613`), que trouxe 23 commits: linhas a2 a
> a6, SPEC-017, `relatorios/`, IATA e portabilidade. O merge não está entre
> os marcos listados no SPEC-003 §7, então esta rodada é voluntária, não
> exigida pela cadência. AUDIT é isento de DEC prévia (DEC-META-014 §2.4).

---

## 1. Escopo auditado

- **Artefatos**: todos os documentos tipados de `docs/` (11 DEC, 17 SPEC,
  4 GUIDE, 1 REP, 1 AUDIT anterior), mais o estado real de `scripts/`,
  `src/`, `analise/` e `data/anac/` contra o que as SPECs declaram.
- **Regras confrontadas**: as 26 declaradas, `R-TAX-01..11` (`SPEC-001`),
  `R-FUN-01..08` (`SPEC-002`) e `R-CON-01..07` (`SPEC-003`). Uma a mais que
  no `AUDIT-001`: a `R-TAX-11`, formalizada na `SPEC-001 v2`.
- **Método**: passada determinística (`gov-check/scripts/check_project.py`,
  exit 0) para as regras `auto`; passada semântica para as demais, com
  duas conferências que regra nenhuma pede explicitamente: `versao:` contra
  a última versão registrada no Histórico, e status das peças que sustentam
  peças aprovadas.

---

## 2. Resultado por regra

| Regra | Severidade | Veredito | Evidência |
|---|---|---|---|
| R-TAX-01 | Alta | Conforme | Script |
| R-TAX-02 | Alta | Conforme | Script |
| R-TAX-03 | Crítica | Conforme | Script. `GUIDE-004` ausente é número reservado no `INDEX_GUIDE`, não lacuna |
| R-TAX-04 | Média | Conforme | Script: todos os `status` em `{proposto, aprovado}` |
| R-TAX-05 | Alta | Conforme | Leitura: as oito DECs aprovadas (001, 002, 003, 005 a 009) têm as sete seções |
| R-TAX-06 | Média | Conforme | Todo SPEC, REP e GUIDE cita ao menos uma DEC no `referencia:` |
| R-TAX-07 | Média | Conforme | Script |
| R-TAX-08 | Crítica | Conforme | Script: sete peças presentes e referenciadas. Ver §3.2 sobre o status da SPEC-003 |
| R-TAX-09 | Alta | N/A | Nenhum documento `superseded` |
| R-TAX-10 | Baixa | Conforme | Script |
| R-TAX-11 | Alta | **Divergência, resolvida nesta auditoria** | SPEC-001 e SPEC-011 (`aprovado`) com v3 no Histórico e `versao: v2` no frontmatter. Ver §3.1 |
| R-FUN-01 | Alta | **Divergência** | 199 arquivos da Básica no disco (2010-01 a 2026-07, completo), mas o `_download_log.csv` não registra 2024-01 a 2026-06. Ver §3.5 |
| R-FUN-02 | Alta | Conforme | Cumprido, conforme a própria SPEC-002 (`SPEC-008 §4`) |
| R-FUN-03 | Alta | **Não verificado** | Exige contagem no Snowflake, sem acesso nesta rodada |
| R-FUN-04 | Média | Conforme | `grep -rli combinada scripts src sql`, nenhuma ocorrência |
| R-FUN-05 | Média | Conforme | Básica nas duas engines; VRA e SIROS só em SQLite, pendência registrada na SPEC-002 §9 |
| R-FUN-06 | Média | **Divergência** | Linha a6 (pontualidade) na `main` sem DEC. Ver §3.3 |
| R-FUN-07 | Média | Não reexaminado | Conforme no `AUDIT-001`; a SPEC-002 não mudou os `C-NN` desde então |
| R-FUN-08 | Baixa | Conforme | Script |
| R-CON-01 | Média | Conforme | SPEC-003 §3.1: todo papel com pessoa ou "não previsto" |
| R-CON-02 | Alta | Conforme | Todo artefato `aprovado` registra a aprovação no Histórico |
| R-CON-03 | Alta | Conforme | Nenhum registro de aprovação pela IA de apoio; a IA não consta da §3.1 |
| R-CON-04 | Média | Conforme | Script |
| R-CON-05 | Média | Conforme | SPEC-003 sem nenhum commit entre 2026-08-25 e esta rodada: não houve edição da §3.1 |
| R-CON-06 | Alta | Conforme | Último AUDIT em 2026-08-25, piso trimestral vence em 2026-11-25 |
| R-CON-07 | Média | Conforme | Script |

**Resumo**: 20 Conforme, 3 Divergência (1 resolvida nesta auditoria), 1 N/A,
1 não verificado, 1 não reexaminado. Nenhuma Crítica. A §3 traz ainda três
achados fora das regras declaradas.

---

## 3. Divergências e resolução

### 3.1 A1 e M1: `versao:` atrás do Histórico

Quatro peças tinham uma versão registrada no Histórico sem o frontmatter
acompanhar: SPEC-001 (v2 → v3) e SPEC-011 (v2 → v3), ambas `aprovado`, o
que é divergência de `R-TAX-11`; SPEC-013 (v12 → v14) e DEC-010 (v1 → v2),
ambas `proposto`, o que é inconsistência sem regra.

**Caminho escolhido pelo autor: (b) corrigir o artefato.** `versao:` e
`data:` alinhados à última versão do Histórico nas quatro, com entrada no
Histórico de cada uma. Nenhuma mudança de conteúdo.

Padrão a observar: as quatro correções pós-aprovação foram lançadas por
sessões assistidas, que escreveram a linha do Histórico e não subiram o
campo. É o mesmo padrão que motivou a `R-TAX-11`. Se reaparecer, cabe
pedir à passada determinística que confira `versao:` contra o Histórico.

### 3.2 A2: SPEC-003 em `proposto` desde 2026-08-24

A última peça da fundação de sete nunca foi aprovada, e o seu §8 dizia que
o `gov-check` ainda não tinha rodado, falso desde o `AUDIT-001`. As regras
`R-CON-NN` que esta auditoria aplica derivam, portanto, de um contrato
ainda em proposta.

**Caminho escolhido pelo autor: (b) corrigir o artefato e aprovar.** O §8
foi corrigido e passa a apontar para o `INDEX_AUDIT.md` como registro vivo.
A aprovação é ato do autor: **SPEC-003 aprovada pelo autor em
2026-10-14**, registrada no Histórico dela. A fundação de sete peças está
completa.

### 3.3 M2: linha a6 sem DEC (dívida)

A a6 é uma sétima pergunta de análise; a SPEC-004, sob a DEC-007, fixa
seis. A pendência já estava declarada no PR #1, mas agora está na `main`.
A a2 também não tem SPEC (seria a SPEC-018); como não existe documento,
não há regra violada, só trabalho pendente.

**Decisão do autor: registrar como dívida.**

### 3.4 M3: DEC-008 `aprovado` apoiada na DEC-004 `proposto` (dívida)

A DEC-004 nasceu do `AUDIT-001` como DEC retroativa de regularização e
continua em `proposto`, 50 dias depois, enquanto a DEC-008, aprovada, a
cita como base. O `AUDIT-001` §4 já ressalvava isso.

**Decisão do autor: registrar como dívida.**

### 3.5 M4 e M5: ambiente obsoleto e log de download (dívida)

- **M4.** O ambiente `pesquisa-azul`, substituído por `gov-sermi-perf` na
  DEC-011, ainda aparece como instrução de uso em 9 peças de `docs/` (fora
  os registros históricos da DEC-010 e da DEC-011) e nas docstrings de 16
  scripts de `analise/`.
- **M5.** O log da Básica (`data/anac/basica/_download_log.csv`, ignorado
  pelo git) tem 169 meses com HTTP 200, de 2010-01 a 2023-12 mais 2026-07,
  e um 404 em 2026-08 (mês ainda não publicado no momento do download). Os
  30 meses de 2024-01 a 2026-06 estão no disco e fora do log. Hipótese
  candidata, não confirmada: o log foi reescrito por uma rodada parcial do
  `BASH_001`. Como o log não é versionado, não há como verificar.

**Decisão do autor: registrar como dívida.**

---

## 4. Dívidas registradas

Operação solo: o dono de todas é o Autor (SPEC-003 §3.1).

| # | Dívida | Horizonte sugerido | Fecha quando |
|---|---|---|---|
| M3 | Aprovar ou revisar a DEC-004 | Dias: é leitura de uma peça já escrita | DEC-004 sai de `proposto` |
| M4 | Trocar `pesquisa-azul` por `gov-sermi-perf` nas instruções de uso | Dias: varredura mecânica, um commit | `grep -rl pesquisa-azul` só devolve os registros históricos |
| M5 | Regenerar o log da Básica | Na próxima rodada de download, que também deve buscar 2026-08 em diante | O log cobre todos os meses presentes no disco |
| M2 | DEC que amplia o escopo para a sétima pergunta (a6), depois a SPEC da linha | Semanas: decisão de escopo, não de forma | DEC aprovada e SPEC da a6 em `proposto` |

---

## 5. Ressalvas

- **Rodadas não registradas.** Houve pelo menos duas passadas de
  `gov-check` entre o `AUDIT-001` e esta: uma em 2026-08-31 (citada no
  Histórico da `SPEC-001 v2`) e uma em 2026-09-04 (commit `ef6af66`). As
  duas geraram correções, mas nenhum AUDIT. Isto não muda a cadência, que
  segue cumprida, mas significa que o `INDEX_AUDIT` subnotifica o freio.
- **Doze peças em `proposto`** além da SPEC-003: DEC-004, DEC-010,
  DEC-011, GUIDE-002, GUIDE-003, GUIDE-005 e SPEC-012 a SPEC-017. Não é
  divergência, porque nenhuma regra impõe prazo para aprovar, mas é o
  maior volume de trabalho de governança em aberto.
- **R-FUN-03 não foi verificada.** A conformidade com a contagem no
  Snowflake vem da última verificação feita, não desta rodada.

---

## 6. Próxima auditoria

Gatilhos (SPEC-003 §7): fechamento da fase B do plano Snowflake, de
qualquer fase do plano de expansão, ou, na ausência de marco, até
**2027-01-14** (piso trimestral contado a partir desta rodada).

---

## 7. Histórico

| Data | Evento |
|---|---|
| 2026-10-14 | AUDIT-002 produzido em status `proposto`, gerado pela skill `gov-check` sem DEC prévia (DEC-META-014 §2.4), a pedido do autor, após o merge do PR #1. 26 regras confrontadas. Decisões do autor: A1/M1 corrigidos (versões); A2 com §8 corrigido; M2 a M5 registrados como dívida. |
| 2026-10-14 | **Aprovado pelo autor** (Bruno Alexandre Serminaro), junto com a SPEC-003 (§3.2). |

---

*Fim do documento.*
