---
documento: SPEC-008
titulo: Ingestão SQLite — Básica
versao: v2
status: aprovado
data: 2026-08-31
autor: Bruno Alexandre Serminaro
referencia: DEC-008, SPEC-005
escopo: projeto
---

# SPEC-008 · Ingestão SQLite — Básica

> SPEC de conteúdo, **retroativa**: documenta a ingestão da Básica no
> caminho SQLite, já implementada e em produção desde antes desta peça
> existir. Mesmo padrão de regularização já usado pela `DEC-004`
> (DEC-META-014 §2.5) — registra o que já funciona, não desenha do zero.
> Materializa a `DEC-008`.

---

## 1. Propósito

Dar rastro formal ao pipeline de ingestão da Básica em SQLite — hoje
implementado (`scripts/`, `sql/ingestao_sqlite/`, `src/ingestao_sqlite/`,
`sql/tratamento/`) sem uma SPEC própria que o descreva de ponta a ponta.

## 2. Audiência

Reaproveita os papéis abstratos do `SPEC-002 §2` — nenhum papel novo.

## 3. Escopo

### 3.1 O que este SPEC entrega

Documentação do pipeline já existente: download → carga raw → view
tipada. Não implementa nada novo.

### 3.2 Fora de escopo

- Mudar qualquer parte do pipeline já implementado — isso seria DEC de
  conteúdo, não esta SPEC.
- VRA e SIROS — `SPEC-009`, `SPEC-010`.

## 4. Pipeline (implementado, carga estendida em 2026-08-31)

```
scripts/BASH_001_basica_download.sh
  → data/anac/basica/*.zip (199 arquivos, 2010-01 a 2026-07 baixados)
  → src/SRC_002_basica_build_schema.py
      (gerou sql/ingestao_sqlite/DDL_001_basica_create_table.sql
       a partir do cabeçalho de arquivos 2024-2026)
  → src/ingestao_sqlite/SRC_001_basica_load_sqlite.py
      (carrega em db/anac_basica.sqlite, idempotente:
       id_basica é chave primária, INSERT OR IGNORE; range de meses
       estendido de 2024-2026 para 2010-2026 em 2026-08-31)
  → basica_raw (111 colunas TEXT, fiel ao arquivo ANAC)
  → sql/tratamento/DDL_001_basica_view_typed_sqlite.sql
  → basica_typed (view, casts corretos — INTEGER/REAL,
       nr_horas_voadas troca vírgula por ponto antes do CAST)
```

### Achado: mudança de schema real da ANAC em 2020-01 (2026-08-31)

Antes de estender a carga a 2010-2023, comparar cabeçalhos de anos
distintos (2010, 2015, 2019, 2020, 2024) revelou: arquivos **2010-01 a
2019-12 têm 110 colunas**; a partir de **2020-01** a ANAC acrescentou a
coluna `nr_chave` (111 colunas). O DDL existente já tinha 111 colunas
(gerado a partir de 2024-2026) — resolve, em achado confirmado, a
hipótese candidata do `SPEC-002 C-02` sobre estabilidade de cabeçalho:
**não é estável**, a divergência está localizada e documentada aqui.

`SRC_001_basica_load_sqlite.py` foi corrigido para detectar as duas
formas de cabeçalho por arquivo e carregar `nr_chave = NULL` para
2010-2019 (ausência real na fonte, não erro de carga) — não trata como
falha, insere normalmente.

## 5. Camada raw (`basica_raw`)

111 colunas, todas `TEXT`, fiéis ao arquivo de origem (Latin-1 → UTF-8 na
carga) — sem tipagem, sem limpeza. `id_basica` é chave primária (`NOT
NULL`). `nr_chave` é `NULL` para todo registro de 2010-01 a 2019-12 (ver
achado acima) — não confundir com dado ausente por erro. Schema completo
documentado em `SPEC-005`.

## 6. Camada typed (`basica_typed`)

View sobre `basica_raw` com `CAST` para tipos reais (`INTEGER`, `REAL`) —
exemplo notável: `nr_horas_voadas` precisa `REPLACE(nr_horas_voadas, ',',
'.')` antes do `CAST AS REAL`, porque o arquivo original usa vírgula
decimal.

## 7. Critérios de sucesso

- **C-01** — Pipeline documentado bate com o código real (§4-§6). **Cumprido.**
- **C-02** — `basica_raw` e `basica_typed` seguem existindo e sendo
  usados por `trusted_essencial` (`DEC-007`) sem contradição com esta
  documentação. **Cumprido.**
- **C-03** *(novo, v2)* — Carga estendida a 2010-2026 executada sem erro,
  com o achado de schema (§4) tratado, não ignorado. **Cumprido**:
  15.607.396 linhas, `basica_raw` em 16 GB, `MIN`/`MAX` de
  `nr_ano_referencia` confirmando 2010-2026.

## 8. Premissas e dependências

- Ambiente `pesquisa-azul` (conda) disponível para rodar os scripts
  Python — mesma premissa do `SPEC-002 §6`.
- Cobertura de carga: **2010-01 a 2026-06, confirmada** — resolve, não
  mais premissa, a divergência que a v1 desta SPEC deixava em aberto.

## 9. Não-objetivos

- Não é objetivo mudar a arquitetura do pipeline — só estender o range de
  carga e corrigir a leitura de schema variável (§4), ambos dentro do
  padrão já existente.
- Não é objetivo confirmar o significado de `nr_chave` (o dado, quando
  existe, não foi investigado além de existir) — fica para quando algo
  precisar dele.

## 10. Regras checáveis (R-COL)

| ID | Regra | Onde verificar | Severidade |
|---|---|---|---|
| **R-COL-09** | O pipeline descrito em §4 bate com os scripts reais em `scripts/`, `src/ingestao_sqlite/`, `sql/ingestao_sqlite/`, `sql/tratamento/`. | Leitura dos scripts × §4-§6 | Média |
| **R-COL-16** *(novo, v2)* | `basica_raw` cobre 2010-01 a 2026-06 sem lacuna de mês; `nr_chave` é `NULL` só para `nr_ano_referencia < 2020`. | `MIN`/`MAX(nr_ano_mes_arquivo)` e `SELECT DISTINCT nr_ano_referencia WHERE nr_chave IS NULL` | Alta |

## 11. Limitações conhecidas

- Se o pipeline mudar depois desta aprovação, esta SPEC fica
  desatualizada até ser revisada — mesmo risco de toda documentação de
  pipeline real.
- `nr_chave` não tem seu propósito investigado — só se sabe quando existe
  (§4).

## 12. Critérios de revisão

Revisitar esta SPEC quando:

- O pipeline de ingestão da Básica mudar (novo script, novo range de
  carga).
- `SPEC-005` for revisada de forma que afete o schema de `basica_raw`.
- A ANAC mudar o cabeçalho de novo (mesmo padrão de risco que gerou o
  achado do `nr_chave`, §4).

## 13. Histórico

| Data | Evento |
|---|---|
| 2026-08-31 | SPEC-008 v1 produzida em status `proposto`, retroativa. Documenta o pipeline de ingestão SQLite da Básica já implementado. Materializa a `DEC-008`. Aguardando aprovação do autor. |
| 2026-08-31 | **Aprovada.** Autor revisou o lote e aprovou explicitamente. |
| 2026-08-31 | **v2 — carga estendida a 2010-2023.** Achado: cabeçalho da Básica muda em 2020-01 (`nr_chave` some antes disso) — resolve `SPEC-002 C-02` em achado confirmado, não mais hipótese. `SRC_001` corrigido para tratar as duas formas de cabeçalho sem falhar. Carga executada: 15.607.396 linhas, 16 GB, 2010-01 a 2026-06 confirmado. C-03 e R-COL-16 adicionados. |

---

*Fim do documento.*
