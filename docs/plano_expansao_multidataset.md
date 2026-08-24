# Plano: expansão para 3 datasets ANAC e dois caminhos de produção paralelos

> Contexto: o projeto nasceu cobrindo só a tabela **Básica** (2024-2026), um
> caminho (Snowflake) e um dashboard futuro. Este documento registra a
> expansão decidida em 2026-08-24: 3 datasets (**Básica**, **VRA**, **SIROS**),
> cobertura histórica desde 2010 onde a fonte permitir, e dois caminhos de
> produção igualmente investidos — Snowflake (medalhão) e SQLite+Python —
> cada um com sua própria camada ouro e dashboard. Jupyter Notebook é comum
> aos dois caminhos, para exploração e tratamento.
>
> Este plano é o guarda-chuva. `docs/plano_objetos_snowflake.md` continua
> válido como o detalhamento de fases do caminho Snowflake para a Básica
> especificamente — vira o "capítulo Básica" deste plano maior. VRA e SIROS
> ganham capítulos equivalentes quando chegar a vez deles.

---

## 1. Fontes de dados — evidência confirmada (2026-08-24)

Testei diretamente (HTTP request, não só documentação) antes de assumir
qualquer período. Convenção: **confirmado** = testei e existe; **hipótese** =
inferido da estrutura de pastas, não testei arquivo por arquivo.

| Dataset | Fonte | Padrão de URL/arquivo | Cadência | Período confirmado |
|---|---|---|---|---|
| **Básica** | `gov.br/anac/.../basica/{ano}/basica{ano}-{mes}.zip` | zip mensal | mensal | **Confirmado 2000-01 até 2026-06** (testei HTTP 200 em 2000, 2005, 2010, 2015, 2020, 2023, além do 2024-2026 já em produção) |
| **VRA** (Voo Regular Ativo) | `sistemas.anac.gov.br/dadosabertos/Voos e operações aéreas/Voo Regular Ativo (VRA)/{ano}/{mês em português}/VRA_{ano}{mês sem zero à esquerda}.csv` (+ `.json`) | csv+json mensal | **Confirmado pastas de 2000 a 2026** (nível de ano/mês, não testei arquivo individual em todos os anos) |
| **SIROS** (Sistema de Registro de Operações, dataset publicado como "Registro de serviços aéreos") | `sistemas.anac.gov.br/dadosabertos/Voos e operações aéreas/Registro de serviços aéreos/{ano}/{mês em português}/registros_{ano}-{mês}-{dia}.csv` (+ `.json`) | csv+json **diário** | **Confirmado só a partir de 2019-11** (pasta 2019 só tem Novembro/Dezembro; antes disso a ANAC não publica em lote nesse portal) |

### Limitação registrada, não forçada

**SIROS não tem "2010 até agora" — só "2019-11 até agora"** no portal de
dados abertos em lote. Existe uma API de consulta ao vivo
(`siros.anac.gov.br/siros/registros/registros/registros.csv`), mas é
consulta pontual, não um arquivo histórico por dia; não é fonte razoável
para reconstruir 2010-2019. Registro isso como fora de alcance, no mesmo
espírito do que já foi feito no plano Snowflake com Interactive Table/Image
Repository: não force um período que a fonte não tem.

### Como a cadência muda o desenho

SIROS é diário, não mensal. Isso muda duas coisas em relação ao padrão que
`scripts/01_download.sh` já usa para Básica (loop ano→mês):

1. O script de download do SIROS precisa de um terceiro nível de loop
   (ano→mês→dia), e o volume de arquivos é ~30x maior por ano coberto.
2. **Snowpipe com auto-ingest** — que o `docs/plano_objetos_snowflake.md`
   descartou para Básica por não bater com a cadência mensal (Fase G,
   marcada opcional) — tem encaixe genuinamente mais honesto aqui. Vale
   reconsiderar essa fase quando chegar a vez do SIROS.

### Fora de escopo, mas existe na mesma fonte

A página da Básica também publica **Combinada** no mesmo padrão e período.
Não foi pedida — registro só para não confundir se aparecer na navegação.

---

## 2. Os dois caminhos

Os scripts de download (bash) alimentam os dois caminhos a partir do mesmo
dado bruto local — não há dois downloads, um por caminho.

```
                          ┌─ scripts/*.sh (download bruto, 1x por dataset) ─┐
                          │                                                        │
              Caminho 1: Snowflake (medalhão)          Caminho 2: SQLite + Python
              ────────────────────────────              ─────────────────────────
   File Format + Stage → RAW → Prata (typed/limpo)      Verificação/validação Python
   → Prata adicional → Ouro (star schema/métricas)      → limpeza → SQLite (fiel ao
   → Dashboard (Power BI / Looker Studio / Streamlit)   original) → Ouro → Streamlit
```

Jupyter Notebook: exploração e tratamento comuns aos dois, não duplicado.

Os dois caminhos são **igualmente de produção** (decisão do usuário,
2026-08-24) — cada um com camada ouro e dashboard próprios. Isso substitui o
que estava registrado antes (Snowflake como foco, SQLite como apoio); vou
atualizar a memória do projeto para refletir essa mudança.

---

## 3. Estrutura de pastas proposta

A estrutura atual (`scripts/`, `src/` com `ingestao_sqlite/`/`ingestao_snowflake/`,
`sql/ingestao_sqlite/`, `sql/ingestao_snowflake/`, `sql/tratamento/`, `sql/analise/`)
já foi desenhada para múltiplos datasets, mas
a numeração sequencial (`01`...`05`, `07`...`10`) pressupõe um pipeline linear
de um dataset só. Com 3 datasets rodando em paralelo, a numeração sequencial
vira **prefixo de dataset dentro do nome do arquivo** (decisão da seção 6),
mantendo as mesmas pastas. Isso combina com a convenção de nome de arquivo
`TIPO_NNN_descricao_curta` fixada em `DEC-001 §6.6` (não retroativa — vale
para arquivo novo a partir de 2026-08-24):

```
scripts/                       (BASH_NNN)
  BASH_001_basica_download.sh  (hoje scripts/01_download.sh; renomeia, estende range)
  BASH_002_vra_download.sh     (novo)
  BASH_003_siros_download.sh   (novo, loop ano/mês/dia)

src/                           (SRC_NNN, comum aos dois caminhos)
  SRC_001_basica_extract_validate.py, SRC_002_basica_build_schema.py, ...
  SRC_00N_vra_...
  SRC_00N_siros_...
  ingestao_sqlite/            (SRC_NNN específico da carga SQLite)
    SRC_00N_basica_load_sqlite.py, SRC_00N_vra_..., SRC_00N_siros_...
  ingestao_snowflake/         (SRC_NNN específico da preparação p/ carga Snowflake)
    SRC_00N_basica_export_csv.py, SRC_00N_vra_..., SRC_00N_siros_...

sql/
  ingestao_sqlite/              (DDL_NNN, ver DEC-001 §6.6)
    DDL_00N_basica_create_table.sql, DDL_00N_vra_..., DDL_00N_siros_...
  ingestao_snowflake/          (DDL_NNN e DML_NNN, ver DEC-001 §6.6)
    DDL_00N_basica_file_format_and_stage.sql, DML_00N_basica_setup_and_load.sql, ...
    DDL_00N_vra_..., DML_00N_vra_...
    DDL_00N_siros_..., DML_00N_siros_...
  tratamento/                  (DDL_NNN — views são DDL)
    DDL_00N_basica_view_typed_sqlite.sql, DDL_00N_basica_view_typed_snowflake.sql
    DDL_00N_vra_...
    DDL_00N_siros_...
  analise/
    (por dataset, quando existir)
```

**Isso é uma proposta, não decisão fechada** — a numeração exata (`NNN`) só
se fixa quando o arquivo é de fato criado, na ordem em que nascer. Não vou
renomear nada até validar.

---

## 4. Organização dos dados no SQLite — decisão em aberto

Você pediu explicitamente para pensar nisso. Três alternativas:

| Alternativa | Descrição | Ganha | Perde |
|---|---|---|---|
| **A. Um banco único** (`anac.sqlite`), tabelas prefixadas por dataset (`basica_raw`, `vra_raw`, `siros_raw`...) | Tudo num arquivo | JOIN entre datasets sem `ATTACH` (ex.: cruzar Básica com VRA pelo mesmo voo) | Um arquivo só cresce muito — SIROS sozinho, diário desde 2019, tem potencial de dezenas de milhões de linhas; um dataset problemático (corrupção, bug de carga) arrisca o banco inteiro |
| **B. Um banco por dataset** (`basica.sqlite`, `vra.sqlite`, `siros.sqlite`) | Isolamento total | Reprocessar/versionar um dataset não mexe nos outros; arquivos menores, mais fáceis de mover/backup | Cruzar dados entre datasets exige `ATTACH DATABASE` nas queries |
| **C. Um banco por dataset por camada** (raw separado do ouro, espelhando o medalhão do Snowflake em SQLite) | Granularidade máxima, mesmo padrão mental dos dois caminhos | Mais arquivos pra gerenciar, mais um nível de indireção | Overhead desnecessário se o volume de cada camada não justificar separar |

**Minha recomendação: B** (um banco por dataset), com `ATTACH` quando
precisar cruzar. É o padrão mais comum para esse volume, reduz o risco de um
dataset inchado/corrompido afetar os outros, e é reversível — se depois
fizer sentido consolidar, dá para migrar. Mas isso muda como as queries de
cruzamento (ex.: Básica x VRA) são escritas desde o início, então prefiro
que você valide antes de eu montar os scripts de carga.

---

## 5. Ordem de implementação

1. **Básica** — já tem pipeline rodando (2024-2026). Estender:
   - `scripts/01_download.sh` → `scripts/BASH_001_basica_download.sh`,
     range **2010** até o presente (decisão da seção 6), tratando possíveis
     exceções de nome de arquivo como já existe para 2026-06.
   - Novo passo de validação de schema ao longo do tempo: `src/02_extract_validate.py`
     hoje só valida consistência entre os 30 meses de 2024-2026; com 26 anos
     de histórico, é razoável esperar mudança de cabeçalho/colunas em algum
     ponto — precisa virar validação explícita, não suposição.
   - Replicar carga para os dois caminhos com o volume novo.
2. **VRA** — dataset novo, os dois caminhos do zero, mesmo padrão de fases do
   que foi feito para Básica no plano Snowflake (File Format/Stage → Raw →
   Prata → ...).
3. **SIROS** — dataset novo, cadência diária exige desenho de download
   diferente (loop ano/mês/dia) e cobre só 2019-11 em diante. Bom candidato
   para reavaliar Snowpipe (Fase G do plano Snowflake) dado o encaixe natural
   com a cadência.

---

## 6. Decisões (validadas em 2026-08-24)

1. **Nomenclatura por dataset**: prefixo no nome do arquivo
   (`basica_download.sh`, `vra_download.sh`, `siros_download.sh`), mesma
   pasta — não subpasta por dataset.
2. **Organização do SQLite**: alternativa B, um banco por dataset
   (`basica.sqlite`, `vra.sqlite`, `siros.sqlite`), `ATTACH DATABASE` quando
   precisar cruzar dados entre eles.
3. **Ano de início da extensão histórica**: **2010**, não 2000. Vale para
   Básica e VRA (SIROS já está fixado em 2019-11 pela fonte, ver seção 1).
4. **Dashboard do caminho Snowflake** (Power BI vs. Looker Studio): em
   aberto por enquanto — decisão de fase posterior, quando a Camada Ouro
   existir.
