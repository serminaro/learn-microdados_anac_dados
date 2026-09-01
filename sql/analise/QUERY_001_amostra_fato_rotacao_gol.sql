-- Amostra exploratoria: 10 primeiras linhas da GOL (GLO) em
-- fato_rotacao_aeronave_gol_azul, ordenadas por data/hora de partida.
-- db/anac_basica.sqlite



SELECT
    id_basica,
    ds_matricula,
    nr_sequencia_matricula,
    nr_voo,
    sg_icao_origem,
    sg_icao_destino,
    dt_partida_real,
    hr_partida_real,
    dt_chegada_real,
    hr_chegada_real,
    tempo_etapa_horas,
    nr_horas_voadas,
    tempo_solo_horas,
    fl_continuidade_ok
FROM fato_rotacao_aeronave_gol_azul
WHERE sg_empresa_icao = 'GLO'
ORDER BY dt_partida_real, hr_partida_real
LIMIT 10;

