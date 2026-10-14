---
documento: SPEC-017
titulo: Autocorrelação como Indicador Operacional — GOL/Azul (memória, amplitude e periodicidade)
versao: v4
status: proposto
data: 2026-09-04
autor: Bruno Alexandre Serminaro
referencia: DEC-007, SPEC-013, SPEC-015, SPEC-016
escopo: projeto
---

# SPEC-017 · Autocorrelação como Indicador Operacional — GOL/Azul

> Documento **vivo**, de natureza diferente das SPECs irmãs desta linha: não
> reporta medição nova. Ele **relê** um achado já registrado em `SPEC-013 §6.8`
> e `SPEC-016 §6.2` (autocorrelação diária maior na Azul que na GOL), que na
> forma em que estava registrado parecia contradizer a leitura de operação
> homogênea sustentada pelo resto da análise, e **especifica o que precisa ser
> medido** para que o número seja interpretável. Origem: discussão durante a
> redação do relatório IMRaD do deep dive
> (`learn-imrad-mintos/gerador-imrad-microdados`), 2026-09-03. Cresce por
> rodada; cada rodada nova vira entrada no Histórico (§13).

---

## 1. Propósito

Três objetivos, em ordem de dependência:

1. **Desfazer uma ambiguidade conceitual** que atravessa `SPEC-013` e
   `SPEC-016`: a autocorrelação de defasagem 1 foi registrada como se medisse
   previsibilidade ou estabilidade, quando mede **memória** (persistência), que
   é propriedade independente de **amplitude** (dispersão) e de
   **periodicidade** (estrutura de calendário).
2. **Listar os fatores de confusão mecânicos** que podem produzir a diferença
   observada entre as duas companhias sem nenhum conteúdo operacional, e
   especificar o teste de cada um.
3. **Converter a autocorrelação em instrumento de decisão operacional**,
   incluindo o cálculo por base como forma de testar a hipótese candidata sobre
   o aumento de tempo de solo nos sete principais hubs da GOL entre 2025 e
   2026, sem depender de investigação de campo.

## 2. Audiência

Reaproveita os papéis abstratos do `SPEC-002 §2` — nenhum papel novo.

## 3. Escopo

### 3.1 O que motiva esta SPEC

`SPEC-016 §6.2` registra autocorrelação diária (lag 1) de **0,613 na GOL** e
**0,805 na Azul** para `tempo_solo_horas`. `SPEC-013 §6.8` registra **0,429 na
GOL** e **0,731 na Azul** para `nr_horas_voadas`. Os dois documentos registram
o número corretamente e nomeiam a Azul como "mais previsível dia a dia".

O problema não é o número, é a palavra. "Previsível" sugere que a série da GOL
é mais instável, o que colide com todo o restante da análise (malha de ciclo
semanal dominante, amplitude de destinos caindo de 30 para 7 entre 2021 e 2025,
medianas de tempo de solo uniformes entre os três modelos, ordenação de frota
que nunca se cruza em 5 anos e meio). Duas leituras opostas do mesmo conjunto de
dados é sinal de conceito mal separado, não de dado contraditório.

### 3.2 O que este SPEC entrega

1. A separação formal entre amplitude, periodicidade e memória (§5).
2. As transformações que tornam a autocorrelação legível para decisão: meia-vida
   de distúrbio e tamanho de amostra efetivo (§5.2).
3. Os três fatores de confusão mecânicos, com teste especificado para cada um
   (§6.2).
4. A especificação do cálculo de autocorrelação **por base**, produto novo desta
   linha de análise (§6.3).
5. Extensões de pesquisa não previstas no desenho original, em anexo (§Anexo A).

### 3.3 Fora de escopo (nesta rodada)

- Executar os cálculos. Esta rodada especifica; a próxima mede.
- Modelagem estrutural (ARIMA, espaço de estados) das séries. O escopo aqui é o
  coeficiente de autocorrelação e suas transformações diretas.
- Qualquer afirmação sobre causa operacional das diferenças entre companhias
  antes de os três fatores de confusão do §6.2 serem descartados.

## 4. Fonte e método

```
fato_rotacao_aeronave_gol_azul (SPEC-012, WHERE fl_solo_valido = 1)
basica_curated_deep            (etapa media, filtro PASSAGEIRO, SPEC-013)
fato_block_time_gol_azul       (SPEC-014, para as extensoes do Anexo A)
  -> analise/a3_tempo_de_solo/*.py   (lag plot ja existente: dist_14, v12)
  -> analise/a4_etapa_media/*.py     (lag plot ja existente: dist_14, v12)
```

Nenhuma fonte nova. Todo o material desta SPEC sai de séries que os scripts
atuais já constroem; o que muda é o que se calcula sobre elas e como se lê o
resultado.

## 5. Variáveis e definições

### 5.1 As três propriedades que estavam sendo confundidas

| Propriedade | Definição | Estatística | Pergunta que responde |
|---|---|---|---|
| Amplitude | Dispersão da série diária em torno do seu nível | `σ` (desvio padrão da média diária) | Quanto o indicador varia? |
| Periodicidade | Estrutura de repetição por calendário | Análise de frequência, ACF em lags 7 e 14 | O indicador é previsível pelo dia da semana? |
| Memória | Fração da variação que persiste de um dia para o seguinte | `r` (autocorrelação lag 1) | O dia de ontem informa sobre hoje? |

São independentes: qualquer combinação é possível. **Amplitude baixa com memória
baixa é a assinatura de processo controlado com reversão rápida à média** (o
sistema é deslocado, corrige, e por isso ontem informa pouco). Amplitude baixa
com memória alta é processo estável e inercial. Amplitude alta com memória baixa
é processo errático.

Registro explícito, para não repetir o erro: `r` é **normalizado pela
variância**. Ele mede a *fração* da variação que persiste, nunca a *quantidade*
de instabilidade. Comparar `r` entre duas companhias sem comparar `σ` não
responde qual das duas é mais estável.

### 5.2 Transformações que tornam `r` legível para decisão

| Grandeza | Fórmula | Leitura |
|---|---|---|
| Meia-vida do distúrbio | `h = ln(0,5) / ln(r)` | Em quantos dias metade de um desvio se dissipa |
| Variância herdada | `r²` | Fração da variação de hoje explicada por ontem |
| Choque diário relativo | `√(1 − r²)` | Fração da variação que é novidade do dia |
| Tamanho de amostra efetivo | `n_ef ≈ n (1 − r) / (1 + r)` | Quantas observações independentes há, de fato, em `n` dias |

Aplicadas aos valores já registrados em `SPEC-013 §6.8` e `SPEC-016 §6.2`:

| Série | `r` | Meia-vida | Variância herdada | `n_ef` em 365 dias |
|---|---|---|---|---|
| Tempo de solo, GOL | 0,613 | 1,4 dia | 38% | 88 |
| Tempo de solo, Azul | 0,805 | 3,2 dias | 65% | 39 |
| Etapa média, GOL | 0,429 | 0,8 dia | 18% | 146 |
| Etapa média, Azul | 0,731 | 2,2 dias | 53% | 57 |

A última coluna é a de consequência prática mais imediata: **um ano de
observação diária de tempo de solo da GOL vale cerca de 88 observações
independentes, não 365**. Qualquer teste de significância sobre estas séries que
use `n` nominal superestima a confiança em torno de quatro vezes.

## 6. Achados e especificação

### 6.1 Releitura do achado já registrado (não é medição nova)

Com a separação do §5.1, o achado de `SPEC-013 §6.8` e `SPEC-016 §6.2` deixa de
contradizer o restante da análise e passa a dizer outra coisa:

- A **GOL é previsível pelo calendário** (ciclo semanal dominante, amplitude
  baixa) e **esquece rápido** (meia-vida de 1,4 dia no tempo de solo).
- A **Azul é previsível pela inércia** (carrega o nível do dia anterior adiante,
  meia-vida de 3,2 dias) com amplitude de malha bem maior.

São dois tipos de previsibilidade, não graus da mesma. E pedem regimes de gestão
diferentes: numa série de memória baixa, um dia fora da faixa é ruído, e reagir a
ele aumenta a variabilidade em vez de reduzir (sobrecontrole); numa série de
memória alta, o dia ruim prevê o próximo, alerta antecipado funciona e a
intervenção tem alavancagem.

**Nada disso é ainda um achado sobre a operação**, porque os três fatores de
confusão abaixo não foram descartados.

### 6.2 Três fatores de confusão mecânicos, com teste especificado

| # | Fator | Por que produziria o resultado sem conteúdo operacional | Teste |
|---|---|---|---|
| C-1 | **Atenuação por tamanho de amostra** | A média diária da GOL é calculada sobre menos etapas (~570/dia contra ~760/dia na etapa média). Ruído amostral maior na média diária atenua `r` por construção | Reamostrar a Azul para o `n` diário da GOL e recalcular `r`; ou estimar a componente de variância intradiária e corrigir a atenuação |
| C-2 | **Mix de frota injeta memória** | A Azul opera até 7 modelos contra 3 Boeings quase idênticos da GOL. Mix que varia lentamente, com tempos de solo distintos por modelo, cria autocorrelação sem conteúdo operacional | Reaproveitar a decomposição mix × intramodelo já implementada (`dist_16`) e recalcular `r` **sobre o componente intramodelo** |
| C-3 | **Sazonalidade semanal contamina o lag 1** | Tempo de solo tem estrutura de dia da semana, e a GOL tem ciclo de 7 dias dominante (achado da análise de destinos). Lag 1 isolado sobre série sazonal não é interpretável | Calcular a ACF completa (lags 1 a 14) e/ou remover o efeito de dia da semana e recalcular `r` sobre o resíduo |

**C-2 é o mais interessante dos três** e inverte a leitura ingênua: a
homogeneidade de frota da GOL **remove por construção** uma fonte de
autocorrelação que a Azul tem. Se C-2 explicar a maior parte da diferença, o `r`
mais baixo da GOL passa a ser *consequência* da homogeneidade observada, não
evidência contra ela.

Registro de honestidade: C-1, C-2 e C-3 afetariam **os dois** indicadores (tempo
de solo e etapa média) na mesma direção. O fato de os dois ordenarem as
companhias igualmente, portanto, confirma que a propriedade é consistente entre
séries, mas **não** distingue causa operacional de causa mecânica.

### 6.3 Produto novo: autocorrelação por base

Todo o cálculo atual é feito para a companhia inteira. Calculado **por base
hub**, o mesmo coeficiente vira um instrumento de diagnóstico:

- Base com **persistência alta**: o tempo de solo de hoje herda o de ontem. Não
  há folga para absorver distúrbio. Assinatura esperada de **restrição de
  capacidade**.
- Base com **persistência baixa**: recupera dentro do mesmo dia. Há folga. Um
  aumento de nível ali é mais compatível com **mudança deliberada de processo**.

Aplicado às sete bases da GOL que registraram aumento de tempo médio de solo
entre 2025 e 2026 (`CGH`, `GRU`, `GIG`, `BSB`, `SSA`, `SDU`, `CNF`), isso
separa duas causas candidatas **sem investigação de campo e sem dado novo**.

Requisitos do cálculo, derivados de §5.1 e §6.2:

1. Reportar `σ` da série diária **junto** com `r`. O segundo não é interpretável
   sozinho.
2. Calcular lags de 1 a 14, não só o lag 1.
3. Reportar o número de etapas por dia de cada base, ou normalizar por ele.
   Bases pequenas terão `r` atenuado por C-1, e a comparação entre bases de
   porte diferente herda esse viés.
4. **Fixar o corte de outlier antes de rodar, declará-lo no produto, e usar o
   mesmo para todas as bases.** `r` depende do corte aplicado à série, e a
   dependência não é desprezível: para o tempo de solo da GOL, a cerca de Tukey
   de `distribuicao_tempo_solo_gol.py` (dist_14) dá `r = 0,613`, e o corte fixo
   de `CORTE_HORAS = 3,0h` de `versus_gol_azul.py` (v12) dá `r = 0,674` sobre a
   mesma série; na Azul, 0,805 contra 0,861. Em meia-vida isso move a GOL de
   1,4 para 1,8 dia, quase 30%. O corte mais apertado eleva `r` nas duas
   companhias e preserva a ordenação entre elas, mas um ranking de bases
   construído com cortes diferentes ordena o critério de limpeza em vez de
   ordenar a operação. Consequência prática: como a cerca de Tukey é calculada
   por companhia (3,542h na GOL, 3,767h na Azul), usá-la por base introduziria
   um corte diferente em cada base; a rodada 2 deve adotar corte único
   declarado, e reportar a sensibilidade de `r` a ele em pelo menos duas
   escolhas de corte. Vale para as duas linhas, e com uma assimetria a
   corrigir: a série diária de **etapa média** (`SPEC-013 §6.8`) é construída
   **sem corte** algum, enquanto a de **tempo de solo** (`SPEC-016 §6.2`) já
   chega truncada. Os quatro coeficientes reaproveitados no §5.2 vêm, portanto,
   de três regimes de limpeza: Tukey por companhia, corte fixo de 3,0h e
   nenhum corte. A rodada 2 deve unificar isso antes de comparar qualquer
   coisa.
5. Produto final: ranking dos hubs por meia-vida de distúrbio, comparável entre
   companhias e ao longo do tempo. Indicador de fragilidade operacional de base
   que hoje não existe neste projeto.

## 7. Critérios de sucesso (desta rodada)

- **C-01** — As três propriedades do §5.1 ficam registradas de forma que
  `SPEC-013` e `SPEC-016` possam ser citadas sem reproduzir a ambiguidade.
  **Cumprido** por este documento.
- **C-02** — Cada fator de confusão do §6.2 tem um teste executável descrito com
  a fonte de dado que já existe. **Cumprido**; execução fica para a rodada 2.
- **C-03** *(rodada 2, pendente)* — `r`, `σ` e ACF(1..14) calculados por base
  hub para GOL e Azul, com contagem diária de etapas reportada, corte de outlier
  único e declarado (§6.3, requisito 4), e a sensibilidade de `r` ao corte
  medida em pelo menos duas escolhas.
- **C-04** *(rodada 2, pendente)* — Veredito sobre C-1, C-2 e C-3: quanto da
  diferença entre companhias sobrevive depois de controlar cada um.

## 8. Premissas e dependências

- Depende das séries diárias já construídas por `SPEC-013` e `SPEC-016`, e das
  regras de validade e corte que elas fixam (`fl_solo_valido`, filtro
  `PASSAGEIRO`, cortes de exibição).
- Assume que a autocorrelação de lag 1 sobre média diária é estimada com
  janela completa e série contínua. Lacunas de calendário (dias sem operação em
  uma base pequena) quebram essa premissa e precisam de tratamento explícito no
  cálculo por base.
- Ambiente `pesquisa-azul` (conda), mesma premissa do `SPEC-002 §6`.

## 9. Não-objetivos

- Não é objetivo modelar a série (ARIMA, espaço de estados). O escopo é o
  coeficiente e suas transformações diretas.
- Não é objetivo concluir qual companhia opera melhor. As duas propriedades
  medidas (previsibilidade por calendário e por inércia) não são ordenáveis numa
  escala única de qualidade.
- Não é objetivo substituir a investigação operacional nos hubs, e sim reduzir o
  espaço de causas antes dela.

## 10. Próximos passos

1. Rodada 2: executar §6.3 (autocorrelação por base) e os três testes de §6.2.
2. Atualizar `SPEC-013 §6.8` e `SPEC-016 §6.2` com referência cruzada a esta
   SPEC, para que o número não volte a ser lido como medida de estabilidade.
3. Avaliar quais itens do Anexo A entram numa rodada 3.

## 11. Limitações conhecidas

- Esta SPEC **não mede nada**. Todo o conteúdo quantitativo é transformação
  determinística de dois pares de coeficientes já registrados. Se esses
  coeficientes tiverem erro de cálculo na origem, todo o §5.2 herda o erro.
- As transformações do §5.2 assumem processo AR(1). Se a série tiver memória
  mais longa ou sazonalidade forte não removida, a meia-vida calculada
  subestima a persistência real, e `n_ef` fica otimista.
- O `n_ef` do §5.2 é aproximação de primeira ordem, válida para AR(1) e para
  inferência sobre a média. Não vale, sem ajuste, para inferência sobre
  variância ou sobre quantis.
- Os coeficientes reaproveitados aqui vêm de regimes de limpeza diferentes:
  tempo de solo, da série truncada pela cerca de Tukey de cada companhia;
  etapa média, da série sem corte nenhum (`SPEC-013 §6.8`, nota de procedência
  da v11). A comparação entre os dois indicadores no §5.2 herda essa
  assimetria: a ordenação entre companhias se repete nas duas linhas, o que
  sustenta a leitura de propriedade consistente das séries, mas a diferença de
  magnitude entre tempo de solo e etapa média não é atribuível só ao
  indicador.
- A mesma série de tempo de solo sob corte fixo de 3,0h dá valores mais altos
  (§6.3, requisito 4), e todo o §5.2 se desloca junto: meia-vida, variância
  herdada e `n_ef` são função de `r`, e portanto do corte. Os números deste
  documento valem para o corte que os originou, não em geral.
- A leitura de "persistência alta implica restrição de capacidade" (§6.3) é
  **hipótese de trabalho**, plausível e não testada. É possível que uma base com
  processo muito padronizado também apresente persistência alta, por outro
  motivo.

## 12. Critérios de revisão

Revisitar esta SPEC (nova entrada no Histórico) quando:

- A rodada 2 for executada, com veredito sobre C-1, C-2 e C-3.
- Qualquer novo indicador diário entrar na linha de análise, já que a mesma
  separação amplitude/periodicidade/memória se aplica.
- Um terceiro operador entrar no projeto (ver Anexo A.9), que muda a
  identificação do que é efeito de companhia e o que é efeito de aeroporto.

## 13. Histórico

| Data | Evento |
|---|---|
| 2026-09-03 | SPEC-017 v1 produzida em status `proposto`, documento vivo. Origem: discussão durante a redação do relatório IMRaD do deep dive (`learn-imrad-mintos/gerador-imrad-microdados`), quando o achado de autocorrelação de `SPEC-013 §6.8`/`SPEC-016 §6.2` apareceu como aparente contradição da leitura de operação homogênea. Entrega: separação formal entre amplitude, periodicidade e memória; transformações de leitura (meia-vida, variância herdada, tamanho de amostra efetivo, com valores calculados para os quatro coeficientes já registrados); três fatores de confusão mecânicos com teste especificado; especificação da autocorrelação por base como diagnóstico de restrição de capacidade nos sete hubs da GOL; nove extensões de pesquisa em anexo. Nenhuma medição nova. Aguardando aprovação do autor. |
| 2026-09-04 | v2, status mantido em `proposto` (R-TAX-11): correção que não reverte decisão. Registrada a dependência de `r` ao corte de outlier, detectada durante a revisão do relatório IMRaD, onde o texto citava os coeficientes da série truncada pela cerca de Tukey (0,613 GOL / 0,805 Azul, `dist_14`) e a figura inserida logo abaixo trazia os da série truncada em `CORTE_HORAS = 3,0h` (0,674 / 0,861, `v12`). Não há erro de cálculo em nenhum dos dois: são cortes diferentes, e o documento anterior não declarava de qual série vinham seus números. Entra como requisito 4 do §6.3 (corte único declarado, mais sensibilidade medida), emenda a C-03 e nova limitação no §11. O IMRaD recebeu o reparo equivalente em Resultados, Métodos e Recomendação 1. |
| 2026-09-04 | v3, status mantido em `proposto` (R-TAX-11). Ao propagar a correção da v2 para `SPEC-016` (v3) e `SPEC-013` (v11), apareceu um terceiro regime: a série diária de etapa média não recebe corte de outlier nenhum, enquanto a de tempo de solo chega truncada. Os quatro coeficientes do §5.2 vêm, portanto, de três regimes de limpeza distintos. Registrado no §6.3 requisito 4 e no §11. Não altera nenhum número nem a leitura de que a ordenação entre companhias se repete nas duas linhas. |
| 2026-09-04 | **v4 — codificação de aeroportos trocada de ICAO para IATA, achados inalterados.** Pedido do autor: as figuras rotulavam bases pelo ICAO de 4 letras (`SBGR`, `SBSP`), que é o que a Básica carrega, enquanto a audiência da análise lê IATA de 3 letras (`GRU`, `CGH`). Módulo novo `analise/iata_bases.py` traduz no ponto de carga contra `dim_airport_location_time_zone` e **preserva a coluna ICAO ao lado** (rastro de auditoria); os scripts passaram a plotar `sg_iata_origem`/`sg_iata_destino`, o SQL continua lendo as colunas ICAO da fonte. As bases citadas em §7 passam a aparecer em IATA, coerentes com as figuras das SPECs irmãs. Nenhum número, corte, agrupamento ou conclusão mudou — troca de rótulo apenas. Corpo deste documento convertido; **linhas anteriores do Histórico preservadas em ICAO** (registram o que se escreveu na data). Dois achados de qualidade no de-para, ambos com fallback para o próprio ICAO: `base_iata` traz a sentinela `'N/I'` para `SBFE`/`SDIY`/`SNJD` (sem tratamento, os três colapsariam num balde único, e `SDIY` tem 317 etapas), e 3 aeródromos não têm IATA (`SBUY` 676 etapas, `LPAR` 2, `SBYS` 1). |

---

## Anexo A — Extensões de pesquisa não previstas no desenho original

Itens que a discussão desta SPEC abriu e que não estavam no escopo de
`DEC-007`. Nenhum é pré-requisito das rodadas planejadas; todos são baratos em
dado (a maior parte usa tabelas que já existem) e caros em tempo de análise.
Organizados por quanto mudam o objeto de estudo.

### Grupo 1 — Trocar o eixo de defasagem: da série diária para a rotação

**A.1 Propagação ao longo da rotação, não do calendário.** Toda a análise atual
mede memória entre *dias*. O objeto operacional real é a cadeia de rotação da
aeronave: atraso na chegada da etapa *n* → tempo de solo na etapa *n+1* → atraso
na partida da etapa *n+1*. Medir autocorrelação com defasagem definida pela
**próxima etapa da mesma matrícula**, e não pelo próximo dia, responde
diretamente "quanto de um distúrbio é absorvido no solo e quanto é repassado
adiante". `fato_rotacao_aeronave_gol_azul` e `fato_block_time_gol_azul` já têm
tudo que isso exige. Na minha leitura é o item de maior retorno do anexo: mede
recuperação onde a recuperação de fato acontece.

**A.2 Curva de absorção por posição na rotação do dia.** A primeira etapa do dia
parte de uma aeronave pernoitada, com folga estrutural; as últimas carregam o
acumulado. Calcular a capacidade de absorção por posição ordinal na rotação
diária separa **buffer de planejamento** (que decai ao longo do dia por desenho)
de **processo em solo** (que não deveria decair). Distinção que o agregado
diário apaga por completo.

**A.3 Correlação cruzada com defasagem entre indicadores.** Medir
`corr(folga_t, tempo_solo_{t+k})` e `corr(atraso_chegada_n, tempo_solo_{n+1})`.
Se a folga programada de hoje prevê o tempo de solo de amanhã, existe um
mecanismo de propagação identificável, e não só uma associação contemporânea.
Nenhuma das SPECs atuais olha defasagem entre variáveis diferentes.

### Grupo 2 — Estrutura fina da persistência

**A.4 Assimetria da persistência.** O coeficiente `r` assume que desvio para
cima e desvio para baixo persistem igual. Operacionalmente isso é improvável:
um dia de tempo de solo alto tende a puxar correção, um dia baixo não. Estimar
`r` condicional ao sinal do desvio (modelo autorregressivo com limiar).
**Assimetria positiva é assinatura de controle ativo**, e seria evidência
direta a favor da leitura de "operação ajustada" que hoje só se sustenta por
amplitude e periodicidade.

**A.5 Memória longa como assinatura de saturação.** Se a ACF decai mais devagar
que exponencial, o processo tem memória longa, comportamento típico de sistema
com fila próximo da capacidade. Estimar o parâmetro de integração fracionária
distinguiria "hub com nível alto" de "hub saturado", que é exatamente a pergunta
por trás do achado dos sete hubs, e que o lag 1 sozinho não alcança.

**A.6 Curva de `r` por escala de agregação.** `r` depende da janela: por etapa,
por dia, por semana, os valores diferem sem se contradizerem. Reportar a curva
inteira é mais informativo que um número, e conecta diretamente com o achado de
ciclo de 7 dias da análise de destinos, que prevê comportamento específico na
transição de escala diária para semanal.

### Grupo 3 — Identificação: separar o que é companhia do que é contexto

**A.7 Detecção de ponto de mudança em vez de comparação por ano civil.** A
comparação 2025 contra 2026 assume que se sabe onde procurar a quebra. Aplicar
detecção de changepoint sobre a série diária de cada hub encontra **quando** o
nível mudou, sem impor a fronteira do ano civil. Pode revelar que o movimento
começou em meados de 2025, ou que é gradual e não uma quebra, o que mudaria a
leitura do achado central do relatório.

**A.8 Decompor a autocovariância, não só a variância.** `dist_16` já decompõe o
**nível** entre efeito de mix e efeito intramodelo. O passo não dado é aplicar a
mesma decomposição à **autocovariância**, que é o que mede quanto do `r` da Azul
é frota e quanto é operação. Fecha o teste de C-2 de forma quantitativa, não só
por comparação de dois coeficientes.

**A.9 Terceiro operador como controle.** Com só GOL e Azul, qualquer diferença
confunde "propriedade da companhia" com "propriedade da rede que ela opera".
Um terceiro operador de porte comparável quebra o empate: se as três divergirem
no mesmo aeroporto, o efeito é de companhia; se convergirem, é do aeroporto.
Isso reabriria a alternativa 4.3 da `DEC-007` (parametrizar em vez de duplicar
objetos por empresa), hoje descartada por só haver duas.

---

*Fim do documento.*
