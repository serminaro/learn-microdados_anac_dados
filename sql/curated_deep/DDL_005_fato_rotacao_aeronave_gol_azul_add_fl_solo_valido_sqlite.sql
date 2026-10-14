-- Camada curated_deep: enriquece fato_rotacao_aeronave_gol_azul (SPEC-012)
-- com fl_solo_valido -- flag de validade de tempo_solo_horas para uso em
-- analises de turnaround (analise/a3_tempo_de_solo). Nao cria tabela
-- nova: mesma granularidade (1 linha por etapa, 2.743.964 linhas GOL+Azul)
-- ja existente -- uma tabela separada duplicaria quase tudo e criaria
-- risco de dessincronia quando fato_rotacao for recarregada (decisao
-- discutida e descartada em sessao, 2026-09-02).
--
-- Regra (medida antes de aplicar, sessao 2026-09-02, GOL+Azul juntos):
-- fl_solo_valido = 0 quando:
--   (a) tempo_solo_horas < 0 -- fisicamente impossivel. 408 linhas
--       (0,0149%). Amostra GOL isolado (sessao anterior): 193/255 vem de
--       continuidade quebrada (criterio b abaixo), 62/255 tem continuidade
--       OK mesmo negativo -- erro de timestamp na propria Basica, nao do
--       pipeline de rotacao.
--   (b) fl_continuidade_ok = 0 -- origem desta etapa != destino da etapa
--       anterior da mesma matricula (ja documentado em fato_rotacao,
--       SPEC-012, como 0,14% do total). Solo aqui nao mede turnaround
--       real (timestamps de aeroportos diferentes). 3.759 linhas.
--   (c) tempo_solo_horas > 72 -- pernoite e fim de semana completo (sexta
--       a noite ate segunda a noite) cabem ate 72h; acima disso e' parada
--       prolongada (manutencao pesada, aeronave fora de operacao). Medido
--       antes de fixar o corte: distribuicao de 24h a 96h decai suave,
--       SEM quebra natural que justifique 72h sobre 48h/60h -- e'
--       julgamento de dominio (cobertura de fim de semana), nao achado
--       estatistico. Documentado como premissa, nao como corte objetivo.
--       4.142 linhas.
-- fl_solo_valido = NULL quando tempo_solo_horas IS NULL (primeira etapa
--   da matricula no periodo, sem etapa anterior para medir solo) -- 433
--   linhas, nao e' invalidez, e' ausencia de medida.
--
-- Uniao dos criterios (a)+(b)+(c), GOL+Azul: 7.919 linhas de 2.743.531
-- com solo nao-nulo (0,2886%) recebem fl_solo_valido=0. Restam 2.735.612
-- com fl_solo_valido=1.
--
-- Nao deleta nenhuma linha -- mesmo espirito de fl_continuidade_ok (ja
-- em fato_rotacao) e fl_match_vra (fato_block_time_gol_azul, SPEC-014):
-- flag, nao filtro destrutivo, decisao de recorte fica com quem consome.
--
-- Efeito colateral que precisa de acao manual: fato_block_time_gol_azul
-- (DDL_004) foi construida com f.* a partir de fato_rotacao ANTES desta
-- coluna existir -- nao herda fl_solo_valido automaticamente. Rodar
-- DDL_004 de novo depois deste script para sincronizar (feito na mesma
-- sessao, 2026-09-02).

DROP TABLE IF EXISTS fato_rotacao_aeronave_gol_azul_novo;

CREATE TABLE fato_rotacao_aeronave_gol_azul_novo AS
SELECT
    f.*,
    CASE
        WHEN f.tempo_solo_horas IS NULL THEN NULL
        WHEN f.tempo_solo_horas < 0 THEN 0
        WHEN f.fl_continuidade_ok = 0 THEN 0
        WHEN f.tempo_solo_horas > 72 THEN 0
        ELSE 1
    END AS fl_solo_valido
FROM fato_rotacao_aeronave_gol_azul f;

DROP TABLE fato_rotacao_aeronave_gol_azul;
ALTER TABLE fato_rotacao_aeronave_gol_azul_novo RENAME TO fato_rotacao_aeronave_gol_azul;

CREATE INDEX idx_fato_rotacao_matricula ON fato_rotacao_aeronave_gol_azul(ds_matricula, nr_sequencia_matricula);
CREATE INDEX idx_fato_rotacao_empresa ON fato_rotacao_aeronave_gol_azul(sg_empresa_icao);
CREATE INDEX idx_fato_rotacao_solo_valido ON fato_rotacao_aeronave_gol_azul(fl_solo_valido);

-- Validacao
SELECT 'linhas' AS metrica, COUNT(*) AS valor FROM fato_rotacao_aeronave_gol_azul;
SELECT 'fl_solo_valido=1' AS metrica, COUNT(*) AS valor FROM fato_rotacao_aeronave_gol_azul WHERE fl_solo_valido = 1;
SELECT 'fl_solo_valido=0' AS metrica, COUNT(*) AS valor FROM fato_rotacao_aeronave_gol_azul WHERE fl_solo_valido = 0;
SELECT 'fl_solo_valido_NULL' AS metrica, COUNT(*) AS valor FROM fato_rotacao_aeronave_gol_azul WHERE fl_solo_valido IS NULL;
SELECT 'tempo_solo_max_com_flag_1' AS metrica, ROUND(MAX(tempo_solo_horas), 2) AS valor
FROM fato_rotacao_aeronave_gol_azul WHERE fl_solo_valido = 1;
