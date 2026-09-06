-- Camada curated_deep: pareto_bases_gol_azul
-- Classifica as bases de GOL e Azul em HUB / OFF-HUB pela regra de Pareto
-- (80% acumulado das etapas), por empresa e por sentido (chegada/partida),
-- na janela dos cinco ultimos anos FECHADOS.
--
-- Substitui rascunho/pareto_bases_gol.csv, planilha estatica de 2026-08-31
-- que ficou stale (achado registrado em SPEC-013 Sec.6.5) e que vivia numa
-- pasta fora do versionamento. View, nao tabela: o SQLite nao tem
-- MATERIALIZED VIEW, entao a escolha real e' entre recalcular na leitura
-- (sempre atual, ~12 s) e materializar numa tabela com refresh explicito
-- (leitura instantanea, mas com o mesmo risco de staleness que originou
-- este arquivo). Optou-se por nunca mais ficar stale.
--
-- ESCOPO. basica_curated_deep contem exatamente duas empresas, AZU/AD
-- (1.564.769 linhas) e GLO/G3 (1.179.195), entao "por empresa" aqui sao
-- duas. Pareto do setor inteiro exigiria basica_silver como fonte, nao
-- esta camada.
--
-- JANELA MOVEL. ano_ini/ano_fim saem do relogio: hoje (2026) cobrem
-- 2021-2025. Consequencia deliberada: o resultado muda de ano em ano, o
-- que resolve o staleness mas custa reprodutibilidade -- figura gerada
-- hoje nao se reproduz identica em 2027. Por isso ano_ini e ano_fim sao
-- colunas da view, e nao filtro invisivel: quem consome grava a janela
-- que leu. Em 2026 a janela nao corta nada (curated_deep comeca em 2021);
-- ela so passa a descartar dado em 2027.
--
-- ROTULO DA BASE (regra canonica, analise/iata_bases.py e SPEC-011). O
-- de-para ICAO->IATA vem da dimensao, resolvido POR AEROPORTO, nunca pela
-- coluna sg_iata_* da propria linha. Motivo medido em 2026-09-05: as
-- colunas sg_iata_* de basica_curated_deep sao inconsistentes dentro do
-- mesmo ICAO -- SDIY aparece como 'FEC' em 77 linhas e 'N/I' em 240,
-- SPJC como 'LIM' em 66 e '...' em 1. Resolver linha a linha parte o
-- mesmo aeroporto em duas bases (SDIY viraria 'FEC' com 77 etapas e
-- 'SDIY' com 240). Pela dimensao, SDIY fica com uma linha so, 317 etapas,
-- batendo com a contagem citada na docstring de iata_bases.py.
--
-- Quando a dimensao nao tem IATA utilizavel, o rotulo continua em ICAO
-- (mesmo fallback de iata_bases.py). A lista de sentinelas replica a de
-- SENTINELAS_IATA e acrescenta '...', encontrado em basica_curated_deep
-- em 2026-09-05 e ainda ausente daquela lista: e' string de 3 caracteres,
-- entao passa por qualquer checagem de comprimento sem levantar suspeita.
--
-- REGRA HUB. Identica a de gerar_pareto_bases_gol.py e as 15 copias em
-- analise/: e' HUB enquanto o acumulado ANTES desta base for < 80%. A base
-- que cruza a linha entra; a seguinte fica de fora.
--
-- Filtro PASSAGEIRO por padrao (SPEC-004 Sec.5.5, convencao do deep dive).
--
-- Verificado em 2026-09-05, janela 2021-2025:
--   AD chegada 172 bases / 23 HUB / 1.382.422 etapas
--   AD partida 167 bases / 23 HUB / 1.382.422 etapas
--   G3 chegada 139 bases / 16 HUB / 1.012.015 etapas
--   G3 partida 133 bases / 16 HUB / 1.012.015 etapas
-- Chegadas e partidas somam o mesmo total por empresa, como tem que ser
-- (toda etapa tem uma origem e um destino). Nenhum rotulo colide dentro
-- de empresa+sentido. O conjunto de 16 HUB de G3/chegada e' identico ao
-- do CSV calculado sobre o historico inteiro; so' a ordem interna muda
-- (GRU/CGH e CWB/FLN trocam de posicao).

DROP VIEW IF EXISTS pareto_bases_gol_azul;

CREATE VIEW pareto_bases_gol_azul AS
WITH janela(ano_ini, ano_fim) AS (
    SELECT CAST(strftime('%Y','now') AS INTEGER) - 5,
           CAST(strftime('%Y','now') AS INTEGER) - 1
),
-- Uma linha por etapa, duplicada nos dois sentidos: a mesma etapa e' uma
-- partida na base de origem e uma chegada na base de destino.
etapa AS (
    SELECT d.sg_empresa_icao, d.sg_empresa_iata,
           'CHEGADA' AS sentido, d.sg_icao_destino AS base_icao, d.ds_matricula
    FROM basica_curated_deep d, janela j
    WHERE d.ds_servico_tipo_linha = 'PASSAGEIRO'
      AND CAST(substr(d.dt_referencia, 1, 4) AS INTEGER) BETWEEN j.ano_ini AND j.ano_fim
    UNION ALL
    SELECT d.sg_empresa_icao, d.sg_empresa_iata,
           'PARTIDA', d.sg_icao_origem, d.ds_matricula
    FROM basica_curated_deep d, janela j
    WHERE d.ds_servico_tipo_linha = 'PASSAGEIRO'
      AND CAST(substr(d.dt_referencia, 1, 4) AS INTEGER) BETWEEN j.ano_ini AND j.ano_fim
),
-- Agrega por ICAO, que e' a chave estavel. O rotulo IATA entra so depois.
agregado AS (
    SELECT sg_empresa_icao, sg_empresa_iata, sentido, base_icao,
           COUNT(*) AS n_etapas,
           COUNT(DISTINCT ds_matricula) AS n_matriculas
    FROM etapa
    GROUP BY 1, 2, 3, 4
),
rotulado AS (
    SELECT a.*,
           CASE WHEN UPPER(TRIM(COALESCE(dim.base_iata, ''))) IN
                     ('', 'N/I', 'NI', 'N/A', 'NA', '-', '--', 'NULL', 'NONE', '...')
                THEN a.base_icao
                ELSE UPPER(TRIM(dim.base_iata))
           END AS base
    FROM agregado a
    LEFT JOIN dim_airport_location_time_zone dim ON dim.base_icao = a.base_icao
),
-- Desempate por base_icao (nao por rotulo): duas bases com o mesmo numero
-- de etapas precisam de ordem deterministica, senao o rank oscila entre
-- execucoes e o corte dos 80% pode cair em bases diferentes.
ranqueado AS (
    SELECT *,
        SUM(n_etapas) OVER (PARTITION BY sg_empresa_icao, sentido) AS n_emp,
        ROW_NUMBER()  OVER (PARTITION BY sg_empresa_icao, sentido
                            ORDER BY n_etapas DESC, base_icao) AS rank_base,
        SUM(n_etapas) OVER (PARTITION BY sg_empresa_icao, sentido
                            ORDER BY n_etapas DESC, base_icao
                            ROWS UNBOUNDED PRECEDING) AS n_acum
    FROM rotulado
)
SELECT
    (SELECT ano_ini FROM janela) AS ano_ini,      -- janela lida (inclusive)
    (SELECT ano_fim FROM janela) AS ano_fim,      -- janela lida (inclusive)
    sg_empresa_icao,                              -- GLO / AZU
    sg_empresa_iata,                              -- G3 / AD
    sentido,                                      -- CHEGADA / PARTIDA
    rank_base,                                    -- 1 = base com mais etapas
    base,                                         -- rotulo IATA, ou ICAO no fallback
    base_icao,                                    -- chave estavel, para rastro
    n_etapas,
    n_matriculas,                                 -- matriculas distintas na base
    ROUND(100.0 * n_etapas / n_emp, 2) AS pct,
    ROUND(100.0 * n_acum  / n_emp, 2) AS pct_acum,
    CASE WHEN 100.0 * (n_acum - n_etapas) / n_emp < 80 THEN 'HUB' ELSE 'OFF-HUB' END AS tipo
FROM ranqueado;
