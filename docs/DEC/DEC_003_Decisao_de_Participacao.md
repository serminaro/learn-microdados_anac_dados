---
documento: DEC-003
titulo: Decisão de participação — operação solo, Claude como par assistivo
versao: v1
status: aprovado
data: 2026-08-24
autor: Bruno Alexandre Serminaro
referencia: SPEC-002, REP-001
escopo: projeto
---

# DEC-003 · Decisão de participação

> Registra a estrutura de quem responde pelo projeto: modo solo, com o
> autor acumulando todos os papéis de decisão e a IA de apoio (Claude) como
> par assistivo sem autoridade de aprovação. O SPEC-003 materializa esta
> decisão como contrato.

---

## 1. Contexto

### Exigências do escopo (SPEC-002)

O SPEC-002 (aprovado) fixou um escopo substancial para projeto solo: 3
datasets, 2 caminhos de produção, 9 critérios de sucesso. Isso levanta uma
pergunta legítima de estrutura: um escopo desse tamanho justificaria buscar
participação além do autor?

### Pessoas disponíveis

Nenhuma. O projeto nasceu e segue como trabalho individual de Bruno
Alexandre Serminaro. Não há coautor, revisor técnico comprometido, nem
terceiro com interesse formal no resultado. A única outra parte envolvida
na produção é a IA de apoio (Claude Code), agente não-humano.

### Por que decidir agora

O REP-001 (§1, P1) já registrou o modo solo como fato do projeto; esta DEC
formaliza essa constatação como decisão deliberada, com alternativas e
consequências — não como default não examinado. É o mesmo movimento que a
DEC-META-013/014 exigem: solo não é ausência de decisão, é uma escolha que
precisa do mesmo rigor de qualquer outra.

Vale registrar uma particularidade deste projeto em relação a um projeto
de estudo puro: `docs/plano_objetos_snowflake.md` já o conecta a
`okr_bruno_azul` e `CARREIRA_estrategia_e_linkedin.md`
(`serminaro-governance/trabalho`) — ou seja, o projeto já tem uso de
portfólio/carreira ativo, não hipotético. Isso não muda a decisão de operar
solo hoje, mas aproxima o gatilho de graduação (§6) do que estaria para um
projeto de estudo isolado sem conexão de carreira.

---

## 2. Decisão

**Operar em modo solo: o autor acumula os papéis de Autor, Gestor e
Diretor; a IA de apoio (Claude) atua como par assistivo, sem autoridade de
aprovação; Peer Review e Supervisor humanos ficam formalmente não
previstos, não vagos por omissão.**

---

## 3. Origem ou rastro

- `SPEC-002 §2` (Audiência): já registrava o par assistivo como papel
  abstrato, sem stakeholder externo com poder de decisão.
- `REP-001 §1` (P1) e `§6` (vieses): o projeto é trabalho individual desde
  o início; o viés de romantização de escopo nomeado ali é justamente o
  tipo de risco que a ausência de revisão externa deixa sem freio humano.
- `docs/plano_objetos_snowflake.md` linha 6: conexão factual e já existente
  com `okr_bruno_azul`/`CARREIRA_estrategia_e_linkedin.md`, usada em §1 e
  §6 para calibrar o gatilho de graduação.
- Precedente do ecossistema pessoal do autor: `learn-aviacao-cco-db`
  SPEC-003 (Contrato de Responsabilidade), que resolveu a mesma pergunta
  para um projeto solo comparável — usado como referência de estrutura,
  não copiado sem ajuste (a diferença de escopo e de conexão com carreira
  justifica cadência de auditoria mais ativa aqui, §6, campo 4).

---

## 4. Alternativas consideradas

### 4.1 Buscar par de revisão humano desde já

Nomear formalmente um Peer Review ou Supervisor humano antes de prosseguir,
dado o escopo grande fixado no SPEC-002.

**Por que descartada.** Não há pessoa real disponível ou comprometida para
esse papel agora. Nomear um papel vago "para constar" seria exatamente o
tipo de peça ornamental que a taxonomia SERMI rejeita (SPEC-META-001
§11.6) — pior do que registrar honestamente "não previsto". Se uma pessoa
real se tornar disponível, é gatilho de graduação (§6), não motivo para
fingir revisão que não existe agora.

### 4.2 Elevar a autoridade do par assistivo (Claude) para aprovar artefatos

Permitir que a IA de apoio aprove peças (DEC/SPEC), não só sugira, para
compensar a ausência de revisor humano.

**Por que descartada.** Contraria o padrão já estabelecido em todo o
ecossistema pessoal do autor (`learn-aviacao-cco-db` R-CON-06: "o par
assistivo não consta como aprovador de nenhum artefato"). Delegar
aprovação a um agente não-humano não resolve o problema de fundo (ausência
de julgamento humano independente) — apenas o esconde atrás de uma
aprovação automatizada. O par assistivo revisa e aponta inconsistência
(como já fez nas revisões de DEC-001/SPEC-001/REP-001/DEC-002/SPEC-002),
mas a decisão de aprovar continua sendo sempre do autor.

### 4.3 Operação solo sem cadência de auditoria fixa (auditoria puramente ad hoc)

Não comprometer nenhuma cadência mínima de auditoria (`gov-check`); rodar
só quando o autor sentir necessidade, sem gatilho temporal.

**Por que descartada.** É o padrão que `learn-aviacao-cco-db` adotou, mas
esse projeto tem menor volume de mudança e nenhuma conexão de carreira
ativa registrada. Este projeto está em expansão ativa (REP-001 §1) e já
conectado a `okr_bruno_azul`/carreira (§1) — deixar a auditoria
inteiramente sem cadência mínima aumenta o risco de o freio compensatório
(§6, campo 2) nunca rodar de fato, justo no projeto onde a conexão de
carreira torna esse freio mais relevante, não menos.

### 4.4 Operação solo, Claude como par assistivo sem autoridade de aprovação, auditoria com cadência mínima por marco (decisão atual)

Mesma estrutura de papéis do precedente (`learn-aviacao-cco-db`), mas com
um compromisso adicional: auditoria de coerência (`gov-check`) rodada ao
fim de cada marco relevante (fechamento de bloco de fundação, fechamento
de fase do plano Snowflake ou do plano de expansão), com piso de uma vez
por trimestre mesmo sem marco.

**Adotada.** Preserva o que já funciona no precedente (papéis, ausência de
autoridade de aprovação da IA, honestidade sobre o limite de não ter freio
humano) e fecha a lacuna que a alternativa 4.3 deixaria aberta, dado que
este projeto tem conexão de carreira mais ativa que o precedente.

---

## 5. Consequências

### 5.1 Positivas

- Estrutura simples, sem papel ornamental: cada papel vago é registrado
  como "não previsto", não como pendência sem dono.
- O par assistivo continua sendo usado ativamente para revisão técnica
  (como já ocorreu em cada aprovação desta fundação), sem ganhar
  autoridade que mascare a ausência de revisor humano real.
- A cadência mínima de auditoria (§6, campo 4) dá um piso concreto ao
  freio compensatório, em vez de depender só da disposição do autor no
  momento.

### 5.2 Negativas

- **Ausência de freio humano externo** continua sendo o risco central:
  sem Peer Review nem Supervisor, o viés de confirmação do autor não tem
  contraparte humana. A auditoria (`gov-check`) e o par assistivo mitigam,
  mas não eliminam esse risco — registrado aqui honestamente, não
  escondido.
- **Acúmulo de papéis (Autor + Gestor + Diretor) na mesma pessoa** significa
  que a mesma pessoa decide o quê, decide o ritmo e decide se o projeto
  continua — sem checagem cruzada entre essas três funções.
- **Cadência mínima de auditoria é compromisso, não garantia**: comprometer
  "ao menos uma vez por trimestre" não impede que, na prática, o autor
  adie — é o próprio critério de reavaliação (§6) que serve de sinal se
  isso acontecer.

### 5.3 O que esta decisão não resolve

- **Não resolve o limite de fundo** (ausência de revisão humana
  independente) — só o mitiga proporcionalmente ao risco atual do
  projeto, no mesmo espírito do precedente (`learn-aviacao-cco-db §7.1`).
- **Não fixa ainda o fluxo de aprovação por tipo de artefato** nem as
  fronteiras de autonomia detalhadas — isso é o SPEC-003, que materializa
  esta decisão.
- **Não decide a pendência D4/D7 do REP-001** (organização de dado,
  separação de ingestão) — assunto de conteúdo técnico, não de
  participação.

---

## 6. Campos estruturantes do SPEC-003

O mínimo que esta DEC fixa para o SPEC-003 formalizar (blueprint DEC-003,
`docs/assets/blueprints/DEC_003.json`):

1. **Modo de participação**: solo. Bruno Alexandre Serminaro acumula
   Autor, Gestor e Diretor.
2. **Freio compensatório em solo**: operação deliberada sem revisão
   humana externa; auditoria recorrente (`gov-check`, regras
   `R-TAX/R-FUN/R-CON` desta fundação) como freio, com gatilho de disparo
   fixado no campo 4.
3. **Cadeia de papéis**: Autor / Gestor / Diretor = Bruno Serminaro
   (acumulados); Par assistivo = Claude, sem autoridade de aprovação;
   Peer Review humano = não previsto; Supervisor de validação = não
   previsto. Atribuição provisória: nenhuma — os papéis vagos são
   formalmente "não previstos", não pendências à espera de nome.
4. **Cadência de revisão e prazo de silêncio**: auditoria de coerência ao
   fim de cada marco relevante (fechamento de bloco de fundação, fase do
   plano Snowflake, fase do plano de expansão), piso de uma vez por
   trimestre mesmo sem marco. **Prazo de silêncio não se aplica**: não há
   Supervisor humano a quem o silêncio deveria valer como aprovação
   automática — a aprovação de qualquer peça é sempre ato ativo do Autor,
   nunca por decurso de prazo.
5. **Gatilho de graduação**: entrada de coautor ou revisor humano
   comprometido; uso ativo do projeto em processo de candidatura/entrevista
   (não hipotético — já conectado a `okr_bruno_azul`/carreira, §1); ou
   surgimento de risco a terceiro (não aplicável hoje). Qualquer um reabre
   esta DEC.

---

## 7. Critérios de reavaliação

Esta decisão deve ser revisitada quando:

- **Surgir terceiro vinculado** (coautor, revisor humano comprometido) —
  gatilho de graduação explícito (§6, campo 5).
- **O projeto for usado ativamente** em candidatura/entrevista, tornando a
  conexão de carreira (§1) concreta em vez de contextual.
- **A cadência mínima de auditoria (§6, campo 4) não rodar de fato** — sinal
  de que o freio compensatório é só nominal, não real.
- **Risco a terceiro surgir** (ex.: dado publicado afetar alguém) — hoje
  não aplicável, dado público sem terceiro dependente.

---

## 8. Histórico

| Data | Evento |
|---|---|
| 2026-08-24 | DEC-003 produzida em status `proposto`. Fixa operação solo (Autor/Gestor/Diretor acumulados por Bruno Serminaro), Claude como par assistivo sem autoridade de aprovação, Peer Review/Supervisor não previstos, e cadência mínima de auditoria por marco (piso trimestral) — diferença deliberada em relação ao precedente `learn-aviacao-cco-db`, justificada pela conexão de carreira já ativa deste projeto. Quatro alternativas avaliadas. Aguardando revisão do autor antes de aprovar e seguir para SPEC-003. |
| 2026-08-24 | **Aprovada.** Revisão contra o blueprint (`DEC_003.json`) sem divergência: sete seções obrigatórias presentes, quatro alternativas com veredito (mínimo 2), consequências negativas nomeiam explicitamente o risco de acúmulo de papéis, critérios de reavaliação incluem o gatilho de graduação exigido, cinco campos estruturantes do SPEC-003 preenchidos (§6). Última DEC da fundação de sete peças — segue para SPEC-003. |
| 2026-09-06 | **Correção pós-aprovação, decisão inalterada (`R-TAX-11`).** A citação de §6 ao blueprint acompanha a mudança de `rascunho/contexto/blueprints/` para `docs/assets/blueprints/`. Motivo registrado na `DEC-001`, mesma data. Nada mais muda. |

---

*Fim do documento.*
