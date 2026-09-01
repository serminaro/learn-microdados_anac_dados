---
documento: SPEC-013
titulo: Análise Exploratória — Etapa Média GOL
versao: v8
status: proposto
data: 2026-09-01
autor: Bruno Alexandre Serminaro
referencia: DEC-007
escopo: projeto
---

# SPEC-013 · Análise Exploratória — Etapa Média GOL

> Documento **vivo**: registra método, código e achados da análise
> exploratória de etapa média (duração) da GOL, detalhando a pergunta 5
> do `SPEC-004 §5.5` só para GOL. Cresce por rodada — cada rodada nova
> vira entrada no Histórico (§13) e atualização das seções de achados,
> não documento novo. Diferente das SPECs anteriores deste projeto
> (retroativas, escritas depois do trabalho validado), esta acompanha o
> trabalho enquanto ele acontece.

---

## 1. Propósito

Explorar a duração média de etapa da GOL (`NR_HORAS_VOADAS`) e suas
relações com frota, bases (origem/destino) e tempo, partindo da janela
temporal mais larga disponível e fechando progressivamente até 2026 —
método de trabalho pedido pelo autor (2026-09-01), não um recorte fixo
definido de antemão.

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
4. *(v4)* Script `analise/a4_etapa_media/gerar_pareto_bases_gol.py` e
   saída `pareto_bases_gol_atualizado.csv` — pareto de bases HUB/OFF-HUB
   (80% acumulado), confrontado contra `rascunho/pareto_bases_gol.csv`
   fornecido pelo autor (§6.5).
5. *(v6)* Janelas fechando (2022→2026, 2023→2026, 2024→2026, 2025→2026,
   além das duas pontas já existentes) e dois cruzamentos novos
   (duração mensal por frota, duração mensal por base HUB) — §6.6, §6.7.

### 3.3 Fora de escopo (nesta rodada)

- Azul — só GOL por pedido explícito do autor (2026-09-01); Azul fica
  para quando o autor pedir, mesmo método.
- Mediana/quartis — `SPEC-004 §5.5` prevê como complemento "se a
  distribuição for assimétrica"; não avaliado ainda nesta rodada, fica
  para próxima se a média mostrar sinal de cauda longa.
- Cálculo de velocidade inferida (`KM_DISTANCIA/NR_HORAS_VOADAS`) — já
  coberto por `sql/analise/QUERY_001` equivalente no nível empresa×
  natureza; não replicado aqui em nível de figura nesta rodada.
- Relação frota×base (que frota opera de qual base) — mencionada como
  direção de exploração pelo autor, não construída ainda.

## 4. Fonte e método

```
basica_curated_deep (SPEC-012, db/anac_basica.sqlite)
  → filtro sg_empresa_icao='GLO' AND ds_servico_tipo_linha='PASSAGEIRO'
  → janela de dt_partida_real (varia por rodada, §6)
  → analise/a4_etapa_media/analise_etapa_media_gol.py (pandas + matplotlib)
  → analise/a4_etapa_media/a4_figuras_gol/*.png
```

**Estética dos gráficos** (ajustada 2026-09-01, pedido do autor): casada
com `rascunho/Deep_Dive_Gol_ANAC_1a_.docx` (material de referência já
produzido para este mesmo deep dive, projeto anterior/paralelo), não com
a paleta padrão da skill `dataviz` deste ambiente — divergência
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

Ambiente: `conda run -n pesquisa-azul python analise/a4_etapa_media/analise_etapa_media_gol.py`
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

### 6.3 Bases HUB de origem (80% acumulado) — SBSP/SBGR concentram volume, nordeste puxa duração

*(v5)* Critério trocado de corte fixo (top-15) para 80% acumulado
(`selecionar_hub`, mesma regra de §6.5/`gerar_pareto_bases_gol.py`) —
pedido do autor, 2026-09-01. Deixa de ser um número fixo de bases: 16 na
janela completa (`SBMO` entra, mesma composição do pareto §6.5), 17 em
2026 isolado (`SBSG` entra, não aparecia no corte fixo de 15 antes).

`top_bases_origem_full_2021_2026.png`, cor = duração média. `SBSP`
(Congonhas) e `SBGR` (Guarulhos) dominam em volume de etapas (~175 mil e
~173 mil no período), muito à frente da 3ª colocada (`SBBR`, Brasília,
~107 mil). Cor revela outro eixo: as bases mais escuras (maior duração
média) não são as de maior volume — `SBFZ` (Fortaleza) e `SBRF` (Recife)
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

### 6.5 Pareto de bases (HUB/OFF-HUB) — confronto contra `rascunho/pareto_bases_gol.csv`, achado de staleness

O autor forneceu `rascunho/pareto_bases_gol.csv` (classificação HUB/OFF-HUB
por acúmulo de 80% das chegadas, mesma família de método de
`SPEC-004 §6`) para conferência contra as bases escolhidas nesta SPEC.
Repliquei a metodologia exata (ranking por chegadas, % acumulado, HUB
enquanto o acumulado **antes** da base é `< 80%`) contra
`basica_curated_deep` atual — script
`analise/a4_etapa_media/gerar_pareto_bases_gol.py`, saída
`analise/a4_etapa_media/pareto_bases_gol_atualizado.csv`.

**O que bate**: 14 das 15 bases HUB do CSV do autor aparecem no
resultado atual; a ordem das posições 3-12 é idêntica nos dois.

**O que diverge**:

| Ponto | `pareto_bases_gol.csv` (autor) | `pareto_bases_gol_atualizado.csv` (esta rodada) |
|---|---|---|
| #1/#2 | `SBGR` > `SBSP` | `SBSP` > `SBGR` |
| `SBVT` | OFF-HUB (rank 16, 80,85% acum.) | **HUB** (rank 14, 77,98% acum.) |
| `SBMO` | HUB, rank 13 | HUB, rank 16 (81,00% acum., quase fora) |
| Total de chegadas (denominador) | ≈ 959 mil (implícito) | 1.156.956 |
| Nº de bases HUB | 15 | **16** |

Magnitude por base diverge de forma não uniforme (70%-88% do valor atual,
dependendo da base) — descarta janela mais curta aplicada uniformemente
como única causa.

**Hipótese testada e descartada**: o CSV do autor não é o recorte 2025
isolado do outro documento de referência (`Deep_Dive_Gol_ANAC_1a_.docx`,
Snowflake `TRUSTED_FLIGHTS`) — GOL 2025 passageiro neste banco dá
exatamente 238.438 etapas (bate com o número que o próprio docx cita),
mas as magnitudes do CSV do autor são ~4× maiores. Descartado.

**Hipótese mais provável (não confirmada por rastro documental direto,
só por coincidência temporal forte)**: `rascunho/pareto_bases_gol.csv`
tem data de modificação `2026-08-31 08:38` — **anterior** à correção do
`SPEC-008 v4` (bug de corte hardcoded que travava `basica_raw` em
2026-06, antes de `2026-07` ser incluído) e anterior à `basica_curated_deep`
existir. Provável snapshot de um estágio anterior do pipeline, não uma
escolha metodológica divergente.

**Resolvido em v5**: `top_bases_origem`/`top_bases_chegadas` (§6.3, §6.4)
trocaram do corte fixo top-15 para o critério de 80% acumulado, pedido
do autor — mesma função `selecionar_hub` usada em ambas as figuras,
consistente com `gerar_pareto_bases_gol.py`.

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

- **`SBGL` (Galeão) tem um platô isolado em 2022-meados de 2023**
  (~2,6-2,7h, bem acima do seu próprio nível antes/depois, ~2,1-2,3h) —
  não presente em nenhuma outra base do top 6. Hipótese candidata, não
  investigada: mudança temporária de malha internacional operada a
  partir do Galeão nesse período.
- **`SBRJ` (Santos Dumont) tem uma quebra de nível abrupta no fim de
  2023** (de ~1,4-1,5h para ~1,2-1,3h, queda de ~15-20%, permanente até
  o fim da série) — não gradual, muda de patamar num só mês. Hipótese
  candidata: mudança de mix de rotas na ponte aérea/shuttle que opera
  dali, não investigada.

**Nota de legibilidade (achado de processo, não de dado)**: a primeira
versão do gráfico por base usava só legenda — com 6 séries na mesma
família de laranja (paleta GOL, §4), as linhas de nível médio
(`SBGR`/`SBBR`/`SBRJ`/`SBSV`, todas entre 2,0-2,2h) ficavam praticamente
indistinguíveis só pela cor. Duas correções: (1) rótulo direto no fim de
cada linha; (2) pedido do autor (2026-09-01) — regra nova fixada em
`analise_etapa_media_gol.py`: gráfico de linha com **mais de 3 séries**
troca do laranja monocromático (`SEQ_ORANGE_CMAP`) para a paleta
categórica validada da skill `dataviz` (`PALETA_CATEGORICA`, 8 cores em
ordem fixa) — laranja GOL segue valendo para série única e para
comparações de até 3 séries (frota, §6.7), onde já era legível.

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
- Ambiente `pesquisa-azul` (conda) com `pandas`/`matplotlib` disponíveis
  — confirmado nesta rodada (`pandas 2.3.3`, `matplotlib 3.11.0`).
- `NR_HORAS_VOADAS` é tempo no ar (airborne), não tempo de bloco
  porta-a-porta — mesma ressalva já registrada em `SPEC-004 §5.5` e
  `SPEC-011`/`SPEC-012` para colunas de horário.

## 9. Não-objetivos (desta rodada)

- Não é objetivo confirmar as hipóteses candidatas do §6.1/§6.2 (efeito
  pós-pandemia, saída do B737 do internacional) — ficam registradas como
  direção de investigação, não resolvidas aqui.
- Não é objetivo cobrir Azul, mediana/quartis, velocidade inferida em
  figura, ou relação frota×base nesta rodada (§3.3).

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
- Azul entrar no escopo desta linha de análise.
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

---

*Fim do documento.*
