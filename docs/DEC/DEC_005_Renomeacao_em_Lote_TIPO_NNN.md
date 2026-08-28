---
documento: DEC-005
titulo: Renomeação em lote dos arquivos de código-fonte existentes para a convenção TIPO_NNN
versao: v1
status: aprovado
data: 2026-08-26
autor: Bruno Alexandre Serminaro
referencia: DEC-001, docs/plano_expansao_multidataset.md
escopo: projeto
---

# DEC-005 · Renomeação em lote para TIPO_NNN

> DEC de conteúdo: autoriza agora a exceção que o próprio DEC-001 §6.6
> previu e deixou fechada ("não foi autorizada nesta rodada") — renomear em
> lote os arquivos de código já em uso (`scripts/01_download.sh`,
> `src/02_...`, `src/03_...`, `sql/ingestao_snowflake/07_...` etc.) para a
> convenção `TIPO_NNN_descricao_curta`, incluindo a atualização de todas as
> referências cruzadas.

---

## 1. Contexto

O `DEC-001 §6.6` fixou a convenção `TIPO_NNN_descricao_curta` como
**prospectiva**: arquivos novos a partir de 2026-08-24 a seguem, mas os já
existentes mantêm o nome atual até uma "decisão explícita de renomeá-los em
lote", porque renomear código em uso é ação de maior consequência (referências
cruzadas em outros scripts, README, docs de plano) e não havia motivo
suficiente para pagar esse custo naquela rodada.

O motivo surge agora: o autor pediu (2026-08-26) para organizar dados e
pastas do repositório e iniciar o download dos três datasets (Básica, VRA,
SIROS — `docs/plano_expansao_multidataset.md`). Criar `BASH_002_vra_download.sh`
e `BASH_003_siros_download.sh` do zero, com `scripts/01_download.sh` mantendo
nome antigo ao lado, deixaria a convenção permanentemente misturada dentro da
mesma pasta assim que os dois caminhos de produção passam a rodar em
paralelo para os três datasets.

## 2. Decisão

**Renomear agora, em lote, os arquivos de código-fonte já existentes em
`scripts/`, `src/` e `sql/` para a convenção `TIPO_NNN_descricao_curta`
fixada no DEC-001 §6.6, atualizando toda referência cruzada (README,
SPEC-002, paths absolutos hardcoded em `.py`/`.sql`) no mesmo commit.**

## 3. Origem ou rastro

- `DEC-001 §6.6`: fixa a convenção e declara explicitamente a exceção que
  esta DEC agora fecha.
- `docs/plano_expansao_multidataset.md §3`: já propunha o mapeamento nome
  atual → nome novo para cada arquivo (não decisão fechada até então).
- Pedido do autor nesta sessão (2026-08-26): organizar pastas do repositório
  antes de iniciar o download dos três datasets.

## 4. Alternativas consideradas

### 4.1 Manter DEC-001 §6.6 como está (não renomear existentes)

Só os arquivos novos (VRA, SIROS) nasceriam com `TIPO_NNN`;
`scripts/01_download.sh`, `src/02_...` etc. ficariam como estão.

**Por que descartada.** Convenção mista dentro da mesma pasta pelo tempo que
o projeto durar (não há gatilho natural futuro para revisitar), dificultando
localizar arquivo por papel assim que os três datasets rodarem lado a lado.

### 4.2 Renomear incrementalmente, só quando cada arquivo for de fato tocado

Adiar o rename de cada arquivo para o momento em que ele precisar ser
editado por outro motivo (ex.: estender range da Básica).

**Por que descartada.** Gera um período indeterminado de convenção mista
(pior que a alternativa 4.1 em previsibilidade, porque o corte não é nem
"tudo antigo" nem "tudo novo", é arbitrário por ordem de edição), e o
`gov-check` teria que lidar com um estado intermediário sem critério claro
de quando cobrar.

### 4.3 Renomear em lote agora, com atualização de todas as referências (decisão atual)

**Adotada.** Paga o custo de consequência (referências cruzadas) uma única
vez, no momento em que o motivo (expansão para 3 datasets) já existe e a
DEC-001 já havia antecipado exatamente esse tipo de gatilho.

## 5. Consequências

### 5.1 Positivas

- Elimina a divergência já sinalizada em `AUDIT-001` (R-FUN-01, sobre o
  range da Básica) no mesmo commit que resolve a nomenclatura.
- Convenção única (`TIPO_NNN`) em todas as pastas de código a partir de
  agora, sem período de transição misto.
- Fecha explicitamente uma exceção que o próprio DEC-001 deixou em aberto,
  em vez de deixá-la pendente indefinidamente.

### 5.2 Negativas

- **Referências cruzadas em vários documentos** (`README.md`, `SPEC-002`,
  paths absolutos hardcoded em `src/*.py` e `sql/*.sql`) precisam ser
  atualizadas no mesmo commit; esquecer uma quebra o pipeline silenciosamente
  (ex.: script que ainda aponta para o nome antigo de outro script).
- **DEC-001 é imutável após aprovação** (princípio da taxonomia): esta DEC
  não edita o corpo do DEC-001, só o supersede pontualmente no trecho do
  §6.6 sobre retroatividade — o registro de que essa exceção existe fica
  aqui e no Histórico do DEC-001, não como reescrita do texto original.
- **`AUDIT-001`, já aprovada/registrada, cita `scripts/01_download.sh` pelo
  nome antigo** (R-FUN-01): o documento de auditoria não é reescrito
  retroativamente (é fotografia do estado em 2026-08-25); a próxima rodada
  de `gov-check` já vai referenciar o nome novo.

### 5.3 O que esta decisão não resolve

- Não decide a numeração `NNN` além da ordem de criação já em uso (mesma
  regra do DEC-001 §6.6).
- Não resolve a "resposta suja" de scripts Snowflake que misturam DDL e DML
  no mesmo arquivo — problema já reconhecido e aceito no DEC-001 §6.6.

## 6. Critérios de reavaliação

Esta decisão deve ser revisitada se:

- O rename quebrar alguma referência em produção não detectada nesta rodada
  (ex.: stage do Snowflake apontando para path de arquivo consolidado com
  nome antigo) — sinal para corrigir a referência, não para reverter o
  rename.
- Um quarto dataset ou um terceiro caminho de produção exigir revisar a
  convenção de pastas por engine (`ingestao_sqlite`/`ingestao_snowflake`)
  além do nome de arquivo.

## 7. Histórico

| Data | Evento |
|---|---|
| 2026-08-26 | DEC-005 produzida em status `proposto`. Fecha a exceção que o DEC-001 §6.6 deixou explicitamente em aberto, motivada pela expansão para 3 datasets (`docs/plano_expansao_multidataset.md`) e pedido do autor de organizar o repositório antes do download. Três alternativas avaliadas. Aguardando revisão do autor antes de aprovar. |
| 2026-08-26 | **Aprovada.** O autor revisou o resumo (Decisão, alternativas, consequências) e aprovou explicitamente antes da execução. Rename em lote e atualização de referências cruzadas (README, paths hardcoded em `.py`/`.sql`) executados no mesmo commit da aprovação. |

---

*Fim do documento.*
