---
documento: DEC-002
titulo: Decisões de descrição — recorte de escopo, critérios de sucesso e não-objetivos
versao: v1
status: aprovado
data: 2026-08-24
autor: Bruno Alexandre Serminaro
referencia: REP-001, SPEC-001
escopo: projeto
---

# DEC-002 · Decisões de descrição

> A partir do acúmulo de REP-001 (achados, decisões D1-D5, premissas e
> vieses) e SPEC-001 (taxonomia já fundada), fixa o recorte de escopo, os
> critérios de sucesso e os não-objetivos que o SPEC-002 vai formalizar.
> Decide o recorte; não descreve o produto — isso é função do SPEC-002.

---

## 1. Contexto

### O que o REP-001 estabeleceu

O REP-001 (aprovado, 2026-08-24) consolidou cinco decisões informais da
sessão (D1-D5, §4), das quais três são de escopo puro — D1 (3 datasets),
D2 (dois caminhos igualmente investidos), D3 (corte temporal 2010) — e
distinguiu achado confirmado de hipótese candidata sobre as fontes de dado
(§5): Básica e VRA têm dado real desde 2000, SIROS só desde 2019-11 e em
cadência diária, não mensal. Também nomeou dois vieses concretos a vigiar
(§6): romantização de escopo (o projeto triplicou de tamanho numa sessão) e
viés de disponibilidade de fonte ("a fonte tem desde 2000" não é motivo
suficiente para processar 26 anos).

D1, D2, D3 e D5 nunca tiveram DEC própria — existiam em prosa dentro de
`docs/plano_expansao_multidataset.md`, sem alternativa descartada
registrada nem critério de reavaliação. D5 já foi formalizada pelo DEC-001
(fundação sob SERMI). D1, D2 e D3 seguem pendentes — é isso que esta DEC
resolve.

### Por que decidir agora

O SPEC-001 (aprovado) já fixou como o projeto documenta; o REP-001
(aprovado) já consolidou o que se sabe e o que se decidiu informalmente.
Pela ordem generativa decisão-primeiro (DEC-META-014 §2.1), o próximo passo
é a DEC que autoriza o SPEC-002 a descrever o produto — não descrever
antes de decidir o recorte com alternativa e consequência explícitas, o
que é exatamente o vício que o REP-001 diagnosticou no estado anterior.

---

## 2. Decisão

**Fixar o recorte de escopo em 3 datasets ANAC (Básica, VRA, SIROS) nos
dois caminhos de produção paralelos e igualmente investidos, cobrindo
2010-presente onde a fonte permite, com critério de sucesso incremental
por dataset e por caminho — não "tudo pronto de uma vez".**

---

## 3. Origem ou rastro

- `REP-001 §4` (D1, D2, D3): as três decisões de escopo que esta DEC
  formaliza, com o texto exato do que foi decidido informalmente.
- `REP-001 §5.1` (achados confirmados): período real de disponibilidade de
  cada fonte, testado por HTTP — usado para calibrar até onde o recorte
  temporal é honesto (não força período que a fonte não tem, caso do
  SIROS).
- `REP-001 §5.2` (hipóteses candidatas): estabilidade de schema não testada
  e volume do SIROS estimado, não medido — usadas para justificar por que
  o critério de sucesso é incremental, não "tudo de uma vez" (§4.4).
- `REP-001 §6` (premissas e vieses): romantização de escopo e viés de
  disponibilidade de fonte — usados diretamente para descartar as
  alternativas de recorte maior (§4.1, §4.3).
- `docs/plano_expansao_multidataset.md`: registro original, informal, das
  decisões D1-D3, agora superado por esta DEC como fonte de rastro
  decisório (o documento de plano continua existindo como detalhamento
  técnico, não como registro de decisão).

---

## 4. Alternativas consideradas

### 4.1 Recorte de datasets: manter só a Básica

Não expandir para VRA e SIROS; continuar o projeto com um dataset só.

**Por que descartada.** É o estado anterior a esta sessão, já superado por
D1. Manter só a Básica desperdiça a oportunidade de praticar ingestão com
cadências diferentes (mensal vs. diária) e um dataset com limite real de
histórico (SIROS), que é justamente o tipo de caso heterogêneo que
enriquece o valor de portfólio e de aprendizado do projeto.

### 4.2 Paridade dos caminhos: Snowflake principal, SQLite secundário

Manter a hierarquia que estava registrada antes desta sessão: Snowflake
como foco de aprendizado, SQLite como apoio/exploração.

**Por que descartada.** Foi revertida deliberadamente pelo autor nesta
mesma sessão (D2) — os dois caminhos passam a ter camada ouro e dashboard
próprios, mesmo nível de investimento. Manter a hierarquia antiga
contradiria uma decisão já tomada e testada ao longo da sessão (a
reorganização de `sql/`/`src/` já reflete paridade, não hierarquia).

### 4.3 Corte temporal: usar o máximo da fonte (2000-presente) para Básica e VRA

Já que Básica e VRA têm dado real desde 2000 (achado confirmado, REP-001
§5.1), processar o histórico completo em vez de recortar em 2010.

**Por que descartada.** É exatamente o viés de disponibilidade de fonte
nomeado no REP-001 §6: a fonte permitir não é motivo suficiente. Processar
16 anos a mais (2000-2009) quase dobra o volume sem que o projeto tenha,
até aqui, avaliado se o ganho analítico justifica o custo de
processamento e o risco de schema instável em período ainda mais antigo
(hipótese candidata não testada, REP-001 §5.2). O corte em 2010 já foi a
escolha original do autor antes mesmo desta sessão de expansão.

### 4.4 Critério de sucesso: "os 3 datasets completos nos 2 caminhos" como critério único

Definir sucesso só quando toda a matriz (3 datasets × 2 caminhos × todas as
camadas) estiver pronta.

**Por que descartada.** Risco real de o projeto nunca declarar sucesso
parcial: SIROS sozinho, em cadência diária, pode revelar volume que exige
redesenho (hipótese candidata não testada, REP-001 §5.2), e um critério
monolítico não dá sinal de progresso enquanto isso não for medido. Um
critério incremental (§6, campo 2) permite declarar sucesso por fatia
(ex.: "Básica estendida a 2010, carregada e validada nos dois caminhos")
sem esperar o projeto inteiro.

### 4.5 Recorte de 3 datasets, 2 caminhos iguais, 2010-presente, critério incremental (decisão atual)

Adota D1, D2, D3 como estavam registrados informalmente, mas com critério
de sucesso incremental em vez de monolítico.

**Adotada.** Resolve a lacuna de rastro do REP-001 sem reabrir decisões já
tomadas e testadas ao longo da sessão (D1-D3), e corrige o único ponto que
o estado anterior não tinha resolvido: o critério de sucesso, que evita o
risco nomeado em §4.4.

---

## 5. Consequências

### 5.1 Positivas

- D1, D2 e D3 ganham DEC própria com alternativa descartada e critério de
  reavaliação — fecham exatamente a lacuna que o REP-001 diagnosticou.
- O critério de sucesso incremental (§6, campo 2) dá ao projeto sinal de
  progresso mensurável sem depender de terminar a matriz inteira antes de
  declarar qualquer vitória.
- Os dois vieses nomeados no REP-001 (romantização de escopo, viés de
  disponibilidade de fonte) foram usados ativamente para descartar
  alternativas (§4.3, implícito em §4.4), não só mencionados e ignorados.

### 5.2 Negativas

- **O recorte continua grande para projeto solo sem prazo externo**: 3
  datasets, 2 caminhos, mesmo com critério incremental, é
  substancialmente mais trabalho do que o projeto original (1 dataset, 1
  caminho). Aceito pelo autor (D1/D2 já testados na sessão), mas o risco
  de romantização de escopo (REP-001 §6) não desaparece só por nomear —
  precisa de vigilância contínua, não só desta DEC.
- **O corte em 2010 exclui 16 anos de dado potencialmente útil**
  (2000-2009) da Básica e do VRA. É escolha deliberada, não limite
  técnico — significa que qualquer análise histórica de mais longo prazo
  fica fora do escopo atual, e revisitar exigiria nova extensão de
  download, não só mudança de critério.
- **Critério de sucesso incremental tem custo de coordenação**: declarar
  sucesso por fatia exige que o SPEC-002 defina C-NN claros o bastante
  para não virar "sempre parcialmente pronto, nunca de fato terminado" —
  risco que esta DEC nomeia mas não resolve (é o SPEC-002 que precisa
  operacionalizar isso em critérios verificáveis).

### 5.3 O que esta decisão não resolve

- **Não decide o conteúdo exato dos critérios de sucesso `C-NN`** — isso é
  o SPEC-002, que formaliza os campos fixados no §6 abaixo.
- **Não decide D4 e D7** (organização de dado em SQLite, separação física
  de ingestão SQLite/Snowflake) — o REP-001 §4 já registrou que são
  decisões técnicas/arquiteturais, candidatas a uma DEC de conteúdo
  dedicada (`DEC-004` ou posterior, `SPEC-001 §9`), não a esta DEC nem ao
  SPEC-002.
- **Não decide participação e responsabilidade** — isso é `DEC-003` e
  `SPEC-003`, próximo bloco.
- **Não resolve a hipótese candidata de estabilidade de schema** nem o
  volume real do SIROS (REP-001 §5.2) — permanecem hipóteses até serem
  testadas na implementação.

---

## 6. Campos estruturantes do SPEC-002

O mínimo que esta DEC fixa para o SPEC-002 formalizar (blueprint DEC-002,
`docs/assets/blueprints/DEC_002.json`):

### 6.1 Recorte de escopo

**Entrega**: pipeline completo (download bruto → ingestão → tratamento →
camada ouro → dashboard) para os 3 datasets ANAC (Básica, VRA, SIROS), nos
dois caminhos de produção (Snowflake medalhão, SQLite+Python), cobrindo
2010-presente onde a fonte permite (SIROS: 2019-11-presente, limite real
da fonte, não do projeto).

**Fica deliberadamente fora**:
- Dataset **Combinada** — existe na mesma fonte que a Básica, nunca foi
  pedida (`docs/plano_expansao_multidataset.md` §1, "fora de escopo").
- Linguagens de UDF/procedure nativas do Snowflake além de Python/Snowpark
  (JavaScript, Java, Scala) — decisão do DEC-001 §6.6.
- R integrado a um dos dois pipelines de produção — fica como ferramenta
  de análise complementar, fora dos caminhos (DEC-001 §6.6).
- Reconstrução de SIROS anterior a 2019-11 — a fonte não tem, não é
  recorte, é limite (REP-001 §5.1).

### 6.2 Critérios de sucesso adotados e descartados

**Adotado**: critério **incremental**, por dataset e por caminho — sucesso
parcial é sucesso real, não só o estado final da matriz completa. Exemplo
de primeiro critério candidato (a formalizar como `C-01` no SPEC-002):
"Básica estendida a 2010, carregada e validada nos dois caminhos".

**Descartado**: critério monolítico ("os 3 datasets completos nos 2
caminhos simultaneamente") — motivo em §4.4.

### 6.3 Não-objetivos

- Não otimizar para latência em tempo real — mesmo o SIROS, diário, é
  processado em lote (batch), não streaming.
- Não otimizar para uso multiusuário ou produção corporativa — é
  portfólio solo, não sistema com SLA externo.
- Não migrar ou dar suporte ao dataset Combinada.

### 6.4 Decomposição escolhida

Matriz **dataset × caminho** (3 × 2 = 6 células), cada célula com suas
próprias camadas (Snowflake: raw → prata → ouro; SQLite: raw → limpo →
ouro). Alternativa descartada: decompor só por caminho (todos os datasets
juntos dentro de cada caminho) — rejeitada porque os datasets têm
cadências de origem diferentes (SIROS diário vs. Básica/VRA mensal), que
exigem desenho de ingestão distinto por dataset, não só por caminho.

### 6.5 Premissas e dependências externas assumidas

- Disponibilidade contínua da ANAC nos padrões de URL testados em
  2026-08-24 (`sistemas.anac.gov.br/dadosabertos/...`,
  `gov.br/anac/.../basica/...`) — pode mudar sem aviso prévio, a fonte é
  de terceiro.
- Conta Snowflake trial permanece ativa e com crédito suficiente para o
  volume ampliado (26 anos → 16 anos de Básica/VRA mais SIROS diário desde
  2019).
- Volume do SIROS não excede o que o processamento local (SQLite) ou o
  warehouse `wh_anac` (XSMALL) suportam sem redesenho — não testado, é
  premissa, não achado (REP-001 §5.2).

---

## 7. Critérios de reavaliação

Esta decisão deve ser revisitada se:

- O ritmo de trabalho solo mostrar que 3 datasets em 2 caminhos é
  inviável no horizonte de tempo real que o autor tem disponível —
  sintoma direto do viés de romantização de escopo (REP-001 §6) se
  materializando.
- A extensão real do download da Básica para 2010 revelar quebra de
  schema (hipótese candidata do REP-001 §5.2 virando achado) que exija
  redesenho do escopo ou do recorte temporal.
- O volume real do SIROS, medido na implementação, invalidar a premissa
  de viabilidade do §6.5.
- O critério de sucesso incremental, na prática, não conseguir ser
  operacionalizado em `C-NN` verificáveis pelo SPEC-002.

---

## 8. Histórico

| Data | Evento |
|---|---|
| 2026-08-24 | DEC-002 produzida em status `proposto`. Formaliza D1 (3 datasets), D2 (dois caminhos iguais) e D3 (corte 2010) do REP-001, com critério de sucesso incremental adotado no lugar do critério monolítico. Cinco alternativas avaliadas, duas rejeitadas por reabrirem vieses já nomeados no REP-001. Aguardando revisão do autor antes de aprovar e seguir para SPEC-002. |
| 2026-08-24 | **Aprovada.** Revisão contra o blueprint (`DEC_002.json`) sem divergência: sete seções obrigatórias presentes, cinco alternativas com veredito (mínimo 2), consequências negativas não vazias, cinco campos estruturantes do SPEC-002 preenchidos (§6). Segue para SPEC-002. |
| 2026-09-06 | **Correção pós-aprovação, decisão inalterada (`R-TAX-11`).** A citação de §6 ao blueprint acompanha a mudança de `rascunho/contexto/blueprints/` para `docs/assets/blueprints/`. Motivo registrado na `DEC-001`, mesma data. Nada mais muda. |

---

*Fim do documento.*
