-- Camada curated_deep: fato_block_time_gol_azul (db/anac_basica.sqlite)
-- Grao: uma linha por etapa de fato_rotacao_aeronave_gol_azul (SPEC-012),
-- enriquecida com o VRA (previsto x real, situacao, justificativa) para
-- destravar a pergunta 6 do SPEC-004 (Sec.5.6, "Block time"): onde ha
-- sobra ou falta de tempo entre o previsto e o realizado.
--
-- Nome unico (nao um objeto por empresa) -- correcao pos-aprovacao de
-- DEC-007 v4 / SPEC-004 v4 (R-TAX-11), alinhando com o padrao que
-- curated_deep/fato_rotacao_aeronave_gol_azul ja fixaram: um objeto so,
-- filtra por sg_empresa_icao.
--
-- Chave de juncao (DEC-007 Sec.2.g, refinada v4): empresa+voo+data+HORA
-- de partida+origem -- medida antes de fechar este DDL (nao assumida):
--   - amostra 2025 GOL/Azul (sessao anterior): sem hora, 6.392 grupos de
--     chave duplicada; com hora, 13 grupos residuais, ~97% correspondencia.
--   - par completo atual (fato_rotacao x vra_curated_deep, 2.743.964 x
--     2.697.490 linhas, medido nesta sessao): 96,96% de correspondencia
--     (2.660.682 linhas), 10 chaves duplicadas do lado Basica, 12 do VRA
--     -- ~0,0004%, essencialmente resolvido. Achado consistente, nao
--     mais hipotese pura.
--
-- Residuo de chave duplicada (10-12 grupos) resolvido por ROW_NUMBER no
-- staging do VRA, mesma tecnica ja usada em voo_trusted (desenhada e
-- descartada em sessao anterior, nao ha arquivo, so o metodo sobrevive).

ATTACH DATABASE 'db/anac_vra.sqlite' AS vra;

DROP TABLE IF EXISTS vra_stage;
DROP TABLE IF EXISTS fato_block_time_gol_azul;

CREATE TABLE vra_stage AS
SELECT
    sg_empresa_icao, nr_voo, sg_icao_origem,
    date(dt_hr_partida_real) AS vra_dt, time(dt_hr_partida_real) AS vra_hr,
    dt_hr_partida_prevista, dt_hr_partida_real,
    dt_hr_chegada_prevista, dt_hr_chegada_real,
    ds_situacao_voo, cd_justificativa
FROM (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY sg_empresa_icao, nr_voo,
                            date(dt_hr_partida_real), time(dt_hr_partida_real),
                            sg_icao_origem
               ORDER BY rowid
           ) AS rn
    FROM vra.vra_curated_deep
)
WHERE rn = 1;

CREATE INDEX idx_vra_stage ON vra_stage(sg_empresa_icao, nr_voo, vra_dt, vra_hr, sg_icao_origem);

-- fato_rotacao_aeronave_gol_azul (todas as colunas) + colunas do VRA +
-- metricas derivadas de block time (previsto x real, atraso, folga).
CREATE TABLE fato_block_time_gol_azul AS
SELECT
    f.*,
    v.dt_hr_partida_prevista,
    v.dt_hr_partida_real AS dt_hr_partida_real_vra,
    v.dt_hr_chegada_prevista,
    v.dt_hr_chegada_real AS dt_hr_chegada_real_vra,
    v.ds_situacao_voo,
    v.cd_justificativa,
    CASE WHEN v.sg_empresa_icao IS NOT NULL THEN 1 ELSE 0 END AS fl_match_vra,
    -- Block time: previsto (VRA) e real (VRA) -- comparar com
    -- f.nr_horas_voadas (Basica, airborne) e f.tempo_etapa_horas mostra
    -- se VRA real diverge do airborne da Basica ou nao (a validar).
    (julianday(v.dt_hr_chegada_prevista) - julianday(v.dt_hr_partida_prevista)) * 24.0
        AS tempo_previsto_horas,
    (julianday(v.dt_hr_chegada_real) - julianday(v.dt_hr_partida_real)) * 24.0
        AS tempo_real_vra_horas,
    -- Atraso em cada ponta (real - previsto, VRA)
    (julianday(v.dt_hr_partida_real) - julianday(v.dt_hr_partida_prevista)) * 24.0
        AS atraso_partida_horas,
    (julianday(v.dt_hr_chegada_real) - julianday(v.dt_hr_chegada_prevista)) * 24.0
        AS atraso_chegada_horas,
    -- A pergunta central: sobra (positivo) ou falta (negativo) de tempo
    -- programado frente ao tempo no ar real (Basica, ja validado em
    -- fato_rotacao Sec. nr_horas_voadas).
    ((julianday(v.dt_hr_chegada_prevista) - julianday(v.dt_hr_partida_prevista)) * 24.0)
        - f.nr_horas_voadas AS folga_horas
FROM fato_rotacao_aeronave_gol_azul f
LEFT JOIN vra_stage v
    ON v.sg_empresa_icao = f.sg_empresa_icao
   AND v.nr_voo = f.nr_voo
   AND v.vra_dt = f.dt_partida_real
   AND v.vra_hr = f.hr_partida_real
   AND v.sg_icao_origem = f.sg_icao_origem;

DROP TABLE vra_stage;

CREATE UNIQUE INDEX idx_fbt_id ON fato_block_time_gol_azul(id_basica);
CREATE INDEX idx_fbt_empresa ON fato_block_time_gol_azul(sg_empresa_icao);
CREATE INDEX idx_fbt_match ON fato_block_time_gol_azul(fl_match_vra);

-- Validacao
SELECT 'linhas' AS metrica, COUNT(*) AS valor FROM fato_block_time_gol_azul;
SELECT 'linhas_com_match_vra' AS metrica, COUNT(*) AS valor FROM fato_block_time_gol_azul WHERE fl_match_vra = 1;
SELECT 'folga_horas_media' AS metrica, ROUND(AVG(folga_horas), 4) AS valor FROM fato_block_time_gol_azul WHERE fl_match_vra = 1;
SELECT 'folga_horas_mediana_aprox' AS metrica, ROUND(folga_horas, 2) AS valor
FROM fato_block_time_gol_azul WHERE fl_match_vra = 1 AND folga_horas IS NOT NULL
ORDER BY folga_horas LIMIT 1 OFFSET (SELECT COUNT(*)/2 FROM fato_block_time_gol_azul WHERE fl_match_vra = 1 AND folga_horas IS NOT NULL);
SELECT 'linhas_falta_tempo (folga<0)' AS metrica, COUNT(*) AS valor FROM fato_block_time_gol_azul WHERE folga_horas < 0;
SELECT 'linhas_sobra_tempo (folga>0)' AS metrica, COUNT(*) AS valor FROM fato_block_time_gol_azul WHERE folga_horas > 0;
SELECT 'atraso_partida_media_min' AS metrica, ROUND(AVG(atraso_partida_horas)*60, 2) AS valor FROM fato_block_time_gol_azul WHERE fl_match_vra = 1;
