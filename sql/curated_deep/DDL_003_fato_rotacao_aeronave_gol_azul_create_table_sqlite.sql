-- Camada curated_deep: fato_rotacao_aeronave_gol_azul (db/anac_basica.sqlite)
-- Grao: uma linha por etapa de basica_curated_deep, enriquecida com:
--   (a) rotacao por matricula (sequencia, destino/chegada da etapa anterior,
--       continuidade espacial, tempo de solo)
--   (b) validacao temporal contra nr_horas_voadas
--   (c) validacao geodesica de km_distancia via dim_airport (haversine,
--       lei dos cossenos esfericos)
--
-- Achado que mudou o desenho original (medido antes de construir, nao
-- assumido): dt_partida_real/hr_partida_real e dt_chegada_real/hr_chegada_real
-- NAO sao horario local por aeroporto -- sao um unico referencial (ANAC),
-- confirmado testando rotas de fuso conhecido e diferente (SBKP->KFLL,
-- Miami UTC-5; SBKP->SBRB, Acre UTC-5, ambas partindo de UTC-3): subtracao
-- ingenua bate exato com nr_horas_voadas em 100% de 2.743.964 linhas
-- (delta <= 0,00003h, ~0,1s). Por isso dim_airport NAO entra para
-- normalizar fuso na duracao de etapa -- so entra para enriquecer a
-- rotacao e para a validacao geodesica (uso genuinamente novo).
--
-- Medido antes de materializar (script de diagnostico, nao versionado):
--   - 100% das linhas com matricula preenchida neste recorte (GOL/Azul,
--     2021+) -- melhor que os ~12% de nulo que SPEC-005 registra pro
--     historico completo da Basica.
--   - continuidade da rotacao (destino da etapa anterior = origem desta):
--     99,86% (2.739.772 de 2.743.531 com etapa anterior). 0,14% quebrada
--     (3.759 linhas) fica registrada como achado, nao investigada a fundo.
--   - cobertura dim_airport: 100% dos ICAO de origem/destino usados aqui
--     tem match (858 aerodromos, SPEC-011).
--   - 2 linhas com duracao de etapa = 0 (dt/hr partida = dt/hr chegada
--     exatos, nr_horas_voadas tambem 0.0 -- concordam entre si, mas nao
--     fazem sentido operacional). Anomalia isolada, nao tratada.

DROP TABLE IF EXISTS fato_rotacao_aeronave_gol_azul;

CREATE TABLE fato_rotacao_aeronave_gol_azul AS
SELECT
    id_basica, sg_empresa_icao, nr_voo, ds_matricula, sg_equipamento_icao,
    ds_modelo, sg_icao_origem, sg_icao_destino,
    dt_partida_real, hr_partida_real, dt_chegada_real, hr_chegada_real,
    km_distancia, nr_horas_voadas,
    nr_sequencia_matricula,
    sg_icao_destino_anterior,
    dt_chegada_anterior,
    CASE
        WHEN sg_icao_destino_anterior IS NULL THEN NULL
        WHEN sg_icao_origem = sg_icao_destino_anterior THEN 1
        ELSE 0
    END AS fl_continuidade_ok,
    CASE
        WHEN dt_chegada_anterior IS NULL THEN NULL
        ELSE (julianday(dt_partida_real || ' ' || hr_partida_real) - julianday(dt_chegada_anterior)) * 24.0
    END AS tempo_solo_horas,
    (julianday(dt_chegada_real || ' ' || hr_chegada_real) - julianday(dt_partida_real || ' ' || hr_partida_real)) * 24.0
        AS tempo_etapa_horas,
    (julianday(dt_chegada_real || ' ' || hr_chegada_real) - julianday(dt_partida_real || ' ' || hr_partida_real)) * 24.0
        - nr_horas_voadas AS delta_horas_voadas,
    km_distancia_geodesica,
    CASE WHEN km_distancia_geodesica IS NULL THEN NULL
         ELSE km_distancia - km_distancia_geodesica END AS delta_km_distancia
FROM (
    SELECT
        b.id_basica, b.sg_empresa_icao, b.nr_voo, b.ds_matricula, b.sg_equipamento_icao,
        b.ds_modelo, b.sg_icao_origem, b.sg_icao_destino,
        b.dt_partida_real, b.hr_partida_real, b.dt_chegada_real, b.hr_chegada_real,
        b.km_distancia, b.nr_horas_voadas,
        ROW_NUMBER() OVER (
            PARTITION BY b.ds_matricula
            ORDER BY datetime(b.dt_partida_real || ' ' || b.hr_partida_real)
        ) AS nr_sequencia_matricula,
        LAG(b.sg_icao_destino) OVER (
            PARTITION BY b.ds_matricula
            ORDER BY datetime(b.dt_partida_real || ' ' || b.hr_partida_real)
        ) AS sg_icao_destino_anterior,
        LAG(datetime(b.dt_chegada_real || ' ' || b.hr_chegada_real)) OVER (
            PARTITION BY b.ds_matricula
            ORDER BY datetime(b.dt_partida_real || ' ' || b.hr_partida_real)
        ) AS dt_chegada_anterior,
        CASE
            WHEN o.latitude IS NULL OR o.longitude IS NULL
              OR d.latitude IS NULL OR d.longitude IS NULL THEN NULL
            WHEN b.sg_icao_origem = b.sg_icao_destino THEN 0.0
            ELSE 6371.0 * acos(
                MIN(1.0, MAX(-1.0,
                    sin(radians(o.latitude)) * sin(radians(d.latitude))
                    + cos(radians(o.latitude)) * cos(radians(d.latitude))
                      * cos(radians(d.longitude) - radians(o.longitude))
                ))
            )
        END AS km_distancia_geodesica
    FROM basica_curated_deep b
    LEFT JOIN dim_airport_location_time_zone o ON o.base_icao = b.sg_icao_origem
    LEFT JOIN dim_airport_location_time_zone d ON d.base_icao = b.sg_icao_destino
);

CREATE INDEX idx_fato_rotacao_matricula ON fato_rotacao_aeronave_gol_azul(ds_matricula, nr_sequencia_matricula);
CREATE INDEX idx_fato_rotacao_empresa ON fato_rotacao_aeronave_gol_azul(sg_empresa_icao);

-- Validacao
SELECT 'linhas' AS metrica, COUNT(*) AS valor FROM fato_rotacao_aeronave_gol_azul;
SELECT 'matriculas_distintas' AS metrica, COUNT(DISTINCT ds_matricula) AS valor FROM fato_rotacao_aeronave_gol_azul;
SELECT 'continuidade_ok' AS metrica, COUNT(*) AS valor FROM fato_rotacao_aeronave_gol_azul WHERE fl_continuidade_ok = 1;
SELECT 'continuidade_quebrada' AS metrica, COUNT(*) AS valor FROM fato_rotacao_aeronave_gol_azul WHERE fl_continuidade_ok = 0;
SELECT 'delta_horas_voadas_max_abs' AS metrica, MAX(ABS(delta_horas_voadas)) AS valor FROM fato_rotacao_aeronave_gol_azul;
SELECT 'delta_km_distancia_media' AS metrica, ROUND(AVG(delta_km_distancia), 2) AS valor FROM fato_rotacao_aeronave_gol_azul WHERE delta_km_distancia IS NOT NULL;
SELECT 'delta_km_distancia_max_abs' AS metrica, ROUND(MAX(ABS(delta_km_distancia)), 2) AS valor FROM fato_rotacao_aeronave_gol_azul WHERE delta_km_distancia IS NOT NULL;
SELECT 'linhas_sem_geodesica' AS metrica, COUNT(*) AS valor FROM fato_rotacao_aeronave_gol_azul WHERE km_distancia_geodesica IS NULL;
