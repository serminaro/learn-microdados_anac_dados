-- Etapa media (stage length) -- GOL e Azul, SPEC-004 Sec.5.5
-- Fonte: basica_curated_deep (db/anac_basica.sqlite)
--
-- Definicao adotada (SPEC-004 Sec.5.5, decisao do autor 2026-08-31):
--   1) Duracao (principal): NR_HORAS_VOADAS -- tempo no ar (airborne),
--      NAO e tempo de bloco porta-a-porta.
--   2) Distancia (complementar): KM_DISTANCIA, so versao simples (AVG) --
--      versao ponderada por ASK fora de escopo (SPEC-004 Sec.3.2).
--   3) Velocidade media inferida (derivada): KM_DISTANCIA/NR_HORAS_VOADAS,
--      reportada nas 2 formas que SPEC-004 Sec.5.5 pede lado a lado:
--      razao das somas (principal, mais robusta) e media das razoes por
--      etapa (da peso igual a cada etapa, mais sensivel a outlier).
--
-- Premissa aplicada aqui, nao explicita no Sec.5.5 mas consistente com o
-- resto do SPEC-004 (ex. Sec.5.1): filtra ds_servico_tipo_linha =
-- 'PASSAGEIRO', exclui CARGUEIRO (45.331 linhas, 1,65% do recorte) --
-- perfil de etapa de carga pode divergir do de passageiro, misturar
-- enviesa a leitura.
--
-- nr_horas_voadas = 0 em 2 linhas (anomalia isolada, SPEC-012 Sec.6.4) --
-- protegido com NULLIF na divisao, nao entra no denominador.

-- ===== 1) Resumo: por empresa x natureza da linha =====
SELECT
    sg_empresa_icao,
    ds_natureza_tipo_linha,
    COUNT(*) AS n_etapas,
    ROUND(AVG(nr_horas_voadas), 3) AS duracao_media_horas,
    ROUND(AVG(km_distancia), 1) AS distancia_media_km,
    ROUND(SUM(km_distancia) * 1.0 / SUM(nr_horas_voadas), 1) AS velocidade_razao_somas_kmh,
    ROUND(AVG(km_distancia * 1.0 / NULLIF(nr_horas_voadas, 0)), 1) AS velocidade_media_razoes_kmh
FROM basica_curated_deep
WHERE ds_servico_tipo_linha = 'PASSAGEIRO'
GROUP BY sg_empresa_icao, ds_natureza_tipo_linha
ORDER BY sg_empresa_icao, ds_natureza_tipo_linha;

-- ===== 2) Detalhe: por empresa x natureza x modelo de equipamento =====
SELECT
    sg_empresa_icao,
    ds_natureza_tipo_linha,
    sg_equipamento_icao,
    COUNT(*) AS n_etapas,
    ROUND(AVG(nr_horas_voadas), 3) AS duracao_media_horas,
    ROUND(AVG(km_distancia), 1) AS distancia_media_km,
    ROUND(SUM(km_distancia) * 1.0 / SUM(nr_horas_voadas), 1) AS velocidade_razao_somas_kmh,
    ROUND(AVG(km_distancia * 1.0 / NULLIF(nr_horas_voadas, 0)), 1) AS velocidade_media_razoes_kmh
FROM basica_curated_deep
WHERE ds_servico_tipo_linha = 'PASSAGEIRO'
GROUP BY sg_empresa_icao, ds_natureza_tipo_linha, sg_equipamento_icao
HAVING COUNT(*) >= 30  -- corta modelo com pouquissima etapa, media instavel
ORDER BY sg_empresa_icao, ds_natureza_tipo_linha, n_etapas DESC;
