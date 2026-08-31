-- Camada silver: vra_silver
-- Todas as 12 colunas de vra_raw, tipadas e organizadas por assunto
-- (identificacao -> rota -> horarios -> situacao), comentario por coluna
-- vindo de SPEC-006. Primeira view "silver" do VRA (vra_typed nunca foi
-- implementado, so proposto em SPEC-009 v1 -- este arquivo substitui essa
-- proposta).
--
-- Convencoes: TEXT vazio vira NULL (NULLIF); horarios via datetime() do
-- SQLite (nao CAST AS DATETIME, mesma razao de basica_silver: SQLite
-- trata tipo nao reconhecido como afinidade NUMERIC, risco de conversao
-- indevida). Mantido timestamp unico (nao separado em data+hora como a
-- Basica) -- decisao registrada em SPEC-009 Sec.6, nao revisada aqui.
--
-- Achado 1 (2026-08-31, validacao desta view): o formato de data do VRA
-- muda de novo, alem do que SPEC-006/SPEC-009 tinham amostrado -- de
-- 2010-01 a 2018-12 o arquivo publica "DD/MM/AAAA HH:MM" (sem segundos);
-- de 2019-01 em diante, ISO "AAAA-MM-DD HH:MM:SS". Os 4 campos de
-- horario abaixo detectam o formato por padrao de caractere (GLOB) e
-- convertem os dois para o mesmo DATETIME de saida.
--
-- Achado 2: os arquivos de 2020-02 e 2020-03 (581.768 linhas) tem
-- "Microsoft.SqlServer.Dts.Pipeline.BlobColumn" (vazamento de objeto
-- interno de ferramenta ETL, aparentemente da propria ANAC) como valor
-- literal em dt_hr_partida_prevista, dt_hr_partida_real,
-- dt_hr_chegada_prevista, dt_hr_chegada_real e ds_situacao_voo -- so
-- essas 5 colunas, confirmado por amostragem de linha inteira; as demais
-- (empresa, voo, rota) estao intactas nesses dois meses. Tratamento:
-- essas 5 colunas viram NULL quando o valor bate com o padrao da falha;
-- a linha inteira NAO e descartada, o resto do dado dela e valido.

DROP VIEW IF EXISTS vra_silver;

CREATE VIEW vra_silver AS
SELECT
    -- ===== IDENTIFICACAO =====
    -- Código ICAO da empresa, mesma convenção da Básica (ex.: SKU)
    NULLIF(sg_empresa_icao, '') AS sg_empresa_icao,
    -- Número comercial do voo
    NULLIF(nr_voo, '') AS nr_voo,
    -- Código de autorização/DI — papel exato não confirmado (mesma incerteza do ID_DI na Básica)
    NULLIF(cd_autorizacao_di, '') AS cd_autorizacao_di,
    -- Código do tipo de linha — categorias exatas (doméstica/internacional) não confirmadas
    NULLIF(cd_tipo_linha, '') AS cd_tipo_linha,
    -- ===== ROTA =====
    -- Código ICAO do aeródromo de origem, mesmo domínio de valores da Básica
    NULLIF(sg_icao_origem, '') AS sg_icao_origem,
    -- Código ICAO do aeródromo de destino
    NULLIF(sg_icao_destino, '') AS sg_icao_destino,
    -- ===== HORARIOS =====
    -- Data+hora programada de partida — coluna que a Básica não tem. NULL se vazio,
    -- corrompido (2020-02/03) ou formato não reconhecido; converte DD/MM/AAAA e ISO.
    CASE
        WHEN dt_hr_partida_prevista GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]*'
            THEN datetime(dt_hr_partida_prevista)
        WHEN dt_hr_partida_prevista GLOB '[0-9][0-9]/[0-9][0-9]/[0-9][0-9][0-9][0-9]*'
            THEN datetime(substr(dt_hr_partida_prevista,7,4) || '-' || substr(dt_hr_partida_prevista,4,2)
                 || '-' || substr(dt_hr_partida_prevista,1,2) || ' ' || substr(dt_hr_partida_prevista,12,5) || ':00')
        ELSE NULL
    END AS dt_hr_partida_prevista,
    -- Data+hora real de partida (mesmo tratamento acima)
    CASE
        WHEN dt_hr_partida_real GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]*'
            THEN datetime(dt_hr_partida_real)
        WHEN dt_hr_partida_real GLOB '[0-9][0-9]/[0-9][0-9]/[0-9][0-9][0-9][0-9]*'
            THEN datetime(substr(dt_hr_partida_real,7,4) || '-' || substr(dt_hr_partida_real,4,2)
                 || '-' || substr(dt_hr_partida_real,1,2) || ' ' || substr(dt_hr_partida_real,12,5) || ':00')
        ELSE NULL
    END AS dt_hr_partida_real,
    -- Data+hora programada de chegada (mesmo tratamento acima)
    CASE
        WHEN dt_hr_chegada_prevista GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]*'
            THEN datetime(dt_hr_chegada_prevista)
        WHEN dt_hr_chegada_prevista GLOB '[0-9][0-9]/[0-9][0-9]/[0-9][0-9][0-9][0-9]*'
            THEN datetime(substr(dt_hr_chegada_prevista,7,4) || '-' || substr(dt_hr_chegada_prevista,4,2)
                 || '-' || substr(dt_hr_chegada_prevista,1,2) || ' ' || substr(dt_hr_chegada_prevista,12,5) || ':00')
        ELSE NULL
    END AS dt_hr_chegada_prevista,
    -- Data+hora real de chegada (mesmo tratamento acima)
    CASE
        WHEN dt_hr_chegada_real GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]*'
            THEN datetime(dt_hr_chegada_real)
        WHEN dt_hr_chegada_real GLOB '[0-9][0-9]/[0-9][0-9]/[0-9][0-9][0-9][0-9]*'
            THEN datetime(substr(dt_hr_chegada_real,7,4) || '-' || substr(dt_hr_chegada_real,4,2)
                 || '-' || substr(dt_hr_chegada_real,1,2) || ' ' || substr(dt_hr_chegada_real,12,5) || ':00')
        ELSE NULL
    END AS dt_hr_chegada_real,
    -- ===== SITUACAO =====
    -- Situação do voo, ex.: REALIZADO, CANCELADO — NULL se vazio ou corrompido (2020-02/03)
    CASE
        WHEN ds_situacao_voo = '' OR ds_situacao_voo LIKE '%BlobColumn%' THEN NULL
        ELSE ds_situacao_voo
    END AS ds_situacao_voo,
    -- Motivo de atraso/cancelamento quando aplicável — domínio de valores não levantado
    NULLIF(cd_justificativa, '') AS cd_justificativa
FROM vra_raw;
