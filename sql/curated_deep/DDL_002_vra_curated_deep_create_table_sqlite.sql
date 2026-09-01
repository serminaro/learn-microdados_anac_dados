-- Camada curated_deep: vra_curated_deep (db/anac_vra.sqlite)
-- Recorte de vra_silver para deep dive GOL/Azul: todas as 12 colunas
-- (SPEC-006 -- ja compacto, todas marcadas essenciais), so GLO/AZU,
-- janela 2021-01-01 ate a ultima data disponivel.
--
-- Construido a partir de vra_silver (nao vra_raw): dt_hr_partida_real
-- bruto tem formato duplo (DD/MM/AAAA ate 2018, ISO a partir de 2019,
-- achado 1 de DDL_004_vra_view_silver_sqlite.sql) e ao menos um valor
-- literal "null" como texto -- comparacao de texto ">= '2021-01-01'"
-- direto no raw e enganosa (ex.: "21/01/2010 00:00" ordena lexicografi-
-- camente acima de "2021-01-01" porque o 2o caractere '1' > '0',
-- contaminaria o filtro com linhas de 2010). vra_silver ja normaliza via
-- GLOB/CASE antes desta tabela filtrar -- filtro seguro.
--
-- Tabela materializada, mesmo raciocinio do DDL_001 desta pasta.

DROP TABLE IF EXISTS vra_curated_deep;

CREATE TABLE vra_curated_deep AS
SELECT
    sg_empresa_icao, nr_voo, cd_autorizacao_di, cd_tipo_linha,
    sg_icao_origem, sg_icao_destino,
    dt_hr_partida_prevista, dt_hr_partida_real,
    dt_hr_chegada_prevista, dt_hr_chegada_real,
    ds_situacao_voo, cd_justificativa
FROM vra_silver
WHERE sg_empresa_icao IN ('GLO', 'AZU')
  AND dt_hr_partida_real >= '2021-01-01';

CREATE INDEX idx_vra_curated_deep_empresa_dt ON vra_curated_deep(sg_empresa_icao, dt_hr_partida_real);

SELECT 'vra_curated_deep_linhas' AS metrica, COUNT(*) AS valor FROM vra_curated_deep;
SELECT 'vra_curated_deep_min_dt' AS metrica, MIN(dt_hr_partida_real) AS valor FROM vra_curated_deep;
SELECT 'vra_curated_deep_max_dt' AS metrica, MAX(dt_hr_partida_real) AS valor FROM vra_curated_deep;
SELECT sg_empresa_icao, COUNT(*) FROM vra_curated_deep GROUP BY sg_empresa_icao;
