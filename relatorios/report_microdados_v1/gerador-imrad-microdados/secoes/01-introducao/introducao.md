<!--
ORIENTAÇÃO — Introdução (Contexto e Pergunta)
Guia metodológico, seção 2: o que motivou a análise, o que está em jogo, e a
pergunta central formulada de forma verificável pelos dados.
-->

## Contexto

Este documento consolida um deep dive exploratório sobre a operação da GOL a partir dos microdados públicos da ANAC, na janela de janeiro de 2021 até o dado mais recente disponível em 2026. A Azul entra como contraponto, não como objeto próprio de análise: serve para dizer se um padrão observado na GOL é característico dela ou apenas o comportamento comum do mercado doméstico brasileiro.

A análise nasceu em duas frentes que este relatório junta pela primeira vez. A primeira, manual, cobriu malha de destinos e composição de frota. A segunda, reprodutível em SQLite e Python, cobriu tempo de solo, etapa média e block time, cada uma com método e achados registrados em documento próprio no projeto de microdados. As duas frentes usam a mesma fonte e a mesma janela, mas não usam exatamente o mesmo critério de limpeza, e essa diferença está declarada nos Métodos.

Não há evento disparador externo, pedido de área operacional ou incidente a explicar. O que está em jogo é de outra natureza: entender, com dado público, o modelo de operação de uma companhia, e verificar se cinco perguntas independentes contam a mesma história sobre ele ou histórias diferentes.

**Status: exploratório.** Nenhuma hipótese foi submetida a teste estatístico formal. O documento separa achado confirmado de hipótese candidata, e não trata a segunda categoria como conclusão.

## Pergunta central

A operação da GOL, lida por cinco indicadores independentes (destinos, frota, tempo de solo, etapa média e block time), é consistente com um modelo de gestão orientado à homogeneidade e à reprodutibilidade, e, se for, onde esse modelo deixa de se sustentar?

A pergunta é verificável no seguinte sentido: homogeneidade implica baixa dispersão e estabilidade temporal dos indicadores, tanto entre modelos de aeronave quanto entre períodos. Os dados podem refutá-la mostrando dispersão alta, ausência de ciclos regulares ou quebras de nível não explicadas. A segunda metade da pergunta assume que nenhum modelo operacional é homogêneo em todas as dimensões, e procura deliberadamente pelo ponto de quebra, em vez de procurar confirmação.
