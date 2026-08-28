-- Roteiro completo para rodar no SnowSQL (ou no editor do Snowsight, colando
-- em blocos) depois que a conta/usuario/warehouse existirem.
-- Substitua <SEU_USUARIO>, <SUA_SENHA_OU_KEYPAIR> etc conforme seu setup.

-- 1) Infraestrutura minima -----------------------------------------------
CREATE WAREHOUSE IF NOT EXISTS wh_anac
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60          -- desliga sozinho 60s sem uso, controla custo
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE;

CREATE DATABASE IF NOT EXISTS anac;
CREATE SCHEMA IF NOT EXISTS anac.basica;

USE WAREHOUSE wh_anac;
USE DATABASE anac;
USE SCHEMA basica;

-- 2) Tabela raw + view tipada ---------------------------------------------
-- Rode DDL_001_basica_create_table_snowflake.sql, neste mesmo diretorio (CREATE TABLE basica_raw), e
-- sql/tratamento/DDL_002_basica_view_typed_snowflake.sql (CREATE VIEW basica_typed) aqui.

-- 3) Stage interno -----------------------------------------------------------
-- Cria o stage sem parsing proprio; o File Format nomeado e a associacao ao
-- stage vivem em DDL_002_basica_file_format_and_stage.sql, neste mesmo diretorio
-- (Fase A do plano), rode-o logo em seguida para o COPY INTO do passo 5 funcionar.
CREATE STAGE IF NOT EXISTS stg_anac_basica;

-- 4) Upload do CSV local para o stage (rodar no terminal via Snowflake CLI, nao aqui) --
-- snow sql -c anac
-- USE DATABASE anac; USE SCHEMA basica;
-- PUT file:///home/bruno/Projetos/learn-microdados_anac_dados/data/anac/basica_consolidado_2010_2026.csv @stg_anac_basica AUTO_COMPRESS=TRUE;
--   -- isso comprime em .gz localmente antes de subir; para 2GB de CSV,
--   -- espere uns minutos dependendo da sua banda de upload.
-- (a conexao "anac" e criada com `snow connection add`, ver guia)

-- 5) Carga idempotente com MERGE (recomendado) ----------------------------
-- Snowflake nao aplica PRIMARY KEY de verdade (ver nota no DDL), entao
-- COPY INTO simples duplicaria linhas se voce rodar 2x. MERGE evita isso.

CREATE OR REPLACE TEMPORARY TABLE basica_stage_tmp LIKE basica_raw;

COPY INTO basica_stage_tmp
FROM @stg_anac_basica/basica_consolidado_2010_2026.csv.gz
ON_ERROR = 'ABORT_STATEMENT';

MERGE INTO basica_raw AS destino
USING basica_stage_tmp AS origem
ON destino.id_basica = origem.id_basica
WHEN NOT MATCHED THEN
    INSERT VALUES (origem.*);

-- 6) Conferencia ------------------------------------------------------------
SELECT COUNT(*) AS total_linhas FROM basica_raw;   -- esperado: 2409265
SELECT nr_ano_mes_arquivo, COUNT(*) FROM basica_raw GROUP BY 1 ORDER BY 1;

-- 7) Teste de fumaca na view tipada (deve bater com o que calculamos antes) --
SELECT
    ROUND(AVG(km_distancia)) AS km_medio,
    ROUND(AVG(bloco_tempo_min)) AS block_min_medio,
    COUNT(*) AS n
FROM basica_typed
WHERE sg_empresa_icao = 'GLO' AND nr_ano_mes_arquivo = '2026-06' AND bloco_tempo_min IS NOT NULL;
-- esperado: km_medio ~1177, block_min_medio ~123, n ~20807
