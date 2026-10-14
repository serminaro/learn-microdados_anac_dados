---
documento: SPEC-003
titulo: Contrato de Responsabilidade do Projeto learn-microdados_anac_dados
versao: v1
status: aprovado
data: 2026-08-24
autor: Bruno Alexandre Serminaro
referencia: DEC-003, SPEC-002
escopo: projeto
---

# SPEC-003 · Contrato de Responsabilidade

> Declara quem responde pelo "o quê" e pelo "como" do projeto
> `learn-microdados_anac_dados`: atribuição da cadeia de papéis a pessoas,
> o instrumento de apoio usado (não um papel), o fluxo de aprovação por
> tipo de artefato, fronteiras de autonomia, regime de exceção, cadência de
> revisão e operação em modo degradado. Materializa o **DEC-003**
> (aprovado, 2026-08-24). É a última das sete peças da fundação
> (DEC-META-014 §2.1).

---

## 1. Propósito

O SPEC-002 declarou os papéis em abstrato (§2: Autor, Par assistivo, Autor
futuro, Leitor do repositório). Este contrato os preenche com pessoas,
fixa como o trabalho flui e o que cada papel decide sozinho. A separação é
proposital: os demais documentos (DEC, SPEC, REP) referem-se a papel
abstrato, não a nome próprio — uma eventual entrada de terceiro não força
reescrever SPEC-001/002 nem qualquer DEC já aprovada.

---

## 2. Escopo do contrato

Governa a produção e aprovação dos artefatos formais previstos no SPEC-001
(DEC, SPEC, REP, GUIDE, BRIEF, AUDIT) neste projeto.

Não governa a execução técnica fora do alcance documental — escrever e
rodar código, depurar pipeline, manter ambiente, conversas exploratórias.
Essas atividades seguem a competência operacional direta do Autor.

---

## 3. Atribuição papel-pessoa

### 3.1 Cadeia de papéis

| Papel | Pessoa | Observação |
|---|---|---|
| **Autor** | Bruno Alexandre Serminaro | Produz os artefatos e o código; responde pela execução e pela aplicação dos critérios do SPEC-002. |
| **Gestor** | Bruno Alexandre Serminaro | Acumula com Autor (DEC-003 §2). Define ritmo e prioridade entre os 3 datasets e os 2 caminhos. |
| **Diretor** | Bruno Alexandre Serminaro | Acumula com Gestor. Decide continuidade, redirecionamento ou encerramento do projeto. |
| **Supervisor de validação** | — (não previsto) | Formalmente não previsto, não vago (DEC-003 §6, campo 3). Dispensado nesta fase pelo mesmo critério de risco baixo/sem terceiro afetado. |
| **Peer Review humano** | — (não previsto) | Idem. Nomeação é gatilho de graduação (DEC-003 §6, campo 5), não pendência com prazo. |

**Sobre o acúmulo Autor + Gestor + Diretor**: é deliberado, registrado com
alternativa e consequência no DEC-003 §4-5, não default não examinado. A
mesma pessoa decide o quê, decide o ritmo e decide se o projeto continua,
sem checagem cruzada entre essas três funções — risco nomeado
explicitamente, não escondido (DEC-003 §5.2).

### 3.2 IA de apoio: instrumento, não papel

A IA de apoio (Claude Code) **não ocupa papel na cadeia acima**. É
instrumento que o Autor usa para apoiar redação, pesquisa e implementação
técnica — a mesma relação que o Autor tem com qualquer outra ferramenta do
projeto (Snowflake CLI, editor, linter). A IA de apoio:

- **Nunca aprova artefato.** Toda transição de `proposto` para `aprovado`
  é ato do Autor, registrado no histórico do próprio artefato.
- **Nunca decide divergência de auditoria.** Quando o `gov-check` apontar
  achado, a escolha entre atualizar o documento ou corrigir o código é do
  Autor.
- **Revisa e sugere.** Nas sete peças desta fundação, a IA de apoio
  revisou cada uma contra seu blueprint antes da aprovação (ver Histórico
  de cada DEC/SPEC) — função de instrumento de revisão, não de aprovador.

### 3.3 Mudança de atribuição

Nomeação de pessoa em papel hoje "não previsto" (Supervisor, Peer Review)
exige nova versão desta SPEC, com entrada no Histórico (papel, pessoa,
data). Por os demais documentos citarem papel abstrato, eles seguem
válidos sem alteração quando isso acontecer (R-CON-05).

---

## 4. Fluxo de aprovação por tipo de artefato

| Tipo | Etapas | Aprovação final |
|---|---|---|
| **DEC, SPEC** | Autor produz em `proposto`; IA de apoio revisa contra o blueprint quando acionada (recomendado para peças de fundação e DECs de conteúdo relevantes) | Autor |
| **REP, GUIDE** | Autor produz; revisão da IA de apoio opcional | Autor |
| **BRIEF (README)** | Autor produz; revisão da IA de apoio recomendada (é a vitrine pública) | Autor |
| **AUDIT** | Gerado pelo skill `gov-check`, sem DEC prévia (DEC-META-014 §2.4); Autor decide o que fazer com cada achado | Autor decide a resposta a cada achado; o AUDIT em si não é "aprovado", é registrado |

A revisão pela IA de apoio é **norma de trabalho do projeto**, não regra
rígida com sanção própria: sua ausência não dispara `R-CON`, mas cada
DEC/SPEC desta fundação já a registrou no próprio Histórico (prática, não
só norma).

---

## 5. Fronteiras de autonomia

| Papel | Decide sozinho |
|---|---|
| **Autor** | Produzir e aprovar qualquer artefato; decisões de execução técnica (código, schema, scripts); declarar DEC quando a decisão for não-trivial; pausar/retomar o trabalho; priorizar entre datasets e caminhos (Gestor). |
| **Diretor (= Autor)** | Encerrar ou redirecionar o projeto, registrado em REP ou DEC. |
| **IA de apoio** | Nada por autoridade própria (§3.2). Propõe, revisa, implementa sob instrução; a decisão de aceitar é sempre do Autor. |

Calibração de pedido de autorização (herdada do modo de trabalho do
Autor com a IA de apoio, já em prática nesta sessão): ações exploratórias
e reversíveis seguem sem confirmar prévia; ações que mudam estrutura,
afetam arquivo já em uso, ou têm efeito externo (commit, push) param para
confirmar. Essa calibração não é regra nova desta SPEC — já era o padrão
observado ao longo de toda esta fundação (cada aprovação de DEC/SPEC foi
ato explícito do Autor, cada commit foi pedido à parte).

---

## 6. Regime de exceção

Não há prazo externo (cliente, contrato) que justifique regime de
urgência formal. Se uma decisão precisar de velocidade fora do ritmo
normal (ex.: fonte da ANAC mudar de formato sem aviso, quebrando o
pipeline em produção), **o Autor declara a exceção no próprio artefato
afetado** (DEC ou nota no README), registrando o motivo e a data — não
existe um papel Supervisor a notificar, então não há fluxo de escalonamento
a seguir.

---

## 7. Cadência de revisão

Diferente do precedente `learn-aviacao-cco-db` (auditoria puramente ad
hoc), este projeto compromete uma **cadência mínima**, fixada no DEC-003
§6 campo 4: auditoria de coerência (`gov-check`) ao fim de cada marco
relevante — fechamento de bloco desta fundação, fechamento de fase do
plano Snowflake (`docs/plano_objetos_snowflake.md`), fechamento de fase do
plano de expansão (`docs/plano_expansao_multidataset.md`) — com **piso de
uma vez por trimestre** mesmo sem marco.

**Prazo de silêncio**: não se aplica. Não há Supervisor humano a quem o
silêncio deveria valer como aprovação automática (§3.1) — toda aprovação é
sempre ato ativo do Autor, nunca por decurso de prazo (mesmo princípio do
precedente).

---

## 8. Operação em modo degradado

O projeto opera, desde sua origem, sem revisão humana externa — não é
modo degradado a corrigir em prazo, é o regime normal aceito para um
projeto solo de baixo risco (DEC-003 §2, §5).

**Freio compensatório**: auditoria recorrente via skill `gov-check`,
contra as regras `R-TAX-NN` (SPEC-001), `R-FUN-NN` (SPEC-002) e `R-CON-NN`
(esta SPEC, §9). A cadência mínima é a do §7.

**Estado atual do freio**: exercido. A primeira rodada (`AUDIT-001`,
2026-08-25) foi disparada pelo fechamento da fundação; a segunda
(`AUDIT-002`, 2026-10-14), pela incorporação à `main` das linhas de análise
a2 a a6. O registro de cada rodada e a próxima data prevista vivem em
`docs/AUDIT/INDEX_AUDIT.md`, não aqui, para que este parágrafo não volte a
envelhecer.

---

## 9. Regras checáveis (R-CON)

| ID | Regra | Onde verificar | Severidade |
|---|---|---|---|
| **R-CON-01** | Cada papel da §3.1 tem pessoa atribuída **ou** marca explícita de "não previsto". Ausência de registro sinaliza divergência. | Inspeção da §3.1 | Média |
| **R-CON-02** | Cada artefato `aprovado` tem registro no Histórico de quem aprovou (sempre o Autor) e, quando houve, da revisão da IA de apoio. | Histórico de cada artefato | Alta |
| **R-CON-03** | A IA de apoio não consta como aprovador de nenhum artefato nem como ocupante de papel na cadeia do §3.1 (§3.2). Registro de "aprovado por Claude" ou de Claude como papel sinaliza violação do contrato. | Inspeção dos históricos e da §3.1 | Alta |
| **R-CON-04** | Esta SPEC e a SPEC-002 referenciam-se mutuamente: SPEC-002 §2 cita esta SPEC para atribuição de pessoa; esta SPEC referencia a SPEC-002 para os papéis abstratos. | Inspeção de `referencia:` e §2 de cada uma | Média |
| **R-CON-05** | Nomeação de pessoa em papel hoje "não previsto" corresponde a nova versão desta SPEC, com entrada no Histórico (§3.3). Edição silenciosa da §3.1 sinaliza divergência. | Diff da §3.1 + histórico de versão | Média |
| **R-CON-06** | A cadência mínima de auditoria do §7 (piso trimestral, ou por marco) é verificável por data do último `AUDIT` em `docs/AUDIT/` (quando existir) contra a data corrente. Atraso além do piso sinaliza que o freio compensatório é nominal, não real. | `docs/AUDIT/INDEX_AUDIT.md` × data corrente | Alta |
| **R-CON-07** | Documento REP/SPEC/BRIEF/GUIDE `aprovado` cita, no `referencia:`, a DEC que o motiva (rastro DEC obrigatório, DEC-META-014 §2.4, AUDIT isento). | Campo `referencia:` de cada peça não-DEC/AUDIT | Média |

---

## 10. Limitações conhecidas

- **Ausência de freio humano externo continua sendo o limite de fundo**
  (DEC-003 §5.2), não resolvido por este contrato — só mitigado
  proporcionalmente ao risco atual do projeto (baixo: sem terceiro
  dependente, dado público sob licença aberta).
- **A cadência do §7 é compromisso, não garantia mecânica.** Nada nesta
  SPEC impede o Autor de adiar; `R-CON-06` só torna o atraso *visível*
  numa auditoria, não o impede de acontecer.
- **`docs/AUDIT/` ainda não existe** — será criado quando a primeira
  auditoria rodar (§8). Até lá, `R-CON-06` não tem histórico para
  verificar; isso não é falha desta SPEC, é o estado esperado antes do
  primeiro marco.
- Este contrato não resolve a pendência D4/D7 do REP-001 (organização de
  dado, separação de ingestão) — não é matéria de participação.

---

## 11. Critérios de revisão

Revisitar esta SPEC quando:

- Qualquer gatilho de graduação do DEC-003 §6 (campo 5) se materializar —
  entrada de terceiro vinculado, uso ativo em candidatura/entrevista, ou
  risco a terceiro.
- A cadência mínima do §7 não rodar de fato, revelado por `R-CON-06`.
- Mudar a atribuição de qualquer papel do §3.1 (nova versão, per §3.3).
- `SPEC-002` for revisada de forma que mude os papéis abstratos que esta
  SPEC atribui.

---

## 12. Histórico

| Data | Evento |
|---|---|
| 2026-08-24 | SPEC-003 v1 produzida em status `proposto`. Última peça da fundação de sete (DEC-META-014). Materializa o DEC-003 (aprovado): operação solo (Autor/Gestor/Diretor acumulados por Bruno Serminaro), IA de apoio declarada instrumento — não papel — sem autoridade de aprovação (§3.2, diferença de framing em relação ao precedente `learn-aviacao-cco-db`, que listava o par assistivo como papel), cadência mínima de auditoria por marco com piso trimestral (§7, diferença material do precedente), 7 regras `R-CON-NN`. Aguarda aprovação do autor — ao aprovar, a fundação de sete peças fica completa. |
| 2026-10-14 | §8, "Estado atual do freio", corrigido: dizia que o `gov-check` ainda não tinha rodado, o que deixou de ser verdade em 2026-08-25 (`AUDIT-001`). Passa a apontar para `INDEX_AUDIT.md` como registro vivo. Achado A2 do `AUDIT-002`. Status e versão inalterados; nenhuma regra, papel ou cadência muda. |
| 2026-10-14 | **Aprovada pelo autor** (Bruno Alexandre Serminaro), na sessão do `AUDIT-002` (§3.2), depois da correção do §8. Com ela, a fundação de sete peças (DEC-META-014) fica completa. Versão inalterada (v1): a aprovação não muda conteúdo. A IA de apoio redigiu a correção do §8 e não aprova (§3.2). |

---

*Fim do documento.*
