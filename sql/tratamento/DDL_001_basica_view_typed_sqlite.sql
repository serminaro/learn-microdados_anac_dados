-- View tipada com as colunas que usamos nas analises (destinos, etapa media,
-- utilizacao de frota, tempo de solo, sobra). Dialeto SQLite (julianday, NULLIF).
-- Colunas confirmadas empiricamente antes de tipar (ver conversa): nr_horas_voadas
-- usa virgula decimal, nr_ask/nr_rpk/nr_atk/nr_rtk/km_distancia/nr_assentos_ofertados/
-- kg_payload sao inteiros puros, id_basica e nr_voo sao sempre numericos (nr_voo fica
-- como TEXT mesmo assim, para nao perder zero a esquerda se algum dia aparecer).
-- ds_matricula vem vazia em ~12% das linhas (294.875 de 2.409.265) -- normal,
-- nao e toda etapa que tem aeronave identificada no boletim.

DROP VIEW IF EXISTS basica_typed;

CREATE VIEW basica_typed AS
SELECT
    CAST(id_basica AS INTEGER)              AS id_basica,
    CAST(id_empresa AS INTEGER)             AS id_empresa,
    sg_empresa_icao,
    sg_empresa_iata,
    nm_empresa,
    ds_tipo_empresa,
    nr_voo,
    ds_natureza_etapa,
    CAST(nr_etapa AS INTEGER)               AS nr_etapa,
    sg_iata_origem,
    sg_iata_destino,
    NULLIF(dt_partida_real, '') || ' ' || NULLIF(hr_partida_real, '') AS partida_ts,
    NULLIF(dt_chegada_real, '') || ' ' || NULLIF(hr_chegada_real, '') AS chegada_ts,
    NULLIF(ds_matricula, '')                AS ds_matricula,
    sg_equipamento_icao,
    ds_modelo,
    CAST(km_distancia AS INTEGER)           AS km_distancia,
    CAST(nr_assentos_ofertados AS INTEGER)  AS nr_assentos_ofertados,
    CAST(kg_payload AS INTEGER)             AS kg_payload,
    CAST(REPLACE(nr_horas_voadas, ',', '.') AS REAL) AS nr_horas_voadas,
    CAST(nr_ask AS INTEGER)                 AS nr_ask,
    CAST(nr_rpk AS INTEGER)                 AS nr_rpk,
    CAST(nr_atk AS INTEGER)                 AS nr_atk,
    CAST(nr_rtk AS INTEGER)                 AS nr_rtk,
    CAST(nr_ano_referencia AS INTEGER)      AS nr_ano_referencia,
    CAST(nr_mes_referencia AS INTEGER)      AS nr_mes_referencia,
    nr_ano_mes_arquivo,
    -- block time em minutos, deriva de partida/chegada; fica NULL se alguma faltar
    CASE
        WHEN dt_partida_real = '' OR hr_partida_real = '' OR dt_chegada_real = '' OR hr_chegada_real = ''
            THEN NULL
        ELSE (julianday(dt_chegada_real || ' ' || hr_chegada_real)
              - julianday(dt_partida_real || ' ' || hr_partida_real)) * 24 * 60
    END AS bloco_tempo_min
FROM basica_raw;
