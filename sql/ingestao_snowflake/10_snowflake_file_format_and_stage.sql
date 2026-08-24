-- Fase A do plano Snowflake (docs/plano_objetos_snowflake.md): formaliza
-- como objetos nomeados o File Format e o parsing do Stage que ate aqui
-- viviam inline dentro do CREATE STAGE de 07_snowflake_setup_and_load.sql,
-- neste mesmo diretorio.
-- Sem mudanca de comportamento: mesmo parsing (CSV, aspas opcionais, 1a
-- linha de cabecalho pulada) que ja estava em producao, so deixa de ficar
-- implicito. Pressupoe que 07 ja rodou (warehouse/db/schema/stage ja existem).

USE WAREHOUSE wh_anac;
USE DATABASE anac;
USE SCHEMA basica;

-- 1) File Format nomeado, reutilizavel por qualquer COPY INTO / stage futuro
-- (Pipe da Fase C, por exemplo), em vez de repetir a definicao em cada lugar.
CREATE OR REPLACE FILE FORMAT anac_basica_csv_ff
    TYPE = CSV
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    SKIP_HEADER = 1
    COMMENT = 'Parsing do CSV consolidado da tabela Basica (UTF-8, gerado por src/ingestao_snowflake/05_export_csv.py)';

-- 2) Stage existente passa a referenciar o File Format nomeado.
-- ALTER, nao CREATE OR REPLACE STAGE: o stage pode ja ter o CSV enviado via
-- PUT (script 07, passo 4), e CREATE OR REPLACE STAGE recria o stage do
-- zero, descartando os arquivos internos ja carregados. ALTER so troca a
-- propriedade de parsing, preservando o conteudo.
ALTER STAGE IF EXISTS stg_anac_basica SET FILE_FORMAT = (FORMAT_NAME = 'anac_basica_csv_ff');

-- 3) Conferencia
SHOW FILE FORMATS LIKE 'anac_basica_csv_ff';
DESC STAGE stg_anac_basica;
LIST @stg_anac_basica;
