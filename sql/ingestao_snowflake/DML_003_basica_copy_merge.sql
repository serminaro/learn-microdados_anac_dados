-- Ultimo passo: carregar o arquivo ja no stage (stg_anac_basica) para a
-- tabela basica_raw, de forma idempotente (MERGE, nao INSERT direto).
-- Rode statement por statement pela extensao do Snowflake no VS Code
-- (botao "Execute" acima de cada bloco), garantindo que o contexto do
-- worksheet esta em database ANAC, schema BASICA antes de comecar.

USE DATABASE anac;
USE SCHEMA basica;

-- 1) Le o arquivo do stage para uma tabela temporaria, com o mesmo formato da raw
CREATE OR REPLACE TEMPORARY TABLE basica_stage_tmp LIKE basica_raw;

COPY INTO basica_stage_tmp
FROM @stg_anac_basica/basica_consolidado_2010_2026.csv.gz
ON_ERROR = 'ABORT_STATEMENT';

-- 2) Merge idempotente: so insere o que ainda nao existe por id_basica
-- (Snowflake nao aceita wildcard "origem.*" dentro de VALUES() no MERGE,
-- por isso a lista de colunas vem explicita, gerada a partir da DDL)
MERGE INTO basica_raw AS destino
USING basica_stage_tmp AS origem
ON destino.id_basica = origem.id_basica
WHEN NOT MATCHED THEN
    INSERT (id_basica,id_empresa,sg_empresa_icao,sg_empresa_iata,nm_empresa,nm_pais,ds_tipo_empresa,nr_voo,nr_singular,id_di,cd_di,ds_di,ds_grupo_di,dt_referencia,nr_ano_referencia,nr_semestre_referencia,nm_semestre_referencia,nr_trimestre_referencia,nm_trimestre_referencia,nr_mes_referencia,nm_mes_referencia,nr_semana_referencia,nm_dia_semana_referencia,nr_dia_referencia,nr_ano_mes_referencia,id_tipo_linha,cd_tipo_linha,ds_tipo_linha,ds_natureza_tipo_linha,ds_servico_tipo_linha,ds_natureza_etapa,hr_partida_real,dt_partida_real,nr_ano_partida_real,nr_semestre_partida_real,nm_semestre_partida_real,nr_trimestre_partida_real,nm_trimestre_partida_real,nr_mes_partida_real,nm_mes_partida_real,nr_semana_partida_real,nm_dia_semana_partida_real,nr_dia_partida_real,nr_ano_mes_partida_real,id_aerodromo_origem,sg_icao_origem,sg_iata_origem,nm_aerodromo_origem,nm_municipio_origem,sg_uf_origem,nm_regiao_origem,nm_pais_origem,nm_continente_origem,nr_etapa,hr_chegada_real,dt_chegada_real,nr_ano_chegada_real,nr_semestre_chegada_real,nm_semestre_chegada_real,nr_trimestre_chegada_real,nm_trimestre_chegada_real,nr_mes_chegada_real,nm_mes_chegada_real,nr_semana_chegada_real,nm_dia_semana_chegada_real,nr_dia_chegada_real,nr_ano_mes_chegada_real,id_equipamento,sg_equipamento_icao,ds_modelo,ds_matricula,id_aerodromo_destino,sg_icao_destino,sg_iata_destino,nm_aerodromo_destino,nm_municipio_destino,sg_uf_destino,nm_regiao_destino,nm_pais_destino,nm_continente_destino,nr_escala_destino,lt_combustivel,nr_assentos_ofertados,kg_payload,km_distancia,nr_passag_pagos,nr_passag_gratis,kg_bagagem_livre,kg_bagagem_excesso,kg_carga_paga,kg_carga_gratis,kg_correio,nr_decolagem,nr_horas_voadas,kg_peso,nr_velocidade_media,nr_pax_gratis_km,nr_carga_paga_km,nr_carga_gratis_km,nr_correio_km,nr_bagagem_paga_km,nr_bagagem_gratis_km,nr_ask,nr_rpk,nr_atk,nr_rtk,id_arquivo,nm_arquivo,nr_linha,dt_sistema,nr_chave,nr_ano_mes_arquivo)
    VALUES (origem.id_basica,origem.id_empresa,origem.sg_empresa_icao,origem.sg_empresa_iata,origem.nm_empresa,origem.nm_pais,origem.ds_tipo_empresa,origem.nr_voo,origem.nr_singular,origem.id_di,origem.cd_di,origem.ds_di,origem.ds_grupo_di,origem.dt_referencia,origem.nr_ano_referencia,origem.nr_semestre_referencia,origem.nm_semestre_referencia,origem.nr_trimestre_referencia,origem.nm_trimestre_referencia,origem.nr_mes_referencia,origem.nm_mes_referencia,origem.nr_semana_referencia,origem.nm_dia_semana_referencia,origem.nr_dia_referencia,origem.nr_ano_mes_referencia,origem.id_tipo_linha,origem.cd_tipo_linha,origem.ds_tipo_linha,origem.ds_natureza_tipo_linha,origem.ds_servico_tipo_linha,origem.ds_natureza_etapa,origem.hr_partida_real,origem.dt_partida_real,origem.nr_ano_partida_real,origem.nr_semestre_partida_real,origem.nm_semestre_partida_real,origem.nr_trimestre_partida_real,origem.nm_trimestre_partida_real,origem.nr_mes_partida_real,origem.nm_mes_partida_real,origem.nr_semana_partida_real,origem.nm_dia_semana_partida_real,origem.nr_dia_partida_real,origem.nr_ano_mes_partida_real,origem.id_aerodromo_origem,origem.sg_icao_origem,origem.sg_iata_origem,origem.nm_aerodromo_origem,origem.nm_municipio_origem,origem.sg_uf_origem,origem.nm_regiao_origem,origem.nm_pais_origem,origem.nm_continente_origem,origem.nr_etapa,origem.hr_chegada_real,origem.dt_chegada_real,origem.nr_ano_chegada_real,origem.nr_semestre_chegada_real,origem.nm_semestre_chegada_real,origem.nr_trimestre_chegada_real,origem.nm_trimestre_chegada_real,origem.nr_mes_chegada_real,origem.nm_mes_chegada_real,origem.nr_semana_chegada_real,origem.nm_dia_semana_chegada_real,origem.nr_dia_chegada_real,origem.nr_ano_mes_chegada_real,origem.id_equipamento,origem.sg_equipamento_icao,origem.ds_modelo,origem.ds_matricula,origem.id_aerodromo_destino,origem.sg_icao_destino,origem.sg_iata_destino,origem.nm_aerodromo_destino,origem.nm_municipio_destino,origem.sg_uf_destino,origem.nm_regiao_destino,origem.nm_pais_destino,origem.nm_continente_destino,origem.nr_escala_destino,origem.lt_combustivel,origem.nr_assentos_ofertados,origem.kg_payload,origem.km_distancia,origem.nr_passag_pagos,origem.nr_passag_gratis,origem.kg_bagagem_livre,origem.kg_bagagem_excesso,origem.kg_carga_paga,origem.kg_carga_gratis,origem.kg_correio,origem.nr_decolagem,origem.nr_horas_voadas,origem.kg_peso,origem.nr_velocidade_media,origem.nr_pax_gratis_km,origem.nr_carga_paga_km,origem.nr_carga_gratis_km,origem.nr_correio_km,origem.nr_bagagem_paga_km,origem.nr_bagagem_gratis_km,origem.nr_ask,origem.nr_rpk,origem.nr_atk,origem.nr_rtk,origem.id_arquivo,origem.nm_arquivo,origem.nr_linha,origem.dt_sistema,origem.nr_chave,origem.nr_ano_mes_arquivo);

-- 3) Conferencia -- deve dar 2409265, igual ao SQLite
SELECT COUNT(*) AS total_linhas FROM basica_raw;

SELECT nr_ano_mes_arquivo, COUNT(*) AS n
FROM basica_raw
GROUP BY nr_ano_mes_arquivo
ORDER BY nr_ano_mes_arquivo;

-- 4) Teste de fumaca na view tipada -- deve bater com o que ja calculamos
-- (GOL, junho/2026: km_medio ~1177, block_min_medio ~123, n ~20807)
SELECT
    ROUND(AVG(km_distancia)) AS km_medio,
    ROUND(AVG(bloco_tempo_min)) AS block_min_medio,
    COUNT(*) AS n
FROM basica_typed
WHERE sg_empresa_icao = 'GLO' AND nr_ano_mes_arquivo = '2026-06' AND bloco_tempo_min IS NOT NULL;
