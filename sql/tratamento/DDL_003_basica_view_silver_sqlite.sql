-- Camada silver: basica_silver
-- Todas as 112 colunas de basica_raw, tipadas, organizadas por categoria
-- (mesma taxonomia de SPEC-005), comentario por coluna vindo de SPEC-005.
-- Substitui basica_typed (removida, SPEC-008 v3) como a camada silver real:
-- basica_typed cobria so ~27 colunas com metricas derivadas misturadas;
-- esta view cobre as 112, sem metrica derivada (isso fica para camada seguinte).
--
-- Convencoes: TEXT vazio vira NULL (NULLIF); datas/horas via date()/time()/
-- datetime() do SQLite (nao CAST AS DATE -- SQLite trata DATE como afinidade
-- NUMERIC, arriscando conversao indevida de string ISO); nr_horas_voadas troca
-- virgula por ponto antes do CAST REAL (formato confirmado do arquivo original).

DROP VIEW IF EXISTS basica_silver;

CREATE VIEW basica_silver AS
SELECT
    -- ===== IDENTIFICACAO DO REGISTRO E DO VOO =====
    -- Chave primária do registro (uma linha = uma etapa de voo realizada) [confirmado]
    CAST(id_basica AS INTEGER) AS id_basica,
    -- Código ICAO (3 letras) da empresa aérea, ex.: GLO, TAM, AZU [alta confiança]
    NULLIF(sg_empresa_icao, '') AS sg_empresa_icao,
    -- Código IATA (2 caracteres) da empresa aérea, ex.: G3, JJ, AD [alta confiança]
    NULLIF(sg_empresa_iata, '') AS sg_empresa_iata,
    -- Número comercial do voo [alta confiança]
    NULLIF(nr_voo, '') AS nr_voo,
    -- Data de referência do boletim (mês/ano de apuração) [alta confiança]
    date(dt_referencia) AS dt_referencia,
    -- ===== REFERENCIA (BOLETIM) E IDENTIFICADORES ADICIONAIS =====
    -- Identificador numérico da empresa aérea [alta confiança]
    CAST(id_empresa AS INTEGER) AS id_empresa,
    -- Nome/razão social da empresa aérea [alta confiança]
    NULLIF(nm_empresa, '') AS nm_empresa,
    -- País de registro da empresa aérea [inferido (padrão de nome)]
    NULLIF(nm_pais, '') AS nm_pais,
    -- Classificação do tipo de empresa aérea (ex.: nacional regular) — categorias exatas não verificadas [incerto — checar dicionário oficial ANAC]
    NULLIF(ds_tipo_empresa, '') AS ds_tipo_empresa,
    -- Identificador numérico da etapa nos sistemas ANAC — termo "singular" não confirmado com precisão [incerto — checar dicionário oficial ANAC]
    CAST(nr_singular AS INTEGER) AS nr_singular,
    -- Identificador do "DI" associado à etapa — sigla DI não confirmada com certeza (possível "Discriminação de Itinerário") [incerto — checar dicionário oficial ANAC]
    CAST(id_di AS INTEGER) AS id_di,
    -- Código do DI (ver ID_DI) [incerto — checar dicionário oficial ANAC]
    NULLIF(cd_di, '') AS cd_di,
    -- Descrição textual do DI (ver ID_DI) [incerto — checar dicionário oficial ANAC]
    NULLIF(ds_di, '') AS ds_di,
    -- Descrição do grupo/categoria a que o DI pertence [incerto — checar dicionário oficial ANAC]
    NULLIF(ds_grupo_di, '') AS ds_grupo_di,
    -- Ano de referência [alta confiança]
    CAST(nr_ano_referencia AS INTEGER) AS nr_ano_referencia,
    -- Semestre de referência (1 ou 2) [alta confiança]
    CAST(nr_semestre_referencia AS INTEGER) AS nr_semestre_referencia,
    -- Nome do semestre de referência (ex.: 1º Semestre) [alta confiança]
    NULLIF(nm_semestre_referencia, '') AS nm_semestre_referencia,
    -- Trimestre de referência (1 a 4) [alta confiança]
    CAST(nr_trimestre_referencia AS INTEGER) AS nr_trimestre_referencia,
    -- Nome do trimestre de referência [alta confiança]
    NULLIF(nm_trimestre_referencia, '') AS nm_trimestre_referencia,
    -- Mês de referência (1 a 12) [alta confiança]
    CAST(nr_mes_referencia AS INTEGER) AS nr_mes_referencia,
    -- Nome do mês de referência [alta confiança]
    NULLIF(nm_mes_referencia, '') AS nm_mes_referencia,
    -- Número da semana no ano de referência [alta confiança]
    CAST(nr_semana_referencia AS INTEGER) AS nr_semana_referencia,
    -- Nome do dia da semana de referência [alta confiança]
    NULLIF(nm_dia_semana_referencia, '') AS nm_dia_semana_referencia,
    -- Dia do mês de referência [alta confiança]
    CAST(nr_dia_referencia AS INTEGER) AS nr_dia_referencia,
    -- Ano-mês de referência, formato AAAAMM [alta confiança]
    CAST(nr_ano_mes_referencia AS INTEGER) AS nr_ano_mes_referencia,
    -- Identificador do tipo de linha aérea [alta confiança]
    CAST(id_tipo_linha AS INTEGER) AS id_tipo_linha,
    -- Código do tipo de linha aérea [alta confiança]
    NULLIF(cd_tipo_linha, '') AS cd_tipo_linha,
    -- Número sequencial da etapa dentro do voo (voos com múltiplas escalas têm mais de uma etapa) [confirmado]
    CAST(nr_etapa AS INTEGER) AS nr_etapa,
    -- ===== CARACTERISTICA DA LINHA E DA ETAPA =====
    -- Descrição do tipo de linha (ex.: doméstica mista, internacional mista, doméstica cargueira) [alta confiança]
    NULLIF(ds_tipo_linha, '') AS ds_tipo_linha,
    -- Natureza do tipo de linha (ex.: doméstica / internacional) [inferido (padrão de nome)]
    NULLIF(ds_natureza_tipo_linha, '') AS ds_natureza_tipo_linha,
    -- Tipo de serviço prestado na linha (ex.: passageiro, carga,) [inferido (padrão de nome)]
    NULLIF(ds_servico_tipo_linha, '') AS ds_servico_tipo_linha,
    -- Natureza da etapa de voo (ex.: comercial, não comercial/posicionamento) [inferido (padrão de nome)]
    NULLIF(ds_natureza_etapa, '') AS ds_natureza_etapa,
    -- ===== HORARIOS REAIS DE PARTIDA E CHEGADA =====
    -- Hora real de partida (decolagem) [confirmado]
    time(hr_partida_real) AS hr_partida_real,
    -- Data real de partida [confirmado]
    date(dt_partida_real) AS dt_partida_real,
    -- Ano de partida real [alta confiança]
    CAST(nr_ano_partida_real AS INTEGER) AS nr_ano_partida_real,
    -- Semestre de partida real (1 ou 2) [alta confiança]
    CAST(nr_semestre_partida_real AS INTEGER) AS nr_semestre_partida_real,
    -- Nome do semestre de partida real (ex.: 1º Semestre) [alta confiança]
    NULLIF(nm_semestre_partida_real, '') AS nm_semestre_partida_real,
    -- Trimestre de partida real (1 a 4) [alta confiança]
    CAST(nr_trimestre_partida_real AS INTEGER) AS nr_trimestre_partida_real,
    -- Nome do trimestre de partida real [alta confiança]
    NULLIF(nm_trimestre_partida_real, '') AS nm_trimestre_partida_real,
    -- Mês de partida real (1 a 12) [alta confiança]
    CAST(nr_mes_partida_real AS INTEGER) AS nr_mes_partida_real,
    -- Nome do mês de partida real [alta confiança]
    NULLIF(nm_mes_partida_real, '') AS nm_mes_partida_real,
    -- Número da semana no ano de partida real [alta confiança]
    CAST(nr_semana_partida_real AS INTEGER) AS nr_semana_partida_real,
    -- Nome do dia da semana de partida real [alta confiança]
    NULLIF(nm_dia_semana_partida_real, '') AS nm_dia_semana_partida_real,
    -- Dia do mês de partida real [alta confiança]
    CAST(nr_dia_partida_real AS INTEGER) AS nr_dia_partida_real,
    -- Ano-mês de partida real, formato AAAAMM [alta confiança]
    CAST(nr_ano_mes_partida_real AS INTEGER) AS nr_ano_mes_partida_real,
    -- Hora real de chegada (pouso) [confirmado]
    time(hr_chegada_real) AS hr_chegada_real,
    -- Data real de chegada [confirmado]
    date(dt_chegada_real) AS dt_chegada_real,
    -- Ano de chegada real [alta confiança]
    CAST(nr_ano_chegada_real AS INTEGER) AS nr_ano_chegada_real,
    -- Semestre de chegada real (1 ou 2) [alta confiança]
    CAST(nr_semestre_chegada_real AS INTEGER) AS nr_semestre_chegada_real,
    -- Nome do semestre de chegada real (ex.: 1º Semestre) [alta confiança]
    NULLIF(nm_semestre_chegada_real, '') AS nm_semestre_chegada_real,
    -- Trimestre de chegada real (1 a 4) [alta confiança]
    CAST(nr_trimestre_chegada_real AS INTEGER) AS nr_trimestre_chegada_real,
    -- Nome do trimestre de chegada real [alta confiança]
    NULLIF(nm_trimestre_chegada_real, '') AS nm_trimestre_chegada_real,
    -- Mês de chegada real (1 a 12) [alta confiança]
    CAST(nr_mes_chegada_real AS INTEGER) AS nr_mes_chegada_real,
    -- Nome do mês de chegada real [alta confiança]
    NULLIF(nm_mes_chegada_real, '') AS nm_mes_chegada_real,
    -- Número da semana no ano de chegada real [alta confiança]
    CAST(nr_semana_chegada_real AS INTEGER) AS nr_semana_chegada_real,
    -- Nome do dia da semana de chegada real [alta confiança]
    NULLIF(nm_dia_semana_chegada_real, '') AS nm_dia_semana_chegada_real,
    -- Dia do mês de chegada real [alta confiança]
    CAST(nr_dia_chegada_real AS INTEGER) AS nr_dia_chegada_real,
    -- Ano-mês de chegada real, formato AAAAMM [alta confiança]
    CAST(nr_ano_mes_chegada_real AS INTEGER) AS nr_ano_mes_chegada_real,
    -- ===== IDENTIFICADOR DE AERODROMO (ORIGEM) =====
    -- Identificador do aeródromo de origem [alta confiança]
    CAST(id_aerodromo_origem AS INTEGER) AS id_aerodromo_origem,
    -- ===== AERODROMOS DE ORIGEM E DESTINO =====
    -- Código ICAO do aeródromo de origem [alta confiança]
    NULLIF(sg_icao_origem, '') AS sg_icao_origem,
    -- Código IATA do aeródromo de origem [confirmado]
    NULLIF(sg_iata_origem, '') AS sg_iata_origem,
    -- Nome do aeródromo de origem [alta confiança]
    NULLIF(nm_aerodromo_origem, '') AS nm_aerodromo_origem,
    -- Município do aeródromo de origem [alta confiança]
    NULLIF(nm_municipio_origem, '') AS nm_municipio_origem,
    -- UF do aeródromo de origem [alta confiança]
    NULLIF(sg_uf_origem, '') AS sg_uf_origem,
    -- Região geográfica (Norte/Sul/etc.) do aeródromo de origem [alta confiança]
    NULLIF(nm_regiao_origem, '') AS nm_regiao_origem,
    -- País do aeródromo de origem [alta confiança]
    NULLIF(nm_pais_origem, '') AS nm_pais_origem,
    -- Continente do aeródromo de origem [alta confiança]
    NULLIF(nm_continente_origem, '') AS nm_continente_origem,
    -- Identificador do aeródromo de destino [alta confiança]
    CAST(id_aerodromo_destino AS INTEGER) AS id_aerodromo_destino,
    -- Código ICAO do aeródromo de destino [alta confiança]
    NULLIF(sg_icao_destino, '') AS sg_icao_destino,
    -- Código IATA do aeródromo de destino [confirmado]
    NULLIF(sg_iata_destino, '') AS sg_iata_destino,
    -- Nome do aeródromo de destino [alta confiança]
    NULLIF(nm_aerodromo_destino, '') AS nm_aerodromo_destino,
    -- Município do aeródromo de destino [alta confiança]
    NULLIF(nm_municipio_destino, '') AS nm_municipio_destino,
    -- UF do aeródromo de destino [alta confiança]
    NULLIF(sg_uf_destino, '') AS sg_uf_destino,
    -- Região geográfica do aeródromo de destino [alta confiança]
    NULLIF(nm_regiao_destino, '') AS nm_regiao_destino,
    -- País do aeródromo de destino [alta confiança]
    NULLIF(nm_pais_destino, '') AS nm_pais_destino,
    -- Continente do aeródromo de destino [alta confiança]
    NULLIF(nm_continente_destino, '') AS nm_continente_destino,
    -- ===== AERONAVE (FROTA) =====
    -- Identificador do tipo/modelo de aeronave (equipamento) [alta confiança]
    CAST(id_equipamento AS INTEGER) AS id_equipamento,
    -- Código ICAO do tipo de aeronave, ex.: A320, B738 [alta confiança]
    NULLIF(sg_equipamento_icao, '') AS sg_equipamento_icao,
    -- Descrição do modelo da aeronave [alta confiança]
    NULLIF(ds_modelo, '') AS ds_modelo,
    -- Matrícula (prefixo de registro) da aeronave — vazia em ~12% das linhas quando a etapa não identifica a aeronave [confirmado]
    NULLIF(ds_matricula, '') AS ds_matricula,
    -- ===== CAMPO SEM USO CONFIRMADO =====
    -- Posição/número da escala na rota até este destino — definição exata não verificada [incerto — checar dicionário oficial ANAC]
    CAST(nr_escala_destino AS INTEGER) AS nr_escala_destino,
    -- ===== DESPACHO E DESEMPENHO DA ETAPA =====
    -- Combustível consumido ou embarcado na etapa, em litros [inferido (padrão de nome)]
    CAST(lt_combustivel AS INTEGER) AS lt_combustivel,
    -- Número de assentos ofertados na etapa [confirmado]
    CAST(nr_assentos_ofertados AS INTEGER) AS nr_assentos_ofertados,
    -- Payload: capacidade de carga paga (passageiros + carga + correio), em kg [confirmado]
    CAST(kg_payload AS INTEGER) AS kg_payload,
    -- Distância voada na etapa, em km [confirmado]
    CAST(km_distancia AS INTEGER) AS km_distancia,
    -- Número de passageiros pagantes transportados [alta confiança]
    CAST(nr_passag_pagos AS INTEGER) AS nr_passag_pagos,
    -- Número de passageiros em cortesia/gratuidade [alta confiança]
    CAST(nr_passag_gratis AS INTEGER) AS nr_passag_gratis,
    -- Peso de bagagem despachada dentro da franquia gratuita, em kg [alta confiança]
    CAST(kg_bagagem_livre AS INTEGER) AS kg_bagagem_livre,
    -- Peso de bagagem despachada acima da franquia, paga pelo passageiro, em kg [alta confiança]
    CAST(kg_bagagem_excesso AS INTEGER) AS kg_bagagem_excesso,
    -- Peso de carga paga transportada, em kg [alta confiança]
    CAST(kg_carga_paga AS INTEGER) AS kg_carga_paga,
    -- Peso de carga transportada gratuitamente, em kg [alta confiança]
    CAST(kg_carga_gratis AS INTEGER) AS kg_carga_gratis,
    -- Peso de correio (mala postal) transportado, em kg [alta confiança]
    CAST(kg_correio AS INTEGER) AS kg_correio,
    -- Contagem de decolagens da etapa (tipicamente 1) — uso exato (ex.: fins de tarifa de pouso) não verificado [incerto — checar dicionário oficial ANAC]
    CAST(nr_decolagem AS INTEGER) AS nr_decolagem,
    -- Duração voada da etapa, em horas (decimal com vírgula no arquivo original) [confirmado]
    CAST(REPLACE(nr_horas_voadas, ',', '.') AS REAL) AS nr_horas_voadas,
    -- Peso associado à etapa, em kg — se refere a payload realizado, peso da aeronave ou outro, não verificado [incerto — checar dicionário oficial ANAC]
    CAST(kg_peso AS INTEGER) AS kg_peso,
    -- Velocidade média da etapa [inferido (padrão de nome)]
    CAST(nr_velocidade_media AS INTEGER) AS nr_velocidade_media,
    -- Passageiros gratuitos × km voado (produção análoga ao RPK, para gratuidade) [inferido (padrão de nome)]
    CAST(nr_pax_gratis_km AS INTEGER) AS nr_pax_gratis_km,
    -- Toneladas de carga paga × km voado [inferido (padrão de nome)]
    CAST(nr_carga_paga_km AS INTEGER) AS nr_carga_paga_km,
    -- Toneladas de carga gratuita × km voado [inferido (padrão de nome)]
    CAST(nr_carga_gratis_km AS INTEGER) AS nr_carga_gratis_km,
    -- Toneladas de correio × km voado [inferido (padrão de nome)]
    CAST(nr_correio_km AS INTEGER) AS nr_correio_km,
    -- Toneladas de bagagem excedente (paga) × km voado [inferido (padrão de nome)]
    CAST(nr_bagagem_paga_km AS INTEGER) AS nr_bagagem_paga_km,
    -- Toneladas de bagagem franqueada (gratuita) × km voado [inferido (padrão de nome)]
    CAST(nr_bagagem_gratis_km AS INTEGER) AS nr_bagagem_gratis_km,
    -- ===== METRICAS-PADRAO DA INDUSTRIA (ASK/RPK/ATK/RTK) =====
    -- Available Seat-Kilometers — assentos ofertados × km voado; métrica-padrão da indústria aérea para capacidade de transporte de passageiros [alta confiança]
    CAST(nr_ask AS INTEGER) AS nr_ask,
    -- Revenue Passenger-Kilometers — passageiros pagos × km voado; métrica-padrão de demanda de passageiros [alta confiança]
    CAST(nr_rpk AS INTEGER) AS nr_rpk,
    -- Available Ton-Kilometers — capacidade total ofertada (payload, em toneladas) × km voado [alta confiança]
    CAST(nr_atk AS INTEGER) AS nr_atk,
    -- Revenue Ton-Kilometers — carga paga total transportada (toneladas) × km voado [alta confiança]
    CAST(nr_rtk AS INTEGER) AS nr_rtk,
    -- ===== METADADO DE PROCESSAMENTO ANAC / PIPELINE =====
    -- Identificador do arquivo de origem do registro no sistema ANAC [alta confiança]
    CAST(id_arquivo AS INTEGER) AS id_arquivo,
    -- Nome do arquivo de origem do registro [alta confiança]
    NULLIF(nm_arquivo, '') AS nm_arquivo,
    -- Número da linha do registro dentro do arquivo de origem [alta confiança]
    CAST(nr_linha AS INTEGER) AS nr_linha,
    -- Data/timestamp de processamento do registro pelo sistema da ANAC [inferido (padrão de nome)]
    datetime(dt_sistema) AS dt_sistema,
    -- Chave técnica adicional do registro — papel exato no processo ANAC não verificado [incerto — checar dicionário oficial ANAC]
    NULLIF(nr_chave, '') AS nr_chave,
    -- Ano-mês (AAAA-MM) do arquivo de origem — coluna de proveniência ADICIONADA por este pipeline (03_build_schema.py), não pertence ao arquivo ANAC original [confirmado]
    NULLIF(nr_ano_mes_arquivo, '') AS nr_ano_mes_arquivo
FROM basica_raw;
