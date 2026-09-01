-- Camada curated_deep: basica_curated_deep (db/anac_basica.sqlite)
-- Recorte de basica_silver para deep dive GOL/Azul: so as 29 colunas
-- essenciais (SPEC-005 Sec.5), so GLO/AZU (Azul Conecta/ACN deixada de
-- fora -- e-mail/entidade regional distinta, nao pedida), janela
-- 2021-01-01 ate a ultima data disponivel, sem teto artificial.
--
-- Achado da checagem antes de materializar: so 7 linhas com
-- dt_partida_real = 2026-08-01 (GLO/AZU), fora da cobertura confirmada
-- pela SPEC-008 (2010-01 a 2026-07). Incluidas -- sao dado real, "ultima
-- data que temos" -- mas 2026-08 fica como mes fragmentario (7 linhas),
-- nao competencia completa; nao usar para agregacao mensal sem filtrar.
--
-- Tabela materializada, nao view -- mesmo raciocinio de performance do
-- DDL_001 de sql/trusted (filtro sem indice sobre basica_raw seria caro
-- recalculado a cada consulta), mas aqui sem JOIN cross-database.

DROP TABLE IF EXISTS basica_curated_deep;

CREATE TABLE basica_curated_deep AS
SELECT
    id_basica, sg_empresa_icao, sg_empresa_iata, nr_voo, dt_referencia,
    nr_etapa,
    ds_tipo_linha, ds_natureza_tipo_linha, ds_servico_tipo_linha, ds_natureza_etapa,
    hr_partida_real, dt_partida_real, hr_chegada_real, dt_chegada_real,
    sg_icao_origem, sg_iata_origem, nm_municipio_origem, sg_uf_origem, nm_pais_origem,
    sg_icao_destino, sg_iata_destino, nm_municipio_destino, sg_uf_destino, nm_pais_destino,
    sg_equipamento_icao, ds_modelo, ds_matricula,
    km_distancia, nr_horas_voadas
FROM basica_silver
WHERE sg_empresa_icao IN ('GLO', 'AZU')
  AND dt_partida_real >= '2021-01-01';

CREATE INDEX idx_basica_curated_deep_empresa_dt ON basica_curated_deep(sg_empresa_icao, dt_partida_real);

SELECT 'basica_curated_deep_linhas' AS metrica, COUNT(*) AS valor FROM basica_curated_deep;
SELECT 'basica_curated_deep_min_dt' AS metrica, MIN(dt_partida_real) AS valor FROM basica_curated_deep;
SELECT 'basica_curated_deep_max_dt' AS metrica, MAX(dt_partida_real) AS valor FROM basica_curated_deep;
SELECT sg_empresa_icao, COUNT(*) FROM basica_curated_deep GROUP BY sg_empresa_icao;
