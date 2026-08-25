---
documento: SPEC-001
titulo: Taxonomia Documental do Projeto learn-microdados_anac_dados
versao: v1
status: aprovado
data: 2026-08-24
autor: Bruno Alexandre Serminaro
referencia: DEC-001
escopo: projeto
---

# SPEC-001 · Taxonomia Documental do Projeto learn-microdados_anac_dados

> Instancia, neste projeto, a taxonomia documental canônica **SERMI**
> (`SPEC-META-001`, `serminaro-governance/_meta`), conforme fixado pelo
> **DEC-001** (fundação sob SERMI, aprovado em 2026-08-24). Define quais
> tipos de documento o projeto usa, o frontmatter obrigatório, a convenção
> de nomes e pastas, e as regras checáveis `R-TAX-NN` que a auditoria de
> coerência (`gov-check`) verifica contra o estado real do repositório.
> Governa documentação, não código-fonte — a convenção de nomes para
> arquivo de código (`BASH`/`SRC`/`DDL`/`DML`/`NOTE`/`R`) está em
> `DEC-001 §6.6`, fora do escopo desta SPEC por decisão explícita do DEC-001
> (§6.5).

---

## 1. Propósito

Esta taxonomia governa a documentação do projeto `learn-microdados_anac_dados`:
o que cada tipo de documento é para, quem o lê, quando nasce, e como fica
localizável e auditável ao longo do tempo. Existe para que decisão,
descrição e narrativa não se misturem no mesmo arquivo — sintoma que o
projeto já tinha antes desta fundação, com `docs/plano_objetos_snowflake.md`
e `docs/plano_expansao_multidataset.md` acumulando plano técnico, decisão
implícita e registro de progresso no mesmo documento (ver REP-001 §3).

---

## 2. Tipos de documento em uso

Os seis tipos da taxonomia SERMI, todos adotados (decisão do DEC-001 §6.2):

| Tipo | Função primária | Audiência primária | Uso neste projeto |
|---|---|---|---|
| **DEC** | Documentar uma decisão: alternativas, consequências, critério de reavaliação | Todos, ênfase em rastreabilidade | Decisões de arquitetura: engines, camadas, corte temporal, organização de dado, convenção de nomenclatura |
| **SPEC** | Descrever o que algo é e como funciona | Autor futuro, mantenedor, leitor técnico | As três de fundação (esta, SPEC-002, SPEC-003) e SPECs de conteúdo futuras (ex.: modelagem dimensional do star schema, Fase D do plano Snowflake) |
| **REP** | Narrar o que aconteceu, com profundidade | Autor, leitor técnico interessado em processo | Síntese da fundação (REP-001) e sínteses de marco futuras (ex.: fechamento de fase do plano Snowflake) |
| **GUIDE** | Descrever como operar algo, passo a passo | Quem executa o procedimento, incl. o autor | Procedimentos recorrentes quando o `README.md` não bastar (ex.: "como rodar o pipeline de um dataset do zero") |
| **BRIEF** | Comunicar estado e valor em alto nível | Visitante do repositório, recrutador, público | `README.md` como BRIEF vitrine (SPEC-META-001 §6.4); BRIEFs de marco sob demanda, sem cadência periódica fixa |
| **AUDIT** | Registrar auditoria de coerência | Autor, freio compensatório da ausência de revisão externa | Gerado pelo skill `gov-check`, sem DEC prévia (isento pela DEC-META-014 §2.4); recomendado desde cedo em projeto solo |

Nenhum tipo fica de fora. A divisão é exaustiva: documento que não cabe em
nenhum dos seis, ou que parece caber em vários ao mesmo tempo, é revisado e
segmentado antes de entrar no acervo — mesmo princípio operacional da
SPEC-META-001 §1.2 ("cada documento tem uma função e uma audiência
primária").

---

## 3. Frontmatter obrigatório

Todo documento `.md` tipado (exceto `INDEX_<TIPO>.md`) abre com:

```yaml
---
documento: <SIGLA-NNN>            # DEC-001, SPEC-002, REP-001, ...
titulo: <Título do documento>
versao: <v1, v2, ...>              # obrigatório em SPEC; demais tipos conforme SPEC-META-001 §8.5
status: <proposto | aprovado | superseded | descartado>
data: <AAAA-MM-DD>
autor: <nome>
supersede: <SIGLA-NNN ou —>        # quando aplicável (DEC que substitui outra)
referencia: <SIGLA-NNN ou —>       # a DEC que motiva o documento (§7, R-TAX-06)
escopo: <projeto>                  # este projeto não usa pessoal/meta
---
```

Numeração local (sem prefixo de escopo): `DEC-001`, `SPEC-001`, não
`DEC-ANAC-001` (DEC-001 §6.1).

---

## 4. Convenção de nomes e numeração

| Tipo | Padrão de nome | Exemplo |
|---|---|---|
| DEC | `DEC_NNN_descricao_curta.md` | `DEC_001_Fundacao_sob_SERMI.md` |
| SPEC | `SPEC_NNN_descricao_curta.md` | `SPEC_001_Taxonomia_Documental.md` |
| REP | `REP_NNN_descricao_curta.md` | `REP_001_Sintese_da_Fundacao.md` |
| GUIDE | `GUIDE_NNN_descricao_curta.md` | `GUIDE_001_Rodar_Pipeline_Basica.md` |
| BRIEF de marco | `BRIEF_NNN_descricao_curta.md` | `BRIEF_001_Fechamento_Fase_A.md` |
| BRIEF vitrine | `README.md` | `README.md` |
| AUDIT | `AUDIT_NNN_descricao_curta.md` | `AUDIT_001_pos_fundacao.md` |

Numeração sequencial dentro de cada tipo, **nunca reutilizada**: documento
descartado ou `superseded` mantém o número. O campo `documento:` do
frontmatter sempre bate com o número no nome do arquivo (R-TAX-03).

---

## 5. Estrutura de pastas

Padrão default de projeto com repositório próprio (SPEC-META-001 §8.4,
fixado pelo DEC-001 §6.3):

```
docs/
├── DEC/        INDEX_DEC.md obrigatório — já existe, 1 DEC aprovada
├── SPEC/       INDEX_SPEC.md recomendado a partir de ~10 documentos — ainda não necessário
├── REP/
├── GUIDE/      criada quando o primeiro GUIDE nascer
├── BRIEF/      criada quando o primeiro BRIEF de marco nascer (README já cumpre o papel de vitrine)
├── AUDIT/      INDEX_AUDIT.md recomendado desde cedo em projeto solo — criar ao primeiro AUDIT
├── assets/     quando houver ativo a versionar (ex.: diagrama do star schema)
├── plano_objetos_snowflake.md          pré-SERMI, solto na raiz de docs/, não retrofitado (DEC-001 §5.3)
└── plano_expansao_multidataset.md      pré-SERMI, idem
```

Os dois documentos de plano pré-SERMI permanecem como estão, fora da
subpasta por tipo — não são peça SERMI, não têm frontmatter, não entram nas
regras `R-TAX-NN` desta SPEC. Migração para peça formal, se e quando fizer
sentido, é por oportunidade (mesmo padrão da `DEC-META-005` no `_meta`),
sem prazo forçado.

`scripts/`, `src/`, `sql/`, `notebook/`, `r/` (quando existir) são estrutura
de código-fonte e dado, não de documentação — regidos pela convenção do
DEC-001 §6.6, não por esta SPEC.

---

## 6. Formato canônico

Todo documento nasce em **Markdown**, versionável por Git, com diff
legível. `.docx`/`.pdf` são derivados eventuais, nunca a fonte. Este
projeto não tem, até o momento, necessidade de derivado — registrado aqui
para o caso de vir a existir (ex.: exportar uma SPEC para leitura offline).

---

## 7. Regras checáveis (R-TAX)

| ID | Regra | Onde verificar | Severidade |
|---|---|---|---|
| **R-TAX-01** | Todo `.md` tipado em `docs/<TIPO>/` (exceto `INDEX_<TIPO>.md`) tem frontmatter YAML com os campos da §3. | Parse do frontmatter | Alta |
| **R-TAX-02** | Nome de arquivo obedece o padrão da §4 por tipo; sem sufixo de versão incrustado no nome (`_v1.md`). | Listagem de `docs/<TIPO>/` vs. regex | Alta |
| **R-TAX-03** | Numeração sequencial dentro de cada tipo, sem reuso; o número do campo `documento:` bate com o do nome do arquivo. | Cruzamento nome × `documento:` | Crítica |
| **R-TAX-04** | `status` pertence a `{proposto, aprovado, superseded, descartado}`. | Parse do campo `status` | Média |
| **R-TAX-05** | Toda DEC com `status: aprovado` contém as sete seções obrigatórias (Contexto, Decisão, Origem ou rastro, Alternativas ≥ 2, Consequências com negativas, Critérios de reavaliação, Histórico). | Parse estrutural de cada DEC aprovada | Alta |
| **R-TAX-06** | Rastro DEC obrigatório: todo SPEC, REP, BRIEF e GUIDE cita, no `referencia:`, a DEC que registra as escolhas que o motivam (AUDIT isento). DEC-META-014 §2.4. | Campo `referencia:` | Média |
| **R-TAX-07** | `docs/DEC/INDEX_DEC.md` existe e lista todas as DECs presentes em `docs/DEC/`, nas tabelas corretas (ativas/proposta/superseded/descartadas). | Cruzamento arquivos × índice | Média |
| **R-TAX-08** | As sete peças de fundação (DEC-001, SPEC-001, REP-001, DEC-002, SPEC-002, DEC-003, SPEC-003) existem e se referenciam mutuamente conforme a ordem generativa da §11A.1 (SPEC-META-001). | Listagem de `docs/DEC/` + `docs/SPEC/` + `docs/REP/` × `referencia:` | Crítica |
| **R-TAX-09** | Documento `superseded` é referenciado por `supersede:` de um sucessor existente, e vice-versa. | Inspeção de `supersede:` | Alta |
| **R-TAX-10** | `docs/plano_objetos_snowflake.md` e `docs/plano_expansao_multidataset.md` são exceção documentada (§5): não exigem frontmatter SERMI nem numeração de tipo. Ausência de frontmatter nesses dois arquivos especificamente **não** é divergência. | Lista fixa de exceções desta SPEC | Baixa |

Regra que a `SPEC-META-001 §11A.2` pede e este projeto não precisa
declarar à parte: o AUDIT nasce de gatilho de controle, não de DEC prévia
— já coberto pela isenção explícita da R-TAX-06.

---

## 8. Limitações conhecidas

- Esta SPEC não cobre convenção de código-fonte (scripts, SQL, notebooks,
  R) — está no DEC-001 §6.6, por decisão explícita de não elevar arquivo de
  código a peça SERMI.
- Não define ainda a numeração de SPECs de conteúdo futuras (ex.: Modelo de
  Dados / star schema) além de reservar a sequência a partir de `SPEC-004`
  (§9) — o mapa exato só se materializa quando cada peça nascer.
- Não resolve se/quando os dois planos pré-SERMI migram para peça formal
  (DEC-001 §5.3); a exceção da R-TAX-10 é válida enquanto essa migração não
  acontecer, não uma isenção permanente por princípio.
- As regras `R-TAX-NN` desta SPEC ainda não foram testadas por uma rodada
  real do skill `gov-check` sobre este projeto — a primeira auditoria pode
  revelar ambiguidade de interpretação que exija ajuste (§10).

---

## 9. Números reservados de fundação

| Número reservado | Peça |
|---|---|
| **DEC-001** | Fundação sob SERMI (aprovada, 2026-08-24) |
| **SPEC-001** | Taxonomia Documental (esta) |
| **REP-001** | Síntese da Fundação |
| **DEC-002** | Decisões de descrição |
| **SPEC-002** | Descrição do Projeto |
| **DEC-003** | Decisão de participação |
| **SPEC-003** | Contrato de Responsabilidade |

`SPEC-004` em diante e `DEC-004` em diante ficam livres para peças de
conteúdo futuras (ex.: SPEC de modelagem dimensional do star schema, DEC de
adoção de engine para uma fase específica do plano Snowflake).

---

## 10. Critérios de revisão

Revisitar esta SPEC quando:

- Aparecer documento que não cabe em nenhum dos seis tipos, ou que cabe em
  mais de um simultaneamente.
- A estrutura de pastas da §5 mudar (novo tipo de ativo, nova exceção).
- `SPEC-META-001` for revisada de forma que afete frontmatter, numeração ou
  a fundação de sete peças.
- A primeira rodada do skill `gov-check` sobre este projeto apontar
  ambiguidade nas regras `R-TAX-NN` que impeça verificação automática.
- O DEC-001 for superseded por uma DEC nova que revise a adoção do SERMI.

---

## 11. Histórico

| Data | Evento |
|---|---|
| 2026-08-24 | SPEC-001 v1 produzida em status `proposto`. Instancia a SPEC-META-001 para este projeto, conforme fixado pelo DEC-001 (aprovado). Dez regras `R-TAX-NN` declaradas. Produzida junto com REP-001, no mesmo bloco de trabalho, com SPEC-001 finalizada primeiro (DEC-META-014 §2.1). Aguarda aprovação do autor. |
| 2026-08-24 | **Aprovada.** Revisão contra o blueprint (`SPEC_001.json`) sem divergência: todas as dez seções obrigatórias presentes, cada regra `R-TAX-NN` com id/enunciado/onde-verificar/severidade, rastro `referencia: DEC-001` coerente com a regra R-TAX-06 que a própria SPEC declara. Segue para DEC-002. |

---

*Fim do documento.*
