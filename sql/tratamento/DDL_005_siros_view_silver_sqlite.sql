-- View silver do SIROS: tipagem sobre siros_raw, todas as 28 colunas de
-- SPEC-007 + dt_arquivo (proveniência).
--
-- Achado (2026-08-31, antes de materializar): dt_registro tem o MESMO tipo
-- de quebra de formato já visto no VRA (SPEC-009 achado 1), na direção
-- oposta -- ISO na era CSV (ate meados de 2024), DD/MM/AAAA HH:MM:SS na
-- era JSON (medido: 4.851.007 linhas ISO, 5.826.375 DD/MM, 0 num terceiro
-- formato). datetime() incondicional teria devolvido NULL silencioso pra
-- mais da metade da tabela. Detectado por GLOB, mesmo padrao do VRA.
--
-- dt_inicio_operacao/dt_fim_operacao NAO tem esse problema: sempre ISO,
-- so mudam de granularidade (datetime completo na era CSV, ex.
-- "2020-03-08 00:00:00"; so data na era JSON, ex. "2024-04-01") -- date()
-- trata os dois corretamente, sem CASE extra.
DROP VIEW IF EXISTS siros_silver;

CREATE VIEW siros_silver AS
SELECT
    NULLIF(cd_empresa, '')           AS cd_empresa,
    NULLIF(nm_empresa, '')           AS nm_empresa,
    NULLIF(nr_voo, '')               AS nr_voo,
    NULLIF(sg_equipamento_icao, '')  AS sg_equipamento_icao,
    NULLIF(fl_opera_segunda, '')     AS fl_opera_segunda,
    NULLIF(fl_opera_terca, '')       AS fl_opera_terca,
    NULLIF(fl_opera_quarta, '')      AS fl_opera_quarta,
    NULLIF(fl_opera_quinta, '')      AS fl_opera_quinta,
    NULLIF(fl_opera_sexta, '')       AS fl_opera_sexta,
    NULLIF(fl_opera_sabado, '')      AS fl_opera_sabado,
    NULLIF(fl_opera_domingo, '')     AS fl_opera_domingo,
    CAST(NULLIF(nr_assentos_ofertados, '') AS INTEGER) AS nr_assentos_ofertados,
    NULLIF(nr_siros, '')             AS nr_siros,
    NULLIF(ds_situacao_siros, '')    AS ds_situacao_siros,
    CASE
        WHEN dt_registro GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]*'
            THEN datetime(dt_registro)
        WHEN dt_registro GLOB '[0-9][0-9]/[0-9][0-9]/[0-9][0-9][0-9][0-9]*'
            THEN datetime(substr(dt_registro,7,4) || '-' || substr(dt_registro,4,2)
                 || '-' || substr(dt_registro,1,2) || ' ' || substr(dt_registro,12,8))
        ELSE NULL
    END AS dt_registro,
    date(dt_inicio_operacao)         AS dt_inicio_operacao,
    date(dt_fim_operacao)            AS dt_fim_operacao,
    NULLIF(ds_natureza_operacao, '') AS ds_natureza_operacao,
    CAST(NULLIF(nr_etapa, '') AS INTEGER) AS nr_etapa,
    NULLIF(cd_origem, '')            AS cd_origem,
    NULLIF(nm_aerodromo_origem, '')  AS nm_aerodromo_origem,
    NULLIF(cd_destino, '')           AS cd_destino,
    NULLIF(nm_aerodromo_destino, '') AS nm_aerodromo_destino,
    time(hr_partida)                 AS hr_partida,
    time(hr_chegada)                 AS hr_chegada,
    NULLIF(ds_tipo_servico, '')      AS ds_tipo_servico,
    NULLIF(ds_objeto_transporte, '') AS ds_objeto_transporte,
    NULLIF(ds_codeshare, '')         AS ds_codeshare,
    date(dt_arquivo)                 AS dt_arquivo
FROM siros_raw;
