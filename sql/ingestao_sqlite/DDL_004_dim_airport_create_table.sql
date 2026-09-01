-- Tabela dimensão de aeródromos: localização e fuso horário.
-- Fonte: data/aerodromos_enriquecido.csv (863 aeródromos distintos, 5
-- SEM_MATCH excluídos por falta de coordenada), sem HOR_VERAO_ATUAL e
-- JA_TEVE_HORARIO_VERAO (pedido do autor, 2026-08-31).
-- utc_offset é REAL, não INTEGER: existem fusos de meia hora (-3.5, 3.5,
-- 4.5, 5.5) na fonte -- achado que só apareceu ao completar de 283 para
-- 858 linhas.
-- municipio_ourairports/pais_iso aceitam NULL: os 8 aeródromos resolvidos
-- manualmente (MANUAL_KEYWORD, aeroporto fechado ou código reatribuído)
-- não têm essa informação na fonte.
DROP TABLE IF EXISTS dim_airport_location_time_zone;

CREATE TABLE dim_airport_location_time_zone (
    base_icao              TEXT PRIMARY KEY,
    base_iata              TEXT,
    latitude               REAL NOT NULL,
    longitude              REAL NOT NULL,
    tz_iana                TEXT NOT NULL,
    utc_offset             REAL NOT NULL,
    nome_ourairports       TEXT NOT NULL,
    municipio_ourairports  TEXT,
    pais_iso               TEXT,
    tipo_ourairports       TEXT NOT NULL
);
