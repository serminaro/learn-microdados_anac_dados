<!--
ORIENTAÇÃO — Discussão (Interpretação)
Guia metodológico, seção 2: o que os achados significam, alternativas com
trade-offs explícitos, incertezas que afetam a confiança. A recomendação em si
tem seção própria; aqui fica o raciocínio que a sustenta.
-->

## Interpretação

Cinco indicadores independentes, calculados a partir de fontes e métodos parcialmente distintos, convergem para a mesma leitura: **a operação da GOL é organizada em torno da homogeneidade e da reprodutibilidade.** A convergência é o que dá força ao argumento, mais do que qualquer um dos indicadores isoladamente.

A malha é construída sobre uma semana típica e repetida, com ciclo dominante de 7 dias, amplitude de variação que cai de 30 destinos em 2021 para 7 em 2025, e dispersão da variação caindo de forma monotônica no mesmo período. A frota tem três modelos de um único fabricante, em transição gradual e planejada, sem entrada de família nova, com idade em serviço mediana em torno de 4 anos e distribuição homogênea entre os dois modelos principais. O tempo de solo tem mediana praticamente idêntica entre os três modelos. A etapa média mantém a ordenação entre modelos estável mês a mês, sem um único cruzamento em cinco anos e meio de série. A folga de block time também não se diferencia por equipamento.

O contraste com a Azul reforça a leitura em vez de apenas contextualizá-la. A Azul opera mais destinos, com ciclos mais difusos e amplitude de variação duas a quatro vezes maior. São dois desenhos de rede distintos, não duas execuções de qualidade diferente do mesmo desenho.

### Três propriedades que a palavra "previsível" confunde

O resultado de autocorrelação parece cortar contra tudo isso: a Azul tem autocorrelação diária maior que a GOL nos dois indicadores em que foi medida. Lida como "a Azul é mais previsível", a leitura contradiz o resto do documento. A contradição desaparece quando se separam três propriedades distintas que a série diária carrega:

| Propriedade | O que mede | Como se mede | O que a GOL mostra |
|---|---|---|---|
| Amplitude | Quanto o indicador varia em torno do seu nível | Desvio padrão da série diária | Baixa na malha: amplitude cai de 30 para 7 destinos entre 2021 e 2025, com dispersão caindo junto |
| Periodicidade | Quanto o indicador é previsível pelo calendário | Análise de frequência da série | Alta: ciclo de 7 dias dominante, contra distribuição difusa da Azul |
| Memória | Quanto o dia de hoje herda do dia anterior | Autocorrelação de defasagem 1 | Baixa: 0,613 no tempo de solo e 0,429 na etapa média |

A leitura de uma operação "ajustada" se apoia em amplitude e periodicidade. A autocorrelação mede memória. As três propriedades são independentes: uma série pode ter amplitude baixa e memória alta, amplitude alta e memória baixa, ou qualquer outra combinação.

Mais que isso, **memória baixa combinada com amplitude baixa é a assinatura de processo bem controlado com reversão rápida à média**: o sistema é deslocado, corrige, e por isso o dia anterior informa pouco sobre o seguinte. Memória alta é inércia, o desvio persiste. Sob essa leitura, a autocorrelação menor da GOL não contraria a homogeneidade observada; é compatível com ela, e possivelmente uma consequência dela.

A tradução operacional da autocorrelação é a meia-vida de um distúrbio, obtida por `ln(0,5) / ln(r)`, que responde quanto tempo um dia ruim contamina os seguintes:

| Indicador | Meia-vida GOL | Meia-vida Azul | Variância do dia herdada do anterior, GOL | Idem, Azul |
|---|---|---|---|---|
| Tempo de solo | 1,4 dia | 3,2 dias | 38% | 65% |
| Etapa média | 0,8 dia | 2,2 dias | 18% | 53% |

As quatro meia-vidas da tabela são conversões de coeficientes medidos sobre regimes de limpeza diferentes: a linha de tempo de solo vem da série truncada pela cerca de Tukey, a de etapa média vem da série sem corte. A comparação que a tabela sustenta é entre colunas, GOL contra Azul dentro de cada linha; a comparação entre linhas é indicativa, não métrica.

Um dia ruim de tempo de solo se dissipa em cerca de um dia e meio na GOL e em mais de três dias na Azul. Esse enquadramento não confirma que a GOL controla melhor: confirma que as duas companhias operam regimes de persistência diferentes, e que a diferença é grande o suficiente para ter consequência prática. As explicações concorrentes, inclusive as puramente mecânicas, estão em Incertezas.

### Onde a homogeneidade quebra

**O ponto de quebra é a base, não o equipamento.** Essa é a leitura mais consequente do documento. Tempo de solo, folga de block time e etapa média se diferenciam por base, e não por modelo de aeronave. E dentro do eixo de base há um sinal específico: os sete principais hubs aumentaram o tempo médio de solo entre 2025 e 2026, com aumentos de 1 a 7 minutos, acompanhados pela mediana em todos os casos. O acompanhamento pela mediana importa: significa deslocamento do corpo da distribuição, não alguns eventos extremos puxando a média.

Esse aumento não tem explicação nos dados disponíveis. Antes de ser lido como perda de eficiência, precisa ser investigado na origem, hub a hub, porque as causas candidatas têm consequências operacionais opostas. Um aumento de tempo de solo por congestionamento de infraestrutura é um custo imposto de fora. Um aumento por mudança deliberada de processo em solo, ou por absorção planejada de folga para proteger a pontualidade da etapa seguinte, é uma escolha, e a leitura correta seria a inversa. Vale registrar que a folga de block time ordena os hubs no mesmo sentido, ainda que com separação pequena entre eles, e que as duas companhias recuperam alguns minutos de atraso durante o voo, o que indica que existe margem sendo administrada no sistema. O dado disponível não distingue as duas explicações.

O enquadramento de memória oferece um caminho para distinguir sem sair do dado que já existe. Um hub onde o tempo de solo persiste de um dia para o outro é um hub sem folga para absorver distúrbio, que é o comportamento esperado de restrição de capacidade. Um hub que recupera no mesmo dia tem folga, e um aumento de nível ali é mais compatível com mudança deliberada de processo. **A autocorrelação calculada por base, e não para a companhia inteira, transforma a pergunta sobre os sete hubs em algo testável com os dados atuais.** Está na seção de Recomendações.

## Alternativas e trade-offs

A homogeneidade observada não é boa nem ruim em si. Ela troca uma coisa por outra, e a troca é explícita nos dados.

| Dimensão | Modelo homogêneo (GOL) | Modelo difuso (Azul) |
|---|---|---|
| Planejamento de manutenção | Favorecido: frota concentrada, três modelos, tempo de solo uniforme entre eles | Mais complexo: até sete modelos de frota |
| Gestão de malha | Processo reproduzível sobre semana típica | Exige decisão mais específica por rota |
| Resposta a mudança de mercado | Menos flexível: a malha repetida é mais cara de reconfigurar | Mais adaptável |
| Previsibilidade por calendário | Alta: ciclo de 7 dias dominante | Baixa: ciclos difusos |
| Persistência de um distúrbio | Curta: meia-vida de 1,4 dia no tempo de solo | Longa: 3,2 dias |
| Alocação de frota por etapa | Ordenação estável entre modelos, sem cruzamento | Não avaliada com a mesma profundidade |

As duas últimas linhas são o núcleo da diferença. A GOL é previsível pelo calendário e esquece rápido; a Azul é previsível pela inércia e carrega o nível adiante. São dois tipos de previsibilidade, e cada um pede um regime de gestão diferente. Numa série de memória baixa, um dia fora da faixa é ruído, e reagir a ele aumenta a variabilidade em vez de reduzir. Numa série de memória alta, o dia ruim prevê o próximo, o alerta antecipado funciona e a intervenção tem alavancagem.

Sobre o que fazer com o sinal dos hubs, três caminhos, com custos diferentes:

1. **Investigar hub a hub agora**, antes do próximo ciclo de planejamento de malha. Custo: tempo de equipe operacional em uma investigação que pode terminar sem achado, já que o aumento pode ser ruído de ano parcial. Ganho: se houver causa real, ela é identificada antes de o próximo ciclo de malha ser construído sobre um pressuposto errado.
2. **Aguardar o fechamento de 2026** e reavaliar com ano completo. Custo: o próximo ciclo de planejamento é construído sem essa informação; se a causa for estrutural, perde-se um ano. Ganho: elimina o risco de investigar um artefato de janela parcial.
3. **Tratar como não acionável** e monitorar por indicador de rotina. Custo: assume que aumentos de 1 a 7 minutos em sete bases simultaneamente não têm significado operacional, o que é uma aposta, não uma conclusão do dado. Ganho: custo zero agora.

A escolha entre 1 e 2 depende de um dado que não está neste documento: quanto custa, em planejamento de malha e escala, construir o próximo ciclo sobre um pressuposto de tempo de solo que pode estar desatualizado. Quem tem esse número decide melhor que este relatório. O cálculo de autocorrelação por base, por ser barato e não depender de área operacional, cabe antes de qualquer um dos três.

## Incertezas

**A janela de 2026 é parcial.** Todos os valores de 2026 cobrem ano incompleto, e o achado central (aumento entre 2025 e 2026) depende disso. Uma parte do aumento pode ser composição sazonal: se os meses cobertos em 2026 pesarem mais nos períodos de maior tempo de solo, a comparação ano contra ano fica enviesada. O achado é sustentado pela simultaneidade em sete bases e pelo acompanhamento da mediana, não por um teste que controle sazonalidade.

**A diferença de autocorrelação tem três explicações mecânicas plausíveis, nenhuma testada.** Antes de ler qualquer conteúdo operacional nos valores de 0,613 contra 0,805, é preciso descartar:

1. **Atenuação por tamanho de amostra.** A média diária da GOL é calculada sobre menos etapas que a da Azul (aproximadamente 570 contra 760 por dia, na etapa média). Ruído amostral maior na média diária atenua a autocorrelação medida, por construção, sem que nada mude na operação. Teste: reamostrar a Azul para o número diário de etapas da GOL e recalcular.
2. **O mix de frota injeta memória.** A Azul opera até sete modelos contra três Boeings quase idênticos da GOL. Se a composição diária da frota varia lentamente e os modelos têm tempos de solo distintos, o próprio mix cria autocorrelação sem conteúdo operacional. A homogeneidade de frota da GOL remove essa fonte por construção, o que significa que parte da diferença pode ser consequência da homogeneidade, e não evidência contra ela. Teste: aplicar a decomposição entre efeito de mix e efeito intramodelo, já implementada na linha de análise, e recalcular a autocorrelação sobre o componente intramodelo.
3. **Sazonalidade semanal contamina a defasagem 1.** Tempo de solo tem estrutura de dia da semana, e a GOL tem ciclo de 7 dias dominante, medido na análise de destinos. A autocorrelação de defasagem 1 isolada, sobre série com sazonalidade, não é interpretável sem a função de autocorrelação completa. Teste: calcular as defasagens de 1 a 14, ou remover o efeito de dia da semana e recalcular sobre o resíduo.

**A autocorrelação é uma medida normalizada, e o desvio padrão das séries diárias não foi medido.** A autocorrelação mede a fração da variação que persiste, não a quantidade de instabilidade. Sem o desvio padrão das duas séries, não é possível afirmar qual companhia é mais estável. Três desfechos possíveis, com leituras opostas: desvio padrão menor na GOL junto com autocorrelação menor indica controle apertado com reversão rápida, e confirma a leitura deste documento; desvio padrão semelhante indica que a GOL é mais ruidosa dia a dia sem memória, e a contraria; desvio padrão maior na GOL indicaria que a homogeneidade observada é do plano, não da execução.

**Qualquer teste de significância sobre estas séries precisa corrigir o tamanho de amostra.** Com autocorrelação, o número de observações independentes é aproximadamente `n(1 - r)/(1 + r)`. Um ano de observação diária de tempo de solo vale cerca de 88 dias independentes na GOL e 39 na Azul; na etapa média, 146 e 57. Tratar 365 dias como 365 observações independentes superestima a confiança em cerca de quatro vezes. Isso atinge diretamente qualquer verificação futura do achado dos sete hubs.

**Duas frentes com critérios de limpeza diferentes.** Destinos e frota vêm da frente manual; tempo de solo, etapa média e block time, da reprodutível. Os números de tempo de solo do corpo da Tabela 3 e os das figuras de comparação com a Azul não vêm do mesmo pipeline nem do mesmo corte de outlier. Isso não invalida nenhuma das duas leituras, mas impede somar ou comparar diretamente valores entre elas.

**Hub é uma classificação construída aqui.** A regra de 80% acumulado é convenção deste trabalho, não designação operacional da companhia. Bases na fronteira mudam de lado conforme a janela, e a própria composição da lista já divergiu entre as duas frentes (15 bases contra 16, com inversão das duas primeiras posições).

**Nenhuma hipótese candidata foi testada.** As oito hipóteses listadas nos Resultados têm evidência sugestiva e nada além disso. A leitura de que a homogeneidade é escolha estratégica, em particular, não é distinguível, com este dado, de uma restrição estrutural que produza o mesmo padrão observável.

**Uma hipótese foi refutada, e isso muda a leitura de uma limitação.** O salto no viés de pareamento com o VRA a partir de janeiro de 2024 foi inicialmente atribuído a evento específico da GOL, coincidente com o início da recuperação judicial da companhia. O mesmo salto, no mesmo mês, aparece na Azul, o que enfraquece a explicação. A explicação alternativa, mudança de processo do lado da fonte VRA, é mais consistente com a evidência e continua não verificada. Enquanto isso não se resolver, os achados de block time carregam uma incerteza de cobertura que os demais não têm.

**A Azul não tem cobertura simétrica.** Ela entra completa em tempo de solo, etapa média e block time, parcialmente em destinos e não entra em frota. Qualquer afirmação comparativa sobre frota, neste documento, é sobre a GOL isoladamente.
