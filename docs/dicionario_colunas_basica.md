# Dicionário de colunas — tabela Básica (ANAC)

> Legendas construídas a partir da convenção de nomes (prefixos `ID_/SG_/CD_/NM_/DS_/NR_/DT_/HR_/KG_/KM_/LT_`),
> do conhecimento de domínio de tráfego aéreo (ASK/RPK/ATK/RTK são métricas-padrão da indústria) e do
> comportamento observado nos dados/scripts deste repositório. **Não é o dicionário oficial da ANAC** —
> onde não há confirmação direta (dado observado, README ou DDL deste projeto), a coluna "confiança" marca isso.
>
> - **confirmado**: verificado no código, dado ou documentação deste repositório.
> - **alta**: nome segue padrão inequívoco (prefixo + termo de aviação/geografia padrão), sem ambiguidade plausível.
> - **inferido**: leitura razoável do nome e do contexto, mas sem confirmação direta — tratar como hipótese.
> - **incerto**: nome não permite inferência segura; precisa do dicionário oficial ANAC para fechar.

| # | Coluna | Legenda | Confiança |
|---|---|---|---|
| 1 | `ID_BASICA` | Chave primária do registro (uma linha = uma etapa de voo realizada) | confirmado |
| 2 | `ID_EMPRESA` | Identificador numérico da empresa aérea | alta confiança |
| 3 | `SG_EMPRESA_ICAO` | Código ICAO (3 letras) da empresa aérea, ex.: GLO, TAM, AZU | alta confiança |
| 4 | `SG_EMPRESA_IATA` | Código IATA (2 caracteres) da empresa aérea, ex.: G3, JJ, AD | alta confiança |
| 5 | `NM_EMPRESA` | Nome/razão social da empresa aérea | alta confiança |
| 6 | `NM_PAIS` | País de registro da empresa aérea | inferido (padrão de nome) |
| 7 | `DS_TIPO_EMPRESA` | Classificação do tipo de empresa aérea (ex.: nacional regular) — categorias exatas não verificadas | incerto — checar dicionário oficial ANAC |
| 8 | `NR_VOO` | Número comercial do voo | alta confiança |
| 9 | `NR_SINGULAR` | Identificador numérico da etapa nos sistemas ANAC — termo "singular" não confirmado com precisão | incerto — checar dicionário oficial ANAC |
| 10 | `ID_DI` | Identificador do "DI" associado à etapa — sigla DI não confirmada com certeza (possível "Discriminação de Itinerário") | incerto — checar dicionário oficial ANAC |
| 11 | `CD_DI` | Código do DI (ver ID_DI) | incerto — checar dicionário oficial ANAC |
| 12 | `DS_DI` | Descrição textual do DI (ver ID_DI) | incerto — checar dicionário oficial ANAC |
| 13 | `DS_GRUPO_DI` | Descrição do grupo/categoria a que o DI pertence | incerto — checar dicionário oficial ANAC |
| 14 | `DT_REFERENCIA` | Data de referência do boletim (mês/ano de apuração) | alta confiança |
| 15 | `NR_ANO_REFERENCIA` | Ano de referência | alta confiança |
| 16 | `NR_SEMESTRE_REFERENCIA` | Semestre de referência (1 ou 2) | alta confiança |
| 17 | `NM_SEMESTRE_REFERENCIA` | Nome do semestre de referência (ex.: 1º Semestre) | alta confiança |
| 18 | `NR_TRIMESTRE_REFERENCIA` | Trimestre de referência (1 a 4) | alta confiança |
| 19 | `NM_TRIMESTRE_REFERENCIA` | Nome do trimestre de referência | alta confiança |
| 20 | `NR_MES_REFERENCIA` | Mês de referência (1 a 12) | alta confiança |
| 21 | `NM_MES_REFERENCIA` | Nome do mês de referência | alta confiança |
| 22 | `NR_SEMANA_REFERENCIA` | Número da semana no ano de referência | alta confiança |
| 23 | `NM_DIA_SEMANA_REFERENCIA` | Nome do dia da semana de referência | alta confiança |
| 24 | `NR_DIA_REFERENCIA` | Dia do mês de referência | alta confiança |
| 25 | `NR_ANO_MES_REFERENCIA` | Ano-mês de referência, formato AAAAMM | alta confiança |
| 26 | `ID_TIPO_LINHA` | Identificador do tipo de linha aérea | alta confiança |
| 27 | `CD_TIPO_LINHA` | Código do tipo de linha aérea | alta confiança |
| 28 | `DS_TIPO_LINHA` | Descrição do tipo de linha (ex.: doméstica, internacional) | alta confiança |
| 29 | `DS_NATUREZA_TIPO_LINHA` | Natureza do tipo de linha (ex.: doméstica / internacional) | inferido (padrão de nome) |
| 30 | `DS_SERVICO_TIPO_LINHA` | Tipo de serviço prestado na linha (ex.: passageiro, carga, mista) | inferido (padrão de nome) |
| 31 | `DS_NATUREZA_ETAPA` | Natureza da etapa de voo (ex.: comercial, não comercial/posicionamento) | inferido (padrão de nome) |
| 32 | `HR_PARTIDA_REAL` | Hora real de partida (decolagem) | confirmado |
| 33 | `DT_PARTIDA_REAL` | Data real de partida | confirmado |
| 34 | `NR_ANO_PARTIDA_REAL` | Ano de partida real | alta confiança |
| 35 | `NR_SEMESTRE_PARTIDA_REAL` | Semestre de partida real (1 ou 2) | alta confiança |
| 36 | `NM_SEMESTRE_PARTIDA_REAL` | Nome do semestre de partida real (ex.: 1º Semestre) | alta confiança |
| 37 | `NR_TRIMESTRE_PARTIDA_REAL` | Trimestre de partida real (1 a 4) | alta confiança |
| 38 | `NM_TRIMESTRE_PARTIDA_REAL` | Nome do trimestre de partida real | alta confiança |
| 39 | `NR_MES_PARTIDA_REAL` | Mês de partida real (1 a 12) | alta confiança |
| 40 | `NM_MES_PARTIDA_REAL` | Nome do mês de partida real | alta confiança |
| 41 | `NR_SEMANA_PARTIDA_REAL` | Número da semana no ano de partida real | alta confiança |
| 42 | `NM_DIA_SEMANA_PARTIDA_REAL` | Nome do dia da semana de partida real | alta confiança |
| 43 | `NR_DIA_PARTIDA_REAL` | Dia do mês de partida real | alta confiança |
| 44 | `NR_ANO_MES_PARTIDA_REAL` | Ano-mês de partida real, formato AAAAMM | alta confiança |
| 45 | `ID_AERODROMO_ORIGEM` | Identificador do aeródromo de origem | alta confiança |
| 46 | `SG_ICAO_ORIGEM` | Código ICAO do aeródromo de origem | alta confiança |
| 47 | `SG_IATA_ORIGEM` | Código IATA do aeródromo de origem | confirmado |
| 48 | `NM_AERODROMO_ORIGEM` | Nome do aeródromo de origem | alta confiança |
| 49 | `NM_MUNICIPIO_ORIGEM` | Município do aeródromo de origem | alta confiança |
| 50 | `SG_UF_ORIGEM` | UF do aeródromo de origem | alta confiança |
| 51 | `NM_REGIAO_ORIGEM` | Região geográfica (Norte/Sul/etc.) do aeródromo de origem | alta confiança |
| 52 | `NM_PAIS_ORIGEM` | País do aeródromo de origem | alta confiança |
| 53 | `NM_CONTINENTE_ORIGEM` | Continente do aeródromo de origem | alta confiança |
| 54 | `NR_ETAPA` | Número sequencial da etapa dentro do voo (voos com múltiplas escalas têm mais de uma etapa) | confirmado |
| 55 | `HR_CHEGADA_REAL` | Hora real de chegada (pouso) | confirmado |
| 56 | `DT_CHEGADA_REAL` | Data real de chegada | confirmado |
| 57 | `NR_ANO_CHEGADA_REAL` | Ano de chegada real | alta confiança |
| 58 | `NR_SEMESTRE_CHEGADA_REAL` | Semestre de chegada real (1 ou 2) | alta confiança |
| 59 | `NM_SEMESTRE_CHEGADA_REAL` | Nome do semestre de chegada real (ex.: 1º Semestre) | alta confiança |
| 60 | `NR_TRIMESTRE_CHEGADA_REAL` | Trimestre de chegada real (1 a 4) | alta confiança |
| 61 | `NM_TRIMESTRE_CHEGADA_REAL` | Nome do trimestre de chegada real | alta confiança |
| 62 | `NR_MES_CHEGADA_REAL` | Mês de chegada real (1 a 12) | alta confiança |
| 63 | `NM_MES_CHEGADA_REAL` | Nome do mês de chegada real | alta confiança |
| 64 | `NR_SEMANA_CHEGADA_REAL` | Número da semana no ano de chegada real | alta confiança |
| 65 | `NM_DIA_SEMANA_CHEGADA_REAL` | Nome do dia da semana de chegada real | alta confiança |
| 66 | `NR_DIA_CHEGADA_REAL` | Dia do mês de chegada real | alta confiança |
| 67 | `NR_ANO_MES_CHEGADA_REAL` | Ano-mês de chegada real, formato AAAAMM | alta confiança |
| 68 | `ID_EQUIPAMENTO` | Identificador do tipo/modelo de aeronave (equipamento) | alta confiança |
| 69 | `SG_EQUIPAMENTO_ICAO` | Código ICAO do tipo de aeronave, ex.: A320, B738 | alta confiança |
| 70 | `DS_MODELO` | Descrição do modelo da aeronave | alta confiança |
| 71 | `DS_MATRICULA` | Matrícula (prefixo de registro) da aeronave — vazia em ~12% das linhas quando a etapa não identifica a aeronave | confirmado |
| 72 | `ID_AERODROMO_DESTINO` | Identificador do aeródromo de destino | alta confiança |
| 73 | `SG_ICAO_DESTINO` | Código ICAO do aeródromo de destino | alta confiança |
| 74 | `SG_IATA_DESTINO` | Código IATA do aeródromo de destino | confirmado |
| 75 | `NM_AERODROMO_DESTINO` | Nome do aeródromo de destino | alta confiança |
| 76 | `NM_MUNICIPIO_DESTINO` | Município do aeródromo de destino | alta confiança |
| 77 | `SG_UF_DESTINO` | UF do aeródromo de destino | alta confiança |
| 78 | `NM_REGIAO_DESTINO` | Região geográfica do aeródromo de destino | alta confiança |
| 79 | `NM_PAIS_DESTINO` | País do aeródromo de destino | alta confiança |
| 80 | `NM_CONTINENTE_DESTINO` | Continente do aeródromo de destino | alta confiança |
| 81 | `NR_ESCALA_DESTINO` | Posição/número da escala na rota até este destino — definição exata não verificada | incerto — checar dicionário oficial ANAC |
| 82 | `LT_COMBUSTIVEL` | Combustível consumido ou embarcado na etapa, em litros | inferido (padrão de nome) |
| 83 | `NR_ASSENTOS_OFERTADOS` | Número de assentos ofertados na etapa | confirmado |
| 84 | `KG_PAYLOAD` | Payload: capacidade de carga paga (passageiros + carga + correio), em kg | confirmado |
| 85 | `KM_DISTANCIA` | Distância voada na etapa, em km | confirmado |
| 86 | `NR_PASSAG_PAGOS` | Número de passageiros pagantes transportados | alta confiança |
| 87 | `NR_PASSAG_GRATIS` | Número de passageiros em cortesia/gratuidade | alta confiança |
| 88 | `KG_BAGAGEM_LIVRE` | Peso de bagagem despachada dentro da franquia gratuita, em kg | alta confiança |
| 89 | `KG_BAGAGEM_EXCESSO` | Peso de bagagem despachada acima da franquia, paga pelo passageiro, em kg | alta confiança |
| 90 | `KG_CARGA_PAGA` | Peso de carga paga transportada, em kg | alta confiança |
| 91 | `KG_CARGA_GRATIS` | Peso de carga transportada gratuitamente, em kg | alta confiança |
| 92 | `KG_CORREIO` | Peso de correio (mala postal) transportado, em kg | alta confiança |
| 93 | `NR_DECOLAGEM` | Contagem de decolagens da etapa (tipicamente 1) — uso exato (ex.: fins de tarifa de pouso) não verificado | incerto — checar dicionário oficial ANAC |
| 94 | `NR_HORAS_VOADAS` | Duração voada da etapa, em horas (decimal com vírgula no arquivo original) | confirmado |
| 95 | `KG_PESO` | Peso associado à etapa, em kg — se refere a payload realizado, peso da aeronave ou outro, não verificado | incerto — checar dicionário oficial ANAC |
| 96 | `NR_VELOCIDADE_MEDIA` | Velocidade média da etapa | inferido (padrão de nome) |
| 97 | `NR_PAX_GRATIS_KM` | Passageiros gratuitos × km voado (produção análoga ao RPK, para gratuidade) | inferido (padrão de nome) |
| 98 | `NR_CARGA_PAGA_KM` | Toneladas de carga paga × km voado | inferido (padrão de nome) |
| 99 | `NR_CARGA_GRATIS_KM` | Toneladas de carga gratuita × km voado | inferido (padrão de nome) |
| 100 | `NR_CORREIO_KM` | Toneladas de correio × km voado | inferido (padrão de nome) |
| 101 | `NR_BAGAGEM_PAGA_KM` | Toneladas de bagagem excedente (paga) × km voado | inferido (padrão de nome) |
| 102 | `NR_BAGAGEM_GRATIS_KM` | Toneladas de bagagem franqueada (gratuita) × km voado | inferido (padrão de nome) |
| 103 | `NR_ASK` | Available Seat-Kilometers — assentos ofertados × km voado; métrica-padrão da indústria aérea para capacidade de transporte de passageiros | alta confiança |
| 104 | `NR_RPK` | Revenue Passenger-Kilometers — passageiros pagos × km voado; métrica-padrão de demanda de passageiros | alta confiança |
| 105 | `NR_ATK` | Available Ton-Kilometers — capacidade total ofertada (payload, em toneladas) × km voado | alta confiança |
| 106 | `NR_RTK` | Revenue Ton-Kilometers — carga paga total transportada (toneladas) × km voado | alta confiança |
| 107 | `ID_ARQUIVO` | Identificador do arquivo de origem do registro no sistema ANAC | alta confiança |
| 108 | `NM_ARQUIVO` | Nome do arquivo de origem do registro | alta confiança |
| 109 | `NR_LINHA` | Número da linha do registro dentro do arquivo de origem | alta confiança |
| 110 | `DT_SISTEMA` | Data/timestamp de processamento do registro pelo sistema da ANAC | inferido (padrão de nome) |
| 111 | `NR_CHAVE` | Chave técnica adicional do registro — papel exato no processo ANAC não verificado | incerto — checar dicionário oficial ANAC |
| 112 | `NR_ANO_MES_ARQUIVO` | Ano-mês (AAAA-MM) do arquivo de origem — coluna de proveniência ADICIONADA por este pipeline (03_build_schema.py), não pertence ao arquivo ANAC original | confirmado |
| 113 | `DT_REFERENCIA_DATE` | Data de referência em tipo DATE — presente apenas neste arquivo colunas.dat; não é gerada em nenhum script/DDL deste repositório hoje (órfã no pipeline atual) | confirmado |
