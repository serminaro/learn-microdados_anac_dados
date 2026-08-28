-- View tipada equivalente a sql/tratamento/DDL_001_basica_view_typed_sqlite.sql,
-- em dialeto Snowflake (TRY_CAST em vez de CAST para nao quebrar a carga
-- inteira se uma linha tiver lixo -- vira NULL em vez de erro; DATEDIFF
-- para o block time em vez de julianday).
-- Depende da tabela basica_raw, criada por sql/ingestao_snowflake/DDL_001_basica_create_table_snowflake.sql.

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
