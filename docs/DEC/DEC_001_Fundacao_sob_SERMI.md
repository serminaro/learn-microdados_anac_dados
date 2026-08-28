---
documento: DEC-001
titulo: Fundação do projeto learn-microdados_anac_dados sob a governança documental SERMI
versao: v1
status: aprovado
data: 2026-08-24
autor: Bruno Alexandre Serminaro
referencia: —
escopo: projeto
---

# DEC-001 · Fundação sob SERMI

> Funda `learn-microdados_anac_dados` sob a taxonomia documental SERMI, na
> forma atual de sete peças em ordem generativa decisão-primeiro
> (DEC-META-014): DEC-001 → SPEC-001 → REP-001 → DEC-002 → SPEC-002 →
> DEC-003 → SPEC-003. Fixa o mínimo que estrutura o SPEC-001: escopo de
> numeração local, os seis tipos de documento adotados, a estrutura de
> pastas `docs/<TIPO>/`, e as três famílias de regra checável (R-TAX,
> R-FUN, R-CON) distribuídas por SPEC-001/002/003. Fixa também, como adendo
> específico deste projeto e não um dos cinco campos do blueprint, a
> convenção de nomes `TIPO_NNN_descricao_curta` para arquivo de
> código-fonte (não peça SERMI) — BASH/SRC/DDL/DML/NOTE/R, prospectiva,
> incluindo a separação física de ingestão SQLite e Snowflake (§6.6).

---

## 1. Contexto

### Situação até aqui

`learn-microdados_anac_dados` existe desde antes desta decisão: consolida a
tabela Básica da ANAC (2024-2026) em SQLite e réplica no Snowflake, com
plano técnico próprio já em andamento (`docs/plano_objetos_snowflake.md`,
fases A-H, Fase A concluída em 2026-08-11). Repositório público no GitHub,
licença MIT. Até esta decisão, o projeto era informal: sem SPEC, sem DEC,
decisões de arquitetura registradas em prosa dentro de documentos de plano
ad hoc, não numa taxonomia com alternativas e consequências explícitas.

Em 2026-08-24, dentro da mesma sessão que motiva esta fundação, o escopo do
projeto mudou de forma material: de 1 dataset para 3 (Básica, VRA, SIROS),
e de um caminho de produção para dois, igualmente investidos (Snowflake
medalhão e SQLite+Python), cada um com camada ouro e dashboard próprios.
Essa expansão está registrada em `docs/plano_expansao_multidataset.md`, mas
como plano informal — sem o registro de alternativas descartadas nem de
critérios de reavaliação que uma DEC exige.

### Por que decidir agora

A expansão de escopo é o gatilho, não um pretexto. Numa sessão só, o projeto
acumulou decisões de arquitetura real (corte temporal 2010, organização de
SQLite por dataset, convenção de nomenclatura, paridade de investimento
entre dois caminhos de produção) que hoje só existem em prosa e na memória
de sessão da IA de apoio — sem rastro formal reproduzível por um leitor
futuro, incluindo o próprio autor. Isso é exatamente o sintoma que a
taxonomia SERMI existe para resolver (SPEC-META-001 §1.1), e o ponto em que
o custo de continuar informal passa a exceder o custo de fundar
formalmente (princípio "o custo da ausência é maior que o custo da
presença", SPEC-META-001 §11.6).

O pedido de fundação partiu do autor, explicitamente referenciando
`serminaro-governance/_meta` como fonte da taxonomia a seguir.

---

## 2. Decisão

**Fundar `learn-microdados_anac_dados` sob a taxonomia documental SERMI,
na forma de sete peças em ordem decisão-primeiro fixada pela DEC-META-014,
com escopo de numeração local.**

---

## 3. Origem ou rastro

- `rascunho/CONTEXTO_DO_PROJETO.txt` (produzido nesta mesma sessão,
  2026-08-24): destila o histórico real do projeto — commits, docs
  técnicos já existentes, e a expansão de escopo desta sessão — como
  matéria-prima desta decisão.
- `rascunho/MEMORIA.txt` §5 (Fatos duráveis): registra as cinco decisões já
  tomadas informalmente nesta sessão (D1-D5) que esta DEC e as seguintes
  (DEC-002, DEC-003) formalizam.
- `docs/plano_objetos_snowflake.md` e `docs/plano_expansao_multidataset.md`:
  os dois documentos de plano já existentes cujo conteúdo motivou a
  percepção de que o projeto tinha crescido além do que a informalidade
  sustenta.
- Precedente direto no ecossistema pessoal do autor: `learn-aviacao-cco-db`
  (projeto-irmão já formalmente governado, embora sob a fundação antiga de
  cinco peças) e `serminaro-governance/_meta` (onde a fundação de sete
  peças foi fixada pela DEC-META-014, 2026-07-19).

---

## 4. Alternativas consideradas

### 4.1 Continuar informal (status quo)

Não adotar SERMI; manter decisões registradas em prosa dentro de documentos
de plano ad hoc (`docs/plano_*.md`), como já vinha sendo feito.

**Por que descartada.** A própria expansão de escopo que motiva esta DEC já
mostrou o limite do formato: cinco decisões de arquitetura real (D1-D5,
`rascunho/MEMORIA.txt` §5) foram tomadas numa sessão sem alternativa
descartada registrada, sem critério de reavaliação, e sem rastro
reproduzível fora da conversa que as gerou. Continuar assim significa que a
próxima expansão de escopo — plausível, dado o ritmo do projeto — repete o
mesmo problema em escala maior. Como o projeto também é peça de portfólio
público, a ausência de rastro decisório é uma lacuna visível para quem
avalia competência de engenharia de dados/governança, não só um
inconveniente interno.

### 4.2 Governança formal só para o caminho Snowflake

Adotar SERMI apenas para as decisões do Caminho 1 (Snowflake medalhão),
deixando o Caminho 2 (SQLite+Python) informal, no argumento de que
Snowflake é a competência técnica mais avançada em jogo.

**Por que descartada.** A decisão de que os dois caminhos são igualmente de
produção (D2) já invalida essa divisão: seria preciso decidir, para cada
nova escolha (ex.: corte temporal D3, organização de banco D4), se ela
"pertence" a um caminho ou aos dois — na prática quase todas afetam os dois
simultaneamente, porque compartilham a mesma etapa de download bruto
(`rascunho/MEMORIA.txt` §5, P2). Fragmentar a governança por caminho
duplicaria trabalho sem reduzir risco.

### 4.3 Repositório de governança separado

Criar um repositório novo, só para as peças SERMI deste projeto, mantendo
`learn-microdados_anac_dados` como repositório só de código/dado.

**Por que descartada.** Quebra o precedente já estabelecido no ecossistema
pessoal do autor: `learn-aviacao-cco-db`, o projeto-irmão mais próximo em
natureza (projeto autoral, portfólio público, aprendizado técnico), mantém
suas peças SERMI dentro do próprio repositório (`docs/DEC/`, `docs/SPEC/`).
Separar aqui criaria uma exceção sem motivo técnico, só overhead de
navegação entre dois repositórios para entender um projeto só.

### 4.4 Fundar sob SERMI, sete peças, dentro do próprio repositório (decisão atual)

`docs/DEC/`, `docs/SPEC/`, `docs/REP/`, `docs/GUIDE/`, `docs/BRIEF/`,
`docs/AUDIT/` dentro do repositório já existente, escopo de numeração
local, seguindo a ordem generativa decisão-primeiro da DEC-META-014.

**Adotada.** Resolve a lacuna de rastro (4.1) sem fragmentar por caminho
(4.2) e sem quebrar o precedente do ecossistema (4.3). Path de menor
resistência: os documentos de plano já existentes (`docs/plano_*.md`)
continuam onde estão, coexistindo com a estrutura nova sem retrofit
obrigatório imediato (ver §6.3).

---

## 5. Consequências

### 5.1 Positivas

- As cinco decisões já tomadas informalmente nesta sessão (D1-D5) ganham
  registro formal com alternativas descartadas e critério de reavaliação,
  a começar por esta própria DEC e pelas DEC-002/DEC-003 que virão.
- Alinha o projeto ao padrão já praticado no ecossistema pessoal do autor
  (`learn-aviacao-cco-db`, `serminaro-governance`), permitindo auditoria
  cruzada pelas mesmas skills (`gov-check`).
- Reforça o valor de portfólio público: rastro decisório documentado é
  evidência direta de competência de governança de dados, o mesmo eixo que
  o projeto já pratica tecnicamente via Snowflake.
- Fecha uma lacuna que tende a piorar, não melhorar, se adiada — o projeto
  está em expansão ativa, não estável.

### 5.2 Negativas

- **Overhead de manutenção real**, que o projeto não tinha antes: cada
  decisão de arquitetura relevante (não toda decisão) passa a exigir uma
  DEC, com alternativas e consequências negativas explícitas. Mitigado pela
  calibração de profundidade (SPEC-META-001 §11.7; INSTRUCAO_DE_TRABALHO.txt
  §5): a regra é sobre existência da peça, não sobre tamanho.
- **Risco de DEC cerimonial**, se a disciplina virar ritual sem reflexão
  real — o próprio corpus SERMI já vigia esse sintoma (DEC-META-014 §8).
  Mitigado por revisão crítica de cada DEC antes de aprovar (não só
  produzir).
- **Sete peças de fundação antes de qualquer execução técnica nova**: mais
  atrito inicial do que o projeto-irmão teve (que fundou sob o padrão antigo
  de cinco peças). Aceito: adotar a forma antiga agora significaria migrar
  depois, quando a DEC-META-014 já é o canon vigente desde 2026-07-19.

### 5.3 O que esta decisão não resolve

- **Não decide o conteúdo do SPEC-002** (escopo formal, critérios de
  sucesso C-NN, não-objetivos) — isso é o DEC-002, que vem depois de
  SPEC-001 e REP-001 existirem.
- **Não decide o conteúdo do SPEC-003** (papéis, cadência de revisão, modo
  degradado) — isso é o DEC-003.
- **Não decide se e quando `docs/plano_objetos_snowflake.md` e
  `docs/plano_expansao_multidataset.md` migram para a taxonomia formal.**
  Ficam como estão, documentos de plano informais coexistindo com as peças
  SERMI, migração por oportunidade (mesmo padrão que a DEC-META-005 já usa
  no `_meta` para fundações antigas) — sem prazo forçado.
- **Não fixa ainda os cinco campos estruturantes do SPEC-001 em documento
  próprio** — ficam fixados abaixo, no corpo desta DEC, e o SPEC-001 os
  formaliza no bloco seguinte de trabalho.

---

## 6. Campos estruturantes do SPEC-001

O mínimo que esta DEC fixa para o SPEC-001 formalizar (blueprint DEC-001,
`rascunho/contexto/blueprints/DEC_001.json`):

### 6.1 Nome do projeto e escopo de numeração

`learn-microdados_anac_dados`, escopo **local** (repositório próprio, sem
prefixo): `DEC-001`, `SPEC-001`, não `DEC-ANAC-001`.

### 6.2 Tipos de documento usados

Os seis tipos da taxonomia, todos adotados — nenhum fica de fora:

| Tipo | Uso previsto neste projeto |
|---|---|
| DEC | Decisões de arquitetura: engines, camadas, corte temporal, organização de dado, convenção de nomenclatura. |
| SPEC | As três de fundação (taxonomia, descrição, contrato) e futuras, se o projeto especificar algo estrutural novo (ex.: modelagem dimensional). |
| REP | Síntese da fundação (REP-001) e sínteses futuras de marco (ex.: fechamento de uma fase do plano Snowflake). |
| GUIDE | Procedimentos operacionais recorrentes (ex.: "como rodar o pipeline de um dataset do zero"), quando o `README.md` não bastar. |
| BRIEF | O próprio `README.md` já cumpre o papel de BRIEF vitrine (SPEC-META-001 §6.4); BRIEFs de marco ficam disponíveis para fechamentos de fase relevantes. |
| AUDIT | Recomendado desde cedo em projeto solo (SPEC-META-001 §10) — é o rastro do freio compensatório da ausência de revisão humana externa (ver DEC-003, a decidir). Gerável por skill (`gov-check`), sem DEC prévia. |

### 6.3 Estrutura de pastas e convenção de nomes

Padrão default de projeto com repositório próprio (SPEC-META-001 §8.4):

```
docs/
├── DEC/       (com INDEX_DEC.md, obrigatório)
├── SPEC/      (com INDEX_SPEC.md quando volumoso)
├── REP/
├── GUIDE/
├── BRIEF/
├── AUDIT/     (com INDEX_AUDIT.md)
└── assets/    (quando houver ativo a versionar)
```

Nomes: `DEC_NNN_descricao_curta.md`, `SPEC_NNN_descricao_curta.md`, etc.
(SPEC-META-001 §8.3), numeração sequencial nunca reutilizada.

`docs/plano_objetos_snowflake.md` e `docs/plano_expansao_multidataset.md`
permanecem soltos na raiz de `docs/`, fora da subpasta por tipo — são
documentos pré-SERMI, não retrofitados por esta decisão (§5.3).

### 6.4 Famílias de regras checáveis

- **R-TAX** declaradas no SPEC-001 (consistência da taxonomia local).
- **R-FUN** declaradas no SPEC-002 (consistência funcional: escopo,
  critérios de sucesso).
- **R-CON** declaradas no SPEC-003 (consistência de responsabilidade:
  papéis, cadência).

### 6.5 Ajustes em relação ao SPEC-META-001

Um ajuste estrutural real, além do padrão default: a extensão da convenção
de nomes `TIPO_NNN_descricao_curta` para arquivo de código-fonte, não só
documentação (§6.6). A SPEC-META-001 não cobre isso — governa os seis tipos
de documento, não os artefatos técnicos que eles descrevem — então este é
um adendo específico deste projeto, registrado aqui por ser o tipo de
convenção que o SPEC-001 vai formalizar. Ponto em aberto, não ajuste
decidido: se `docs/assets/` for necessário (ex.: diagrama do star schema),
segue o padrão canônico (`shared/` + subpasta por tipo/número) sem
necessidade de nova DEC.

### 6.6 Convenção de nomes para arquivo de código-fonte (não documental)

Decisão adicional, tomada em 2026-08-24 na mesma sessão, a pedido do autor:
arquivos de código-fonte (shell, Python, SQL, Jupyter Notebook, R) não são
peças SERMI — não têm frontmatter YAML, não têm status `proposto/aprovado`,
não entram no rastro DEC obrigatório do pós-fundação (DEC-META-014 §2.4) —
mas adotam a **mesma mecânica de nome** `TIPO_NNN_descricao_curta.ext`,
numeração sequencial global por tipo (não reiniciada por pasta), nunca
reutilizada, no mesmo espírito de rastreabilidade que `DEC_NNN` já usa.

| Tipo de arquivo | Prefixo | Onde vive | Exemplo |
|---|---|---|---|
| Shell (download bruto) | `BASH` | `scripts/` | `BASH_001_basica_download.sh` |
| Python — comum aos dois caminhos | `SRC` | `src/` | `SRC_001_basica_extract_validate.py` |
| Python — ingestão SQLite | `SRC` | `src/ingestao_sqlite/` | `SRC_001_basica_load_sqlite.py` |
| Python — ingestão Snowflake | `SRC` | `src/ingestao_snowflake/` | `SRC_001_basica_export_csv.py` |
| SQL — definição de schema (DDL: `CREATE TABLE`/`VIEW`/`FILE FORMAT`, `ALTER STAGE`) | `DDL` | `sql/ingestao_sqlite/`, `sql/ingestao_snowflake/`, `sql/tratamento/` | `DDL_001_basica_create_table.sql` |
| SQL — manipulação/carga de dado (DML: `COPY INTO`, `MERGE`, `PUT`, orquestração de carga) | `DML` | `sql/ingestao_snowflake/` | `DML_001_basica_copy_merge.sql` |
| Jupyter Notebook | `NOTE` | `notebook/` | `NOTE_001_basica_exploracao.ipynb` |
| R (análise complementar) | `R` | `r/` (pasta nova, paralela a `scripts/`/`sql/`) | `R_001_basica_estatistica_descritiva.R` |

Notas e limites, honestos sobre onde a convenção tensiona com o que já
existe:

- **A descrição curta preserva a convenção de dataset já decidida**
  (`docs/plano_expansao_multidataset.md` §6): o slug depois do número segue
  levando o prefixo do dataset (`basica_`, `vra_`, `siros_`) quando
  aplicável. As duas convenções são ortogonais, não concorrentes — `TIPO_NNN`
  identifica o artefato, o slug continua legível por dataset.
- **DDL/DML é rótulo dentro das pastas existentes, não as substitui**
  (decisão do autor, 2026-08-24): `sql/ingestao_sqlite/`,
  `sql/ingestao_snowflake/`, `sql/tratamento/` e `sql/analise/` continuam
  organizadas por papel no pipeline; `DDL`/`DML` classifica o arquivo dentro
  delas.
- **Ingestão SQLite e Snowflake são fisicamente separadas, download
  continua único** (decisão do autor, 2026-08-24): `scripts/` (download
  bruto) é comum aos dois caminhos; `src/` guarda só o que é comum
  (extração/validação, geração de schema), com `src/ingestao_sqlite/` e
  `src/ingestao_snowflake/` para o que é específico de cada engine; o
  espelho `sql/ingestao_sqlite/` (DDL raw do SQLite) e `sql/ingestao_snowflake/`
  (DDL raw + DML de carga do Snowflake, já existente) seguem o mesmo
  princípio do lado SQL.
- **Scripts que misturam DDL e DML não têm resposta limpa.**
  `07_snowflake_setup_and_load.sql` e `08_snowflake_run_all.sql` (hoje em
  `sql/ingestao_snowflake/`) declaram infraestrutura (`CREATE WAREHOUSE`,
  `CREATE STAGE`) e carga (`COPY INTO`, `MERGE`) no mesmo arquivo. Classificar
  esses como `DML` pelo propósito dominante (o objetivo do arquivo é carregar
  dado; a infra é pré-requisito, não o fim) é a leitura adotada, mas é
  simplificação reconhecida, não uma divisão que o conteúdo do arquivo torna
  óbvia por si só.
- **R não tem caminho de produção próprio ainda.** Por decisão do autor
  (2026-08-24), R fica fora dos dois caminhos (Snowflake e SQLite+Python),
  como ferramenta complementar de análise, ao lado do Jupyter Notebook — não
  dentro de nenhum dos dois pipelines de carga.
- **"Linguagens suportadas pelo Snowflake" não vira categoria própria.**
  Por decisão do autor (2026-08-24), fica restrito a reforçar o que já existe
  (Python/Snowpark, `SRC`); não há, por ora, arquivo JavaScript/Java/Scala
  para UDF ou procedure nativa do Snowflake neste projeto.
- **Esta convenção é prospectiva, não retroativa.** Os arquivos já
  reorganizados nesta sessão (`scripts/01_download.sh`,
  `sql/ingestao_snowflake/07_...sql` etc.) mantêm o nome atual até uma
  decisão explícita de renomeá-los em lote — renomear código já em uso é
  ação de maior consequência (referências cruzadas em outros scripts,
  README, docs de plano) e não foi autorizada nesta rodada. Arquivos novos,
  a partir de agora, seguem `TIPO_NNN_descricao_curta.ext`.

---

## 7. Critérios de reavaliação

Esta decisão deve ser revisitada se:

- A disciplina de DEC virar ritual sem trade-off real — sintoma que a
  própria DEC-META-014 (§8) já vigia no escopo `_meta`.
- O projeto for descontinuado ou arquivado, tornando a manutenção da
  fundação sem função.
- O volume de decisões acumuladas mostrar que a fundação de sete peças é
  desproporcional ao tamanho real do projeto, sugerindo revisão de
  granularidade (sem regredir a perfil reduzido sem freio, DEC-META-013
  §2.3, preservado pela DEC-META-014).
- A auditoria de coerência (`gov-check`), quando rodada pela primeira vez
  após a fundação completa, apontar divergência estrutural que exija
  revisar o que foi fixado no §6.

---

## 8. Histórico

| Data | Evento |
|---|---|
| 2026-08-24 | DEC-001 produzida em status `proposto`. Funda o projeto sob a taxonomia SERMI de sete peças (DEC-META-014), escopo local, seis tipos de documento adotados, `docs/<TIPO>/` como estrutura de pastas. Origem: expansão de escopo da mesma sessão (`docs/plano_expansao_multidataset.md`) e pedido explícito do autor. Aguardando revisão do autor antes de aprovar e seguir para SPEC-001 + REP-001. |
| 2026-08-24 | **Aprovada.** O autor pediu revisão e aprovação explicitamente. Revisão encontrou uma divergência real antes de aprovar: o resumo no topo do documento não refletia o conteúdo já incorporado ao §6.6 (convenção de nomes para código-fonte, adicionada em rodada de trabalho posterior à redação inicial) — corrigido no mesmo momento da aprovação, não deixado como dívida. Nenhuma outra divergência estrutural encontrada contra o blueprint (`rascunho/contexto/blueprints/DEC_001.json`): todas as seções obrigatórias presentes, 4 alternativas com veredito (mínimo 2), consequências negativas não vazias, ao menos um critério de reavaliação. Segue para SPEC-001 + REP-001. |
| 2026-08-26 | **Supersede pontual pelo DEC-005** (não reabre nem reescreve esta DEC, que é imutável após aprovada): o trecho do §6.6 que declarava a convenção `TIPO_NNN` retroativa não autorizada é substituído pela autorização explícita do DEC-005, motivada pela expansão para 3 datasets. O restante do §6.6 (convenção prospectiva, regras de slug/DDL/DML) permanece em vigor sem alteração. |

---

*Fim do documento.*
