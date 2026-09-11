---
documento: DEC-011
titulo: Nenhum valor de máquina ou de pessoa cravado no código: raiz derivada, ambiente declarado, e paridade BASH/PS1
versao: v1
status: proposto
data: 2026-09-11
autor: Bruno Alexandre Serminaro
referencia: DEC-001, DEC-005, SPEC-002, SPEC-003
escopo: projeto
---

# DEC-011 · Portabilidade e valores cravados

> Formaliza uma regra que o código já aplica em 17 arquivos e já cita 20
> vezes por nome, sem que a decisão citada existisse. Cobre dois motivos
> distintos sob um princípio comum: o pipeline tem que rodar em outra
> máquina (portabilidade), e o repositório é público (higiene). Os dois
> falham pelo mesmo mecanismo, um valor local escrito dentro do fonte.

---

## 1. Contexto

O pipeline nasceu numa máquina só. Isso deixou três classes de valor local
gravadas no fonte:

- **Caminho absoluto do repositório.** `DEST`, `DB_PATH` e `DDL_PATH` dos
  sete scripts de ingestão apontavam para
  `/home/bruno/Projetos/learn-microdados_anac_dados`, assim como o `DEST`
  dos três scripts de download e a leitura do CSV no
  `notebook/note-001`.
- **Interpretador de uma instalação específica.** Seis dos sete `.py` de
  ingestão abriam com `#!/home/bruno/miniconda3/envs/pesquisa-azul/bin/python`,
  caminho de um ambiente conda que não existe fora daquela máquina.
- **Endereço de pessoa.** `scripts/enviar_figuras_por_email.py` trazia
  remetente e destinatário escritos no arquivo.

A primeira classe quebra em qualquer clone: o script roda, não encontra o
diretório, e falha. A segunda quebra antes disso, na linha do shebang. A
terceira não quebra nada, e é justamente por isso que é a pior das três: o
repositório é declarado **peça de portfólio público** pela `SPEC-002 §1`, e
endereço de e-mail commitado entra no histórico do git de forma permanente
e indexável, sobrevivendo à própria remoção.

Há ainda um quarto caso, de natureza diferente: o `PUT` do Snowflake roda no
**cliente**, não no servidor, então ele precisa mesmo de um caminho de
máquina. Não é um valor a eliminar, é um valor a parametrizar.

O gatilho concreto foi a intenção de operar o pipeline também a partir de uma
máquina Windows. `analise/` já tinha nascido com a raiz derivada do próprio
arquivo (`analise/iata_bases.py:55`,
`analise/a4_etapa_media/analise_etapa_media_gol.py:23`); `scripts/`, `src/`,
`sql/` e `notebook/` ficaram para trás.

## 2. Decisão

Nenhum valor de máquina, de ambiente ou de pessoa fica escrito dentro de
arquivo de código versionado. A regra se materializa em cinco mecanismos,
um por classe de valor (§2.1 a §2.5), mais o ajuste de convenção que o
quinto exige (§2.6).

### 2.1 Raiz do repositório: derivada do próprio arquivo

Cada script calcula a raiz a partir da sua própria localização e monta os
demais caminhos a partir dela. Consequência: roda de qualquer diretório de
trabalho, em qualquer clone, em qualquer sistema.

| Linguagem | Forma |
|---|---|
| Python | `REPO_ROOT = Path(__file__).resolve().parents[N]` |
| Shell | `REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"` |
| PowerShell | `$RepoRoot = Split-Path -Parent $PSScriptRoot` |
| Notebook | `Path.cwd().parent if Path.cwd().name == 'notebook' else Path.cwd()` |

O notebook é o caso fraco: `__file__` não existe em Jupyter, então a
derivação depende do diretório de trabalho do kernel e assume que ele é a
raiz ou `notebook/`. É a melhor aproximação disponível, não uma garantia.

Caminhos são montados por junção (`REPO_ROOT / "data" / "anac"`), nunca por
concatenação de string com separador literal.

### 2.2 Interpretador: `#!/usr/bin/env python3`, ambiente declarado à parte

Nenhum shebang aponta para caminho de instalação. Quem decide qual Python roda
é o ambiente ativo no momento da chamada. O ambiente é conda, e o repositório
declara **dois**, com papéis diferentes:

| Arquivo | Ambiente | Papel |
|---|---|---|
| `environment_gov-sermi-perf.yml` (raiz) | `gov-sermi-perf` | Ambiente **compartilhado** entre os projetos do autor, o mesmo usado no trabalho. Amplo e estável por opção: roda o pipeline, a análise e o que vier de outros projetos. |
| `relatorios/*/*/environment_report.yml` | `report-docx` | Ambiente **mínimo e próprio** dos geradores de relatório, com três dependências. Existe porque a `DEC-010 §5` exige que cada gerador seja autocontido. |

```bash
conda env create -f environment_gov-sermi-perf.yml     # uma vez, por máquina
conda activate gov-sermi-perf                # a cada sessão
./src/ingestao_sqlite/SRC_001_basica_load_sqlite.py
```

A escolha de usar um ambiente compartilhado, e não um por repositório, é
deliberada (decisão do autor, 2026-09-11): o custo de manter um ambiente por
projeto, em muitos projetos que compartilham quase toda a dependência, não se
paga. O preço está em §5.2.

O shebang antigo embutia a escolha do ambiente dentro de cada um dos seis
arquivos, e embutia a escolha errada: apontava para `pesquisa-azul`, ambiente
de outro projeto. A diferença entre o arranjo antigo e o novo não é "ambiente
do projeto" contra "ambiente compartilhado": é **ambiente escolhido em silêncio
por arquivo** contra **ambiente declarado em um lugar e ativado
explicitamente**.

A troca tem custo, registrado em §5.2: o shebang deixa de garantir
interpretador correto, e rodar sem ativar o ambiente falha por módulo ausente.

### 2.3 Dado de pessoa e credencial: variável de ambiente ou argumento

Endereço de e-mail e senha vêm de `--de`/`--para`, de `EMAIL_REMETENTE`/
`EMAIL_DESTINATARIO`/`GMAIL_APP_PASSWORD`, ou de prompt interativo sem eco.
**Sem default cravado**: na ausência de todos, o script para com erro. Um
default seria pior que a ausência, porque envia para o lugar errado em
silêncio.

A regra vale para qualquer valor que identifique pessoa ou autorize acesso,
não só e-mail e senha de aplicativo.

### 2.4 Caminho de cliente no Snowflake: variável do CLI (provisório)

> **Escopo limitado, por decisão do autor (2026-09-11).** O caminho Snowflake
> vai ser retomado como **onda própria de trabalho**, com decisão específica.
> O que esta seção fixa é o mínimo para que os dois `.sql` já existentes
> parem de exigir edição de arquivo versionado antes de rodar. Não é a forma
> final da parametrização do caminho Snowflake, e cai sob a decisão dessa
> onda quando ela vier (§6).

O `PUT` recebe a raiz como variável do Snowflake CLI
(`snow sql -D "REPO_ROOT=..."`, referenciada como `&{REPO_ROOT}`), não
cravada no `.sql`. No roteiro manual por blocos (`DML_001`), onde não há
invocação de CLI para carregar variável, fica um marcador `<RAIZ_DO_REPO>`
para colagem, acompanhado de exemplo nas duas plataformas. Exemplo dentro de
comentário, explicitamente rotulado como exemplo, não conta como valor
cravado: ele não é lido por nenhuma execução.

Nos dois casos o caminho usa barra normal (`/`) também no Windows, porque o
`PUT` espera URI, não caminho nativo.

### 2.5 Paridade multi-OS: `PS1_NNN` espelha `BASH_NNN`

O download bruto, única etapa do pipeline escrita em shell, ganha um
equivalente PowerShell por script, **pareado pelo número**:

| Linux/macOS | Windows | Dataset |
|---|---|---|
| `BASH_001_basica_download.sh` | `PS1_001_basica_download.ps1` | Básica |
| `BASH_002_vra_download.sh` | `PS1_002_vra_download.ps1` | VRA |
| `BASH_003_siros_download.sh` | `PS1_003_siros_download.ps1` | SIROS |

O par compartilha fonte, critério de nome de arquivo, formato de log e
idempotência. Mudou a regra em um, muda no outro na mesma sessão, ou os dois
divergem em silêncio. O cabeçalho de cada `.ps1` carrega essa obrigação
escrita.

O resto do pipeline (extração, validação, schema, carga) é Python e já é
multiplataforma: não recebe, nem deve receber, equivalente em `.ps1`.

### 2.6 Supersede pontual do DEC-001 §6.6

A tabela de prefixos do `DEC-001 §6.6` não previa PowerShell. Esta DEC
acrescenta a linha, pelo mesmo mecanismo que o `DEC-005` usou para alterar
só o trecho de retroatividade daquela seção:

| Tipo de arquivo | Prefixo | Onde vive | Exemplo |
|---|---|---|---|
| PowerShell (download bruto, par Windows do `BASH`) | `PS1` | `scripts/` | `PS1_001_basica_download.ps1` |

A numeração de `PS1` **não é sequencial própria**: ela espelha a do `BASH`
que o arquivo traduz. `PS1_002` existe porque `BASH_002` existe, e um
`PS1_004` sem `BASH_004` seria um erro de convenção, não um arquivo novo
legítimo. Essa é a única exceção à numeração sequencial global por tipo que
o `DEC-001 §6.6` fixa, e existe porque o número aqui carrega semântica de
pareamento, não de ordem de criação.

## 3. Origem ou rastro

- **Prática anterior à decisão**: `analise/` já nasceu com raiz derivada
  (`iata_bases.py`, `pareto_hub.py`, os scripts das linhas a3/a4/a5),
  entre 2026-08-31 e 2026-09-04. A regra existia de fato antes de existir
  de direito.
- **Primeira aplicação commitada**: `23959ef` (2026-09-05), que removeu os
  endereços de e-mail do script de envio e já citou `DEC-011` pelo nome.
- **Aplicação que acompanha esta DEC**: 13 arquivos modificados e 3 criados
  (os `.ps1`), versionados na branch `analise/a3-a5-e-spec-017` junto com ela.
  Somados ao script de envio já commitado em `23959ef`, são 17 arquivos de
  código e 20 citações a `DEC-011`.
- **Achado que a motivou**: levantamento do estado do repositório em
  2026-09-11, que encontrou código citando uma decisão inexistente,
  violando a ordem decisão-primeiro do `DEC-META-014 §2.4`.
- **Peça que a condiciona**: `SPEC-002 §1` (portfólio público), que é o que
  transforma endereço cravado de inconveniência em exposição.

Esta DEC é, portanto, **retroativa em parte** (§2.3 e a prática de `analise/`
já valiam) e **prospectiva em parte** (§2.1, §2.2, §2.4, §2.5 e §2.6 passam a
valer com o commit que a acompanha).

## 4. Alternativas consideradas

### 4.1 Caminho por variável de ambiente (`ANAC_REPO_ROOT`)

Exigiria `export` antes de qualquer execução, e falharia com mensagem obscura
quando esquecido. A derivação pelo próprio arquivo não tem passo de
configuração: clonar e rodar basta. Variável de ambiente fica reservada para
o que **não pode** ser derivado (credencial, endereço), onde a exigência de
configuração explícita é justamente o ponto.

### 4.2 Arquivo de configuração central (`config.yml` na raiz)

Um só lugar para todos os caminhos, lido por todos os scripts. Ganha
flexibilidade (dado fora do repositório, por exemplo) e perde autonomia: cada
script passa a depender de um arquivo externo e de um parser. Como todo
caminho do projeto é relativo à raiz, não há nada que configurar. Reabre se
`data/` ou `db/` precisarem morar fora da árvore do repositório, o que é
plausível dado que `db/` já passa de 26 GB (§6).

### 4.3 Windows via WSL, sem script nativo

Zero duplicação, zero código novo, e o `.sh` segue sendo a única
implementação. Descartada porque impõe WSL a quem só tem PowerShell, para
uma etapa (baixar arquivo por HTTP) que o PowerShell faz nativamente.

### 4.4 Um único download em Python, substituindo `.sh` e `.ps1`

Elimina a duplicação de vez e usa um runtime que o pipeline já exige. Foi a
alternativa mais forte, e a decisão contra ela é deliberada e revisável:
mantém-se o download inspecionável em shell, na linguagem que cada
plataforma fala. O custo aceito é a duplicação de lógica em duas linguagens,
mitigada pelo pareamento por número (§2.5) e não eliminada por ele.

### 4.5 Manter BASH e PS1 pareados (decisão atual)

Escolhida em 2026-09-11, com o risco de divergência assumido explicitamente.

## 5. Consequências

### 5.1 Positivas

- O repositório clonado roda sem edição em Linux, macOS e Windows.
- O `.py` executa sob qualquer ambiente Python ativo, e a dependência fica
  declarada em arquivo (`environment_gov-sermi-perf.yml`, ou `environment_report.yml`
  dentro de cada gerador), reproduzível por `conda env create`, em vez de
  embutida em seis shebangs.
- Nenhum endereço de pessoa entra no histórico do git a partir daqui.
- O `PUT` deixa de exigir edição de arquivo versionado antes de rodar, o
  que mantém o caminho Snowflake utilizável até a onda que vai retomá-lo
  (§2.4).
- `analise/` deixa de ser a única pasta coerente: a regra que ela já seguia
  passa a valer para o repositório inteiro.

### 5.2 Negativas

- **Duplicação real de lógica de download.** Três pares de scripts que
  precisam mudar juntos. A fonte da ANAC já provou ser instável no critério
  de nome (`basica202606.zip`, sem hífen), então a regra que cada par
  implementa vai mudar de novo.
- **A paridade não é verificada por nada.** Não há teste, nem hook, nem
  passo de auditoria que compare `BASH_NNN` com `PS1_NNN`. A garantia é
  disciplina do autor, assentada em comentário de cabeçalho.
- **Nenhum dos três `.ps1` foi executado em Windows.** São traduções
  conferidas por leitura, não por execução. Enquanto isso não mudar, são
  hipótese de funcionamento, não fato verificado.
- **A derivação do notebook é a mais frágil das quatro** (§2.1), e falha em
  silêncio se o kernel subir de um terceiro diretório.
- **O ambiente compartilhado carrega o que este projeto não usa.** O
  `environment_gov-sermi-perf.yml` traz `python-pptx`, `xlsxwriter`, `duckdb`,
  `scikit-learn`, `plotly`, `altair` e comentários sobre `apresentacao/` e um
  arquivo protegido por IRM, nada disso usado aqui. Num repositório declarado
  portfólio público (`SPEC-002 §1`), quem clonar recebe o ambiente de trabalho
  do autor, não a dependência mínima do pipeline. Consequência aceita em troca
  de não manter um ambiente por projeto; o que o repositório de fato importa
  está em §3 desta DEC.
- **O nome do ambiente não diz nada sobre o projeto.** `gov-sermi-perf` num
  repositório `learn-microdados_anac_dados` só é legível para quem já conhece
  o arranjo, e é por isso que o cabeçalho do arquivo explica o porquê logo na
  primeira linha.
- **O shebang deixa de garantir o interpretador.** Antes, `./SRC_001...py`
  rodava com o Python certo mesmo sem ambiente ativo, porque o caminho do
  conda estava no arquivo. Agora, rodar sem `conda activate` cai no Python do
  sistema e falha por `ModuleNotFoundError`, erro menos óbvio de diagnosticar
  que o `bad interpreter` antigo. O custo é assumido: era garantia de uma
  máquina só, e falsa em qualquer outra.
- Prefixo `PS1` abre a primeira exceção à numeração sequencial por tipo do
  `DEC-001 §6.6`, o que custa uma nota permanente na convenção.

### 5.3 O que esta decisão não resolve

- **Saídas salvas de notebook.** `notebook/note-001` e
  `analise/a4_etapa_media/analise_etapa_media_gol.ipynb` ainda carregam
  `/home/bruno/...` dentro de células de **output** (stderr e repr de
  `PosixPath`), congelado de execuções anteriores. A regra alcança o fonte,
  não o resultado salvo; some na próxima execução limpa.
- **`relatorios/`.** Os geradores das duas peças (`DEC-010`) não foram
  auditados contra a regra de caminho e de valor cravado. A separação de
  ambiente, essa sim, está resolvida: `environment_report.yml`, ambiente
  `report-docx`, decidido em 2026-09-11 e registrado no Histórico da
  `DEC-010`.
- **O conteúdo do ambiente não é auditado por esta DEC.** Ela fixa onde a
  dependência se declara, não quais versões são as certas. O conjunto de
  bibliotecas é matéria do autor, e mudá-lo afeta todos os projetos que
  compartilham `gov-sermi-perf`, não só este. O `python=3.13` foi decidido em
  2026-09-11 por essa razão, fora da DEC.
- **Os dois ambientes foram criados, não exercitados.** `gov-sermi-perf` e
  `report-docx` existem nesta máquina desde 2026-09-11, mas nenhum script do
  pipeline rodou sob eles ainda. Criar resolve a instalação, não prova a
  execução.
- **Snowflake além do `PUT`.** Nome de conexão (`anac`), de banco e de
  schema seguem escritos nos `.sql`. São nomes de objeto lógico, não de
  máquina, e ficam para a onda própria do caminho Snowflake (§2.4).
- **Credencial do Snowflake.** Vive no arquivo de conexão do CLI, fora do
  repositório, por conta do próprio `snow connection add`. Esta DEC não
  governa esse arquivo.
- **Histórico já escrito.** Os endereços removidos em `23959ef` continuam
  recuperáveis nos commits anteriores. A regra impede novos, não apaga
  velhos, e reescrever o histórico não foi considerado.
- **Tamanho de dado.** Portabilidade de caminho não torna o pipeline
  portável na prática: `data/` passa de 51 GB e `db/` de 26 GB. Rodar em
  outra máquina é possível, barato não é.

## 6. Critérios de reavaliação

Esta decisão deve ser revisitada se:

- Um par `BASH`/`PS1` divergir de fato, ou a execução em Windows exigir mais
  que tradução de shell (reabre a alternativa 4.4, download único em
  Python).
- A etapa de download passar a exigir lógica que shell não sustenta bem
  (retentativa com backoff, paralelismo, verificação de integridade), com o
  mesmo efeito: reabre 4.4.
- **A onda de trabalho do caminho Snowflake começar.** O §2.4 é provisório
  por construção e passa a ser matéria da decisão dessa onda, inclusive a
  possibilidade de o `PUT` sair do `.sql` e virar passo de script Python com
  o conector, o que dispensaria a variável do CLI.
- O ambiente compartilhado `gov-sermi-perf` passar a conflitar entre projetos
  (versão que um exige e outro não suporta), o que reabre a alternativa do
  ambiente por repositório, descartada em §2.2 por custo de manutenção.
- `data/` ou `db/` precisarem morar fora da árvore do repositório, por
  volume ou por disco separado (reabre 4.2, arquivo de configuração, ou 4.1,
  variável de ambiente).
- Um terceiro sistema operacional ou um executor em contêiner entrar em
  cena, tornando o pareamento por linguagem insustentável.
- Qualquer valor de pessoa ou credencial reaparecer no fonte, o que
  significa que a regra de §2.3 não está sendo sustentada por disciplina e
  precisa de verificação automatizada.

## 7. Histórico

| Data | Evento |
|---|---|
| 2026-09-11 | DEC-011 v1 produzida em status `proposto`, parcialmente retroativa. Escopo, estratégia multi-OS e forma de formalizar o prefixo `PS1` confirmados com o autor antes da redação. Aguardando aprovação do autor, e com ela o commit dos 16 arquivos de código que a citam e ainda não foram versionados. |
| 2026-09-11 | Iteração sobre o rascunho, a pedido do autor: §2.2 passa a nomear o ambiente conda como lugar único da dependência, e §2.4 é rebaixada a provisória porque o caminho Snowflake terá onda própria. |
| 2026-09-11 | Segunda iteração, decisão do autor sobre ambientes: `gov-sermi-perf` é ambiente **compartilhado** entre projetos e o mesmo usado no trabalho, por opção, não por descuido. §2.2 passa a descrever os dois ambientes (`gov-sermi-perf` amplo na raiz, `report-docx` mínimo nos geradores) e a nomear a autocontenção da `DEC-010` como motivo do segundo. §5.2 registra o preço do compartilhamento (dependência de outros projetos num repo público, nome sem relação com o projeto) como consequência aceita, não como defeito. §5.3 mantém como pendência só o que é de fato pendência: o arquivo fora do versionamento e a inexistência dos dois ambientes nesta máquina. `environment_gov-sermi-perf.yml` ajustado no mesmo passo: `timezonefinder` acrescentado (era dependência real e ausente), `scipy` movido de pip para conda-forge, cabeçalho declarando o papel compartilhado do arquivo. |
| 2026-09-11 | Terceira iteração, decisões do autor: Python sobe de 3.12 para **3.13** nos dois ambientes (o pin divergia do uso real, que já alternava 3.12 e 3.13); o arquivo da raiz passa a se chamar `environment_gov-sermi-perf.yml`, alinhando nome de arquivo e nome de ambiente, já que ele não é do ANAC; os dois ambientes foram criados nesta máquina; e o conjunto inteiro foi versionado. §5.3 perde a pendência de versionamento, que deixou de existir, e passa a registrar que criar ambiente não é o mesmo que exercitá-lo. |

---

*Fim do documento.*
