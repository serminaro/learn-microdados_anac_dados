<!--
ORIENTAÇÃO — Recomendações
O "o quê fazer", apoiado no raciocínio da Discussão. Se a análise concluir
"depende", registrar a decisão pendente e o critério de escolha em vez de
forçar uma recomendação (guia-metodologico.md, seção 5).
-->

Este é um documento exploratório e nenhuma das recomendações abaixo é uma decisão operacional pronta. Três são pedidos de análise ou investigação; a última é uma decisão pendente com o critério de escolha explicitado. Estão em ordem de custo crescente, e a primeira deve preceder as demais.

### Recomendação 1: calcular a autocorrelação do tempo de solo por base, não só por companhia

Repetir o cálculo de autocorrelação de defasagem 1 separadamente para cada uma das bases hub, em vez de uma única vez para a companhia inteira. Custo: uma rodada dos scripts que já existem, sem dado novo e sem envolver área operacional.

O valor está em transformar a hipótese candidata 7 dos Resultados em algo testável. Um hub onde o tempo de solo persiste de um dia para o outro é um hub sem folga para absorver distúrbio, comportamento esperado de restrição de capacidade. Um hub que recupera no mesmo dia tem folga, e um aumento de nível ali é mais compatível com mudança deliberada de processo. Aplicado às sete bases que subiram entre 2025 e 2026, o cálculo separa as duas causas candidatas antes de qualquer investigação de campo.

Três cuidados, todos derivados das incertezas da Discussão:

1. Reportar o desvio padrão da série diária junto com a autocorrelação. O segundo número não é interpretável sozinho.
2. Calcular as defasagens de 1 a 14, não só a de 1. Com ciclo semanal presente, a defasagem 1 isolada é ambígua.
3. Normalizar pelo número de etapas por dia de cada base, ou reportá-lo. Bases pequenas terão autocorrelação atenuada por ruído amostral, e a comparação entre bases de porte diferente herda esse viés.
4. **Fixar o corte de outlier antes de rodar, e o mesmo para todas as bases.** O coeficiente medido depende do corte: sobre a cerca de Tukey a autocorrelação de tempo de solo da GOL é 0,613, e sobre corte fixo de 3,0 horas é 0,674, o que move a meia-vida do distúrbio de 1,4 para 1,8 dia, quase 30%. Bases medidas com cortes diferentes não se comparam, e um ranking construído assim ordena o critério de limpeza em vez de ordenar a operação.

O produto é um ranking dos hubs por meia-vida de distúrbio, que hoje não existe nem neste documento nem na linha de análise, e que é um indicador de fragilidade operacional da base comparável entre companhias e ao longo do tempo.

### Recomendação 2: investigar o aumento de tempo de solo nos sete principais hubs

Abrir investigação operacional nas sete bases que registraram aumento simultâneo do tempo médio de solo entre 2025 e 2026 (Congonhas, Guarulhos, Galeão, Brasília, Salvador, Santos Dumont e Confins), com o objetivo de distinguir entre três causas candidatas: restrição de infraestrutura, congestionamento, ou mudança deliberada de processo em solo.

A distinção importa porque as três têm consequência oposta. Custo imposto de fora e escolha de planejamento se parecem no indicador e se comportam de forma diferente na decisão.

Antes de abrir a investigação, dois passos baratos reduzem o risco de perseguir artefato. O primeiro é a Recomendação 1. O segundo é **refazer a comparação 2025 contra 2026 controlando composição sazonal**, comparando os mesmos meses dos dois anos em vez do ano inteiro, e corrigindo o tamanho de amostra pela autocorrelação medida. Nenhum dos dois depende de área operacional.

### Recomendação 3: unificar o critério de limpeza entre as duas frentes de análise

Destinos e frota foram construídos com tratamento manual; tempo de solo, etapa média e block time, com pipeline reprodutível e regra de validade aplicada no banco. As duas frentes já divergiram de forma mensurável na classificação de bases hub (15 bases contra 16, com inversão das duas primeiras posições).

Recomenda-se reconstruir destinos e frota sobre a mesma camada curada usada pelas demais perguntas. O ganho não é de precisão numérica, é de comparabilidade: hoje não se pode cruzar diretamente um achado de malha com um achado de tempo de solo sem ressalva de método.

### Decisão pendente: quando agir sobre o sinal dos hubs

Esta não é uma recomendação, é uma decisão que o documento não tem elementos para tomar. A escolha é entre investigar agora, antes do próximo ciclo de planejamento de malha, ou aguardar o fechamento de 2026 e reavaliar com ano completo.

**Critério de escolha:** investigar agora se o custo de reconstruir o próximo ciclo de malha sobre um pressuposto de tempo de solo desatualizado for maior que o custo de uma investigação operacional que pode terminar sem achado. Quem tem o primeiro número decide; este relatório não tem.

O resultado da Recomendação 1 deve entrar nessa decisão: se as sete bases mostrarem persistência alta, o sinal ganha peso e a espera fica mais cara; se mostrarem recuperação rápida, o aumento de nível é mais compatível com mudança de processo e a urgência cai.
