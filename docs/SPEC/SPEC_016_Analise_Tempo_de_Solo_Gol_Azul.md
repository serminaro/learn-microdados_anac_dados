---
documento: SPEC-016
titulo: Análise Exploratória — Tempo de Solo GOL/Azul (Turnaround)
versao: v5
status: proposto
data: 2026-10-14
autor: Bruno Alexandre Serminaro
referencia: DEC-007, SPEC-012, SPEC-013, SPEC-017
escopo: projeto
---

# SPEC-016 · Análise Exploratória — Tempo de Solo GOL/Azul (Turnaround)

> Documento **vivo**, produzido retroativamente (achado de auditoria
> documental, 2026-09-03): cobre a linha de análise de `tempo_solo_horas`
> (`fato_rotacao_aeronave_gol_azul`, `SPEC-012`) que já estava concluída
> — GOL, Azul e comparação — sem nenhum SPEC registrando método ou
> achados. Mesmo padrão de `SPEC-013`/`SPEC-015`: cresce por rodada, cada
> rodada nova vira entrada no Histórico (§13).

---

## 1. Propósito

Explorar `tempo_solo_horas` (turnaround entre etapas consecutivas da
mesma aeronave) da GOL e da Azul: forma da distribuição, relação com
frota/distância/etapa média, segmentação por hub/destino/horário, e
estabilidade temporal — espelho estrutural de `SPEC-013` (etapa média),
trocando a variável de resposta de `nr_horas_voadas` para
`tempo_solo_horas`.

## 2. Audiência

Reaproveita os papéis abstratos do `SPEC-002 §2` — nenhum papel novo.

## 3. Escopo

### 3.1 Regras padrão desta linha de análise

- **Só etapas `PASSAGEIRO`** — mesma regra de `SPEC-013 §3.1`.
- **Limpeza de dado no banco, não em pandas**: `fl_solo_valido`
  (`DDL_005`, `SPEC-012 §6.5`) exclui `tempo_solo_horas` negativo,
  continuidade de rotação quebrada e `>72h` **antes** de qualquer script
  desta linha rodar — `load_data()` só filtra `fl_solo_valido = 1`, não
  reimplementa a regra.
- **Corte de truncagem para visualização é decisão desta linha de
  análise, não do banco** — mesmo com `fl_solo_valido=1`, a distribuição
  ainda tem cauda longa (pernoite legítimo até 72h conta como "outlier"
  pela convenção de Tukey, não por erro, §6.1) — cada script escolhe seu
  próprio corte de exibição (§6.1, §6.4).

### 3.2 O que este SPEC entrega

1. Scripts GOL: `analise/a3_tempo_de_solo/analise_tempo_solo_gol.py`
   (`ana_NN`, janelas fechando) e
   `analise/a3_tempo_de_solo/distribuicao_tempo_solo_gol.py` (`dist_NN`,
   forma+Tukey→segmentação) → `a3_figuras_gol/`.
2. Scripts Azul, espelho exato dos de GOL → `a3_figuras_azul/`.
3. Script de comparação: `analise/a3_tempo_de_solo/versus_gol_azul.py` →
   `a3_figuras_versus/`, 12 gráficos `vNN`.
4. Achados de cada rodada, registrados em §6.

### 3.3 Fora de escopo (nesta rodada)

- Investigar a causa raiz dos 0,29% de linhas com `tempo_solo_horas`
  inválido — já registrada como achado de `SPEC-012 §6.5`, não
  reinvestigada aqui.
- Separar tempo de solo em componentes (taxi, portão, conexão) — não há
  dado de nível de detalhe suficiente na fonte.
- Teste estatístico formal de qualquer hipótese candidata do §6.

## 4. Fonte e método

```
fato_rotacao_aeronave_gol_azul (SPEC-012, WHERE fl_solo_valido = 1)
  + basica_curated_deep (so' para filtro PASSAGEIRO e natureza da linha,
    mapeamento id_basica -> ds_servico_tipo_linha/ds_natureza_tipo_linha,
    mesma tecnica de SPEC-013, nao JOIN sem indice)
  → analise/a3_tempo_de_solo/{analise,distribuicao}_tempo_solo_{gol,azul}.py
  → analise/a3_tempo_de_solo/versus_gol_azul.py (importa os 4 modulos acima)
  → analise/a3_tempo_de_solo/a3_figuras_{gol,azul,versus}/*.png
```

Ambiente: `conda run -n gov-sermi-perf python analise/a3_tempo_de_solo/distribuicao_tempo_solo_gol.py`
(mesma premissa do `SPEC-002 §6`).

## 5. Variável analisada

| Variável | Definição | Interpretação |
|---|---|---|
| `tempo_solo_horas` | Partida desta etapa − chegada da etapa anterior, mesma matrícula (`SPEC-012 §5.3`) | Turnaround real em solo. Só válido onde `fl_continuidade_ok=1` (mesmo aeroporto) — por isso `fl_solo_valido` já filtra isso na fonte. |

## 6. Achados

### 6.1 Forma da distribuição — cauda longa até o teto de validade (72h)

Mesmo após `fl_solo_valido=1`, a distribuição de `tempo_solo_horas`
mantém cauda longa: cerca de Tukey calculada sobre os dados filtrados dá
limite inferior negativo (fisicamente impossível, forçado a `0h`) e
superior bem abaixo do teto de validade de `72h`:

| | GOL | Azul |
|---|---|---|
| Cerca de Tukey (superior) | 3,542h | 3,767h |
| % de etapas "fora" da cerca | 15,27% | 15,20% |
| Máximo observado (já ≤72h por `fl_solo_valido`) | 71,9h | 72,0h |

**Leitura correta, registrada no código para não confundir quem ler
depois**: pernoite/fim de semana legítimo (até 72h, dentro da regra de
validade do `SPEC-012 §6.5`) vira "outlier" pela convenção estatística de
Tukey — não é erro de dado, é a cerca sendo aplicada a uma distribuição
estruturalmente bimodal (turnaround curto entre etapas do mesmo dia vs.
pernoite entre dias).

### 6.2 Autocorrelação diária — Azul com mais memória dia-a-dia que a GOL

Lag plot (lag 1 dia) sobre a média diária de `tempo_solo_horas`:
**GOL r=0,613**, **Azul r=0,805**, sobre a série **truncada pela cerca de
Tukey de cada companhia** (3,542h na GOL, 3,767h na Azul; `dist_14` de
`distribuicao_tempo_solo_gol.py`/`_azul.py`, que a partir de `dist_02` opera
sobre a base truncada). O comparativo `versus_gol_azul.py` (`v12`) calcula o
mesmo coeficiente sobre corte fixo de `CORTE_HORAS = 3,0h` para as duas
empresas e obtém **0,674** e **0,861**: mesmos dados, corte diferente. Ver
`SPEC-017 §6.3`, requisito 4. Ao contrário do achado equivalente
para `folga_horas` em block time (`SPEC-015 §6.8`, onde a GOL é mais
autocorrelacionada), aqui é a **Azul** que carrega mais o nível do dia
anterior para o seguinte — achado específico desta variável, não
generalizável entre as duas linhas de análise sem checar caso a caso.

> **Correção de leitura (v2, ver `SPEC-017`).** A redação original desta
> seção dizia "Azul mais previsível dia-a-dia". Está errado como
> interpretação: `r` mede **memória** (fração da variação que persiste),
> não previsibilidade nem estabilidade, e é normalizado pela variância —
> comparar `r` entre companhias sem comparar `σ` não diz qual série é
> mais estável. Lido corretamente, `r` mais baixo na GOL é compatível com
> processo que corrige rápido (meia-vida de distúrbio de 1,4 dia contra
> 3,2 dias na Azul), não com operação mais instável. `SPEC-017` separa
> amplitude, periodicidade e memória, e nomeia três fatores de confusão
> mecânicos (tamanho de amostra diário, mix de frota, sazonalidade
> semanal) que precisam ser descartados antes de qualquer leitura
> operacional deste par de números. `σ` da série diária não foi medido
> nesta rodada.

> **Nota de procedência (v3, ver `SPEC-017 §6.3` requisito 4).** `r` depende
> do corte de outlier aplicado à série, e a dependência não é desprezível: o
> corte mais apertado (3,0h fixo) eleva o coeficiente nas duas empresas e
> move a meia-vida de distúrbio da GOL de 1,4 para 1,8 dia, quase 30%. A
> ordenação entre as companhias se mantém nos dois cortes. Comparações
> futuras, e sobretudo o ranking por base da rodada 2, precisam declarar o
> corte e usar o mesmo em todas as unidades comparadas.

### 6.3 Top bases por volume — bases diferentes das de etapa média

`selecionar_hub` (80% acumulado) sobre `tempo_solo_horas`: GOL top 10
lideradas por `GRU, CGH, BSB, GIG, SDU...`; Azul por
`VCP, CNF, REC, SDU, CGH...` — ranking de bases não é idêntico ao de
`SPEC-013 §6.3` (etapa média), esperado: volume de *rotação* (pousos +
decolagens de uma base) não é a mesma coisa que volume de *etapas*
originadas ali.

### 6.4 GOL x Azul — corte de truncagem único, `CORTE_HORAS=3h`, aplicado a todos os 12 gráficos

Histórico da decisão (pedido do autor, 2026-09-02): a primeira versão do
`versus_gol_azul.py` truncava em `72h` (teto de validade) só para os
gráficos que precisavam de eixo legível (`v04`/`v05`/`v08`). O violin por
modelo (`v05`) ficou achatado e ilegível nessa escala — a cauda até 72h
comprime visualmente a maior parte da massa de dado, que vive abaixo de
3h. Corrigido para `CORTE_HORAS=3h` só no `v05` a princípio; o autor então
decidiu **generalizar**: `CORTE_HORAS=3h` fixo para as duas empresas,
aplicado **uma vez** em `main()`, valendo para os 12 gráficos —
inclusive os que antes usavam a população inteira sem corte (`v01`,
`v03`, `v09`, `v10`, `v11`).

**Efeito registrado explicitamente no código para não ficar implícito**:
isso muda o que esses 5 gráficos representam — passam a excluir pernoite
e fim de semana da conta inteira (não só da visualização). Contagem
resultante: GOL 959.208 de 1.154.494 etapas (83,1%), Azul 1.268.313 de
1.536.241 (82,6%) — proporção de exclusão comparável entre as duas
companhias, não é um corte que penaliza uma mais que a outra.

Mesmos princípios de design de `SPEC-013`/`a4` aplicados: eixo
compartilhado quando a pergunta é "quem é maior" (`v01`, `v02`, `v05`-
`v07`, `v09`, `v10`, `v12`), escala de cor compartilhada em
hexbin/heatmap (`v03`, `v08`, `v11`), densidade em vez de contagem bruta
nos histogramas (`v04`) — Azul tem mais etapas que GOL mesmo pós-corte.

### 6.5 Achados de legibilidade (processo, não de dado)

Duas correções pedidas pelo autor durante a rodada GOL, replicadas
automaticamente para Azul por serem genéricas:

- **`dist_02` (violin por modelo)**: precisava de linha de referência de
  média **e** mediana em cada um dos 3 violinos — adicionado, junto com
  numeração (`dist_NN`) em todas as figuras geradas pelo script (antes
  sem numeração sequencial).
- **`ana_06` (tempo de solo médio mensal por base, várias séries na
  mesma família de cor)**: legenda adicional para identificar cada base
  pelo código ICAO — pedida pelo autor, depois movida para dentro da
  área do gráfico (canto superior direito) para economizar espaço, em
  vez de ocupar área externa ao eixo.

## 7. Critérios de sucesso (desta rodada)

- **C-01** — Os 5 scripts (2× `analise_`, 2× `distribuicao_`, 1×
  `versus_`) rodam sem erro. **Cumprido**: confirmado nesta auditoria
  (2026-09-03), reexecução limpa dos 5, mesmos números reportados em §6.
- **C-02** — Cada figura inspecionada visualmente antes de reportar
  achado. **Cumprido durante as rodadas originais** (sessão de trabalho
  anterior a este documento) — não re-verificado imagem a imagem nesta
  auditoria retroativa, só a execução dos scripts.

## 8. Premissas e dependências

- Depende de `fato_rotacao_aeronave_gol_azul` (`SPEC-012`, incluindo
  `fl_solo_valido`, `SPEC-012 §6.5`) já carregada e correta.
- Ambiente `gov-sermi-perf` (conda, `DEC-011 §2.2`) com `pandas`/`matplotlib`/`seaborn`.

## 9. Não-objetivos

- Não é objetivo investigar a causa dos 0,29% de `tempo_solo_horas`
  inválido — já é achado de `SPEC-012 §6.5`.
- Não é objetivo decompor o tempo de solo em taxi/portão/conexão — dado
  não permite esse nível de granularidade.

## 10. Próximos passos

- Nenhum pedido explicitamente pelo autor até o momento desta auditoria;
  linha de análise tratada como concluída na rodada atual.

## 11. Limitações conhecidas

- Corte `CORTE_HORAS=3h` no `versus_gol_azul.py` (§6.4) é decisão de
  legibilidade, não estatística — descarta ~17% das etapas de cada
  companhia (pernoite/fim de semana) dos 12 gráficos comparativos.
- Cerca de Tukey em `dist_01` classifica pernoite legítimo como outlier
  (§6.1) — não usar esse corte como critério de "detecção de anomalia"
  sem essa ressalva.

## 12. Critérios de revisão

Revisitar esta SPEC (nova entrada no Histórico) quando:

- Uma nova rodada desta linha de análise for pedida pelo autor.
- `fl_solo_valido` (`SPEC-012 §6.5`) mudar de critério.

## 13. Histórico

| Data | Evento |
|---|---|
| 2026-09-03 | SPEC-016 v1 produzida em status `proposto`, documento vivo, retroativa (achado de auditoria documental: a linha de análise de tempo de solo já estava concluída — GOL, Azul, comparação, 5 scripts, dezenas de figuras — sem nenhum SPEC registrando método ou achados). Cobre: forma da distribuição com cauda até o teto de validade de 72h (pernoite legítimo lido como outlier pela cerca de Tukey, não erro); autocorrelação diária maior na Azul (r=0,805) que na GOL (r=0,613); decisão de corte único `CORTE_HORAS=3h` aplicada aos 12 gráficos do `versus_gol_azul.py`, generalizada a partir de um corte pontual que só cobria 3 gráficos; duas correções de legibilidade (referência de média/mediana em violin plot, legenda de base movida para dentro da área do gráfico). Aguardando aprovação do autor. |
| 2026-09-03 | **v2 — correção de leitura, achado inalterado.** O coeficiente de §6.2 não muda; muda a interpretação registrada. A redação original ("Azul mais previsível dia-a-dia") confundia memória com estabilidade e ignorava que `r` é normalizado pela variância. Nota de correção adicionada a §6.2, remetendo à `SPEC-017`, que separa amplitude/periodicidade/memória, converte `r` em meia-vida de distúrbio e tamanho de amostra efetivo, e nomeia três fatores de confusão mecânicos ainda não descartados. Origem: discussão durante a redação do relatório IMRaD do deep dive. |
| 2026-09-04 | **v3 — nota de procedência, achado inalterado.** Coeficientes de §6.2 inalterados; declarada a série de que vêm (truncada pela cerca de Tukey por companhia, `dist_14`) e registrado que o comparativo `v12` dá 0,674/0,861 sobre corte fixo de 3,0h. Não há erro de cálculo em nenhum dos dois: são cortes diferentes, e a v2 não dizia qual originava seus números. Origem: revisão do relatório IMRaD do deep dive, onde o texto citava um par e a figura inserida logo abaixo estampava o outro. Ver `SPEC-017 §6.3` requisito 4 e §11. |
| 2026-09-04 | **v4 — codificação de aeroportos trocada de ICAO para IATA, achados inalterados.** Pedido do autor: as figuras rotulavam bases pelo ICAO de 4 letras (`SBGR`, `SBSP`), que é o que a Básica carrega, enquanto a audiência da análise lê IATA de 3 letras (`GRU`, `CGH`). Módulo novo `analise/iata_bases.py` traduz no ponto de carga contra `dim_airport_location_time_zone` e **preserva a coluna ICAO ao lado** (rastro de auditoria); os scripts passaram a plotar `sg_iata_origem`/`sg_iata_destino`, o SQL continua lendo as colunas ICAO da fonte. 94 figuras de `a3_tempo_de_solo` regeradas. Nenhum número, corte, agrupamento ou conclusão mudou — troca de rótulo apenas. Corpo deste documento convertido; **linhas anteriores do Histórico preservadas em ICAO** (registram o que se escreveu na data). Dois achados de qualidade no de-para, ambos com fallback para o próprio ICAO: `base_iata` traz a sentinela `'N/I'` para `SBFE`/`SDIY`/`SNJD` (sem tratamento, os três colapsariam num balde único, e `SDIY` tem 317 etapas), e 3 aeródromos não têm IATA (`SBUY` 676 etapas, `LPAR` 2, `SBYS` 1). |
| 2026-10-14 | **v5, correção de instrução, achados inalterados.** Instrução de ambiente trocada de `pesquisa-azul`, ambiente de outro projeto, para `gov-sermi-perf`, o declarado na `DEC-011 §2.2` (2 ocorrência(s)). Dívida M4 do `AUDIT-002`. Status mantido em `proposto`; nenhum método, achado ou critério muda. |

---

*Fim do documento.*
