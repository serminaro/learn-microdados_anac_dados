# learn-microdados_anac_dados

Pipeline de consolidação dos microdados públicos da ANAC em SQLite local e
réplica no Snowflake. Escopo original: tabela **Básica** (2024-2026, 30
arquivos mensais). Em expansão (decisão de 2026-08-24, ver
`docs/plano_expansao_multidataset.md`) para 3 datasets — **Básica** e
**VRA** (2010-01 até o presente), **SIROS** (2019-11 até o presente,
cadência diária) — e dois caminhos de produção igualmente investidos:
Snowflake (medalhão) e SQLite+Python. Download já cobre os três; a carga
em SQLite/Snowflake (extração, validação, schema, load) segue implementada
só para a Básica até o momento.

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
  mercado O-D. Fora de escopo deste repositório.

Além da Básica, o repositório também baixa:

- **VRA** (Voo Regular Ativo): mesma granularidade de etapa de voo, fonte
  `sistemas.anac.gov.br/dadosabertos`, cadência mensal.
- **SIROS** (Registro de serviços aéreos): fonte `sistemas.anac.gov.br/dadosabertos`,
  cadência **diária**, só a partir de 2019-11 (a fonte não publica lote
  anterior a isso).

Fonte da Básica: [gov.br/anac — Microdados](https://www.gov.br/anac/pt-br/assuntos/regulados/empresas-aereas/Instrucoes-para-a-elaboracao-e-apresentacao-das-demonstracoes-contabeis/envio-de-informacoes).

## Estrutura

Convenção de nomes de código (`TIPO_NNN_descricao_curta`) fixada em
`docs/DEC/DEC_001_Fundacao_sob_SERMI.md §6.6` e aplicada retroativamente aos
arquivos já existentes por `docs/DEC/DEC_005_Renomeacao_em_Lote_TIPO_NNN.md`.

```
scripts/                                  (BASH_NNN, download bruto, comum aos dois caminhos)
  BASH_001_basica_download.sh             baixa os zips mensais da Básica (2010-01 até o presente)
  BASH_002_vra_download.sh                baixa os csv/json mensais da VRA (2010-01 até o presente)
  BASH_003_siros_download.sh              baixa os csv/json diários do SIROS (2019-11 até o presente)
src/                                       (SRC_NNN, comum aos dois caminhos salvo subpastas)
  SRC_001_basica_extract_validate.py      extrai e valida consistência entre os meses da Básica
  SRC_002_basica_build_schema.py          gera o DDL da Básica a partir do cabeçalho real
  SRC_003_enriquecer_bases_aerodromos.py  enriquece aeródromos com coordenadas/fuso/horário de verão
  ingestao_sqlite/
    SRC_001_basica_load_sqlite.py         carga idempotente da Básica no SQLite
  ingestao_snowflake/
    SRC_001_basica_export_csv.py          exporta CSV único consolidado da Básica (UTF-8), insumo do PUT/COPY
sql/
  ingestao_sqlite/                        (DDL_NNN) DDL específico do caminho SQLite
    DDL_001_basica_create_table.sql       DDL SQLite da Básica (camada raw)
  ingestao_snowflake/                     (DDL_NNN + DML_NNN) DDL/carga específicos do caminho Snowflake
    DDL_001_basica_create_table_snowflake.sql  DDL Snowflake da Básica (camada raw)
    DDL_002_basica_file_format_and_stage.sql   File Format + Stage nomeados (Fase A do plano de objetos)
    DML_001_basica_setup_and_load.sql          roteiro Snowflake da Básica (referência, por blocos)
    DML_002_basica_run_all.sql                 idem, em arquivo único não-interativo
    DML_003_basica_copy_merge.sql              carga Snowflake da Básica via stage + MERGE idempotente
  tratamento/                             (DDL_NNN) views tipadas / limpeza (as duas engines)
    DDL_001_basica_view_typed_sqlite.sql   view tipada da Básica (SQLite)
    DDL_002_basica_view_typed_snowflake.sql view tipada da Básica (Snowflake)
  analise/                                reservada, preparação analítica (vazia por enquanto)
data/    (gitignored) zips/csv brutos e extraídos, CSV consolidado — por dataset
db/      (gitignored) banco(s) SQLite finais (hoje: db/anac_basica.sqlite, ~2,5GB)
```

`data/` e `db/` não são versionados: são grandes e 100% reprodutíveis a
partir dos scripts. O `db/anac_basica.sqlite` sozinho já passa do limite de
100MB por arquivo do GitHub.

## Pipeline

Requer Python 3.12+, `sqlite3` de linha de comando, `curl`, e (opcional, só
para a réplica Snowflake) o [Snowflake CLI](https://docs.snowflake.com/en/developer-guide/snowflake-cli/index).

Download bruto (os três datasets, comum aos dois caminhos de produção):

```bash
./scripts/BASH_001_basica_download.sh          # baixa os zips da Básica (2010-01 até o presente)
./scripts/BASH_002_vra_download.sh             # baixa os csv/json da VRA (2010-01 até o presente)
./scripts/BASH_003_siros_download.sh           # baixa os csv/json diários do SIROS (2019-11 até o presente)
```

Extração, validação e carga (implementado só para a Básica até o momento):

```bash
./src/SRC_001_basica_extract_validate.py            # extrai + valida (comum aos dois caminhos)
./src/SRC_002_basica_build_schema.py                # gera sql/ingestao_sqlite/DDL_001_basica_create_table.sql
./src/ingestao_sqlite/SRC_001_basica_load_sqlite.py # carrega db/anac_basica.sqlite
sqlite3 db/anac_basica.sqlite < sql/tratamento/DDL_001_basica_view_typed_sqlite.sql
./src/ingestao_snowflake/SRC_001_basica_export_csv.py  # gera data/anac/basica_consolidado_2010_2026.csv
```

Para replicar no Snowflake (depois de configurar uma conexão com
`snow connection add`): rode os scripts em `sql/ingestao_snowflake/` na ordem
`DDL_001_basica_create_table_snowflake.sql` → `DDL_002_basica_file_format_and_stage.sql`
→ `DML_001_basica_setup_and_load.sql` (ou `DML_002_basica_run_all.sql`, versão
consolidada não-interativa) pela extensão do Snowflake no VS Code (ou
`snow sql -f`), após criar a view tipada com
`sql/tratamento/DDL_002_basica_view_typed_snowflake.sql`. Para recargas
subsequentes idempotentes, use `DML_003_basica_copy_merge.sql`.

VRA e SIROS ainda não têm scripts de extração/validação/schema/load — só o
download bruto. Capítulos equivalentes ao da Básica ficam para quando
chegar a vez de cada um (`docs/plano_expansao_multidataset.md §5`).

## Camadas de dados

Padrão raw → typed (Básica, único dataset com carga implementada até o
momento):

- **`basica_raw`**: todas as 111 colunas como TEXT, fiéis ao arquivo
  original (Latin-1 → UTF-8 na carga). Nenhuma transformação. Chave:
  `id_basica`.
- **`basica_typed`** (view): casts corretos (`nr_horas_voadas` usa vírgula
  decimal; demais métricas numéricas são inteiros puros), `partida_ts`/
  `chegada_ts` combinando data+hora, e `bloco_tempo_min` já calculado.

## Notas de consistência (achados empíricos)

> Os números abaixo refletem a carga original da Básica (2024-01 a
> 2026-06, 30 arquivos), anterior à extensão de range para 2010-presente.
> Serão atualizados depois que o download estendido for consolidado e
> recarregado.

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
