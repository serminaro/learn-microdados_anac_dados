# SPEC-010 — Perguntas de Análise: Deep Dive GOL (dados ANAC)

**Data:** 2026-08-17
**Autor:** Bruno Serminaro (CCO Azul), com apoio de Cortex Code
**Fonte de dado:** `SANDBOX_CCO.ANAC_MICRODATA.TRUSTED_FLIGHTS` (dynamic table, microdados básicos ANAC), filtrado para `SG_EMPRESA_ICAO = 'GLO'`
**Dicionário de referência:** `docs/dicionario_colunas_basica.md`

## 1. Objetivo

Caracterizar a operação da GOL (concorrente) a partir do microdado público básico da ANAC, como insumo de deep dive competitivo para o CCO da Azul. O dado usado é 100% público/regulatório (classificação: Pública/Interna, sem informação Confidencial da Azul envolvida nesta análise).

## 2. Premissa metodológica

Cada pergunta segue o mesmo processo: (1) destravar o conceito por trás do termo, porque a maioria admite mais de uma definição defensável; (2) mapear as colunas candidatas no dicionário; (3) declarar premissas e incertezas de dado antes de calcular; (4) quando há mais de uma definição igualmente válida, reportar as alternativas em vez de escolher uma só de forma arbitrária.

Filtro comum a todas as perguntas, salvo indicação em contrário: ano de referência 2025 (`NR_ANO_PARTIDA_REAL = 2025`), etapas de serviço `PASSAGEIRO` (exclui `CARGUEIRO`, `DS_SERVICO_TIPO_LINHA`).

## 3. As cinco perguntas

| # | Pergunta | Bloco | Status |
|---|---|---|---|
| A | Quantidade de destinos atendidos | 1 | Respondida |
| B | Etapa média | 1 | Respondida |
| C | Utilização de frota | 1 | Respondida |
| D | Block time: onde a GOL tem sobra? Existe estratégia por trás? | 2 | A detalhar |
| E | Tempo de solo em hubs e off-hubs | 2 | A detalhar |

---

## A. Quantidade de destinos atendidos

### Conceito

"Destino" admite três leituras: aeroportos distintos como ponto de chegada (`SG_IATA_DESTINO`), municípios distintos como ponto de chegada (`NM_MUNICIPIO_DESTINO`), ou a malha como um todo (união de aeroportos que aparecem como origem ou destino). A leitura literal (só `SG_IATA_DESTINO`) subestima a rede real: no dado 2025 há aeroportos que a GOL usa como origem mas nunca aparecem como destino no ano (e vice-versa), então "destino isolado" e "malha" não coincidem.

### Colunas usadas

`SG_IATA_ORIGEM`, `SG_IATA_DESTINO`, `NM_MUNICIPIO_DESTINO`, `DS_NATUREZA_TIPO_LINHA` (doméstica/internacional), `DS_SERVICO_TIPO_LINHA` (filtro passageiro), `NR_MES_PARTIDA_REAL`, `NR_ANO_PARTIDA_REAL`.

### Definição adotada

Reportar aeroporto-destino, município-destino e malha total (união origem+destino), com quebra doméstica/internacional. Métrica principal recomendada: malha total, por capturar a rede real sem o viés de contar só o sentido "destino".

### Premissas e incertezas

- Ano completo (visão anual), não foto de dezembro.
- Aeroporto ≠ município: cidades com mais de um aeroporto (ex.: São Paulo com CGH/GRU/VCP) contam como aeroportos distintos, não como uma cidade só.
- Etapas cargueiras excluídas; se incluídas, a malha de carga pode diferir da malha de passageiros.

### Resultado (GOL 2025, base passageiro, 238.438 etapas)

| Métrica | Doméstica | Internacional | Total (malha unificada) |
|---|---|---|---|
| Aeroportos como destino | 69 | 50 | 99 |
| Aeroportos como origem | 69 | 52 | 101 |
| Aeroportos na malha (união) | — | — | **102** |
| Municípios como destino | 68 | 33 | 98 |

Variação mensal pequena (61 a 68 municípios doméstico+internacional combinados por mês), sem sazonalidade forte de abertura/fechamento de rota ao longo do ano.

---

## B. Etapa média

### Conceito

Métrica-padrão da indústria (stage length), mas com duas formas de cálculo que não coincidem: média simples de distância por etapa (`AVG(KM_DISTANCIA)`), ou média ponderada por capacidade oferecida (`SUM(ASK) / SUM(assentos ofertados)`, equivalente a ponderar a distância pelos assentos de cada etapa). A ponderada é a mais comum em relatórios de indústria aérea.

### Colunas usadas

`KM_DISTANCIA`, `NR_ASK`, `NR_ASSENTOS_OFERTADOS`, `DS_NATUREZA_TIPO_LINHA`, `DS_SERVICO_TIPO_LINHA`, `NR_MES_PARTIDA_REAL`.

### Definição adotada

Reportar as duas (simples e ponderada por ASK), segmentado por doméstica/internacional, porque misturar os dois segmentos no mesmo número é viés de agregação (etapa internacional é ~2,6x mais longa que a doméstica).

### Premissas e incertezas

- Etapas cargueiras excluídas (mesma base de A).
- Nenhuma etapa de reposicionamento (ferry) identificada separadamente no ano; `DS_NATUREZA_ETAPA` não distingue isso (ver correção no dicionário, item 3 abaixo).

### Resultado (GOL 2025, base passageiro)

| Recorte | Simples (km) | Ponderada por ASK (km) |
|---|---|---|
| Doméstica | 1.032 | 1.046 |
| Internacional | 2.684 | 2.664 |
| Total | 1.156 | 1.165 |

As duas versões ficam próximas em ambos os segmentos (diferença < 1,5%). Achado a investigar (hipótese, não conclusão): na internacional a ponderada é menor que a simples, sugerindo que etapas internacionais mais curtas usam aeronaves/configurações com mais assentos.

---

## C. Utilização de frota

### Conceito

"Utilização de frota" mistura pelo menos três métricas distintas: horas de bloco voadas por dia por aeronave (uso do ativo), ciclos/decolagens por dia (uso do ativo em frequência), e load factor (uso da capacidade oferecida, não do ativo). São complementares, não substitutos.

### Colunas usadas

`NR_HORAS_VOADAS`, `SG_EQUIPAMENTO_ICAO`, `DS_MODELO`, `DS_MATRICULA`, `DT_PARTIDA_REAL`, `DS_SERVICO_TIPO_LINHA`.

### Definição adotada

Horas voadas por dia por aeronave, agregado por tipo de frota (`SG_EQUIPAMENTO_ICAO`), normalizado pelo número de aeronaves distintas (`DS_MATRICULA`) do tipo e por 365 dias.

### Premissas e incertezas

- `DS_MATRICULA` sem nulos para GOL 2025 (verificado: 0% vazio), diferente do ~12% de nulos citado no dicionário para a base histórica completa; a métrica por matrícula é confiável neste recorte.
- `NR_HORAS_VOADAS` é horas voadas, provavelmente tempo no ar (airborne, decolagem a pouso), não tempo de bloco porta a porta. A utilização real (block time) tende a ser um pouco maior, pois inclui taxi. Ver correção no dicionário, item 2.
- Dividir por 365 dias assume frota estável o ano inteiro; aeronave que entrou/saiu da frota no meio do ano tem utilização subestimada (denominador conta dias em que ela não operava).

### Resultado (GOL 2025, base passageiro)

| Frota | Aeronaves distintas | Horas voadas/ano | Horas voadas/dia/aeronave |
|---|---|---|---|
| B38M (737 MAX 8) | 59 | 239.526 | **11,12** |
| B737 (737-700) | 12 | 37.162 | 8,48 |
| B738 (737-800) | 72 | 205.004 | 7,80 |

O MAX 8 roda cerca de 3,3h/dia mais que a frota mais antiga, consistente com uma leitura de priorização operacional da aeronave mais nova/eficiente (leitura sobre o número, não algo que o dado prova por si).

---

## 4. Correções aplicadas ao dicionário (`docs/dicionario_colunas_basica.md`)

1. `NR_HORAS_VOADAS`: rebaixado de "confirmado" para "incerto"; nota explícita sobre a ambiguidade airborne time x block time, decisiva para as perguntas D e E.
2. Nota adicionada: o dataset básico não tem horários programados/previstos (`HR_PARTIDA_PREVISTA`/`HR_CHEGADA_PREVISTA` não existem); análise de folga contra o programado exigiria o dataset VRA da ANAC.
3. `DS_NATUREZA_ETAPA`: corrigido de "comercial/não comercial" (inferido, incorreto) para "doméstica/internacional" (confirmado no dado GOL 2025), redundante com `DS_NATUREZA_TIPO_LINHA`.

## 5. Próximos passos

- Detalhar D (proxy de sobra de block time por rota + tipo de equipamento, já que não há horário programado no dataset básico) e E (hub inferido pelo volume de operações, já que não há coluna de classificação hub no dado ANAC).
- Validar com o usuário se a leitura "malha total" (pergunta A) deve ser a métrica oficial reportada, em vez de "destino isolado".
