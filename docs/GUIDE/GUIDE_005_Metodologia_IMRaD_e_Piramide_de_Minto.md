---
documento: GUIDE-005
titulo: Metodologia IMRaD + Pirâmide de Minto para análise decisória
versao: v1
status: proposto
data: 2026-09-04
autor: Bruno Alexandre Serminaro
referencia: DEC-010, SPEC-004, SPEC-017
escopo: projeto
---

# GUIDE-005 · Metodologia IMRaD + Pirâmide de Minto

> Guia de escrita das duas peças produzidas em `relatorios/`: o relatório
> IMRaD, que carrega o rastro, e o comunicado Minto, que carrega a decisão.
> Enquanto `SPEC-004` fixa **quais perguntas** a análise responde e as SPECs
> de linha (`SPEC-013`, `SPEC-015`, `SPEC-016`, `SPEC-017`) registram **o que
> foi medido**, este documento fixa **como o resultado vira documento legível
> por quem audita e por quem decide**.
>
> Origem: escrito em `learn-imrad-mintos/docs/guia-metodologico.md` durante a
> construção dos geradores, e trazido para cá com o `DEC-010`. A cópia de
> origem não é versionada (aquele repositório não tem git); esta é a versão
> canônica a partir de 2026-09-04.

---


Domínio de referência: análise de dados em aviação, com desdobramento para comunicação executiva. A lógica é genérica dentro desse domínio — serve para OTP, manutenção, custo operacional, segurança, ou qualquer outro tema analítico, sem amarrar o template a uma métrica específica.

## 1. Por que dois modelos para um problema

Análise de dados em aviação serve, tipicamente, dois públicos com necessidades opostas:

- Quem audita o método (engenharia, segurança, compliance, o analista revisando o próprio trabalho depois) precisa do percurso completo: dados usados, premissas, limitações, como se chegou ao achado.
- Quem decide (executivo, gestor operacional) precisa da resposta primeiro. Não tem tempo nem motivo para percorrer o raciocínio antes de saber o que está sendo recomendado.

Um documento único não serve bem aos dois. Se é escrito na ordem do método (como um artigo), força o decisor a ler até o fim para chegar à recomendação. Se é escrito na ordem da decisão (como um pitch), esconde o lastro que quem audita precisa verificar.

Solução: **IMRaD carrega o rastro** (evidência, método, limites, é o documento de trabalho). **Minto carrega a decisão** (resposta primeiro, razões, pedido de ação, é a interface de decisão). O e-mail deriva do relatório — nunca inventa achado que não esteja no corpo do relatório, e cada razão do e-mail deve ser rastreável a uma seção específica dele.

Premissa deste guia: existe uma peça de trabalho (relatório) e uma peça de decisão (e-mail), e elas não competem pelo mesmo formato. Se essa premissa não se sustentar no seu contexto (por exemplo, se o único público for técnico e nunca houver decisor executivo), o Minto perde função e o IMRaD sozinho basta.

## 2. IMRaD adaptado para análise decisória

Não é artigo acadêmico. Mesma espinha dorsal (Introduction, Methods, Results, Discussion), adaptada para produzir uma recomendação, não para reportar um experimento fechado.

**Introdução — Contexto e Pergunta**
O que motivou a análise (evento, pedido, sinal de alerta). O que está em jogo (decisão, custo, risco). Pergunta central formulada de forma verificável — algo que os dados podem, em princípio, responder ou refutar.

**Métodos — Dados e Abordagem**
Fontes de dados (sistema de origem, período, granularidade). Premissas assumidas explicitamente. O que ficou fora do escopo e por quê. Limitações conhecidas dos dados ou do método. Esta seção é o que torna o relatório auditável — é a mais frequentemente cortada sob pressão de prazo, e é a que mais falta depois quando alguém questiona um achado.

**Resultados — Achados**
O que os dados mostram, com incerteza explícita (intervalo, tamanho de amostra, qualidade da fonte). Separar claramente achado confirmado de hipótese candidata — evidência sugestiva mas insuficiente para inferência forte não entra na mesma prateleira que achado sustentado.

**Discussão — Interpretação e Decisão**
O que os achados significam. Alternativas consideradas e seus trade-offs explícitos. Recomendação. Incertezas que afetam a confiança nela. Próximo passo de verificação ou aprendizado — como se vai saber, depois, se a decisão foi boa.

Exemplos ilustrativos de perguntas centrais no domínio aviação: variação de OTP (on-time performance) por hub, causas de aumento no turnaround time, tendência de MTBF em uma frota, evolução de CASK (custo por ASK) período a período, padrão em eventos de segurança reportados. Nenhum é obrigatório no template — são âncoras para calibrar o nível de granularidade esperado.

## 3. Pirâmide de Minto para o e-mail executivo

Regra central: resposta primeiro. Nunca a jornada antes da conclusão.

**Estrutura descendente (top-down):**

1. **Situação** — uma a duas frases de contexto que ancoram o leitor, sem recapitular a análise inteira.
2. **Recomendação** (governing thought) — a resposta direta, no primeiro parágrafo.
3. **Porquês** — as razões que sustentam a recomendação, idealmente três, organizadas de forma MECE (mutuamente exclusivas, coletivamente exaustivas — cada razão cobre uma parte distinta do argumento, sem sobreposição nem lacuna óbvia). Cada uma com evidência resumida em uma linha e referência à seção correspondente do relatório.
4. **Pedido de ação** — o que o destinatário precisa decidir, aprovar ou fazer, e até quando.

Regra de rastreabilidade: cada "porquê" do e-mail precisa apontar para uma seção específica do IMRaD. É isso que diferencia a pirâmide de um argumento retórico solto — o e-mail é auditável porque referencia o documento que sustenta cada afirmação.

## 4. Fluxo de produção

1. O processo de cinco etapas (sensemaking → evidência → modelagem → alternativas → recomendação) alimenta diretamente as seções Resultados e Discussão do IMRaD.
2. O relatório IMRaD é escrito primeiro. É o documento de trabalho, versionável, e o rastro auditável.
3. O e-mail Minto é extraído depois, por poda, não por resumo. Poda significa escolher a recomendação final e as razões mais fortes e descartar o resto — não compactar tudo proporcionalmente.

## 5. Onde o modelo para de servir

- Minto assume que existe uma recomendação clara. Se a análise concluir "depende" ou deixar trade-offs abertos sem decisão, forçar isso na pirâmide produz falso conforto — o e-mail deve então apresentar a decisão pendente e o critério de escolha, não uma recomendação artificial.
- IMRaD assume que há método relevante a expor. Para sensemaking muito preliminar (poucos dados, primeira exploração), a seção Métodos fica fina — isso deve ser dito explicitamente na Introdução (status: exploratório), não escondido atrás da estrutura formal.
- Nenhum dos dois modelos substitui o julgamento sobre o que é relevante. São moldes para organizar uma análise já pensada, não um substituto para pensá-la.

---

## 6. Onde este guia se conecta ao resto do projeto

| Peça | Papel |
|---|---|
| `SPEC-004` | Fixa as perguntas de análise. A pergunta central da Introdução do IMRaD deriva daí. |
| `SPEC-013`, `SPEC-015`, `SPEC-016` | Registram o que foi medido em cada linha. Alimentam Resultados. |
| `SPEC-017` | Releitura da autocorrelação. Alimenta Discussão e a Recomendação 1. |
| `relatorios/<versao>/gerador-imrad-microdados` | Produz o relatório. |
| `relatorios/<versao>/gerador-minto-microdados` | Produz o comunicado, por poda do relatório. |
| `DEC-010` | Registra por que `relatorios/` existe fora da estrutura da `SPEC-001 §5`. |

**Divergência declarada.** O comunicado gerado em
`relatorios/<versao>/gerador-minto-microdados` é **autoconsistente**: contra a regra de
rastreabilidade da §3 deste guia, ele não aponta para seções do relatório.
Cada porquê carrega o número dentro do próprio parágrafo, porque a peça
precisa funcionar para quem nunca vai abrir o IMRaD. O custo é real e está
registrado no `config.yml` daquele gerador: a auditabilidade deixa de ser
verificável por referência e passa a depender de quem escreve não inventar
achado. A poda continua sendo feita a partir do IMRaD, só não fica visível no
documento final.

---

## 7. Histórico

| Data | Evento |
|---|---|
| 2026-09-04 | GUIDE-005 v1, status `proposto`. Trazido de `learn-imrad-mintos/docs/guia-metodologico.md`, sem alteração do texto das §1 a §5. Acrescentadas a nota de origem no topo, a §6 de conexão com as peças do projeto e este histórico. Motivo: os geradores passaram a viver em `relatorios/` (ver `DEC-010`), e o ponteiro `../docs/guia-metodologico.md` que eles carregavam apontaria, neste repositório, para uma pasta que existe com outro conteúdo. |

---

*Fim do documento.*
