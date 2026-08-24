# learn-microdados_anac_dados

Pipeline de consolidação dos microdados públicos de tráfego aéreo da ANAC
(tabela **Básica**, 2024–2026) em SQLite local e réplica no Snowflake, com
validação de consistência entre os 30 arquivos mensais de origem.

## Contexto

A URL de origem, apesar de estar sob o caminho de "Demonstrações Contábeis"
no site da ANAC, entrega na prática a página **Microdados** de estatísticas
operacionais de tráfego aéreo (voos, não dados financeiros). A ANAC publica
dois conjuntos com nomenclatura própria — **Básica** e **Combinada** — que não
têm relação com "dados básicos e consolidados" contábeis:

- **Básica**: uma linha por etapa de voo fisicamente realizada (decolagem →
  pouso), com as métricas de produção/tráfego (ASK, RPK, ATK, RTK, assentos
  ofertados, horas voadas). Usada para análise operacional.
- **Combinada**: uma linha por par origem-destino real do passageiro/carga,
  decompondo conexões. Não tem métricas de produção. Usada para análise de
  mercado O-D.

Este repositório trabalha só com a **Básica**. Fonte:
[gov.br/anac — Microdados](https://www.gov.br/anac/pt-br/assuntos/regulados/empresas-aereas/Instrucoes-para-a-elaboracao-e-apresentacao-das-demonstracoes-contabeis/envio-de-informacoes).

## Estrutura

```
scripts/
  01_download.sh                          baixa os 30 zips mensais (2024-01 a 2026-06)
src/
  02_extract_validate.py                  extrai e valida consistência entre os meses (comum aos dois caminhos)
  03_build_schema.py                      gera o DDL a partir do cabeçalho real (comum aos dois caminhos)
  ingestao_sqlite/
    04_load_sqlite.py                     carga idempotente no SQLite
  ingestao_snowflake/
    05_export_csv.py                      exporta CSV único consolidado (UTF-8), insumo do PUT/COPY do Snowflake
sql/
  ingestao_sqlite/                        DDL + carga específicos do caminho SQLite
    create_table_basica.sql               DDL SQLite (camada raw)
  ingestao_snowflake/                     DDL + carga/orquestração específicos do caminho Snowflake
    create_table_basica_snowflake.sql     DDL Snowflake (camada raw)
    07_snowflake_setup_and_load.sql       roteiro Snowflake (referência, por blocos)
    08_snowflake_run_all.sql              idem, em arquivo único não-interativo
    09_snowflake_copy_merge.sql           carga Snowflake via stage + MERGE idempotente
    10_snowflake_file_format_and_stage.sql  File Format + Stage nomeados (Fase A do plano de objetos)
  tratamento/                             views tipadas / limpeza (as duas engines)
    create_view_basica_typed_sqlite.sql   view tipada (SQLite)
    create_view_basica_typed_snowflake.sql  view tipada (Snowflake)
  analise/                                reservada, preparação analítica (vazia por enquanto)
data/    (gitignored) zips, txts extraídos, CSV consolidado
db/      (gitignored) banco SQLite final (~2,5GB)
```

`data/` e `db/` não são versionados: são grandes e 100% reprodutíveis a
partir dos scripts. O `db/anac_basica.sqlite` sozinho já passa do limite de
100MB por arquivo do GitHub.

## Pipeline

Requer Python 3.12+, `sqlite3` de linha de comando e (opcional, só para a
réplica Snowflake) o [Snowflake CLI](https://docs.snowflake.com/en/developer-guide/snowflake-cli/index).

```bash
./scripts/01_download.sh                       # baixa os 30 zips (comum aos dois caminhos)
./src/02_extract_validate.py                   # extrai + valida (comum aos dois caminhos)
./src/03_build_schema.py                       # gera sql/ingestao_sqlite/create_table_basica.sql
./src/ingestao_sqlite/04_load_sqlite.py        # carrega db/anac_basica.sqlite
sqlite3 db/anac_basica.sqlite < sql/tratamento/create_view_basica_typed_sqlite.sql
./src/ingestao_snowflake/05_export_csv.py      # gera data/anac/basica_consolidado_2024_2026.csv
```

Para replicar no Snowflake (depois de configurar uma conexão com
`snow connection add`): rode os scripts em `sql/ingestao_snowflake/` na ordem
numérica (`07` → `10`) pela extensão do Snowflake no VS Code (ou `snow sql -f`),
após criar infraestrutura e tabela com
`sql/ingestao_snowflake/create_table_basica_snowflake.sql` e a view tipada
com `sql/tratamento/create_view_basica_typed_snowflake.sql`.

## Camadas de dados

Padrão raw → typed:

- **`basica_raw`**: todas as 111 colunas como TEXT, fiéis ao arquivo
  original (Latin-1 → UTF-8 na carga). Nenhuma transformação. Chave:
  `id_basica`.
- **`basica_typed`** (view): casts corretos (`nr_horas_voadas` usa vírgula
  decimal; demais métricas numéricas são inteiros puros), `partida_ts`/
  `chegada_ts` combinando data+hora, e `bloco_tempo_min` já calculado.

## Notas de consistência (achados empíricos)

- Os 30 arquivos mensais (2024-01 a 2026-06) têm cabeçalho idêntico, sem
  `id_basica` duplicado dentro ou entre meses, e `nr_ano_referencia`/
  `nr_mes_referencia` sempre batendo com o nome do arquivo.
- O nome do arquivo mais recente foge do padrão: `basica202606.zip` (sem
  hífen), diferente de `basicaYYYY-MM.zip` nos demais — tratado
  explicitamente no script de download.
- `ds_matricula` (aeronave) vem vazia em ~12% das linhas (294.875 de
  2.409.265) — normal, nem toda etapa tem aeronave identificada no boletim.
- Total consolidado: **2.409.265 linhas**, idêntico no SQLite, no CSV
  exportado e na tabela Snowflake.

## Licença

O código deste repositório (scripts e DDL) está sob licença MIT, ver
[LICENSE](LICENSE). Os microdados em si são publicados pela ANAC sob
Creative Commons Atribuição-SemDerivações 3.0 Não Adaptada, e não são
versionados aqui (ver `.gitignore`).
