---
documento: SPEC-004
titulo: Perguntas de Análise — Deep Dive GOL e Azul via microdados ANAC (genérico, dois caminhos)
versao: v4
status: aprovado
data: 2026-08-31
autor: Bruno Alexandre Serminaro
referencia: DEC-007, SPEC-005
escopo: projeto
---

# SPEC-004 · Perguntas de Análise: Deep Dive GOL e Azul

> Declara o que este bloco de conteúdo entrega: definição **genérica**
> (agnóstica de engine) de cada pergunta de análise, a arquitetura de
> camadas fixada pela `DEC-007`, e a implementação concreta em cada
> caminho de produção (Snowflake, SQLite+Python) para as perguntas usadas
> como exemplo de referência. Primeira SPEC de conteúdo do projeto
> (`SPEC-001 §9`).

---

## 1. Propósito

Responder, dentro deste projeto de portfólio, seis perguntas de análise
sobre a operação de dois concorrentes (GOL e Azul), com: (i) cada pergunta definida de forma genérica, sem pensar em
engine; (ii) duas perguntas — comportamento do tempo de solo e
caracterização das bases hub/off-hub — detalhadas por completo, do
conceito até a implementação em cada caminho de produção, como referência
de tradução genérico → implementação para as demais. Materializa a
`DEC-007`.

## 2. Audiência

Reaproveita os papéis abstratos do `SPEC-002 §2` (Autor, Par assistivo,
Autor futuro, Leitor do repositório) — nenhum papel novo.

## 3. Escopo

### 3.1 O que este SPEC entrega

1. **Definição genérica** das seis perguntas de análise (§5), sem
   amarrar a nenhum motor.
2. **Camada `trusted_essencial`** e **duas camadas `curated`**
   (`curated_deep_dive_gol`, `curated_deep_dive_azul`) — arquitetura
   fixada pela `DEC-007`, válida nos dois caminhos.
3. **Detalhamento completo** das perguntas "Comportamento do tempo de
   solo" e "Caracterização das bases (hub/off-hub)" (§6): método passo a
   passo, e implementação concreta nos dois caminhos (SQLite+Python,
   Snowflake) — as duas perguntas compartilham a mesma sequência de
   cálculo (`DEC-007 §2.b`), por isso um único detalhamento cobre as
   duas.
4. **Registro explícito de bloqueio** da pergunta "Block time" até a
   ingestão do VRA existir neste projeto.

### 3.2 Fora de escopo

- Implementação SQL completa das outras três perguntas respondíveis
  (destinos/rota/mercado, distribuição da frota, etapa média) — esta
  versão fixa só a definição genérica (§5); a implementação segue o
  padrão do §6 quando for a vez de cada uma.
- Métodos avançados de análise que vão além da definição mínima da
  pergunta (ex.: decomposição em frequência/Fourier
  da sazonalidade de destinos) — tratados como extensão opcional de
  referência, não requisito desta SPEC (§5.1).
- Análise de rota e mercado (§5.1): esta versão só **define o conceito e
  o método** — a execução fica para quando o autor implementar (§5.1,
  "status: em andamento").
- Etapa média ponderada por ASK (`NR_ASK`, `NR_ASSENTOS_OFERTADOS`) — fora
  de escopo (decisão do autor, 2026-08-30); a etapa média por distância
  **não** sai da lista (correção de 2026-08-31, `DEC-007 §1`) — funde-se
  com a duração sob "Etapa média" (§5.5), só a ponderação por ASK fica de
  fora. Pela mesma decisão, a análise de fluxo por rota/mercado (§5.1)
  fica limitada a **frequência de etapas**, não a capacidade ofertada.
- Responder "block time" com proxy sem horário programado —
  `DEC-007 §4.4` descartou essa via.
- Reaproveitar objetos do ambiente de trabalho `SANDBOX_CCO` — este
  projeto usa dado público recarregado nos próprios objetos
  (`basica_raw`/`basica_silver`), sem dependência daquele schema.

## 4. Decomposição do produto

### 4.1 Cadeia de camadas (genérica, um nome por objeto nos dois caminhos)

```
basica_raw → basica_silver → trusted_essencial → curated_deep_dive_gol
                                                → curated_deep_dive_azul
```

`trusted_essencial` reduz de 112 para 29 colunas; cada `curated` filtra
por `sg_empresa_icao` e pela janela `dt_partida_real >= '2021-01-01'`.
`basica_silver` (2026-08-31) substitui `basica_typed` — cobre as 112
colunas de `basica_raw`, organizadas e comentadas a partir de `SPEC-005`,
não mais um recorte de ~27 colunas com métrica derivada misturada
(`SPEC-008 v3`). Mesmos nomes literais nos dois caminhos, seguindo o
precedente de `sql/tratamento/DDL_003_..._sqlite.sql` (Snowflake segue
com `basica_typed`, divergência temporária registrada, não resolvida
aqui).

### 4.2 Estrutura de pastas (código, por caminho)

```
sql/tratamento/   próximos DDL_NNN (ordem de criação, os dois caminhos):
                    trusted_essencial (SQLite e Snowflake)
sql/analise/      primeiro conteúdo real da pasta, próximos DDL_NNN:
                    curated_deep_dive_gol (SQLite e Snowflake)
                    curated_deep_dive_azul (SQLite e Snowflake)
```

Número exato de cada `DDL_NNN` decidido na ordem de criação
(`DEC-001 §6.6`), não fixado aqui.

### 4.3 Mapa pergunta → colunas → camada

| # | Pergunta | Colunas-chave (`SPEC-005`) | Camada | Status |
|---|---|---|---|---|
| 1 | Números de destinos, rotas e mercados | `SG_ICAO_ORIGEM`/`DESTINO`, `SG_IATA_ORIGEM`/`DESTINO`, `NM_MUNICIPIO_ORIGEM`/`DESTINO`, `DS_NATUREZA_TIPO_LINHA` | `curated_deep_dive_*` | Destinos: respondida. Rota/mercado: em andamento |
| 2 | Distribuição da frota | `DS_MATRICULA`, `SG_EQUIPAMENTO_ICAO`, `DS_MODELO`, `DT_PARTIDA_REAL` | `curated_deep_dive_*` | Respondível agora |
| 3 | Comportamento do tempo de solo | `DS_MATRICULA`, `SG_EQUIPAMENTO_ICAO`, `DT_PARTIDA_REAL`, `HR_PARTIDA_REAL`, `DT_CHEGADA_REAL`, `HR_CHEGADA_REAL`, `SG_ICAO_ORIGEM`/`DESTINO` | `curated_deep_dive_*` | **Detalhada nesta versão (§6)** |
| 4 | Caracterização das bases (hub/off-hub) | `SG_ICAO_DESTINO`, `SG_IATA_DESTINO`, `DT_PARTIDA_REAL` | `curated_deep_dive_*` | **Detalhada nesta versão (§6)** |
| 5 | Etapa média (duração principal + distância + velocidade inferida) | `NR_HORAS_VOADAS`, `KM_DISTANCIA`, `DS_NATUREZA_TIPO_LINHA`, `SG_EQUIPAMENTO_ICAO` | `curated_deep_dive_*` | Respondível agora |
| 6 | Block time (sobra e estratégia) | Exige horário programado — não existe na Básica | `curated_block_time_*` (desenhada, §5.6) | **Bloqueada (VRA)** |

## 5. Definição genérica de cada pergunta

Método comum (mantido pela `DEC-007 §2.a`): destravar o conceito, mapear
colunas candidatas, declarar
premissas/incertezas antes de calcular, reportar alternativas quando há
mais de uma definição igualmente válida.

### 5.1 Números de destinos, rotas e mercados

**Conceito — destinos (respondido).** Malha de destinos: aeroporto-destino,
município-destino, ou malha unificada (união de aeroportos como origem **ou** destino) — a leitura
literal (só destino) subestima a rede real.

**Colunas — destinos.** `SG_ICAO_ORIGEM`/`SG_ICAO_DESTINO`,
`SG_IATA_ORIGEM`/`SG_IATA_DESTINO`, `NM_MUNICIPIO_DESTINO`,
`DS_NATUREZA_TIPO_LINHA` (doméstica/internacional),
`DS_SERVICO_TIPO_LINHA` (filtro passageiro), `DT_PARTIDA_REAL` (quebra
temporal).

**Método — destinos.** Contar valores distintos de destino (aeroporto,
município) e malha unificada, por período (mês, ano); reportar quebra
doméstica/internacional.

**Extensão de referência, não requisito mínimo.** Já existe análise de
ciclos semanais e decomposição em frequência (Fourier) da variação do
número de destinos, para GOL e Azul, 2021-2026 — fica registrada como
método avançado de referência, não como critério de sucesso desta versão.

---

**Extensão em andamento (pedido do autor, 2026-08-31): rota e mercado.**
Objetivo: verificar se um mercado tem fluxo maior num sentido do que no
outro (assimetria direcional) — pergunta distinta de "quantos destinos
existem", ainda não respondida, o autor pretende implementar.

**Conceito — rota.** Par **ordenado** origem→destino, no nível
operacional do dado — aeroporto (`SG_ICAO_ORIGEM`/`SG_ICAO_DESTINO` ou
IATA). Cada etapa pertence a exatamente uma rota; GRU→SDU e SDU→GRU são
duas rotas distintas (sentidos opostos da mesma ligação física). É a
unidade certa para métricas inerentemente direcionais (ex.: quantas
etapas partiram de GRU para SDU).

**Conceito — mercado.** Par **não ordenado**, definido **por par de
aeroportos** (decisão do autor, 2026-08-31): mercado GRU–SDU é diferente
de mercado CGH–SDU, mesmo que ambos liguem São Paulo e Rio de Janeiro —
não agrega por município. Duas rotas de sentido oposto (A→B e B→A)
pertencem ao mesmo mercado — é a unidade certa para comparar fluxo entre
sentidos, porque uma rota já fixa o sentido (não há "desequilíbrio de
sentido" dentro de uma única rota).

**Colunas.** Já cobertas pelas 29 essenciais, **nenhuma coluna nova
necessária**: `SG_ICAO_ORIGEM`/`SG_ICAO_DESTINO` (chave de rota e de
mercado, nível aeroporto), `SG_IATA_ORIGEM`/`SG_IATA_DESTINO` (leitura),
`DT_PARTIDA_REAL` (quebra temporal). `NM_MUNICIPIO_ORIGEM`/`DESTINO` não
entram nesta pergunta — ficam disponíveis na `trusted_essencial` para
outro uso, mas não são a chave de mercado adotada aqui.

**Método (rascunho de abordagem, a validar na implementação).**

1. Construir a chave de mercado: par não ordenado de aeroporto (ICAO ou
   IATA) — normalizar ordenando os dois códigos (ex.: sempre o menor
   alfabeticamente como primeiro elemento da chave), para que A→B e B→A
   caiam na mesma chave.
2. Dentro de cada mercado, rotular cada etapa pelo "sentido" (sentido 1 =
   da ordem alfabética menor para a maior; sentido 2 = o oposto).
3. Contar etapas por sentido, dentro de cada mercado e período.
4. Comparar sentido 1 vs. sentido 2: razão (ou diferença percentual) de
   etapas.
5. Reportar mercados com maior assimetria (razão mais distante de 1:1).

**Premissa/limitação a registrar.** "Fluxo" nesta pergunta fica medido
por **frequência de etapas** (decisão do autor, 2026-08-31) — não por
capacidade ofertada. `NR_ASSENTOS_OFERTADOS`/`NR_ASK` seguem fora do
conjunto essencial; medir assimetria por capacidade fica **deliberadamente
adiado para outro momento**, não é ausência não examinada.

**Status.** Em andamento, não concluída — diferente da extensão de
Fourier/sazonalidade (só referência), esta é ativamente perseguida pelo
autor; vira parte de C-03 quando implementada.

### 5.2 Distribuição da frota

**Conceito.** Composição percentual da frota por modelo de equipamento e
idade de serviço por matrícula (tempo entre primeira e última aparição no
dado). Substitui a antiga "utilização de frota" (horas voadas/dia) — o
foco muda de intensidade de uso para composição/idade (`DEC-007 §1`).

**Colunas.** `DS_MATRICULA`, `SG_EQUIPAMENTO_ICAO`, `DS_MODELO`,
`DT_PARTIDA_REAL`.

**Método.** % de etapas (ou de matrículas distintas) por modelo, evolução
ano a ano; idade de serviço por matrícula = `MAX(DT_PARTIDA_REAL) −
MIN(DT_PARTIDA_REAL)`, agregada por modelo (mediana, quartis).

**Premissa herdada de análise anterior**: `DS_MATRICULA` sem nulos para o
recorte GOL 2025 era achado confirmado; para o recorte 2021-presente e
para Azul, é premissa a reconfirmar, não achado herdado automaticamente.

### 5.3 Comportamento do tempo de solo

Ver **§6** — detalhada nesta versão, do conceito à implementação em cada
caminho. Cobre a distribuição do tempo de solo (mediana, quartis,
outliers) por modelo de equipamento — sem depender da classificação de
base em hub/off-hub, que é a pergunta 4.

### 5.4 Caracterização das bases (hub/off-hub)

Ver **§6** — detalhada nesta versão. Cobre a classificação de aeroportos
em hub/off-hub por volume de chegadas — pergunta de estrutura de rede,
separada da pergunta 3 (`DEC-007 §2.b`, split pedido pelo autor,
2026-08-31); as duas se cruzam naturalmente (tempo de solo comparado
entre hub e off-hub, §6.3 passo 7), mas cada uma tem conceito e método
próprios.

### 5.5 Etapa média

**Conceito.** Retoma a "etapa média" (stage length), mas com a duração do
voo — não a distância — como métrica principal, por decisão do autor (2026-08-31): a pergunta
fundamentalmente é sobre quanto tempo a aeronave passa no ar por etapa,
não sobre quantos km ela percorre. Três métricas, uma pergunta:

1. **Duração** (principal): tempo no ar (airborne) médio por etapa —
   `NR_HORAS_VOADAS`. Não é tempo de bloco porta-a-porta (mesma ressalva
   já registrada para essa coluna, §11); por isso esta pergunta não
   substitui a pergunta 6 (block time), são conceitos distintos mesmo
   usando a coluna de origem em comum.
2. **Distância** (complementar): distância média por etapa —
   `KM_DISTANCIA`, só a versão simples (`AVG`); a versão ponderada por ASK
   segue fora de escopo (decisão de 2026-08-30, `§3.2`).
3. **Velocidade média inferida** (derivada): `KM_DISTANCIA / NR_HORAS_VOADAS`
   — não é velocidade de cruzeiro pura, é uma média que embute
   decolagem/subida/descida (porque `NR_HORAS_VOADAS` é airborne time
   completo da etapa, não só o trecho de cruzeiro); tratar como proxy
   grosseira de desempenho operacional, não como especificação técnica da
   aeronave.

**Colunas.** `NR_HORAS_VOADAS`, `KM_DISTANCIA`, `DS_NATUREZA_TIPO_LINHA`
(doméstica/internacional), `SG_EQUIPAMENTO_ICAO` (segmentação por modelo).

**Método.** Para as três métricas, segmentar por natureza da linha e por
modelo de equipamento. Duração e distância: média (e mediana, se a
distribuição for assimétrica) por etapa. Velocidade: duas formas de
agregação não coincidem, mesmo problema já nomeado para a etapa média
original —
  - **razão das somas**: `SUM(KM_DISTANCIA) / SUM(NR_HORAS_VOADAS)` no
    segmento, mais robusta (não é distorcida por etapas de duração muito
    curta com razão instável);
  - **média das razões por etapa**: `AVG(KM_DISTANCIA / NR_HORAS_VOADAS)`,
    dá peso igual a cada etapa independente da duração.

  Reportar as duas, seguindo a mesma prática já adotada nesta SPEC
  (alternativas quando há mais de uma definição válida, §5); razão das somas
  como métrica principal recomendada, por ser menos sensível a etapas
  atípicas de duração muito curta.

**Premissas e incertezas.** `NR_HORAS_VOADAS` é airborne time, não block
time — a velocidade inferida herda essa limitação (superestima a
velocidade de cruzeiro real, porque o denominador já é menor que o tempo
de bloco). Etapas com `NR_HORAS_VOADAS` muito baixo (ruído de dado) podem
gerar velocidades inferidas irreais — considerar o mesmo tipo de corte de
outlier usado na pergunta 3 (§6.3, passo 4) se a distribuição mostrar
cauda longa.

### 5.6 Block time (sobra e estratégia)

**Desbloqueada (v4)** — exigia horário programado (`HR_PARTIDA_PREVISTA`/
`HR_CHEGADA_PREVISTA`), inexistente na Básica; dependia da ingestão do
VRA neste projeto. VRA ingerido (`SPEC-012`), bloqueio superado. Não se
tenta proxy sem horário programado (`DEC-007 §4.4`) — não foi necessário,
o horário programado real já está disponível.

**Desenho registrado, não implementado (`DEC-007 §2.g`, v4).** O VRA já
existe neste projeto (`SPEC-012`) — bloqueio original superado. Esta
pergunta nasce como objeto dedicado, **único** —
`fato_block_time_gol_azul`, não `curated_block_time_gol`/
`curated_block_time_azul` como versões anteriores registravam (correção
`R-TAX-11`, alinhando com o padrão de objeto único que `curated_deep`/
`fato_rotacao_aeronave_gol_azul` já fixaram) — não como extensão de
`curated_deep_dive_*`. A junção Básica × VRA é materializada **uma
vez** por carga, não repetida a cada consulta:

- **SQLite**: `ATTACH DATABASE 'vra.sqlite' AS vra;` dentro do script que
  constrói a curated, `CREATE TABLE ... AS SELECT` (join Básica × VRA),
  `DETACH`. As bases `basica.sqlite`/`vra.sqlite` continuam separadas
  (`DEC-004` intacta) — só o resultado da junção vira objeto único.
- **Snowflake**: referência cross-schema nativa
  (`ANAC.VRA.<objeto> JOIN ANAC.BASICA.<objeto>`), sem custo de sintaxe
  extra — assimetria maior entre caminhos do que nas perguntas 3/4
  (R-ANL-06), aceita como consequência (`DEC-007 §5.2`).
- **Chave de junção**: hipótese original — empresa (ICAO) + número de
  voo + data de partida + aeroporto de origem. **Refinada (v4)**: hora de
  partida adicionada à chave — medido fora deste documento (sessão de
  trabalho, amostra GOL/Azul 2025): sem hora, 6.392 grupos de chave
  duplicada (mesmo nº de voo pode operar duas vezes no mesmo dia
  calendário); com hora, cai para 13 grupos residuais, correspondência
  ~97%. Ainda não medida contra o par atual de tabelas — fica para a
  implementação.

## 6. Perguntas de referência, detalhadas: Tempo de solo e Bases hub/off-hub

> As perguntas 3 (comportamento do tempo de solo) e 4 (caracterização das
> bases hub/off-hub) nasceram como uma pergunta só ("Tempo de Solo –
> Hub e Off-Hub"). O autor pediu (2026-08-31) separá-las em duas perguntas
> formais — conceito e critério de sucesso próprios para cada uma — sem
> perder o fato de que a implementação é compartilhada (a classificação
> hub/off-hub, pergunta 4, é insumo do passo 7 da pergunta 3). Por isso
> um único detalhamento de método cobre as duas: §6.1-§6.2 são a pergunta
> 3, §6.3 (passo 6) é a pergunta 4, §6.3 (passo 7) é o cruzamento das
> duas.

### 6.1 Conceito

**Pergunta 3 — comportamento do tempo de solo.** Tempo de solo é o
intervalo entre o pouso de uma etapa e a decolagem da etapa seguinte da
**mesma aeronave**, no **mesmo aeroporto**. A pergunta caracteriza a
distribuição desse intervalo (mediana, quartis, outliers) por modelo de
equipamento — sem depender de classificação de base.

**Pergunta 4 — caracterização das bases (hub/off-hub).** "Hub" e
"off-hub" não existem como classificação no dado ANAC — não há coluna —
são derivados por volume de chegadas, seguindo a convenção adotada nesta
análise: regra de Pareto, aeroportos que,
ordenados por número de chegadas decrescente, somam até 80% do total
acumulado são **hub**; os demais, **off-hub**. É convenção, não valor
absoluto — outra convenção (ex.: top-N fixo) mudaria a lista. Esta
pergunta é de estrutura de rede (quais bases concentram volume), não de
tempo — pode ser respondida independentemente da pergunta 3.

### 6.2 Colunas usadas (das 29 essenciais, `SPEC-005`)

**Pergunta 3.** `DS_MATRICULA` (chave de sequência por aeronave),
`SG_EQUIPAMENTO_ICAO` (segmentação por modelo), `DT_PARTIDA_REAL`,
`HR_PARTIDA_REAL`, `DT_CHEGADA_REAL`, `HR_CHEGADA_REAL` (cálculo do
intervalo), `SG_ICAO_ORIGEM`/`SG_ICAO_DESTINO` (continuidade de
aeroporto).

**Pergunta 4.** `SG_ICAO_DESTINO` (contagem de chegadas por base),
`SG_IATA_DESTINO` (leitura), `DT_PARTIDA_REAL` (quebra por ano).

### 6.3 Método genérico, passo a passo (independente de engine)

**Pergunta 3 (passos 1-5):**

1. Ordenar as etapas de cada aeronave (`DS_MATRICULA`) por
   `DT_PARTIDA_REAL`, `HR_PARTIDA_REAL`.
2. Para cada etapa, localizar a etapa seguinte da mesma aeronave (próxima
   partida, mesma matrícula).
3. Tempo de solo = (data+hora de partida da etapa seguinte) − (data+hora
   de chegada da etapa atual), **só quando** o aeroporto de destino da
   etapa atual é igual ao aeroporto de origem da etapa seguinte — senão é
   gap de dado ou reposicionamento não capturado, descartado da amostra,
   não forçado.
4. Remover outliers: calcular Q1 e Q3 do tempo de solo (minutos), IQR =
   Q3 − Q1, limite superior = Q3 + 1,5 × IQR. Descartar valores acima do
   limite.
5. Agregar por modelo de equipamento (`SG_EQUIPAMENTO_ICAO`): mediana, Q1,
   Q3 do tempo de solo, sem outliers. **Entrega da pergunta 3.**

**Pergunta 4 (passo 6):**

6. Classificar bases (aeroportos) em hub/off-hub: contar chegadas por
   `SG_ICAO_DESTINO`, ordenar decrescente, calcular % acumulado, hub =
   bases que juntas somam até 80% das chegadas. **Entrega da pergunta 4.**

**Cruzamento das duas (passo 7, aplicação conjunta, não pergunta própria):**

7. Agregar por base × ano: mediana e média do tempo de solo (resultado da
   pergunta 3), comparando hub vs. off-hub (resultado da pergunta 4).

### 6.4 Premissas e incertezas

- Gaps de dado (troca de matrícula não capturada, aeronave que sai/entra
  de operador) geram tempos de solo espúrios — mitigado pelo corte IQR do
  passo 4, não eliminado. (Pergunta 3.)
- Classificação hub/off-hub por Pareto (80%) é convenção adotada nesta
  análise; outra convenção (top-10 fixo, corte em 90%) mudaria a lista de
  hubs — reportar sempre a lista junto com o critério usado. (Pergunta 4.)
- Etapas onde o destino de uma etapa não bate com a origem da seguinte são
  descartadas do cálculo (passo 3) — reduz a amostra, é comportamento
  esperado, não erro de dado. (Pergunta 3.)
- Valor de referência de análise anterior (GOL, janela ~2021-presente):
  limiar de outlier ≈ 212,5 min (3h30) — **valor a recalcular neste
  projeto**, não herdado como constante fixa (fonte de dado e momento de
  extração são diferentes). (Pergunta 3.)

### 6.5 Implementação — caminho SQLite+Python

SQLite não tem função nativa de percentil/mediana
(`PERCENTILE_CONT`/`MEDIAN` inexistem). A sequência de etapa por aeronave
(pergunta 3, passos 1-3) usa window functions nativas do SQLite
(`LEAD()` sobre `PARTITION BY ds_matricula ORDER BY dt_partida_real,
hr_partida_real`, suportado desde SQLite 3.25) — é join relacional puro,
fica em SQL. Os passos 4 (IQR, pergunta 3) e 6 (Pareto, pergunta 4), que
exigem percentil, rodam em **Python** (`pandas.Series.quantile`), lendo o
resultado direto via `pandas.read_sql` — coerente com o nome do próprio
caminho ("SQLite+Python"), sem forçar uma função que o motor não tem
nativamente.

```sql
-- SQLite: sequência de etapas por aeronave e tempo de solo bruto (pergunta 3)
-- (sql/analise/, view ou CTE consumida por src/ em Python)
WITH etapas_ordenadas AS (
  SELECT
    ds_matricula, sg_equipamento_icao,
    dt_partida_real, hr_partida_real, dt_chegada_real, hr_chegada_real,
    sg_icao_origem, sg_icao_destino,
    LEAD(dt_partida_real) OVER (
      PARTITION BY ds_matricula ORDER BY dt_partida_real, hr_partida_real
    ) AS prox_dt_partida,
    LEAD(hr_partida_real) OVER (
      PARTITION BY ds_matricula ORDER BY dt_partida_real, hr_partida_real
    ) AS prox_hr_partida,
    LEAD(sg_icao_origem) OVER (
      PARTITION BY ds_matricula ORDER BY dt_partida_real, hr_partida_real
    ) AS prox_origem
  FROM curated_deep_dive_gol
)
SELECT *,
  (julianday(prox_dt_partida || ' ' || prox_hr_partida) -
   julianday(dt_chegada_real || ' ' || hr_chegada_real)) * 24 * 60
    AS minutos_solo
FROM etapas_ordenadas
WHERE sg_icao_destino = prox_origem;
```

```python
# Python: IQR (pergunta 3, passo 4) + classificação hub/off-hub
# (pergunta 4, passo 6), fora do SQL
df = pd.read_sql(query_acima, conn)

q1, q3 = df["minutos_solo"].quantile([0.25, 0.75])
limite = q3 + 1.5 * (q3 - q1)
df_limpo = df[df["minutos_solo"] <= limite]

chegadas = df["sg_icao_destino"].value_counts()
pareto = (chegadas / chegadas.sum()).cumsum()
hubs = pareto[pareto <= 0.80].index.tolist()
```

### 6.6 Implementação — caminho Snowflake

Snowflake tem `PERCENTILE_CONT`/`MEDIAN` nativos — todos os passos ficam
inteiros em SQL/view, sem etapa em Python, coerente com o caminho ser
Snowflake nativo (view ou dynamic table sobre `curated_deep_dive_gol`).

```sql
-- Snowflake: sequência + tempo de solo + corte IQR (pergunta 3), tudo em SQL
WITH etapas_ordenadas AS (
  SELECT *,
    LEAD(DT_PARTIDA_REAL) OVER (
      PARTITION BY DS_MATRICULA ORDER BY DT_PARTIDA_REAL, HR_PARTIDA_REAL
    ) AS PROX_DT_PARTIDA,
    LEAD(HR_PARTIDA_REAL) OVER (
      PARTITION BY DS_MATRICULA ORDER BY DT_PARTIDA_REAL, HR_PARTIDA_REAL
    ) AS PROX_HR_PARTIDA,
    LEAD(SG_ICAO_ORIGEM) OVER (
      PARTITION BY DS_MATRICULA ORDER BY DT_PARTIDA_REAL, HR_PARTIDA_REAL
    ) AS PROX_ORIGEM
  FROM CURATED_DEEP_DIVE_GOL
),
tempo_solo AS (
  SELECT *,
    DATEDIFF('minute',
      DT_CHEGADA_REAL || ' ' || HR_CHEGADA_REAL,
      PROX_DT_PARTIDA || ' ' || PROX_HR_PARTIDA) AS MINUTOS_SOLO
  FROM etapas_ordenadas
  WHERE SG_ICAO_DESTINO = PROX_ORIGEM
),
limiar AS (
  SELECT
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY MINUTOS_SOLO) AS Q3,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY MINUTOS_SOLO)
      - PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY MINUTOS_SOLO) AS IQR
  FROM tempo_solo
)
SELECT t.*
FROM tempo_solo t, limiar l
WHERE t.MINUTOS_SOLO <= l.Q3 + 1.5 * l.IQR;
```

Classificação hub/off-hub (pergunta 4, passo 6) fica também em SQL, com
soma cumulativa em janela (`SUM(chegadas) OVER (ORDER BY chegadas DESC)`
dividida pelo total), sem sair do motor.

### 6.7 Nota de método (as duas implementações acima são pseudo-SQL ilustrativo)

Os blocos das §6.5/§6.6 servem para fixar a técnica, não são o DDL final
— nomes de coluna, tratamento de nulo e o script definitivo nascem na
implementação (`sql/analise/`), fora do escopo desta SPEC.

## 7. Critérios de sucesso

- **C-01** — `trusted_essencial` criada e validada nos dois caminhos
  (SQLite, Snowflake): as 29 colunas de `SPEC-005` presentes,
  tipos herdados corretamente de `basica_silver`.
- **C-02** — `curated_deep_dive_gol` e `curated_deep_dive_azul` criadas
  nos dois caminhos, contagem de linhas maior que zero para cada, filtro
  de empresa e janela temporal confirmados por amostragem.
- **C-03** — Perguntas 1 (destinos; rota/mercado quando implementada), 2
  (distribuição da frota) e 5 (etapa média) respondidas para GOL e para
  Azul, seguindo a metodologia da §5, registradas em REP futura.
- **C-04** — Perguntas 3 (comportamento do tempo de solo) e 4
  (caracterização das bases hub/off-hub) respondidas **e** implementadas
  nos dois caminhos, seguindo o método do §6 — critério mais forte que
  C-03, por serem as perguntas de referência desta SPEC.
- **C-05** *(provisório, bloqueado)* — Pergunta 6 (block time) respondida,
  condicionada à ingestão do VRA (`SPEC-002 §4.1`).

## 8. Premissas e dependências

- `basica_silver` já existe e está validada no caminho SQLite (112
  colunas, ver `SPEC-008 §6`); caminho Snowflake segue com `basica_typed`
  por ora (divergência registrada, `SPEC-004 §4.1`).
- Cobertura temporal de `basica_raw`/`silver` inclui 2021-01-01 até o
  presente, dentro do corte geral 2010-presente (`DEC-002 §4.3`) —
  premissa a confirmar por contagem simples antes de rodar as `curated`.
- `SG_EMPRESA_ICAO` `'GLO'` e `'AZU'` existem e são estáveis no período —
  não testado.
- Dataset VRA permanece "a implementar" (`SPEC-002 §4.1`); C-05 fica
  bloqueado até isso mudar.
- SQLite usado neste projeto é ≥ 3.25 (suporte a window functions,
  `LEAD`/`LAG`) — não confirmado explicitamente, mas consistente com o
  ambiente já em uso (`README.md`).

## 9. Não-objetivos

- Não é objetivo cobrir todos os concorrentes do mercado — deep dive
  dirigido (GOL, Azul).
- Não é objetivo resolver "block time" com proxy — `DEC-007 §4.4`.
- Não é objetivo unificar as duas `curated` numa view parametrizada —
  `DEC-007 §4.3`.
- Não é objetivo replicar a análise de frequência/Fourier do docx como
  requisito mínimo — fica como extensão de referência (§5.1).
- Não é objetivo medir assimetria de mercado por capacidade (ASK,
  assentos ofertados) nesta versão — decisão do autor de adiar para outro
  momento (§5.1); a métrica fica em frequência de etapas.
- Não é objetivo implementar `curated_block_time_gol`/`azul` nesta
  versão — o desenho (§5.6) fica registrado, a construção espera o VRA
  existir neste projeto.

## 10. Regras checáveis (R-ANL)

| ID | Regra | Onde verificar | Severidade |
|---|---|---|---|
| **R-ANL-01** | `trusted_essencial` contém exatamente as 29 colunas de `SPEC-005`, nos dois caminhos — `NR_ASK`/`NR_ASSENTOS_OFERTADOS` ficam de fora. | `DESCRIBE`/`PRAGMA table_info` vs. lista desta SPEC, nos dois caminhos | Alta |
| **R-ANL-02** | `curated_deep_dive_gol` filtra só `sg_empresa_icao = 'GLO'`; `curated_deep_dive_azul` filtra só `'AZU'`; nenhuma mistura. | `SELECT DISTINCT sg_empresa_icao` em cada view, nos dois caminhos | Crítica |
| **R-ANL-03** | Ambas as `curated` restringem `dt_partida_real >= '2021-01-01'`, sem limite superior fixo. | `MIN(dt_partida_real)` em cada view | Alta |
| **R-ANL-04** | A pergunta 6 (block time) não aparece como "respondida" em nenhuma REP futura antes do VRA existir neste projeto. | Inspeção de REP futura × estado do pipeline VRA | Alta |
| **R-ANL-05** | Cada pergunta respondida (REP futura) segue a estrutura da §5 desta SPEC: conceito, colunas usadas, premissas/incertezas, definição adotada. | Estrutura da REP × §5 desta SPEC | Média |
| **R-ANL-06** | As perguntas 3 e 4 (comportamento do tempo de solo; caracterização das bases hub/off-hub) têm definição equivalente nos dois caminhos — mesmo conceito, mesmo corte IQR, mesma regra de Pareto; a divergência entre caminhos fica só na técnica (SQL puro vs. SQL+Python), nunca na definição. | Comparação §6.5 × §6.6 × implementação real | Alta |

## 11. Limitações conhecidas

- **Divergência numérica esperada entre caminhos**: mesmo com definição
  idêntica, `pandas.quantile` (SQLite+Python) e `PERCENTILE_CONT`
  (Snowflake) podem calcular o percentil por métodos ligeiramente
  diferentes (interpolação) — pequena diferença numérica não é erro, é
  fricção esperada de dois motores; grande diferença é sinal de bug.
- Pesos/definições de "destino", "distribuição da frota" e "etapa média"
  carregam ambiguidade conceitual reconhecida desde a formulação original
  das perguntas — esta SPEC herda, não resolve a ambiguidade, só fixa onde
  e como calcular.
- `NR_HORAS_VOADAS` é airborne time, não block time real — afeta a
  pergunta 5 (duração e velocidade inferida).
- `DS_MATRICULA` tem ~12% de nulos na base histórica completa
  (`SPEC-005`, linha 25); não testado se esse percentual se
  mantém no recorte 2021-presente para GOL/Azul.
- A velocidade média inferida (§5.5) tem duas formas de agregação não
  coincidentes (razão das somas vs. média das razões); a escolha de qual
  reportar como principal é recomendação desta SPEC, não valor fechado.
- A análise de rota/mercado (§5.1) ainda não foi implementada — o método
  descrito é rascunho, não validado contra dado real.
- "Fluxo" na pergunta de rota/mercado mede frequência de etapas, não
  capacidade — decisão deliberada do autor (2026-08-31), adiada para outro
  momento, não lacuna não examinada.
- **Chave de junção Básica × VRA (§5.6) é hipótese, não achado** — empresa
  + voo + data + origem é a leitura mais provável dada a estrutura pública
  conhecida do VRA, mas só se confirma inspecionando o dicionário real do
  dataset, ainda não baixado neste projeto.
- **Assimetria de custo entre caminhos é maior na pergunta 6 do que nas
  demais**: SQLite paga `ATTACH`/materialização (§5.6), Snowflake não paga
  custo de sintaxe extra (cross-schema nativo) — mais desigual que a
  assimetria de percentil das perguntas 3/4 (R-ANL-06).

## 12. Critérios de revisão

Revisitar esta SPEC quando:

- VRA ganhar ingestão completa — desbloqueia C-05/pergunta 6 e aciona a
  construção de `curated_block_time_gol`/`azul` (§5.6); confirmar a chave
  de junção contra o dicionário real do VRA nesse momento.
- A implementação real das perguntas 3 e 4 (§6) revelar divergência de
  definição (não só de técnica) entre os dois caminhos — violaria
  R-ANL-06.
- Mais de uma pergunta cross-dataset aparecer (ex.: quando SIROS entrar) —
  revisitar junto com `DEC-004 §6`; sinal para considerar um padrão de
  junção único, não um objeto dedicado por pergunta.
- Contagem de linhas de `curated_deep_dive_gol` ou `azul` vier zero ou
  anômala — revisar antes de aprovar C-02.
- Um terceiro concorrente entrar em escopo — revisitar `DEC-007 §4.3`.
- O autor decidir retomar a análise de assimetria por capacidade (ASK,
  assentos ofertados) — hoje deliberadamente adiada (§5.1).

## 13. Histórico

| Data | Evento |
|---|---|
| 2026-08-30 | SPEC-004 v1 produzida em status `proposto`, escopo Snowflake-only. Materializa a DEC-007 original: camada `TRUSTED_ESSENCIAL` + `CURATED_DEEP_DIVE_GOL`/`AZUL`, metodologia herdada de `rascunho/SPEC-010`, pergunta D bloqueada até VRA. |
| 2026-08-30 | Pendência do ASK resolvida: etapa média só na versão simples (`AVG(KM_DISTANCIA)`); `NR_ASK`/`NR_ASSENTOS_OFERTADOS` fora de escopo. |
| 2026-08-31 | Revisão maior a pedido do autor: perguntas reformuladas de forma genérica e agnóstica de engine, escopo estendido para os dois caminhos de produção, pergunta "tempo de solo (hub/off-hub)" detalhada por completo (§6) como exemplo de referência, com implementação SQLite+Python e Snowflake. Seis regras `R-ANL-NN`. |
| 2026-08-31 | Correção do autor: "tempo médio no ar" não substitui "etapa média", as duas se fundem sob "Etapa média" (§5.5) — duração como métrica principal, distância como complementar (só versão simples), velocidade média inferida como terceira métrica, duas formas de agregação reportadas lado a lado. |
| 2026-08-31 | Revisão de escopo a pedido do autor: pergunta "tempo de solo (hub/off-hub)" separada em duas (comportamento do tempo de solo; caracterização das bases hub/off-hub), cada uma com conceito e critério de sucesso próprios, implementação compartilhada (§6); pergunta "destinos" ganhou extensão em andamento de rota e mercado (§5.1), com definição de rota (par ordenado, nível aeroporto) e mercado (par não ordenado, nível aeroporto/mercado), método de assimetria direcional. Seis perguntas agora. |
| 2026-08-31 | Duas decisões do autor fecham pontos em aberto da §5.1: mercado definido por **par de aeroportos** (não por município); assimetria medida por **frequência de etapas**, capacidade (ASK/assentos ofertados) deliberadamente adiada para outro momento. §5.1, §9, §11, §12 atualizados. |
| 2026-08-31 | Debate sobre engenharia de dado com três bancos separados (Básica, VRA, SIROS): registrado o desenho de `curated_block_time_gol`/`azul` (§5.6) — objeto dedicado, materialização única por caminho, chave de junção hipotética (empresa+voo+data+origem). §9, §11, §12 atualizados. |
| 2026-08-31 | **Aprovada.** Treze seções presentes, cada `C-NN` com artefato/método de verificação, seis regras `R-ANL-NN` com id/enunciado/onde-verificar/severidade, `referencia: DEC-007` coerente com R-TAX-06. Autor revisou o resumo (quadro "Aprovações ANAC") e aprovou explicitamente. |
| 2026-08-31 | **v2 — correção pós-aprovação, decisão inalterada.** A pedido do autor, `rascunho/SPEC-010-ANAC-Perguntas_Analise-Deep_Dive-Gol.md` e `rascunho/Deep_Dive_Gol_ANAC_1a_.docx` foram excluídos do repositório; toda citação a eles foi removida ou reescrita em prosa autocontida. Citações a `rascunho/colunas.txt` substituídas por `SPEC-005` (Dicionário de Colunas — Básica), que o formaliza. `referencia:` do frontmatter passa a `DEC-007, SPEC-005`. Nenhuma definição de pergunta, método ou critério de sucesso muda. |
| 2026-08-31 | **v3 — correção pós-aprovação, decisão inalterada.** `basica_typed` retirada; `basica_silver` (112 colunas, `SPEC-008 v3`) assume seu papel na cadeia de camadas (§4.1) e como base de `trusted_essencial` (C-01, §8). Caminho Snowflake segue com `basica_typed` por ora, divergência registrada. Nenhum critério de sucesso ou definição de pergunta muda. |
| 2026-09-01 | **v4 — correção pós-aprovação, decisão inalterada (`R-TAX-11`).** Pergunta 6 (Block time, §5.6) desbloqueada: VRA ingerido (`SPEC-012`), bloqueio original superado. Objeto renomeado de `curated_block_time_gol`/`curated_block_time_azul` (dois objetos) para `fato_block_time_gol_azul` (objeto único), alinhando com o padrão que `curated_deep`/`fato_rotacao_aeronave_gol_azul` já fixaram desde então — pedido do autor. Chave de junção refinada de hipótese pura para achado real (hora adicionada à chave elimina quase toda duplicidade, medido em amostra 2025 GOL/Azul) — ainda não medida contra o par atual de tabelas. §5.6 atualizado. Mesma correção espelhada em `DEC-007 v4`. |
| 2026-09-07 | **Precisão do registro de exclusão, decisão inalterada.** A entrada de 2026-08-31 acima diz que `Deep_Dive_Gol_ANAC_1a_.docx` e `SPEC-010-ANAC-Perguntas_Analise-Deep_Dive-Gol.md` foram "excluídos do repositório". Verificado em 2026-09-07: a afirmação vale para a árvore de trabalho e para o `HEAD`, e não para o histórico publicado. Os dois foram adicionados no commit `607cb8a` e removidos em `a74fff3`, ambos de 2026-08-31, e `607cb8a` é alcançável a partir de `origin/main`. Como o repositório é público, os dois blobs (`9f32b1de` e `a80d8e41`) seguem acessíveis a quem tiver o hash do commit. O autor optou por manter o histórico como está, apoiado na classificação já registrada no próprio rascunho (dado 100% público/regulatório, sem informação confidencial). Registrado aqui para que "excluído" não seja lido como "inacessível". |

---

*Fim do documento.*
