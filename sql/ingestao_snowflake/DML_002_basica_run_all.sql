-- Roteiro unico e pronto para rodar via:
--   snow sql -c anac -f sql/ingestao_snowflake/DML_002_basica_run_all.sql
-- Junta infra + tabela + view + stage + upload + carga idempotente + conferencia.
-- Combina sql/ingestao_snowflake/DDL_001_basica_create_table_snowflake.sql + sql/tratamento/DDL_002_basica_view_typed_snowflake.sql
-- com sql/ingestao_snowflake/DML_001_basica_setup_and_load.sql.

-- 1) Infraestrutura minima -----------------------------------------------
CREATE WAREHOUSE IF NOT EXISTS wh_anac
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE;

CREATE DATABASE IF NOT EXISTS anac;
CREATE SCHEMA IF NOT EXISTS anac.basica;

USE WAREHOUSE wh_anac;
USE DATABASE anac;
USE SCHEMA basica;

-- 2) Tabela raw -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS basica_raw (
    id_basica TEXT NOT NULL,
    id_empresa TEXT,
    sg_empresa_icao TEXT,
    sg_empresa_iata TEXT,
    nm_empresa TEXT,
    nm_pais TEXT,
    ds_tipo_empresa TEXT,
    nr_voo TEXT,
    nr_singular TEXT,
    id_di TEXT,
    cd_di TEXT,
    ds_di TEXT,
    ds_grupo_di TEXT,
    dt_referencia TEXT,
    nr_ano_referencia TEXT,
    nr_semestre_referencia TEXT,
    nm_semestre_referencia TEXT,
    nr_trimestre_referencia TEXT,
    nm_trimestre_referencia TEXT,
    nr_mes_referencia TEXT,
    nm_mes_referencia TEXT,
    nr_semana_referencia TEXT,
    nm_dia_semana_referencia TEXT,
    nr_dia_referencia TEXT,
    nr_ano_mes_referencia TEXT,
    id_tipo_linha TEXT,
    cd_tipo_linha TEXT,
    ds_tipo_linha TEXT,
    ds_natureza_tipo_linha TEXT,
    ds_servico_tipo_linha TEXT,
    ds_natureza_etapa TEXT,
    hr_partida_real TEXT,
    dt_partida_real TEXT,
    nr_ano_partida_real TEXT,
    nr_semestre_partida_real TEXT,
    nm_semestre_partida_real TEXT,
    nr_trimestre_partida_real TEXT,
    nm_trimestre_partida_real TEXT,
    nr_mes_partida_real TEXT,
    nm_mes_partida_real TEXT,
    nr_semana_partida_real TEXT,
    nm_dia_semana_partida_real TEXT,
    nr_dia_partida_real TEXT,
    nr_ano_mes_partida_real TEXT,
    id_aerodromo_origem TEXT,
    sg_icao_origem TEXT,
    sg_iata_origem TEXT,
    nm_aerodromo_origem TEXT,
    nm_municipio_origem TEXT,
    sg_uf_origem TEXT,
    nm_regiao_origem TEXT,
    nm_pais_origem TEXT,
    nm_continente_origem TEXT,
    nr_etapa TEXT,
    hr_chegada_real TEXT,
    dt_chegada_real TEXT,
    nr_ano_chegada_real TEXT,
    nr_semestre_chegada_real TEXT,
    nm_semestre_chegada_real TEXT,
    nr_trimestre_chegada_real TEXT,
    nm_trimestre_chegada_real TEXT,
    nr_mes_chegada_real TEXT,
    nm_mes_chegada_real TEXT,
    nr_semana_chegada_real TEXT,
    nm_dia_semana_chegada_real TEXT,
    nr_dia_chegada_real TEXT,
    nr_ano_mes_chegada_real TEXT,
    id_equipamento TEXT,
    sg_equipamento_icao TEXT,
    ds_modelo TEXT,
    ds_matricula TEXT,
    id_aerodromo_destino TEXT,
    sg_icao_destino TEXT,
    sg_iata_destino TEXT,
    nm_aerodromo_destino TEXT,
    nm_municipio_destino TEXT,
    sg_uf_destino TEXT,
    nm_regiao_destino TEXT,
    nm_pais_destino TEXT,
    nm_continente_destino TEXT,
    nr_escala_destino TEXT,
    lt_combustivel TEXT,
    nr_assentos_ofertados TEXT,
    kg_payload TEXT,
    km_distancia TEXT,
    nr_passag_pagos TEXT,
    nr_passag_gratis TEXT,
    kg_bagagem_livre TEXT,
    kg_bagagem_excesso TEXT,
    kg_carga_paga TEXT,
    kg_carga_gratis TEXT,
    kg_correio TEXT,
    nr_decolagem TEXT,
    nr_horas_voadas TEXT,
    kg_peso TEXT,
    nr_velocidade_media TEXT,
    nr_pax_gratis_km TEXT,
    nr_carga_paga_km TEXT,
    nr_carga_gratis_km TEXT,
    nr_correio_km TEXT,
    nr_bagagem_paga_km TEXT,
    nr_bagagem_gratis_km TEXT,
    nr_ask TEXT,
    nr_rpk TEXT,
    nr_atk TEXT,
    nr_rtk TEXT,
    id_arquivo TEXT,
    nm_arquivo TEXT,
    nr_linha TEXT,
    dt_sistema TEXT,
    nr_chave TEXT,
    nr_ano_mes_arquivo TEXT NOT NULL,
    PRIMARY KEY (id_basica)   -- informativo, Snowflake nao aplica de fato
);

-- 3) View tipada --------------------------------------------------------
CREATE OR REPLACE VIEW basica_typed AS
SELECT
    TRY_CAST(id_basica AS INTEGER)              AS id_basica,
    TRY_CAST(id_empresa AS INTEGER)              AS id_empresa,
    sg_empresa_icao,
    sg_empresa_iata,
    nm_empresa,
    ds_tipo_empresa,
    nr_voo,
    ds_natureza_etapa,
    TRY_CAST(nr_etapa AS INTEGER)                AS nr_etapa,
    sg_iata_origem,
    sg_iata_destino,
    TRY_TO_TIMESTAMP_NTZ(dt_partida_real || ' ' || hr_partida_real, 'YYYY-MM-DD HH24:MI:SS') AS partida_ts,
    TRY_TO_TIMESTAMP_NTZ(dt_chegada_real || ' ' || hr_chegada_real, 'YYYY-MM-DD HH24:MI:SS') AS chegada_ts,
    NULLIF(ds_matricula, '')                     AS ds_matricula,
    sg_equipamento_icao,
    ds_modelo,
    TRY_CAST(km_distancia AS INTEGER)            AS km_distancia,
    TRY_CAST(nr_assentos_ofertados AS INTEGER)   AS nr_assentos_ofertados,
    TRY_CAST(kg_payload AS INTEGER)              AS kg_payload,
    TRY_CAST(REPLACE(nr_horas_voadas, ',', '.') AS FLOAT) AS nr_horas_voadas,
    TRY_CAST(nr_ask AS INTEGER)                  AS nr_ask,
    TRY_CAST(nr_rpk AS INTEGER)                  AS nr_rpk,
    TRY_CAST(nr_atk AS INTEGER)                  AS nr_atk,
    TRY_CAST(nr_rtk AS INTEGER)                  AS nr_rtk,
    TRY_CAST(nr_ano_referencia AS INTEGER)       AS nr_ano_referencia,
    TRY_CAST(nr_mes_referencia AS INTEGER)       AS nr_mes_referencia,
    nr_ano_mes_arquivo,
    DATEDIFF(
        'minute',
        TRY_TO_TIMESTAMP_NTZ(dt_partida_real || ' ' || hr_partida_real, 'YYYY-MM-DD HH24:MI:SS'),
        TRY_TO_TIMESTAMP_NTZ(dt_chegada_real || ' ' || hr_chegada_real, 'YYYY-MM-DD HH24:MI:SS')
    ) AS bloco_tempo_min
FROM basica_raw;

-- 4) File Format nomeado + Stage interno -----------------------------------
-- Mesmo File Format de sql/ingestao_snowflake/DDL_002_basica_file_format_and_stage.sql
-- (Fase A do plano), definido aqui tambem para o roteiro ficar autossuficiente.
CREATE OR REPLACE FILE FORMAT anac_basica_csv_ff
    TYPE = CSV
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    SKIP_HEADER = 1
    COMMENT = 'Parsing do CSV consolidado da tabela Basica (UTF-8, gerado por src/ingestao_snowflake/SRC_001_basica_export_csv.py)';

CREATE STAGE IF NOT EXISTS stg_anac_basica
    FILE_FORMAT = (FORMAT_NAME = 'anac_basica_csv_ff');

-- 5) Upload do CSV local (PUT roda no cliente, precisa do arquivo local existir) --
-- O caminho e' de maquina, nao de servidor: PUT le o arquivo no cliente. Por isso
-- entra como variavel do Snowflake CLI (-D), nao cravado (DEC-011). Rode com:
--   Linux:   snow sql -c anac -D "REPO_ROOT=/home/bruno/Projetos/learn-microdados_anac_dados" -f <este arquivo>
--   Windows: snow sql -c anac -D "REPO_ROOT=D:/Projetos/learn-microdados_anac_dados" -f <este arquivo>
-- Use barra normal (/) tambem no Windows: o PUT espera URI, nao caminho nativo.
PUT file://&{REPO_ROOT}/data/anac/basica_consolidado_2010_2026.csv
    @stg_anac_basica AUTO_COMPRESS=TRUE OVERWRITE=FALSE;

-- 6) Carga idempotente com MERGE ------------------------------------------
CREATE OR REPLACE TEMPORARY TABLE basica_stage_tmp LIKE basica_raw;

COPY INTO basica_stage_tmp
FROM @stg_anac_basica/basica_consolidado_2010_2026.csv.gz
ON_ERROR = 'ABORT_STATEMENT';

MERGE INTO basica_raw AS destino
USING basica_stage_tmp AS origem
ON destino.id_basica = origem.id_basica
WHEN NOT MATCHED THEN
    INSERT (id_basica,id_empresa,sg_empresa_icao,sg_empresa_iata,nm_empresa,nm_pais,ds_tipo_empresa,nr_voo,nr_singular,id_di,cd_di,ds_di,ds_grupo_di,dt_referencia,nr_ano_referencia,nr_semestre_referencia,nm_semestre_referencia,nr_trimestre_referencia,nm_trimestre_referencia,nr_mes_referencia,nm_mes_referencia,nr_semana_referencia,nm_dia_semana_referencia,nr_dia_referencia,nr_ano_mes_referencia,id_tipo_linha,cd_tipo_linha,ds_tipo_linha,ds_natureza_tipo_linha,ds_servico_tipo_linha,ds_natureza_etapa,hr_partida_real,dt_partida_real,nr_ano_partida_real,nr_semestre_partida_real,nm_semestre_partida_real,nr_trimestre_partida_real,nm_trimestre_partida_real,nr_mes_partida_real,nm_mes_partida_real,nr_semana_partida_real,nm_dia_semana_partida_real,nr_dia_partida_real,nr_ano_mes_partida_real,id_aerodromo_origem,sg_icao_origem,sg_iata_origem,nm_aerodromo_origem,nm_municipio_origem,sg_uf_origem,nm_regiao_origem,nm_pais_origem,nm_continente_origem,nr_etapa,hr_chegada_real,dt_chegada_real,nr_ano_chegada_real,nr_semestre_chegada_real,nm_semestre_chegada_real,nr_trimestre_chegada_real,nm_trimestre_chegada_real,nr_mes_chegada_real,nm_mes_chegada_real,nr_semana_chegada_real,nm_dia_semana_chegada_real,nr_dia_chegada_real,nr_ano_mes_chegada_real,id_equipamento,sg_equipamento_icao,ds_modelo,ds_matricula,id_aerodromo_destino,sg_icao_destino,sg_iata_destino,nm_aerodromo_destino,nm_municipio_destino,sg_uf_destino,nm_regiao_destino,nm_pais_destino,nm_continente_destino,nr_escala_destino,lt_combustivel,nr_assentos_ofertados,kg_payload,km_distancia,nr_passag_pagos,nr_passag_gratis,kg_bagagem_livre,kg_bagagem_excesso,kg_carga_paga,kg_carga_gratis,kg_correio,nr_decolagem,nr_horas_voadas,kg_peso,nr_velocidade_media,nr_pax_gratis_km,nr_carga_paga_km,nr_carga_gratis_km,nr_correio_km,nr_bagagem_paga_km,nr_bagagem_gratis_km,nr_ask,nr_rpk,nr_atk,nr_rtk,id_arquivo,nm_arquivo,nr_linha,dt_sistema,nr_chave,nr_ano_mes_arquivo)
    VALUES (origem.id_basica,origem.id_empresa,origem.sg_empresa_icao,origem.sg_empresa_iata,origem.nm_empresa,origem.nm_pais,origem.ds_tipo_empresa,origem.nr_voo,origem.nr_singular,origem.id_di,origem.cd_di,origem.ds_di,origem.ds_grupo_di,origem.dt_referencia,origem.nr_ano_referencia,origem.nr_semestre_referencia,origem.nm_semestre_referencia,origem.nr_trimestre_referencia,origem.nm_trimestre_referencia,origem.nr_mes_referencia,origem.nm_mes_referencia,origem.nr_semana_referencia,origem.nm_dia_semana_referencia,origem.nr_dia_referencia,origem.nr_ano_mes_referencia,origem.id_tipo_linha,origem.cd_tipo_linha,origem.ds_tipo_linha,origem.ds_natureza_tipo_linha,origem.ds_servico_tipo_linha,origem.ds_natureza_etapa,origem.hr_partida_real,origem.dt_partida_real,origem.nr_ano_partida_real,origem.nr_semestre_partida_real,origem.nm_semestre_partida_real,origem.nr_trimestre_partida_real,origem.nm_trimestre_partida_real,origem.nr_mes_partida_real,origem.nm_mes_partida_real,origem.nr_semana_partida_real,origem.nm_dia_semana_partida_real,origem.nr_dia_partida_real,origem.nr_ano_mes_partida_real,origem.id_aerodromo_origem,origem.sg_icao_origem,origem.sg_iata_origem,origem.nm_aerodromo_origem,origem.nm_municipio_origem,origem.sg_uf_origem,origem.nm_regiao_origem,origem.nm_pais_origem,origem.nm_continente_origem,origem.nr_etapa,origem.hr_chegada_real,origem.dt_chegada_real,origem.nr_ano_chegada_real,origem.nr_semestre_chegada_real,origem.nm_semestre_chegada_real,origem.nr_trimestre_chegada_real,origem.nm_trimestre_chegada_real,origem.nr_mes_chegada_real,origem.nm_mes_chegada_real,origem.nr_semana_chegada_real,origem.nm_dia_semana_chegada_real,origem.nr_dia_chegada_real,origem.nr_ano_mes_chegada_real,origem.id_equipamento,origem.sg_equipamento_icao,origem.ds_modelo,origem.ds_matricula,origem.id_aerodromo_destino,origem.sg_icao_destino,origem.sg_iata_destino,origem.nm_aerodromo_destino,origem.nm_municipio_destino,origem.sg_uf_destino,origem.nm_regiao_destino,origem.nm_pais_destino,origem.nm_continente_destino,origem.nr_escala_destino,origem.lt_combustivel,origem.nr_assentos_ofertados,origem.kg_payload,origem.km_distancia,origem.nr_passag_pagos,origem.nr_passag_gratis,origem.kg_bagagem_livre,origem.kg_bagagem_excesso,origem.kg_carga_paga,origem.kg_carga_gratis,origem.kg_correio,origem.nr_decolagem,origem.nr_horas_voadas,origem.kg_peso,origem.nr_velocidade_media,origem.nr_pax_gratis_km,origem.nr_carga_paga_km,origem.nr_carga_gratis_km,origem.nr_correio_km,origem.nr_bagagem_paga_km,origem.nr_bagagem_gratis_km,origem.nr_ask,origem.nr_rpk,origem.nr_atk,origem.nr_rtk,origem.id_arquivo,origem.nm_arquivo,origem.nr_linha,origem.dt_sistema,origem.nr_chave,origem.nr_ano_mes_arquivo);

-- 7) Conferencia ------------------------------------------------------------
SELECT COUNT(*) AS total_linhas FROM basica_raw;   -- esperado: 2409265

SELECT nr_ano_mes_arquivo, COUNT(*) AS n
FROM basica_raw
GROUP BY nr_ano_mes_arquivo
ORDER BY nr_ano_mes_arquivo;

SELECT
    ROUND(AVG(km_distancia)) AS km_medio,
    ROUND(AVG(bloco_tempo_min)) AS block_min_medio,
    COUNT(*) AS n
FROM basica_typed
WHERE sg_empresa_icao = 'GLO' AND nr_ano_mes_arquivo = '2026-06' AND bloco_tempo_min IS NOT NULL;
-- esperado: km_medio ~1177, block_min_medio ~123, n ~20807
