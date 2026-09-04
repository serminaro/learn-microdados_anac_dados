<!--
ORIENTAÇÃO (comentário — nunca aparece no .docx gerado)
Abstract acadêmico: um parágrafo denso e direto (tipicamente 100-200 palavras),
sem subtítulos. Objetivo → método (1 frase) → resultado principal → conclusão.
Escrito por último, depois de fechar Discussão e Conclusão.

Isto NÃO é a Pirâmide de Minto (Situação/Recomendação/Porquês/Pedido de ação):
essa versão, voltada a decisor, fica no gerador_mintos e responde as mesmas
perguntas em outra densidade.
-->

Este documento investiga se a operação da GOL, lida por cinco indicadores independentes (destinos, frota, tempo de solo, etapa média e block time), é consistente com um modelo de gestão orientado à homogeneidade, e onde essa leitura deixa de se sustentar. Foram usados microdados públicos da ANAC (bases Básica e VRA) entre janeiro de 2021 e julho de 2026, com a Azul como contraponto, combinando uma análise manual de malha e frota com uma linha de análise reprodutível em SQLite e Python para os três indicadores operacionais. Os cinco indicadores convergem: malha construída sobre semana típica com amplitude de variação caindo de 30 para 7 destinos entre 2021 e 2025, frota de três modelos em transição ordenada, e tempo de solo, etapa média e folga de block time que não se diferenciam por modelo de aeronave. A homogeneidade quebra no eixo da base: os sete principais hubs aumentaram o tempo médio de solo entre 2025 e 2026, sem explicação nos dados disponíveis. A autocorrelação diária, maior na Azul nos dois indicadores em que foi medida, não contradiz essa leitura: ela mede memória, não amplitude, e um distúrbio de tempo de solo tem meia-vida de 1,4 dia na GOL contra 3,2 dias na Azul. Recomenda-se calcular a autocorrelação por base antes de qualquer investigação de campo, porque persistência alta em um hub é assinatura de restrição de capacidade e persistência baixa não é.
