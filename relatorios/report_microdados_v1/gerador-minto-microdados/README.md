# Gerador Minto, microdados ANAC (.docx)

Gera o **comunicado de decisão** no formato Pirâmide de Minto, conforme `../../docs/GUIDE/GUIDE_005_Metodologia_IMRaD_e_Piramide_de_Minto.md`, seção 3. É a peça de decisão, par do relatório IMRaD (`../gerador-imrad-microdados`): mesma análise, mesmas figuras, densidade e ordem diferentes.

Regra central: **resposta primeiro**. A Recomendação vem antes dos Porquês, sempre. Se o leitor parar na Recomendação, ele já sabe o que precisa decidir.

Saída: `saida/deep_dive_gol_minto.docx`.

Esta instância substitui a estrutura indutiva de `gerador-analise-mintos` (cinco porquês, um por indicador), que fica preservada em `learn-imrad-mintos` para comparação. O que mudou, e por quê, está na seção "Estrutura do argumento" abaixo.

## A relação com o relatório

A peça deriva do relatório por **poda, não por resumo**. Poda é escolher a recomendação final e as razões mais fortes e descartar o resto; resumo é compactar tudo proporcionalmente. Nenhum achado pode aparecer aqui sem estar no IMRaD.

**O texto é autoconsistente**, e isso é uma divergência deliberada do guia metodológico. O guia (`GUIDE-005 §3`) pede que cada porquê aponte para uma seção do relatório, e é assim que ele fica auditável. Aqui não aponta: cada porquê carrega dentro do próprio parágrafo o número que o sustenta, mais figura, porque a peça precisa funcionar para quem nunca vai abrir o relatório. O custo da escolha é real e vale registrar: a auditabilidade deixa de ser por referência e passa a depender de quem escreve não inventar achado. A poda continua sendo feita a partir do IMRaD, só não fica visível no documento final.

Nesta rodada ficaram deliberadamente de fora, por poda: as oito hipóteses candidatas, a hipótese refutada sobre o pareamento com o VRA, a recomendação de unificar critério de limpeza entre as duas frentes, e 29 das 36 figuras do relatório.

## Estrutura do argumento: dedutiva

Minto admite dois modos de sustentar a ideia governante, e prefere o primeiro no topo:

| Modo | Forma | Comportamento sob ataque |
|---|---|---|
| Indutivo | Um grupo de razões da mesma espécie, que somam | Uma razão derrubada não leva as outras junto |
| Dedutivo | Uma cadeia: premissa maior, premissa menor, portanto | Derrubar o primeiro elo derruba o argumento inteiro |

Este documento usa o **dedutivo**, por decisão do autor. O motivo é o casamento com a ideia governante. A Recomendação aqui é uma **ação** ("rode o teste antes de mobilizar equipe"), e a pergunta que ela levanta no leitor é *"por que antes?"*. Uma lista indutiva de achados responde a outra pergunta, *"por que acreditar que há um problema?"*, e deixa a ordem das providências sem sustentação própria. A cadeia responde à pergunta certa porque termina exatamente na ação pedida.

Os três elos:

1. Um sistema construído para se repetir teve, num único ponto, um desvio simultâneo. *(premissa maior: o que existe no mundo)*
2. Esse desvio vive no eixo da base, onde duas causas com respostas opostas competem. *(premissa menor: o comentário sobre a primeira)*
3. Existe um cálculo que separa as duas sem sair do dado atual, e ele é mais barato que qualquer ação. *(o significado implicado, que é a Recomendação)*

O que se paga: as razões deixam de ser independentes, e o leitor precisa carregar as premissas até o fim. É por isso que os três elos são curtos. A cadeia só compensa enquanto couber na cabeça de quem lê uma vez só.

**Os cinco indicadores continuam cobertos, sem mandar na estrutura.** Na versão indutiva cada indicador virava um porquê, o que organizava a pirâmide pela estrutura da coleta em vez da do argumento. Aqui destinos e frota estabelecem o pano de fundo homogêneo no elo 1, em número; etapa média e block time localizam a variação no eixo da base no elo 2, e a etapa média leva as duas figuras do contraste; tempo de solo atravessa os três.

## Estrutura de arquivos

```
gerador-minto-microdados/
├── environment.yml
├── config.yml               # cabeçalho de comunicado, faixa de porquês, ordem das seções
├── gerar_docx.py
├── modelo_de_escrita.docx   # base de estilo (não editar)
├── secoes/
│   ├── 00-situacao/          SCQA: situação, complicação, questão
│   ├── 01-recomendacao/      a resposta, primeiro (governing thought)
│   ├── 02-porques/           a cadeia dedutiva, exatamente 3 elos
│   ├── 03-pedido-de-acao/    o que decidir, aprovar ou fazer, e até quando
│   ├── 04-decisao-pendente/  opcional: o trade-off aberto e o critério que o resolve
│   └── 05-nota-metodologica/ opcional: os limites que afetam a confiança
└── saida/
```

Cada `.md` traz comentários `<!-- -->` com a orientação do que escrever ali, incluindo os erros típicos de cada seção. Comentários nunca aparecem no `.docx`.

## Por que estas seções

| Pasta | Papel na pirâmide |
|---|---|
| `00-situacao` | A entrada, em três dos quatro tempos do SCQA: **situação** (o que o leitor concorda sem esforço), **complicação** (o que quebrou nela) e **questão** (a pergunta verificável que a complicação levanta). A quarta, a resposta, é a seção seguinte. |
| `01-recomendacao` | O pensamento governante, respondendo à questão acima e a nenhuma outra. Teste: é uma **ação** ou uma **afirmação**? Minto pede a primeira. "A GOL opera um modelo homogêneo" é achado, não recomendação. |
| `02-porques` | A cadeia dedutiva de três elos. Cada elo abre com a conexão explícita ao anterior, e cada um traz pelo menos uma figura. |
| `03-pedido-de-acao` | O que o destinatário decide, aprova ou faz, com prazo. Terminar em "sugere-se avaliar" devolve o problema para quem recebeu. |
| `04-decisao-pendente` | Existe porque nem toda análise fecha numa recomendação. Quando a conclusão é "depende", o guia (`GUIDE-005 §5`) manda declarar a decisão pendente e o critério, não forçar uma recomendação artificial. |
| `05-nota-metodologica` | A poda das Limitações do IMRaD: só o que mudaria a leitura de quem decide com base nesta página. |

## Os porquês: faixa validada

A quantidade de porquês é validada na geração. Cada porquê é um `### Título` no markdown de `02-porques`, e a faixa vem do `config.yml`:

```yaml
porques:
  minimo: 3
  maximo: 3
```

Fora da faixa o gerador **aborta**, porque é erro de conteúdo e não de formatação. Aqui a faixa está travada em 3 porque o argumento é dedutivo: um quarto elo não existe em dedução, e a mensagem de erro é o lembrete disso. Ou o conteúdo novo é evidência dentro de um dos três elos, ou o argumento voltou a ser indutivo, e nesse caso o comentário de orientação de `02-porques/porques.md` precisa ser reescrito antes, e a faixa volta para `minimo: 3 / maximo: 10`.

## Figuras

Convenção deste gerador: **uma figura na Recomendação e pelo menos uma por elo da cadeia, e nenhuma figura sem argumento**. Numa peça autoconsistente a figura não é ilustração, é o argumento visual. A pergunta antes de inserir é "que frase do parágrafo esta figura prova?"; sem resposta curta, ela não entra. A da Recomendação é a que mostra o problema de que a decisão trata.

**Nada de boxplot nem de violin plot.** Eles descrevem a forma de uma distribuição, que é pergunta de relatório. Aqui a pergunta é sempre comparativa ou temporal, e a resposta é série ao longo do tempo, ranking ou dispersão de pontos. Um gestor não lê quartil de passagem, e uma caixa lida errado atrasa a decisão em vez de acelerá-la.

**Contraste vem em par colado, na mesma escala.** As duas figuras do elo 2 são o exemplo: mesma métrica, mesmo período, mesmo eixo vertical, uma por base e outra por modelo. É a comparação entre as duas que sustenta a afirmação, e a frase que instrui a leitura vem antes das duas.

As figuras vivem em `figuras/` dentro da pasta da seção, com prefixo indicando o elo em que entram (`rec_`, `p1`, `p2a`, `p2b`, `p3`). Todas são **cópias literais** das do relatório IMRaD, para que os dois documentos nunca mostrem versões diferentes do mesmo gráfico:

| Arquivo aqui | Origem em `../gerador-imrad-microdados` | O que prova |
|---|---|---|
| `rec_tempo_solo_medio_top_hubs.png` | `res_11_tempo_solo_medio_top_hubs_docx.png` | Sete das oito linhas sobem no trecho final: é o problema |
| `p1_tempo_solo_mensal_por_base.png` | `res_14_tempo_solo_mensal_por_base_gol.png` | As bases convergem para um corredor estreito a partir de 2023: é a homogeneidade |
| `p2a_etapa_media_por_base.png` | `res_22_etapa_media_mensal_por_base_gol.png` | Quebras de nível permanentes, por base |
| `p2b_etapa_media_por_modelo.png` | `res_21_etapa_media_mensal_por_frota_gol.png` | Nenhuma quebra e nenhum cruzamento, por modelo |
| `p3_tempo_solo_lag_plot.png` | `res_17_tempo_solo_lag_plot_gol_azul.png` | O que o teste enxerga: nuvem colada à diagonal é memória |

Para conferir que não divergiram: `md5sum` dos pares acima. A procedência das figuras dos dois geradores, contra as originais de `analise/` deste repositório, está em `../PROCEDENCIA_FIGURAS.md`, com o comando de verificação. Quatro das cinco figuras desta peça são idênticas às de `analise/`; a quinta vem do documento manual do autor.

Três figuras saíram na revisão de 04/09/2026, e o motivo de cada uma vale como critério: o boxplot de tempo de solo por modelo e o de folga por hub por serem boxplot (o segundo, além disso, mostrava oito caixas quase idênticas, contradizendo a legenda que o acompanhava); o painel de destinos por ano (`res_02`) por ter seis subpainéis em duas escalas verticais diferentes, o que impede justamente a comparação que ele existia para fazer. A malha e a frota continuam no elo 1, em número, sem figura.

## Cabeçalho

Diferente do gerador IMRaD, o cabeçalho aqui é de comunicado, e é livre. Vem de `config.yml`, chave `documento.cabecalho`, como lista de pares:

```yaml
cabecalho:
  - rotulo: "Para"
    valor: "Planejamento de malha / Operações de solo"
  - rotulo: "Decisão pedida"
    valor: "..."
```

Sem essa chave, o script cai no cabeçalho de relatório do gerador IMRaD (data, janela temporal, base de dados, contexto).

## Gerar

```bash
conda activate gov-sermi-perf
python gerar_docx.py
```

## Sintaxe do markdown

Mesma dos outros geradores do repositório: `##` e `###` para subtítulos, `-` e `1.` para listas, `**negrito**`, `*itálico*`, `` `monoespaçado` ``, `![legenda](figuras/x.png)` para figuras, tabelas com `|`, e `<!-- -->` para orientação que não sai no documento.

Cuidado com o volume de texto: a peça de decisão vive de parágrafo curto ao lado da figura. Se um elo precisar de mais de três parágrafos para se sustentar, provavelmente o conteúdo pertence ao relatório.
