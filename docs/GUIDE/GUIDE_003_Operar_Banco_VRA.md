---
documento: GUIDE-003
titulo: Operar o banco VRA (SQLite)
versao: v1
status: proposto
data: 2026-08-31
autor: Bruno Alexandre Serminaro
referencia: DEC-008, SPEC-009
escopo: projeto
---

# GUIDE-003 · Operar o banco VRA (SQLite)

> Passo a passo para rodar, atualizar e consultar `db/anac_vra.sqlite` —
> o que `SPEC-009` descreve como arquitetura, este documento descreve
> como executar. Segundo de três GUIDEs de banco (`INDEX_GUIDE.md`);
> `GUIDE-002` cobre Básica, `GUIDE-004` (reservada) cobrirá SIROS.

---

## 1. Propósito

Dar ao autor o procedimento completo para ter `vra_raw`/`vra_silver`
funcionando localmente, sem precisar reconstruir o raciocínio de
`SPEC-009` toda vez.

## 2. Pré-requisitos

- Ambiente conda `pesquisa-azul` ativo.
- `data/anac/vra/` com os arquivos brutos (ou disposto a baixá-los —
  passo 3).
- ~3 GB livres em disco para `db/anac_vra.sqlite`.

## 3. Rodar do zero (ou atualizar)

```bash
# 1. Baixa o que faltar (idempotente)
bash scripts/BASH_002_vra_download.sh

# 2. Carrega em SQLite (idempotente — pula mês já carregado)
~/miniconda3/envs/pesquisa-azul/bin/python \
  src/ingestao_sqlite/SRC_002_vra_load_sqlite.py
```

O passo 2 recria `vra_raw` se não existir (via
`sql/ingestao_sqlite/DDL_002_vra_create_table.sql`) e carrega todo mês
encontrado em `data/anac/vra/VRA_*.csv`. Roda em ~25 min na carga
completa 2010-2026 (2026-08-31, medido: 17.459.155 linhas). Idempotência
é por mês (`nr_ano_mes_arquivo`), não por linha — não há chave primária
natural no VRA (§5).

Para (re)gerar a view silver (idempotente — o script começa com `DROP
VIEW IF EXISTS vra_silver`):

```bash
sqlite3 db/anac_vra.sqlite < sql/tratamento/DDL_004_vra_view_silver_sqlite.sql
```

`vra_silver` tipa as 12 colunas de `vra_raw`: datas/hora via
`datetime()`, com detecção por `GLOB` do formato de origem (§5); a coluna
de situação do voo (`ds_situacao_voo`) com o achado do §5 já tratado.

## 4. Consultar

```bash
sqlite3 db/anac_vra.sqlite
```

```sql
-- linhas totais e cobertura
SELECT COUNT(*), MIN(nr_ano_mes_arquivo), MAX(nr_ano_mes_arquivo) FROM vra_raw;

-- voos GOL com horário previsto e real, mais recentes, já tipados
SELECT sg_empresa_icao, nr_voo, sg_icao_origem, sg_icao_destino,
       dt_hr_partida_prevista, dt_hr_partida_real
FROM vra_silver
WHERE sg_empresa_icao = 'GLO'
ORDER BY dt_hr_partida_real DESC
LIMIT 5;
```

## 5. Armadilhas conhecidas

- **Sem chave primária natural** — o VRA bruto não publica identificador
  de linha (diferente de `id_basica` na Básica). A candidata registrada
  em `SPEC-009 §5` (`sg_empresa_icao + nr_voo + dt_hr_partida_real`) não
  foi testada quanto a unicidade; não assumir que é única sem checar.
- **`dt_hr_partida_real`/`dt_hr_chegada_real` são timestamp único**, não
  separados em data+hora como na Básica (`dt_partida_real`+
  `hr_partida_real`) — decisão deliberada de manter como a fonte publica
  (`SPEC-009 §6`), não confundir os dois esquemas ao cruzar com Básica.
- **Esta é a única das três bases com horário programado**
  (`dt_hr_partida_prevista`/`dt_hr_chegada_prevista`) — é a peça que
  faltava para a pergunta 6 (block time) da `SPEC-004`, ainda bloqueada
  porque o cruzamento com a Básica (`DEC-007 §2.g`) não foi implementado.
- **O formato de data muda uma segunda vez, em 2018-12/2019-01**
  (`DD/MM/AAAA HH:MM` até 2018-12, ISO a partir de 2019-01) — achado só
  confirmado na validação de `vra_silver` (`SPEC-009 §4`, achado 1). Quem
  ler `vra_raw` direto e aplicar `datetime()` sem checar o formato recebe
  `NULL` silencioso nos 9 anos mais antigos. `vra_silver` já detecta os
  dois formatos por `GLOB`; um terceiro formato futuro cairia em `NULL`
  sem aviso (mesma limitação registrada em `SPEC-009 §12`).
- **`2020-02` e `2020-03` têm 5 colunas corrompidas na fonte**
  (581.768 linhas com `Microsoft.SqlServer.Dts.Pipeline.BlobColumn` —
  artefato de ETL vazado pela própria ANAC, `SPEC-009 §4`, achado 2).
  `vra_silver` já converte essas 5 colunas para `NULL` nesses meses,
  preservando o resto da linha (`sg_empresa_icao`, `nr_voo`, aeródromos,
  `cd_justificativa`). Quem consultar `vra_raw` direto nesses dois meses
  vai ver a string literal, não `NULL` — não confundir com dado real.

## 6. Referências

- `SPEC-006` — dicionário de colunas do VRA (12 colunas, todas essenciais).
- `SPEC-009` — arquitetura do pipeline (o "o quê"; este GUIDE é o "como").
- `DEC-008` — decisão que autoriza este pipeline como padrão para as 3 bases.
- `DEC-007 §2.g` — desenho (ainda não implementado) da junção Básica × VRA.

## 7. Histórico

| Data | Evento |
|---|---|
| 2026-08-31 | GUIDE-003 v1 produzido em status `proposto`. Segundo de três GUIDEs de banco de dados. Aguardando aprovação do autor. |
| 2026-08-31 | Atualizado (ainda v1/`proposto`, sem mudança de status): `vra_silver` implementado (`SPEC-009 v2`), substitui a menção a `vra_typed` como "ainda não implementada". Duas armadilhas novas documentadas: segunda mudança de formato de data (2018-12/2019-01) e corrupção de fonte em 2020-02/03 (`BlobColumn`). §1, §3, §4, §5 revisados. |

---

*Fim do documento.*
