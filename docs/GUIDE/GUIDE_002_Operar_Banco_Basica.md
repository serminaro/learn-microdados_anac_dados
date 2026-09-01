---
documento: GUIDE-002
titulo: Operar o banco Básica (SQLite)
versao: v1
status: proposto
data: 2026-08-31
autor: Bruno Alexandre Serminaro
referencia: DEC-008, SPEC-008
escopo: projeto
---

# GUIDE-002 · Operar o banco Básica (SQLite)

> Passo a passo para rodar, atualizar e consultar `db/anac_basica.sqlite`
> — o que `SPEC-008` descreve como arquitetura, este documento descreve
> como executar. Primeiro de três GUIDEs de banco (`INDEX_GUIDE.md`);
> `GUIDE-003` cobre VRA, `GUIDE-004` (reservada) cobrirá SIROS.

---

## 1. Propósito

Dar ao autor (ou a quem retomar o projeto depois) o procedimento
completo para ter `basica_raw`/`basica_silver` funcionando localmente,
sem precisar reconstruir o raciocínio de `SPEC-008` toda vez.

## 2. Pré-requisitos

- Ambiente conda `pesquisa-azul` ativo (`~/miniconda3/envs/pesquisa-azul/bin/python`).
- Repositório clonado, `data/anac/basica/` com os arquivos brutos (ou
  disposto a baixá-los — passo 3).
- ~17 GB livres em disco para `db/anac_basica.sqlite`.

## 3. Rodar do zero (ou atualizar)

```bash
# 1. Baixa o que faltar (idempotente — pula arquivo já em disco)
bash scripts/BASH_001_basica_download.sh

# 2. Carrega em SQLite (idempotente — INSERT OR IGNORE por id_basica)
~/miniconda3/envs/pesquisa-azul/bin/python \
  src/ingestao_sqlite/SRC_001_basica_load_sqlite.py
```

O passo 2 recria `basica_raw` se não existir (via
`sql/ingestao_sqlite/DDL_001_basica_create_table.sql`) e cobre todo mês de
`data/anac/basica/*.zip` já baixado, a partir de 2010-01
(`month_files()` descobre por existência de arquivo, não por mês
hardcoded — corrigido em 2026-08-31, `SPEC-008 v4`, um corte fixo antigo
deixava mês novo baixado sem carregar). Roda ~12-13 min por execução
completa (2026-08-31, medido em duas rodadas): **reexecução não é mais
rápida que a primeira** — o script relê todos os arquivos toda vez,
`INSERT OR IGNORE` só evita duplicar linha já carregada, não pula mês
inteiro. Idempotente, mas não incremental em tempo de execução.

Para (re)gerar a view silver (idempotente — o script começa com `DROP
VIEW IF EXISTS basica_silver`):

```bash
sqlite3 db/anac_basica.sqlite < sql/tratamento/DDL_003_basica_view_silver_sqlite.sql
```

`basica_typed` (`DDL_001_basica_view_typed_sqlite.sql`) foi **retirada**
em 2026-08-31 — cobria só ~27 das 112 colunas, misturando tipagem com
métrica derivada. `basica_silver` a substitui: as 112 colunas de
`basica_raw`, tipadas, organizadas nas 8 categorias de `SPEC-005`, com
comentário `--` por coluna gerado do mesmo dicionário. Sem métrica
derivada (isso fica para uma camada seguinte, ainda não construída).

## 4. Consultar

```bash
sqlite3 db/anac_basica.sqlite
```

```sql
-- linhas totais e cobertura
SELECT COUNT(*), MIN(nr_ano_referencia), MAX(nr_ano_referencia) FROM basica_raw;

-- uma etapa GOL, já tipada (casts corretos, nr_horas_voadas com ponto,
-- datas/horas via date()/time())
SELECT * FROM basica_silver WHERE sg_empresa_icao = 'GLO' LIMIT 5;
```

Consultas em `basica_raw` são mais lentas que o esperado à primeira vista
(ex.: `COUNT(*)` levou ~40s na tabela cheia, 2026-08-31) — é I/O em tabela
de 16 GB sem índice nas colunas mais comuns de filtro livre
(`dt_referencia`); prefira `nr_ano_referencia`/`nr_mes_referencia`
(indexados, `idx_basica_raw_ano_mes_ref`) quando possível.

## 5. Armadilhas conhecidas

- **`nr_chave` é `NULL` para `nr_ano_referencia < 2020`** — a ANAC não
  publicava essa coluna antes de 2020-01 (achado real, `SPEC-008 §4`).
  Não é dado faltando por erro de carga; filtrar por ela sem lidar com
  `NULL` descarta 10 anos de histórico silenciosamente.
- **`nr_horas_voadas` usa vírgula decimal no arquivo original** — já
  tratado em `basica_silver` (`REPLACE(..., ',', '.')`), mas quem ler
  `basica_raw` direto precisa lembrar disso.
- **Encoding do arquivo original é Latin-1**, convertido para UTF-8 na
  carga — não deveria aparecer para quem só consulta o banco, mas vale
  saber se algo parecer corrompido num campo de texto.
- **Datas/horas usam `date()`/`time()`/`datetime()`, não `CAST(... AS
  DATE)`** — SQLite trata tipo não reconhecido como afinidade `NUMERIC`,
  risco de conversão indevida de string ISO. Se for estender
  `basica_silver`, seguir o mesmo padrão.

## 6. Referências

- `SPEC-005` — dicionário completo de colunas, flag de essencialidade.
- `SPEC-008` — arquitetura do pipeline (o "o quê"; este GUIDE é o "como").
- `DEC-008` — decisão que autoriza este pipeline como padrão para as 3 bases.

## 7. Histórico

| Data | Evento |
|---|---|
| 2026-08-31 | GUIDE-002 v1 produzido em status `proposto`. Primeiro de três GUIDEs de banco de dados. Aguardando aprovação do autor. |
| 2026-08-31 | Atualizado (ainda v1/`proposto`, sem mudança de status): `basica_typed` retirada, substituída por `basica_silver` (`SPEC-008 v3`). §1, §3, §4, §5 revisados. |
| 2026-08-31 | Atualizado de novo: corte de mês fixo no loader corrigido (`SPEC-008 v4`), cobertura real passa a ser 2010-01 a 2026-07. Corrigida também a afirmação de que reexecução incremental é rápida — não é, o script relê tudo toda vez. §3 revisado. |

---

*Fim do documento.*
