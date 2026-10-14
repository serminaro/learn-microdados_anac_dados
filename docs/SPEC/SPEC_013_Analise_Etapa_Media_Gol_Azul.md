---
documento: SPEC-013
titulo: Análise Exploratória — Etapa Média GOL/Azul
versao: v15
status: proposto
data: 2026-10-14
autor: Bruno Alexandre Serminaro
referencia: DEC-007, SPEC-017
escopo: projeto
---

# SPEC-013 · Análise Exploratória — Etapa Média GOL/Azul

> Documento **vivo**: registra método, código e achados da análise
> exploratória de etapa média (duração), detalhando a pergunta 5 do
> `SPEC-004 §5.5` — GOL primeiro (rodadas 1-8, só GOL por pedido
> explícito do autor), Azul e comparação GOL x Azul depois (v9). Cresce
> por rodada — cada rodada nova vira entrada no Histórico (§13) e
> atualização das seções de achados, não documento novo. Diferente das
> SPECs anteriores deste projeto (retroativas, escritas depois do
> trabalho validado), esta acompanha o trabalho enquanto ele acontece —
> exceto a v9, produzida retroativamente (achado de auditoria
> documental, 2026-09-03, ver Histórico).

---

## 1. Propósito

Explorar a duração média de etapa (`NR_HORAS_VOADAS`) da GOL e da Azul e
suas relações com frota, bases (origem/destino) e tempo, partindo da
janela temporal mais larga disponível e fechando progressivamente até
2026 — método de trabalho pedido pelo autor (2026-09-01), não um recorte
fixo definido de antemão. GOL explorada primeiro (rodadas 1-8), Azul e
comparação GOL x Azul depois (v9, §6.8-§6.9).

## 2. Audiência

Reaproveita os papéis abstratos do `SPEC-002 §2` — nenhum papel novo.

## 3. Escopo

### 3.1 Regra padrão desta linha de análise

**Só etapas `PASSAGEIRO`, exclui `CARGUEIRO`, salvo instrução explícita em
contrário** — regra fixada pelo autor (2026-09-01) para toda esta linha
de análise GOL, não só para esta rodada. Aplicada em `basica_curated_deep`
via `WHERE ds_servico_tipo_linha = 'PASSAGEIRO'`.

### 3.2 O que este SPEC entrega

1. Script reprodutível (`analise/a4_etapa_media/analise_etapa_media_gol.py`)
   que gera as figuras de cada rodada.
2. Figuras em `analise/a4_etapa_media/a4_figuras_gol/` (não versionadas em `sql/`, ficam
   fora da árvore de camadas de dado porque são artefato de análise, não
   de ingestão/tratamento).
3. Achados de cada rodada, registrados em §6 conforme a janela investigada.
4. *(v4, revisto em v13)* Pareto de bases HUB/OFF-HUB (80% acumulado),
   confrontado contra `analise/a4_etapa_media/pareto_bases_gol_autor_2026-08-31.csv`
   fornecido pelo autor (§6.5). O cálculo hoje mora na view
   `pareto_bases_gol_azul` (`sql/curated_deep/DDL_006`), não mais no
   script `gerar_pareto_bases_gol.py`, removido em v13.
5. *(v6)* Janelas fechando (2022→2026, 2023→2026, 2024→2026, 2025→2026,
   além das duas pontas já existentes) e dois cruzamentos novos
   (duração mensal por frota, duração mensal por base HUB) — §6.6, §6.7.
6. *(v9)* Replicação completa para a Azul (mesmos scripts, espelho
   exato) — `analise_etapa_media_azul.py`,
   `distribuicao_etapa_media_azul.py` → `a4_figuras_azul/` (§6.8).
7. *(v9)* Comparação GOL x Azul — `versus_gol_azul.py` → 21 gráficos
   (`v01`-`v12` + `novo_01`-`novo_09`) → `a4_figuras_versus/` (§6.9).
8. *(v9)* Notebook didático `analise_etapa_media_gol.ipynb` — refaz a
   análise GOL passo a passo para ensinar pandas/numpy/matplotlib/
   seaborn; não produz achado novo de negócio, registrado aqui só como
   entrega (§3.4).

### 3.3 Fora de escopo (nesta rodada)

- Mediana/quartis — `SPEC-004 §5.5` prevê como complemento "se a
  distribuição for assimétrica"; não avaliado ainda nesta rodada, fica
  para próxima se a média mostrar sinal de cauda longa.
- Cálculo de velocidade inferida (`KM_DISTANCIA/NR_HORAS_VOADAS`) — já
  coberto por `sql/analise/QUERY_001` equivalente no nível empresa×
  natureza; não replicado aqui em nível de figura nesta rodada.
- Relação frota×base (que frota opera de qual base) — mencionada como
  direção de exploração pelo autor, não construída ainda.

### 3.4 *(v9)* Notebook didático — objetivo diferente do script de produção

`analise_etapa_media_gol.ipynb` refaz `analise_etapa_media_gol.py` passo
a passo, mas com propósito distinto: **ensinar** pandas/numpy/matplotlib/
seaborn através desta análise real, não produzir achado novo (o
notebook herda e explica o que o script de produção já mediu) —
registrado aqui só como inventário de entrega, sem critério de sucesso
próprio nem achado em §6.

## 4. Fonte e método

```
basica_curated_deep (SPEC-012, db/anac_basica.sqlite)
  → filtro sg_empresa_icao='GLO' AND ds_servico_tipo_linha='PASSAGEIRO'
  → janela de dt_partida_real (varia por rodada, §6)
  → analise/a4_etapa_media/analise_etapa_media_gol.py (pandas + matplotlib)
  → analise/a4_etapa_media/a4_figuras_gol/*.png
```

**Estética dos gráficos** (ajustada 2026-09-01, pedido do autor): casada
com o documento de referência escrito à mão pelo autor para este mesmo
deep dive (fundo branco, grid leve, títulos em negrito, paleta `Set2`),
que vive no projeto paralelo `learn-imrad-mintos` e não neste
repositório, e não com a paleta padrão da skill `dataviz` deste
ambiente — divergência
deliberada, registrada aqui para não parecer inconsistência. Fundo
branco, grid leve nos dois eixos, títulos em negrito (2 linhas, subtítulo
entre parênteses), rótulos numéricos diretos em negrito sobre
barras/pontos, legenda com moldura. Regras não-negociáveis da skill que
seguem valendo mesmo com a paleta trocada: hues categóricas em ordem
fixa (nunca trocadas entre gráficos), hue sequencial mapeando uma segunda
magnitude (duração) sobre barras de contagem (`top_bases_origem`), sem
eixo duplo em nenhum gráfico, série única sempre na mesma cor (sem
"arco-íris" por categoria quando não há múltiplas séries reais).

**Paleta** (v3, 2026-09-01): laranja da marca GOL, pedido explícito do
autor — troca a paleta `Set2` (verde-menta/coral) da v2 pelo laranja da
companhia. `#FF6900` (série única / doméstica), `#B34700` (tom mais
escuro, internacional), rampa sequencial laranja claro→escuro
(`top_bases_origem`), linha de média em cinza neutro (`#4d4d4d`, contraste
contra o laranja, não mais uma cor da paleta anterior). **Hex
aproximado** — sem manual de marca oficial disponível neste ambiente;
ajustar `GOL_ORANGE`/`GOL_ORANGE_DARK` no script se o autor tiver o valor
exato do manual de marca.

Ambiente: `conda run -n gov-sermi-perf python analise/a4_etapa_media/analise_etapa_media_gol.py`
(mesma premissa de ambiente do `SPEC-002 §6`).

## 5. Janelas investigadas até agora

| Rodada | Janela | Etapas (GOL, passageiro) |
|---|---|---|
| 1 | 2021-01-01 a 2026-07-31 (full) | 1.156.949 |
| 1 | 2026-01-01 a 2026-07-31 | 144.936 |
| 6 | 2022-01-01 a 2026-07-31 | 1.022.317 |
| 6 | 2023-01-01 a 2026-07-31 | 819.295 |
| 6 | 2024-01-01 a 2026-07-31 | 595.536 |
| 6 | 2025-01-01 a 2026-07-31 | 383.374 |

`2026-07-31` como teto, não `2026-08` — mesma razão já documentada em
`SPEC-012 §6.3`: agosto/2026 é mês fragmentário na fonte (7 linhas em
todo o `basica_curated_deep`, não específico da GOL).

## 6. Achados — Rodada 1 (2026-09-01)

### 6.1 Duração média mensal — sazonalidade recorrente, amplitude crescente

`duracao_media_mensal_full_2021_2026.png`. Padrão que se repete ano a
ano: pico em torno de janeiro/fim de ano, vale em torno de
abril-junho — visível nas 5 janelas anuais completas da série. A
amplitude do pico cresce ao longo do tempo: janeiro/2021 ~2,07h,
janeiro/2025 ~2,15h (o maior pico da série). 2021 tem dois vales bem mais
profundos que os anos seguintes (~1,89h, fev. e jul./2021) — hipótese não
testada: efeito de malha internacional reduzida no início da retomada
pós-pandemia (menos rotas longas puxando a média pra cima). Não
confirmado, fica como hipótese candidata para próxima rodada.

`duracao_media_mensal_2026.png` (recorte 2026): mesmo formato do padrão
recorrente — janeiro/fevereiro altos (2,12h/2,10h), vale em maio
(1,95h), subindo de novo até julho (2,09h). Consistente com o padrão
histórico, não é uma quebra de tendência.

### 6.2 Duração por modelo de frota — ordenação estável, gap dom.×intl. constante

`duracao_media_por_frota_full_2021_2026.png` e `..._2026.png`. Três
modelos com volume suficiente (corte ≥30 etapas): `B38M` (737 MAX 8) >
`B738` (737-800) > `B737` (737-700), tanto doméstica quanto
internacional, nas duas janelas. Razão internacional/doméstica é
consistente entre modelos (~2,0-2,1×) e entre janelas — não é um modelo
específico distorcendo a leitura.

**Achado (2026)**: `B737` não aparece com barra internacional em 2026 —
confirmado que não é artefato do corte de 30 etapas: só **4** etapas
internacionais de `B737` em 2026 inteiro, contra 830 no período
2021-2026 completo. Consistente com saída gradual do `B737` do
internacional GOL — hipótese candidata (não confirmada: pode ser
realocação de frota, não decisão de rede), fica para investigar se
relevante à pergunta.

### 6.3 Bases HUB de origem (80% acumulado) — CGH/GRU concentram volume, nordeste puxa duração

*(v5)* Critério trocado de corte fixo (top-15) para 80% acumulado
(`selecionar_hub`, mesma regra de §6.5 e da view `pareto_bases_gol_azul`) —
pedido do autor, 2026-09-01. Deixa de ser um número fixo de bases: 16 na
janela completa (`MCZ` entra, mesma composição do pareto §6.5), 17 em
2026 isolado (`NAT` entra, não aparecia no corte fixo de 15 antes).

`top_bases_origem_full_2021_2026.png`, cor = duração média. `CGH`
(Congonhas) e `GRU` (Guarulhos) dominam em volume de etapas (~175 mil e
~173 mil no período), muito à frente da 3ª colocada (`BSB`, Brasília,
~107 mil). Cor revela outro eixo: as bases mais escuras (maior duração
média) não são as de maior volume — `FOR` (Fortaleza) e `REC` (Recife)
saltam com duração média >2,75h apesar de volume bem menor (~28-30 mil
etapas), plausivelmente por concentrar rotas mais longas
(internacional/interregional) proporcionalmente à sua operação.

### 6.4 Bases HUB com mais chegadas (80% acumulado) — mesmo ranking de origem, sem surpresa

`top_bases_chegadas_full_2021_2026.png`. Ranking praticamente idêntico
ao de origem (§6.3), esperado numa malha onde a maioria das etapas tem
ida e volta pela mesma base — não é achado novo, é confirmação de
consistência interna do dado (uma aeronave que chega numa base tende a
também partir dela, condizente com a taxa de continuidade de 99,86% já
medida em `SPEC-012 §6.4`).

### 6.5 Pareto de bases (HUB/OFF-HUB) — confronto contra o CSV do autor, achado de staleness

O autor forneceu `pareto_bases_gol_autor_2026-08-31.csv` (classificação HUB/OFF-HUB
por acúmulo de 80% das chegadas, mesma família de método de
`SPEC-004 §6`) para conferência contra as bases escolhidas nesta SPEC.
Repliquei a metodologia exata (ranking por chegadas, % acumulado, HUB
enquanto o acumulado **antes** da base é `< 80%`) contra
`basica_curated_deep` atual. O cálculo desta rodada saiu de um script
descartável (`gerar_pareto_bases_gol.py`, removido em v7); os números
abaixo são os que ele produziu, sobre o histórico inteiro.

**O que bate**: 14 das 15 bases HUB do CSV do autor aparecem no
resultado atual; a ordem das posições 3-12 é idêntica nos dois.

**O que diverge**:

| Ponto | CSV do autor (2026-08-31) | Esta rodada (v4, histórico inteiro) |
|---|---|---|
| #1/#2 | `GRU` > `CGH` | `CGH` > `GRU` |
| `VIX` | OFF-HUB (rank 16, 80,85% acum.) | **HUB** (rank 14, 77,98% acum.) |
| `MCZ` | HUB, rank 13 | HUB, rank 16 (81,00% acum., quase fora) |
| Total de chegadas (denominador) | ≈ 959 mil (implícito) | 1.156.956 |
| Nº de bases HUB | 15 | **16** |

Magnitude por base diverge de forma não uniforme (70%-88% do valor atual,
dependendo da base) — descarta janela mais curta aplicada uniformemente
como única causa.

**Hipótese testada e descartada**: o CSV do autor não é o recorte 2025
isolado do documento de referência escrito à mão, que trabalhava sobre
uma tabela Snowflake e não sobre este banco. GOL 2025 passageiro aqui dá
exatamente 238.438 etapas, número que bate com o citado naquele
documento, mas as magnitudes do CSV do autor são cerca de 4x maiores.
Descartado.

**Hipótese mais provável (não confirmada por rastro documental direto,
só por coincidência temporal forte)**: o CSV do autor
tem data de modificação `2026-08-31 08:38` — **anterior** à correção do
`SPEC-008 v4` (bug de corte hardcoded que travava `basica_raw` em
2026-06, antes de `2026-07` ser incluído) e anterior à `basica_curated_deep`
existir. Provável snapshot de um estágio anterior do pipeline, não uma
escolha metodológica divergente.

**Resolvido em v5**: `top_bases_origem`/`top_bases_chegadas` (§6.3, §6.4)
trocaram do corte fixo top-15 para o critério de 80% acumulado, pedido
do autor — mesma função `selecionar_hub` usada em ambas as figuras,
consistente com a regra da view `pareto_bases_gol_azul`.

### 6.6 Janelas fechando (2021→2026, 2022→2026, ..., 2025→2026) — sazonalidade se confirma em qualquer corte

*(v6)* `duracao_media_mensal_{2022,2023,2024,2025}_2026.png` — mesma
figura de §6.1, piso do eixo temporal subindo ano a ano, teto fixo em
2026-07-31. Sazonalidade (pico jan./fim de ano, vale abr.-jun.) se
mantém visível em toda janela, inclusive nas mais curtas (2025_2026, só
19 meses) — não é artefato de olhar 5+ anos de uma vez, é um padrão que
sobrevive ao corte.

### 6.7 Cruzamentos tempo×frota e tempo×base — achados novos de nível

*(v6)* `duracao_media_mensal_por_frota_full_2021_2026.png`: as três
linhas (`B38M`, `B738`, `B737`) nunca se cruzam em todo o período —
ordenação de nível é estável mês a mês, não só na média agregada (§6.2).
`B737` tem a trajetória mais ruidosa e a única com viés de queda visível
ao longo do tempo (de ~1,9h em 2021 para ~1,3-1,5h em 2026) — consistente
com o achado de saída do B737 do internacional (§6.2), mas agora visível
também dentro da doméstica.

`duracao_media_mensal_por_base_full_2021_2026.png` (top 6 HUB por
volume, rótulo direto no fim de cada linha — ver nota de legibilidade
abaixo): dois achados de nível, não visíveis nos agregados de §6.3/§6.4:

- **`GIG` (Galeão) tem um platô isolado em 2022-meados de 2023**
  (~2,6-2,7h, bem acima do seu próprio nível antes/depois, ~2,1-2,3h) —
  não presente em nenhuma outra base do top 6. Hipótese candidata, não
  investigada: mudança temporária de malha internacional operada a
  partir do Galeão nesse período.
- **`SDU` (Santos Dumont) tem uma quebra de nível abrupta no fim de
  2023** (de ~1,4-1,5h para ~1,2-1,3h, queda de ~15-20%, permanente até
  o fim da série) — não gradual, muda de patamar num só mês. Hipótese
  candidata: mudança de mix de rotas na ponte aérea/shuttle que opera
  dali, não investigada.

**Nota de legibilidade (achado de processo, não de dado)**: a primeira
versão do gráfico por base usava só legenda — com 6 séries na mesma
família de laranja (paleta GOL, §4), as linhas de nível médio
(`GRU`/`BSB`/`SDU`/`SSA`, todas entre 2,0-2,2h) ficavam praticamente
indistinguíveis só pela cor. Duas correções: (1) rótulo direto no fim de
cada linha; (2) pedido do autor (2026-09-01) — regra nova fixada em
`analise_etapa_media_gol.py`: gráfico de linha com **mais de 3 séries**
troca do laranja monocromático (`SEQ_ORANGE_CMAP`) para a paleta
categórica validada da skill `dataviz` (`PALETA_CATEGORICA`, 8 cores em
ordem fixa) — laranja GOL segue valendo para série única e para
comparações de até 3 séries (frota, §6.7), onde já era legível.

### 6.8 *(v9)* Replicação Azul — mesmo método, achados equivalentes

`analise_etapa_media_azul.py`/`distribuicao_etapa_media_azul.py`,
espelho exato dos scripts GOL (mesmas janelas, mesmo filtro PASSAGEIRO):

| | GOL | Azul |
|---|---|---|
| Etapas (full 2021-2026, passageiro) | 1.156.949 | 1.541.677 |
| Cerca de Tukey (superior) | 4,43h | 3,49h |
| % de etapas fora da cerca | 1,45% | 3,70% |
| Autocorrelação diária (lag-1), série **sem corte** | r = 0,429 | r = 0,731 |

> **Nota de leitura (v10, ver `SPEC-017`).** `r` mede **memória** (fração da
> variação diária que persiste), não estabilidade, e é normalizado pela
> variância — `σ` da série diária não foi medido nesta rodada. Em meia-vida
> de distúrbio: 0,8 dia na GOL contra 2,2 dias na Azul. Três fatores de
> confusão mecânicos (tamanho de amostra diário, mix de frota, sazonalidade
> semanal) precisam ser descartados antes de leitura operacional; `SPEC-017`
> especifica o teste de cada um.

> **Nota de procedência (v11, ver `SPEC-017 §6.3` requisito 4).** A cerca de
> Tukey da linha acima **não** é aplicada a este cálculo. A série diária de
> `nr_horas_voadas` é construída direto do `load_data()` (`dist_13`/`dist_14`
> de `distribuicao_etapa_media_gol.py`/`_azul.py`, e `v09`/`v12` de
> `versus_gol_azul.py`), sem truncagem: aqui o corte de Tukey só entra nos
> gráficos que o declaram no título. Isso difere de tempo de solo, onde a
> série diária de `SPEC-016 §6.2` já chega truncada pela cerca de cada
> companhia. Consequência: `r = 0,429` daqui e `r = 0,613` de `SPEC-016` são
> de regimes de limpeza diferentes. A ordenação entre companhias é a mesma
> nas duas linhas, e é isso que sustenta a leitura de propriedade consistente
> das séries; a diferença de magnitude entre as duas linhas, porém, não é
> atribuível só ao indicador, porque o corte também mudou. Qualquer cálculo
> por base (rodada 2 de `SPEC-017`) deve declarar o corte e usar o mesmo em
> todas as unidades comparadas.
| Top bases (80% acumulado) | `CGH, GRU, BSB...` (§6.3) | `VCP, CNF, REC, SDU, CGH...` |

Ranking de bases da Azul difere do de GOL — esperado, reflete a malha
própria de cada companhia (Campinas/Viracopos como base dominante da
Azul, não Congonhas/Guarulhos). Nenhuma inversão de achado qualitativo
frente ao padrão já visto na GOL (sazonalidade, ordenação de frota) foi
registrada nesta rodada — replicação confirmatória, não contraditória.

### 6.9 *(v9)* GOL x Azul — 21 gráficos de comparação (`versus_gol_azul.py`)

`versus_gol_azul.py` importa os 4 scripts (GOL+Azul) como módulos, sem
reimplementar a query — mesmo eixo/escala compartilhados quando a
pergunta é "quem é maior" ou "onde a densidade é mais forte", densidade
em vez de contagem bruta (Azul tem ~1,54M etapas contra ~1,16M da GOL).

Primeira rodada selecionou 12 gráficos (`v01`-`v12`) dos mais de 25 já
gerados nos scripts fonte. Auditoria posterior (pedido do autor,
2026-09-02) encontrou **9 tipos que faltavam** — alguns avisados na hora
da primeira seleção, outros omissão real, não percebida até a auditoria.
Adicionados com prefixo `novo_` (não renumerados dentro de `v01`-`v12`,
para não confundir referência já em uso):

| Prefixo | Conteúdo | Nota |
|---|---|---|
| `novo_01` | Dispersão etapa média × tempo de solo, por matrícula | — |
| `novo_02` | Dispersão etapa média × distância, por modelo | — |
| `novo_03` | Hexbin por hub individual | Escopo reduzido de 10 para 5 hubs por empresa — decisão explícita, não omissão |
| `novo_04` | Grade hexbin top 6, GOL empilhado sobre Azul | Um layout só (não os dois possíveis) — decisão explícita |
| `novo_05` | Decomposição real × contrafactual, mix de frota | — |
| `novo_06` | Duração média mensal por modelo, valor absoluto | Não é o mesmo que `v10` (esse é % de participação) |
| `novo_07` | Duração média mensal por base HUB | Legenda em caixa, não rótulo direto na ponta da linha — lição já aprendida em `a3_tempo_de_solo` (`SPEC-016 §6.5`) |
| `novo_08` | Top bases HUB por nº de chegadas | — |
| `novo_09` | Violin único com média/mediana/Q1/Q3 | — |

**Achado de processo**: a auditoria "quais gráficos faltaram" (pedido
explícito do autor, não espontânea) revelou que a primeira seleção de 12
gráficos tinha lacunas reais, não só cortes deliberados — checagem de
completude contra o inventário de gráficos já gerados nos scripts fonte
é prática a repetir nas próximas linhas de análise antes de declarar um
`versus_gol_azul.py` "completo".

## 7. Critérios de sucesso (desta rodada)

- **C-01** — Script roda sem erro, gera as 8 figuras esperadas (4 tipos ×
  2 janelas). **Cumprido**: `analise/a4_etapa_media/a4_figuras_gol/` com 8 arquivos
  `.png`, script confirmado idempotente (sobrescreve, não acumula lixo).
- **C-02** — Cada figura inspecionada visualmente antes de reportar
  achado (não só gerada) — prática da skill `dataviz`, passo 7.
  **Cumprido** para as 6 figuras centrais a este relato (mensal ×2,
  frota ×2, bases origem/chegadas full).

## 8. Premissas e dependências

- Depende de `basica_curated_deep` (`SPEC-012`) já carregada e correta —
  esta SPEC não revalida o tratamento dela, só herda.
- Ambiente `gov-sermi-perf` (conda, `DEC-011 §2.2`) com `pandas`/`matplotlib` disponíveis
  — confirmado nesta rodada (`pandas 2.3.3`, `matplotlib 3.11.0`).
- `NR_HORAS_VOADAS` é tempo no ar (airborne), não tempo de bloco
  porta-a-porta — mesma ressalva já registrada em `SPEC-004 §5.5` e
  `SPEC-011`/`SPEC-012` para colunas de horário.

## 9. Não-objetivos (desta rodada)

- Não é objetivo confirmar as hipóteses candidatas do §6.1/§6.2 (efeito
  pós-pandemia, saída do B737 do internacional) — ficam registradas como
  direção de investigação, não resolvidas aqui.
- Não é objetivo cobrir mediana/quartis, velocidade inferida em figura,
  ou relação frota×base nesta rodada (§3.3) — Azul **entrou** no escopo
  na v9 (§6.8, §6.9), não é mais não-objetivo.

## 10. Próximos passos (direção pedida pelo autor)

- Fechar a janela mais (ex.: trimestre a trimestre de 2026) e comparar
  contra o mesmo trimestre de anos anteriores — a sazonalidade do §6.1
  sugere que isso é mais informativo que olhar 2026 isolado.
- Relação frota × base: qual frota opera de qual base, para entender se
  o gap de duração das bases do nordeste (§6.3) é efeito de frota ou de
  rede.
- Testar a hipótese pós-pandemia de 2021 (§6.1) contra proporção de
  etapas internacionais por mês naquele ano.
- Avaliar necessidade de mediana/IQR se algum recorte futuro mostrar
  distribuição visivelmente assimétrica (não visto ainda nas médias
  agregadas desta rodada).

## 11. Limitações conhecidas

- Corte de `≥30 etapas` no gráfico de frota pode ocultar modelo raro
  relevante — sempre checar contagem real antes de interpretar ausência
  como "não existe" (feito manualmente para `B737`/2026 nesta rodada,
  §6.2, mas não é automático no script).
- Hipóteses candidatas do §6.1/§6.2 não têm teste estatístico nem
  investigação de causa — são leitura sobre o padrão visual, não achado
  confirmado.
- `top_bases_chegadas` e `top_bases_origem` medem contagem de etapas, não
  de passageiros/ASK — um ranking por volume de tráfego real (não
  frequência de etapa) pode diferir se o mix de aeronave variar muito
  entre bases.

## 12. Critérios de revisão

Revisitar esta SPEC (nova entrada no Histórico, não novo documento)
quando:

- Uma nova rodada de janela/recorte for pedida pelo autor.
- Alguma hipótese candidata do §6 for testada e confirmada ou refutada.

## 13. Histórico

| Data | Evento |
|---|---|
| 2026-09-01 | SPEC-013 v1 produzida em status `proposto`, documento vivo. Rodada 1: script `analise_etapa_media_gol.py` criado, 8 figuras geradas (mensal, frota, bases origem/chegadas × janela full 2021-2026 e 2026), achados registrados em §6 — sazonalidade recorrente de amplitude crescente, ordenação estável de frota com gap dom./intl. constante (~2×), achado de `B737` quase saindo do internacional em 2026 (4 etapas vs 830 no período completo), concentração SBSP/SBGR com nordeste (SBFZ/SBRF) puxando duração média sem puxar volume. |
| 2026-09-01 | **v2 — ajustes de infraestrutura pedidos pelo autor.** Pasta de figuras movida de `analise/a4_figuras_gol/` para `analise/a4_etapa_media/a4_figuras_gol/` (dentro da pasta da pergunta, não solta na raiz de `analise/`). Estética dos gráficos trocada para casar com `rascunho/Deep_Dive_Gol_ANAC_1a_.docx`: fundo branco, grid leve, títulos em negrito 2 linhas, paleta `Set2` (verde-menta/coral), rótulos diretos em negrito, legenda com moldura — diverge deliberadamente da paleta padrão da skill `dataviz`, registrado em §4. 8 figuras regeradas. §3.2, §4, §7 atualizados. |
| 2026-09-01 | **v3 — paleta trocada para laranja GOL, pedido do autor.** `Set2` (verde-menta/coral) da v2 substituída por laranja da marca (`#FF6900`/`#B34700`, aproximado — sem manual de marca oficial disponível, ajustar se o autor tiver o hex exato), rampa sequencial de `top_bases_origem` também para laranja, linha de média recolorida para cinza neutro (contraste). 8 figuras regeradas. §4 atualizado. |
| 2026-09-01 | **v4 — pareto de bases atualizado, confrontado contra o CSV do autor.** `rascunho/pareto_bases_gol.csv` conferido metodologicamente contra `basica_curated_deep` atual (script novo, `gerar_pareto_bases_gol.py`). 14/15 bases HUB batem, ordem central (rank 3-12) idêntica; divergências reais: `SBSP`/`SBGR` trocados na 1ª/2ª posição, `SBVT` HUB no dado atual vs OFF-HUB no CSV do autor, `SBMO` cai de rank 13 para 16, total de chegadas 1.156.956 vs ≈959 mil implícito no CSV do autor. Hipótese de recorte 2025 isolado testada e descartada (238.438 etapas bate com o docx de referência, mas não com a magnitude do CSV). Explicação mais provável: CSV do autor é anterior à correção do `SPEC-008 v4` e à existência de `basica_curated_deep` (staleness de pipeline, não escolha metodológica). Pendência aberta: se os gráficos §6.3/§6.4 devem trocar de corte fixo (top-15) para o critério de 80% acumulado — não decidido. §3.2, §6.5 novos. |
| 2026-09-01 | **v5 — critério de bases trocado para 80% acumulado, pedido do autor.** `fig_top_bases_origem`/`fig_top_bases_chegadas` (script) trocam de corte fixo top-15 para a mesma regra de `gerar_pareto_bases_gol.py` (função nova `selecionar_hub`, compartilhada pelas duas figuras). Contagem de bases passa a variar por janela: 16 na janela completa (antes 15, `SBMO` entra), 17 em 2026 isolado (`SBSG` entra, ausente do corte fixo). Pendência do histórico v4 resolvida. 8 figuras regeradas. §6.3, §6.4, §6.5 atualizados. |
| 2026-09-01 | **v6 — janelas fechando e cruzamentos tempo×frota/tempo×base, pedido do autor.** 4 janelas novas (2022→2026, 2023→2026, 2024→2026, 2025→2026, mesmo teto 2026-07-31, piso subindo), mais as duas pontas já existentes (2021→2026, 2026 isolado) — sazonalidade se confirma em qualquer corte (§6.6). Dois cruzamentos novos: duração mensal por frota (3 linhas, nunca se cruzam, `B737` com viés de queda visível) e por base HUB (top 6, achados de nível novos — platô isolado de `SBGL` em 2022-23, quebra de patamar de `SBRJ` no fim de 2023) (§6.7). Achado de processo: paleta monocromática de 6 séries ficou pouco legível só com legenda, corrigido com rótulo direto no fim de cada linha. 14 figuras no total. §3.2, §5, §6.6, §6.7 novos/atualizados. |
| 2026-09-01 | **v7 — regra de paleta por nº de séries, pedido do autor.** Gráfico de linha com mais de 3 séries troca do laranja monocromático para paleta categórica "normal", colorida (`PALETA_CATEGORICA`, 8 cores validadas da skill `dataviz`, ordem fixa) — laranja GOL segue valendo para série única e até 3 séries (frota). Aplicado em `duracao_media_mensal_por_base` (6 séries); rótulo direto no fim da linha mantido como reforço, não mais como única correção. 14 figuras regeradas. §6.7 atualizado. |
| 2026-09-01 | **v8 — gráfico por base (colorido) estendido a 2025_2026 e 2026 isolado, pedido do autor.** `duracao_media_mensal_por_base` rodado também para as duas janelas mais fechadas (antes só `full_2021_2026`). Nas janelas mais curtas o platô de `SBGL` (§6.7, específico de 2022-23) não aparece, esperado — fica fora do recorte. 16 figuras no total. §6.7 atualizado. |
| 2026-09-03 | **v9 — correção retroativa (achado de auditoria documental): rodada Azul + comparação GOL x Azul + notebook didático, todas já concluídas, não estavam registradas.** Título do documento passa a "Etapa Média GOL/Azul" (deixa de ser GOL-only). Azul replicada (mesmo método, §6.8): 1.541.677 etapas, cerca de Tukey 3,49h (3,70% fora), autocorrelação diária r=0,731 — maior que a da GOL (r=0,429, também preenchido retroativamente nesta v9). `versus_gol_azul.py` documentado (§6.9): 12 gráficos da primeira seleção + 9 gráficos `novo_NN` de uma auditoria de completude pedida pelo autor (2026-09-02), que achou lacunas reais na seleção original. Notebook `analise_etapa_media_gol.ipynb` registrado como entrega didática (§3.4), sem achado de negócio próprio. §3.2, §3.3, §3.4 (novo), §6.8/§6.9 (novos), §9, §12 atualizados. |
| 2026-09-03 | **v10 — nota de leitura, achado inalterado.** Coeficientes de §6.8 inalterados; acrescentada nota remetendo à `SPEC-017` para não ler autocorrelação como medida de estabilidade. Origem: discussão durante a redação do relatório IMRaD do deep dive. |
| 2026-09-04 | **v11 — nota de procedência, achado inalterado.** Coeficientes de §6.8 inalterados; declarado que a série diária de etapa média é construída **sem corte de outlier**, e que a cerca de Tukey listada na mesma tabela não se aplica a esse cálculo. Registrado que isso difere de `SPEC-016 §6.2` (tempo de solo, série já truncada pela cerca de cada companhia), de modo que os coeficientes das duas linhas vêm de regimes de limpeza diferentes: a ordenação entre companhias se mantém, a diferença de magnitude entre indicadores não é atribuível só ao indicador. Origem: revisão do relatório IMRaD do deep dive, que começou pela divergência de corte em tempo de solo e alcançou esta linha. Ver `SPEC-017 §6.3` requisito 4. |
| 2026-09-04 | **v12 — codificação de aeroportos trocada de ICAO para IATA, achados inalterados.** Pedido do autor: as figuras rotulavam bases pelo ICAO de 4 letras (`SBGR`, `SBSP`), que é o que a Básica carrega, enquanto a audiência da análise lê IATA de 3 letras (`GRU`, `CGH`). Módulo novo `analise/iata_bases.py` traduz no ponto de carga contra `dim_airport_location_time_zone` e **preserva a coluna ICAO ao lado** (rastro de auditoria); os scripts passaram a plotar `sg_iata_origem`/`sg_iata_destino`, o SQL continua lendo as colunas ICAO da fonte. 82 figuras de `a4_etapa_media` regeradas, mais as 40 de `a3`/`a4` cujo nome de arquivo carregava o ICAO (`dist_10_hexbin_horario_partida_SBGR.png` → `..._GRU.png`, as antigas removidas após conferir o par). Nenhum número, corte, agrupamento ou conclusão mudou — troca de rótulo apenas. Corpo deste documento convertido; **linhas anteriores do Histórico preservadas em ICAO** (registram o que se escreveu na data). Dois achados de qualidade no de-para, ambos com fallback para o próprio ICAO: `base_iata` traz a sentinela `'N/I'` para `SBFE`/`SDIY`/`SNJD` (sem tratamento, os três colapsariam num balde único, e `SDIY` tem 317 etapas), e 3 aeródromos não têm IATA (`SBUY` 676 etapas, `LPAR` 2, `SBYS` 1). |
| 2026-09-05 | **v13, pareto migrado de CSV estático para view SQLite.** `rascunho/pareto_bases_gol.csv` (evidência do autor, não reproduzível) movido para `analise/a4_etapa_media/pareto_bases_gol_autor_2026-08-31.csv`; `pareto_bases_gol_atualizado.csv` e `gerar_pareto_bases_gol.py` removidos, substituídos pela view `pareto_bases_gol_azul` (`sql/curated_deep/DDL_006_pareto_bases_gol_azul_create_view_sqlite.sql`), que cobre as duas empresas e os dois sentidos (chegada e partida) numa janela móvel de cinco anos fechados. Motivo: o CSV ficou stale porque era estático, e a view não pode ficar. §3.2, §5.2, §6.5 atualizados; entradas de Histórico anteriores preservadas como registro do que se sabia à época. **Achado novo, refina §6.5 sem contradizê-lo:** na janela 2021-2025 a ordem `GRU` > `CGH` volta a ser a do CSV do autor, e o denominador cai de 1.156.956 para 1.012.015 chegadas (autor: ≈959 mil). A janela explica a inversão #1/#2 e parte da diferença de magnitude, mas não explica `VIX` nem a contagem de HUB (16 na janela, 16 no histórico inteiro, 15 no autor). O §6.5 já dizia que janela curta uniforme não era a *única* causa; segue valendo, com uma causa a menos em aberto. **Achado de qualidade de dado:** as colunas `sg_iata_*` de `basica_curated_deep` são inconsistentes dentro do mesmo ICAO (`SDIY` como `FEC` em 77 linhas e `N/I` em 240; `SPJC` como `LIM` em 66 e `...` em 1). A view resolve o rótulo por ICAO contra a dimensão, mesma regra de `analise/iata_bases.py`; resolver linha a linha partiria o mesmo aeroporto em duas bases. |
| 2026-09-07 | **v14, citações ao documento de referência tornadas autocontidas, achados inalterados.** §4 e §6.5 citavam `rascunho/Deep_Dive_Gol_ANAC_1a_.docx`, arquivo agora removido do disco deste projeto: era cópia byte a byte idêntica (md5 `b5b3a5d7`) da que vive em `learn-imrad-mintos`, e três peças já o davam por excluído desde 2026-08-31. As duas citações passam a descrever o documento em prosa, sem apontar caminho, mesmo tratamento que a `DEC-007 v2` aplicou. A estética casada e o número de 238.438 etapas de GOL 2025 continuam valendo: nenhum número, método ou conclusão muda. O comentário de paleta em `analise/a4_etapa_media/analise_etapa_media_gol.py` acompanha. |
| 2026-10-14 | Frontmatter alinhado ao Histórico: `versao: v14` e `data: 2026-09-07`, os da última versão registrada acima, que tinha sido lançada sem subir o frontmatter. Achado M1 do `AUDIT-002`. Nenhuma mudança de conteúdo. |
| 2026-10-14 | **v15, correção de instrução, achados inalterados.** Instrução de ambiente trocada de `pesquisa-azul`, ambiente de outro projeto, para `gov-sermi-perf`, o declarado na `DEC-011 §2.2` (2 ocorrência(s)). Dívida M4 do `AUDIT-002`. Status mantido em `proposto`; nenhum método, achado ou critério muda. |

---

*Fim do documento.*
