---
documento: SPEC-015
titulo: Análise Exploratória — Block Time GOL/Azul (Folga e Atrasos)
versao: v2
status: proposto
data: 2026-10-14
autor: Bruno Alexandre Serminaro
referencia: DEC-007, SPEC-014
escopo: projeto
---

# SPEC-015 · Análise Exploratória — Block Time GOL/Azul (Folga e Atrasos)

> Documento **vivo**: registra método, código e achados da análise
> exploratória de `folga_horas`/`atraso_partida_horas`/
> `atraso_chegada_horas` (`fato_block_time_gol_azul`, `SPEC-014`) — GOL
> primeiro, depois Azul, depois comparação GOL x Azul. Mesmo padrão de
> `SPEC-013` (etapa média): cresce por rodada, cada rodada nova vira
> entrada no Histórico (§13), não documento novo. Complementa `SPEC-014`,
> que documenta a tabela/dado (`fato_block_time_gol_azul`), não a
> análise.

---

## 1. Propósito

Explorar `folga_horas` (sobra/falta de tempo programado) e os atrasos de
partida/chegada da GOL e da Azul: forma da distribuição, estabilidade
temporal e segmentação por frota/hub/natureza/continuidade — seguindo o
método completo (forma+cerca → run sequence → lag plot → segmentação)
**desde o início**, corrigindo a ordem usada por engano em
`a3_tempo_de_solo`/`a4_etapa_media` (lá só se fez run sequence e lag plot
depois, quando pedido; aqui a estabilidade temporal é checada antes de
qualquer segmentação, decisão combinada com o autor em 2026-09-02).

## 2. Audiência

Reaproveita os papéis abstratos do `SPEC-002 §2` — nenhum papel novo.

## 3. Escopo

### 3.1 Regras padrão desta linha de análise

- **Só etapas `PASSAGEIRO`** — mesma regra fixada em `SPEC-013 §3.1` para
  toda a linha de análise GOL/Azul, aplicada aqui via mapeamento
  `id_basica → ds_servico_tipo_linha` (`fato_block_time_gol_azul` não
  filtra serviço nativamente, achado desta rodada, §6.1).
- **Ordem método → segmentação**: forma+cerca de Tukey, run sequence, lag
  plot, **só depois** segmentação por frota/hub/natureza/continuidade —
  pedido do autor, 2026-09-02, correção deliberada da ordem inversa usada
  em `a3`/`a4`.
- **Corte fixo `±60min` ("família cerca_")** substituindo a cerca de
  Tukey para run sequence/lag plot/segmentação — pedido do autor,
  2026-09-03 (§6.6). Unidades em minutos nesses gráficos (mais legível
  que hora fracionária numa faixa estreita).

### 3.2 O que este SPEC entrega

1. Script GOL: `analise/a5_block_time/distribuicao_block_time_gol.py` →
   `a5_figuras_gol/` (18 gráficos `dist_NN` + 16 gráficos `cerca_dist_NN`,
   rodada completa, §6).
2. Script Azul (escopo reduzido, §6.7):
   `analise/a5_block_time/distribuicao_block_time_azul.py` →
   `a5_figuras_azul/` (5 gráficos `dist_NN` + 16 `cerca_dist_NN`).
3. Script de comparação: `analise/a5_block_time/versus_gol_azul.py` →
   `a5_figuras_versus/` (11 gráficos `vNN`, todos no corte fixo
   `±60min`, §6.8).
4. Achados de cada rodada, registrados em §6.

### 3.3 Fora de escopo (nesta rodada)

- Propagação de atraso entre etapas via rotação (atraso de chegada da
  etapa N vs. atraso de partida da etapa N+1, mesma aeronave) — direção
  de investigação registrada, não construída.
- Uso de `ds_situacao_voo`/`cd_justificativa` (colunas do VRA presentes
  em `fato_block_time_gol_azul`, nunca usadas nesta rodada).
- Granularidade por hora do dia ou rota OD específica.
- Folga como % do tempo previsto (só a diferença absoluta foi explorada).
- Teste estatístico formal da hipótese "viés de match VRA ligado à
  recuperação judicial da GOL" (§6.5) — refutada por comparação simples
  com a Azul (§6.8), não por teste formal.

## 4. Fonte e método

```
fato_block_time_gol_azul (SPEC-014, db/anac_basica.sqlite)
  + basica_curated_deep (só para filtro PASSAGEIRO e natureza da linha)
  → filtro sg_empresa_icao='GLO'|'AZU', dt_partida_real em WINDOW_FULL
  → analise/a5_block_time/distribuicao_block_time_{gol,azul}.py (pandas + matplotlib + seaborn)
  → analise/a5_block_time/versus_gol_azul.py (importa os dois módulos acima)
  → analise/a5_block_time/a5_figuras_{gol,azul,versus}/*.png
```

`WINDOW_FULL = ("2021-01-01", "2026-06-30")` — teto diferente de
`a3`/`a4` (que usam `2026-07-31`): achado desta rodada (§6.2), o VRA só
tem dado até `2026-07-01 03:22`, contra `2026-08-01` da Básica. Mesmo
teto vale para GOL e Azul (fonte VRA compartilhada, não é peculiaridade
de uma companhia).

Ambiente: `conda run -n gov-sermi-perf python analise/a5_block_time/distribuicao_block_time_gol.py`
(mesma premissa do `SPEC-002 §6`).

## 5. Variáveis analisadas

| Variável | Definição | Interpretação |
|---|---|---|
| `folga_horas` | `tempo_previsto_horas` (VRA) − `nr_horas_voadas` (Básica) | Positivo = sobra de tempo programado; negativo = falta. **Não é** taxi estrutural puro nem margem estratégica pura — as duas coisas misturadas (`SPEC-014 §6.2`, §11). |
| `atraso_partida_horas` | `dt_hr_partida_real_vra` − `dt_hr_partida_prevista` | Positivo = saiu atrasado; negativo = saiu adiantado. |
| `atraso_chegada_horas` | `dt_hr_chegada_real_vra` − `dt_hr_chegada_prevista` | Positivo = chegou atrasado; negativo = chegou adiantado. |
| `Δ atraso em voo` *(métrica nova desta rodada)* | `atraso_chegada_horas` − `atraso_partida_horas` | Negativo = recuperou atraso durante o voo; positivo = piorou em voo. Criada porque atraso de partida e de chegada são quase redundantes (`r≈0,976-0,977`, §6.4) — a diferença é o conteúdo novo. |

## 6. Achados

### 6.1 Filtro PASSAGEIRO não é herdado — mesmo bug do script antigo

`fato_block_time_gol_azul` (como `fato_rotacao_aeronave_gol_azul`) herda
`basica_curated_deep` inteira, cargueiro incluso. O script antigo
(`analise_block_time_gol_azul.py`) afirmava o contrário no docstring.
Medido e corrigido: **21.494 etapas de CARGUEIRO (1,9%) na GOL**, **22.884
(1,5%) na Azul**, removidas via mapeamento `id_basica`.

### 6.2 Atraso: garbage de timestamp VRA (não é outlier real)

`|atraso_partida_horas| > 24h` ou `|atraso_chegada_horas| > 24h`:
timestamp VRA corrompido (chegando a ~8748h/365 dias na GOL, ~48-49h na
Azul), todas as linhas marcadas REALIZADO/justificativa N/A. Filtro
pontual (não cerca de Tukey, não vira coluna de validade no banco — escala
pequena demais, mesmo raciocínio de `SPEC-014 §11`):

| | GOL | Azul |
|---|---|---|
| Atraso partida, linhas removidas | 71 (0,006%) | 113 (0,008%) |
| Atraso chegada, linhas removidas | 95 (0,009%) | 138 (0,01%) |

`folga_horas` **não** é afetada (usa `nr_horas_voadas` da Básica, não os
timestamps "reais" do VRA).

### 6.3 VRA atrasado um mês — julho/2026 excluído da janela

`fl_match_vra` caindo para ~100% "sem match" em julho/2026 revelou que o
VRA só tem dado até `2026-07-01 03:22`, contra `2026-08-01` da Básica —
artefato de atraso de publicação da fonte, não sinal operacional.
`WINDOW_FULL` ajustado para terminar em `2026-06-30` (§4); mesmo teto
aplicado à Azul, verificado sem resíduo de pico artificial na janela
(`dist_07`/Azul: faixa mensal `[0%, 3,47%]`, sem spike).

### 6.4 Atraso de partida e de chegada são quase redundantes — métrica nova (Δ atraso em voo)

`corr(atraso_partida_horas, atraso_chegada_horas)` = **0,976 (GOL)**,
**0,970 (Azul)** — os dois "contam quase a mesma história" isoladamente.
Em vez de replicar os 4 gráficos de atraso de partida para atraso de
chegada sem ganho analítico, criada a métrica `Δ atraso em voo`
(§5) — mede recuperação/perda de atraso durante o voo:

| | GOL | Azul |
|---|---|---|
| Δ atraso em voo, média | −2,8min (corte fixo: −2,9min) | −2,2min |
| Δ atraso em voo, mediana | −4,0min (corte fixo: −4,0min) | −3,0min |

Em mediana, as duas companhias recuperam alguns minutos de atraso durante
o voo. Os 4 gráficos de atraso de chegada (dist_15/16/17/18) foram
construídos mesmo assim, por pedido explícito do autor ("quero ver a cara
deles") — confirmam visualmente a redundância esperada.

### 6.5 Viés de match VRA cresce a partir de 2024 — em GOL e Azul (refuta hipótese GOL-específica)

`fl_match_vra=0` (sem par no VRA) salta de ~0% (2021-2023) para uma faixa
mais alta a partir de janeiro/2024 — **em ambas as companhias**:

| | GOL | Azul |
|---|---|---|
| % geral sem match | 1,42% | 1,15% |
| Faixa mensal | `[0%, 9,64%]` | `[0%, 3,47%]` |

O padrão de início (mesma virada de ano) e o formato do salto são
compartilhados entre as duas empresas independentes — isso **enfraquece**
a hipótese candidata levantada informalmente durante a rodada GOL (viés
ligado à recuperação judicial da GOL, que começou em jan/2024): se fosse
específico da GOL, não apareceria com o mesmo timing na Azul. Mais
consistente com uma mudança de processo/qualidade de dado do lado do VRA
(fonte compartilhada), não confirmada, não investigada a fundo. Hipótese
original marcada como refutada por evidência simples, não substituída por
outra confirmada.

### 6.6 Corte fixo `±60min` ("família cerca_") substitui a cerca de Tukey para run sequence/lag/segmentação

Cerca de Tukey varia por variável e por cerca calculada (ex.:
`[-0,51h, 0,49h]` em atraso de partida GOL vs. `[-0,68h, 0,59h]` em
atraso de chegada) — pedido do autor, 2026-09-03: usar um corte único e
redondo, `±60 minutos`, para as 3 variáveis, com unidade de exibição em
minutos (não hora fracionária). `LIMITE_CERCA_MIN = 60.0`, aplicado em
`folga_horas`/`atraso_partida_horas`/`atraso_chegada_horas`
independentemente — mais permissivo que a cerca de Tukey para folga (que
tinha ±18-25min), mais restrito que a cerca de Tukey para atraso
(±30-40min). Cobre run sequence, lag plot e toda a segmentação por
modelo/hub/natureza/continuidade — **não** existe versão "cerca_" para
`dist_07` (viés de match) e `dist_13` (top bases sem match), que não
dependem de truncar folga/atraso.

**Achado de processo (binning)**: `folga_horas`/`atraso_*_horas` são
granularidade de minuto inteiro na fonte (só ruído de ponto flutuante da
conversão hora→minuto). Bins de largura fixa não alinhados ao minuto
(ex.: 80 bins sobre 120min = 1,5min/bin) produzem serrilhado artificial
nos histogramas — corrigido com `binwidth=1` centralizado no inteiro em
toda a família `cerca_`.

### 6.7 Replicação Azul — escopo reduzido, pedido do autor

Ao contrário da rodada GOL (18 gráficos "plain" + 16 "cerca_"), a
replicação Azul (2026-09-03) tem escopo intencionalmente menor: só os 3
gráficos de forma+distribuição (`dist_01`/`04`/`15`, folga e os dois
atrasos, cerca de Tukey) mais viés de match (`dist_07`) e top bases sem
match (`dist_13`) — 5 gráficos "plain" no total, sem replicar run
sequence/lag plot/segmentação em versão Tukey-based, já que o corte fixo
`±60min` (§6.6) havia acabado de ser validado na GOL como política
razoável. Toda a segmentação da Azul roda direto na família `cerca_` (16
gráficos, mesma cobertura da GOL).

**Achado de processo (rótulos em violin plot)**: a Azul tem até 7 modelos
de frota (`A339, A21N, A20N, E195, AT76, E295, A332`) contra 3 da GOL
(`B738, B737, B38M`). O desenho original dos rótulos de média/mediana
(texto ao lado de cada violino, largura de figura fixa) foi projetado e
validado só com 3 categorias — com 7, os rótulos invadiam o violino
vizinho, ilegível. Corrigido de forma genérica (não um ajuste pontual
para a Azul): largura da figura escala com o nº de modelos
(`max(9.0, 1.5 * len(ordem))`), e os rótulos passam a ficar numa faixa
centralizada **acima** de cada violino (não mais ao lado), confinados à
própria coluna — funciona para qualquer nº de categorias. A legenda
(Média/Mediana) foi movida de `upper right` para `lower right` pelo mesmo
motivo (colidia com o rótulo da última categoria depois da mudança).
Replicado de volta na GOL para manter os dois scripts em paridade, mesmo
sem o bug se manifestar lá (só 3 categorias).

### 6.8 GOL x Azul — comparação direta, corte fixo `±60min`

`versus_gol_azul.py`, 11 gráficos, todos no corte fixo `±60min` (§6.6),
eixo Y/X ou escala de cor compartilhados conforme a pergunta (mesmo
princípio de `a3`/`a4`):

- **Forma da distribuição de folga** (`v02`, densidade compartilhada):
  Azul mais concentrada/pontual (pico de densidade mais alto e mais
  estreito) que a GOL.
- **Autocorrelação diária de folga** (`v11`, lag plot): GOL mais
  autocorrelacionada dia-a-dia (`r=0,808`) que a Azul (`r=0,660`) — a
  GOL "herda" mais o nível de folga do dia anterior.
- **Viés de match mensal** (`v09`): confirma visualmente o achado do
  §6.5 lado a lado — mesmo timing de virada (início de 2024), GOL com
  amplitude de pico maior (até 9,64%) que a Azul (até 3,47%).

## 7. Critérios de sucesso (desta rodada)

- **C-01** — Scripts das 3 rodadas (GOL, Azul, versus) rodam sem erro,
  geram as figuras esperadas. **Cumprido**: 18+16 (GOL), 5+16 (Azul),
  11 (versus) — 66 arquivos `.png` no total, confirmados por listagem de
  diretório.
- **C-02** — Cada figura inspecionada visualmente antes de reportar
  achado. **Cumprido** para as figuras centrais a cada achado do §6
  (amostragem representativa dos 3 scripts, incluindo as que motivaram
  correção de bug, §6.6/§6.7).
- **C-03** — Bugs de legibilidade encontrados durante a inspeção visual
  corrigidos antes de fechar a rodada, não deixados como pendência
  silenciosa. **Cumprido**: serrilhado de binning (§6.6), colisão de
  rótulo em violin plot com muitas categorias (§6.7), título estourando
  largura de figura fixa (lag plot da família `cerca_`).

## 8. Premissas e dependências

- Depende de `fato_block_time_gol_azul` (`SPEC-014`) e
  `basica_curated_deep` (`SPEC-012`) já carregadas e corretas — esta SPEC
  não revalida o tratamento delas, só herda.
- Ambiente `gov-sermi-perf` (conda, `DEC-011 §2.2`) com `pandas`/`matplotlib`/`seaborn`
  disponíveis.
- `tempo_real_vra_horas` ≈ `nr_horas_voadas` (`SPEC-014 §6.2`) — premissa
  herdada, não reavaliada aqui: `folga_horas` mistura taxi estrutural com
  margem estratégica, não separável com o dado disponível.

## 9. Não-objetivos (desta rodada)

- Não é objetivo confirmar a causa do salto de viés de match a partir de
  2024 (§6.5) — hipótese GOL-específica refutada por comparação simples,
  causa real não investigada.
- Não é objetivo separar taxi estrutural de margem estratégica dentro de
  `folga_horas` — limitação herdada de `SPEC-014 §6.2/§11`.
- Não cobre os itens do §3.3 (propagação de atraso via rotação,
  `ds_situacao_voo`/`cd_justificativa`, granularidade horária/OD, folga
  em %).

## 10. Próximos passos (direção pedida pelo autor ou identificada na rodada)

- Investigar a causa do salto de viés de match a partir de 2024 (§6.5) —
  candidato: mudança de processo do lado do VRA, não confirmado.
- Propagação de atraso entre etapas via rotação (atraso de chegada da
  etapa N vs. atraso de partida da etapa N+1, mesma aeronave) — pergunta
  ainda em aberto da lista original de brainstorm desta linha de análise.
- Avaliar se `ds_situacao_voo`/`cd_justificativa` (nunca usadas) trazem
  sinal sobre a causa dos atrasos, não só a magnitude.

## 11. Limitações conhecidas

- `folga_horas` mistura taxi estrutural com margem estratégica —
  limitação herdada, não resolvida nesta rodada (`SPEC-014 §6.2/§11`).
- Corte fixo `±60min` (§6.6) é uma escolha de legibilidade/comparabilidade,
  não um limiar estatístico — descarta a cauda (outliers legítimos além
  de 1h) das visualizações da família `cerca_`; os gráficos "plain"
  (Tukey, sem truncar em minutos) continuam sendo a fonte de verdade para
  a forma completa da distribuição, incluindo cauda.
- Achado do §6.5 (viés de match crescente) é hipótese refutada
  (GOL-específica) mas não substituída por uma causa confirmada — fica
  como pergunta em aberto, não como achado fechado.
- Replicação Azul (§6.7) tem escopo menor que a GOL por decisão
  deliberada, não por limitação técnica — se precisar da versão
  "Tukey-based" completa de run sequence/lag/segmentação da Azul, não
  existe ainda, teria que ser construída à parte.

## 12. Critérios de revisão

Revisitar esta SPEC (nova entrada no Histórico, não novo documento)
quando:

- Uma nova rodada de análise (nova variável, nova segmentação, nova
  comparação) for pedida pelo autor.
- A causa do salto de viés de match (§6.5) for investigada e confirmada
  ou refutada com evidência adicional.
- Algum dos itens do §3.3/§10 for construído.

## 13. Histórico

| Data | Evento |
|---|---|
| 2026-09-03 | SPEC-015 v1 produzida em status `proposto`, documento vivo, retroativa (cobre as rodadas GOL, Azul e versus já concluídas na sessão de trabalho). GOL: 18 gráficos `dist_NN` (forma+cerca de Tukey → run sequence → lag plot → segmentação, nessa ordem) + 16 `cerca_dist_NN` (corte fixo ±60min). Azul: escopo reduzido (5 `dist_NN` + 16 `cerca_dist_NN`), pedido do autor. Comparação: `versus_gol_azul.py`, 11 gráficos, corte fixo ±60min. Achados centrais: bug de filtro PASSAGEIRO não herdado (mesmo padrão de `SPEC-012`/`SPEC-013`, 21.494 GOL / 22.884 Azul etapas de CARGUEIRO removidas); garbage de timestamp VRA em atraso (|atraso|>24h, escala <0,01%); VRA atrasado um mês, `WINDOW_FULL` ajustado para 2026-06-30; atraso de partida e chegada quase redundantes (r≈0,97), métrica nova "Δ atraso em voo" criada; viés de match VRA cresce a partir de 2024 em **ambas** as companhias, refutando hipótese informal de causa GOL-específica; corte fixo ±60min ("família cerca_") substitui cerca de Tukey para run sequence/lag/segmentação, acompanhado de correção de binning (serrilhado) e de correção de rótulo em violin plot (colisão com >4 categorias, corrigida de forma genérica e replicada na GOL). Aguardando aprovação do autor. |
| 2026-10-14 | **v2, correção de instrução, achados inalterados.** Instrução de ambiente trocada de `pesquisa-azul`, ambiente de outro projeto, para `gov-sermi-perf`, o declarado na `DEC-011 §2.2` (2 ocorrência(s)). Dívida M4 do `AUDIT-002`. Status mantido em `proposto`; nenhum método, achado ou critério muda. |

---

*Fim do documento.*
