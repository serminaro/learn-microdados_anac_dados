---
documento: DEC-009
titulo: Dimensão de aeródromo (localização e fuso horário) como tabela auxiliar em anac_basica.sqlite
versao: v1
status: aprovado
data: 2026-08-31
autor: Bruno Alexandre Serminaro
referencia: DEC-004
escopo: projeto
---

# DEC-009 · Dimensão de aeródromo em `anac_basica.sqlite`

> DEC retroativa, mesmo padrão do `DEC-004`: formaliza uma tabela que o
> autor já pediu para carregar (`dim_airport_location_time_zone`),
> registrando o porquê de ela existir, de onde vem, e por que mora dentro
> do banco da Básica em vez de um banco de referência próprio. Materializa
> a `SPEC-011`.

---

## 1. Contexto

O projeto já produz dado de localização e fuso de aeródromo desde
2026-08-25 (`data/aerodromos_enriquecido.csv`, `src/SRC_001_enriquecer_
bases_aerodromos.py`): cruza os 913 aeródromos observados como origem ou
destino nos microdados (2015-2026) com o OurAirports (dado aberto, lat/
long) e com `tzdata` (fuso IANA, offset UTC padrão, e dois flags de
horário de verão calculados empiricamente contra o calendário real, não
por suposição regional). Esse arquivo nunca teve DEC/SPEC própria — dívida
registrada aqui, não resolvida por esta DEC (§6).

O autor forneceu primeiro `data/dim_airport_location_time_zone.csv`:
um subconjunto de 283 dos 863 aeródromos únicos de
`aerodromos_enriquecido.csv`, sem as colunas `QT_OCORRENCIAS`/`_match`. O
critério desse corte nunca foi confirmado — o autor pediu, na sequência,
para completar a tabela direto a partir do arquivo cheio
(`data/aerodromos_enriquecido.csv`), tornando a pergunta sem objeto: a
tabela final não depende mais do recorte de 283, cobre o universo inteiro
da fonte primária.

Completar revelou três achados que o recorte de 283 não expunha:

- **5 linhas `_match = SEM_MATCH`** (`N/I`, `LGAT`, `SABG`, `MMTY`,
  `SBER`) não têm coordenada nem fuso — inutilizáveis como dimensão de
  localização, excluídas da tabela.
- **`UTC_OFFSET_PADRAO_H` tem fuso de meia hora** (`-3.5`, `3.5`, `4.5`,
  `5.5` — Terra Nova, Irã, Afeganistão, Índia). O recorte de 283 não tinha
  nenhum desses casos por acaso (amostra sem esses países), então o
  esquema original (`utc_offset INTEGER`) nunca foi testado contra o dado
  real. Corrigido para `REAL`.
- **O arquivo de origem tem granularidade (ICAO, IATA observado nos
  microdados)**, não uma linha por aeroporto: 46 códigos `BASE_ICAO`
  aparecem em mais de uma linha, quase todos por ruído de IATA (mesmo
  aeroporto, código IATA diferente observado ao longo do tempo). Um caso
  é divergência real: `SBQV` foi reatribuído entre dois aeroportos
  físicos diferentes (o antigo, fechado, e o atual `SBQV`/Glauber de
  Andrade Rocha) — resolvido pela mesma regra de desempate (fica a linha
  de maior `QT_OCORRENCIAS`), que por coincidência reproduz a escolha que
  a resolução manual original (`_match = MANUAL_KEYWORD`) já tinha feito.

Pedido do autor: carregar a tabela completa, descartando as duas colunas
de horário de verão (`HOR_VERAO_ATUAL`, `JA_TEVE_HORARIO_VERAO`).

## 2. Decisão

**(a) `dim_airport_location_time_zone` entra em `anac_basica.sqlite`**,
como exceção pontual ao isolamento "um banco por dataset" do `DEC-004
§4.4`: dado de referência de aeródromo não é um dataset ANAC, não precisa
do isolamento que o `DEC-004` desenhou para Básica/VRA/SIROS. Materializar
dentro de um banco já existente evita abrir um quarto banco só para menos
de mil linhas.

**(b) Fonte é `data/aerodromos_enriquecido.csv` direto**, não mais o
recorte `data/dim_airport_location_time_zone.csv` — o autor pediu
para completar com a fonte primária, então o recorte fica histórico, sem
uso no pipeline de carga.

**(c) Exclusão das 5 linhas `SEM_MATCH`** (sem coordenada, ver §1) — não
servem como dimensão de localização, entrariam como `NULL` em toda coluna
geográfica se fossem carregadas.

**(d) Deduplicação por `BASE_ICAO`, critério "maior `QT_OCORRENCIAS`"**
— resolve tanto o ruído de IATA (45 casos) quanto a única divergência real
(`SBQV`, §1), com o mesmo resultado que a resolução manual original já
tinha escolhido.

**(e) Colunas de horário de verão fora da tabela**, pedido explícito do
autor. O dado não se perde: continua existindo em
`aerodromos_enriquecido.csv`, só não entra nesta tabela.

**(f) `base_iata` vazio ou `"..."` (placeholder, ex.: `SBYS` / Campo
Fontenelle) vira `NULL`; `municipio_ourairports`/`pais_iso` vazios (os 8
aeródromos `MANUAL_KEYWORD`: fechados ou com ICAO reatribuído) também
viram `NULL`** — mesmo critério de coerência que `basica_silver`/
`vra_silver` já usam (`NULLIF`), string vazia nunca é o valor carregado.

**(g) Materializada como `TABLE`, não `VIEW`**: é dado estático de
referência, sem necessidade de recálculo a cada consulta.

## 3. Origem ou rastro

- `data/aerodromos_enriquecido.csv` e `src/SRC_001_enriquecer_bases_
  aerodromos.py`: origem do dado, commit `2799524` (2026-08-25).
- Pedido do autor nesta sessão (2026-08-31): carregar o subconjunto como
  tabela, sem as colunas de horário de verão, e documentar via SPEC.
- `DEC-004 §4.4`: organização física que esta DEC abre uma exceção pontual
  para acomodar.

## 4. Alternativas consideradas

### 4.1 Banco de referência dedicado (`anac_referencia.sqlite`)

Um banco novo, só para dado de referência (aeródromo, e o que mais vier).

**Por que descartada, por ora.** Overhead de mais um banco para 283
linhas hoje. Revisitar se mais tabelas de referência externa aparecerem
(§6) ou se a dimensão precisar ser consultada a partir do `vra.sqlite`
com a mesma frequência que do `basica.sqlite`.

### 4.2 Manter as colunas de horário de verão

Carregar o subconjunto completo, sem remover nada.

**Por que descartada.** Pedido explícito do autor, sem motivo técnico
para contestar: o dado continua disponível na fonte
(`aerodromos_enriquecido.csv`) para quem precisar depois.

### 4.3 Manter o recorte de 283 em vez de completar com a fonte cheia

Ficar só com o subconjunto que o autor forneceu primeiro, sem completar.

**Por que descartada.** O próprio autor pediu a complementação com
`aerodromos_enriquecido.csv` — fica sem objeto manter um recorte parcial
quando a fonte completa está disponível e já é gerada pelo pipeline do
projeto (`SRC_001_enriquecer_bases_aerodromos.py`).

## 5. Consequências

### 5.1 Positivas

- Tabela pronta para `JOIN` com `basica_raw`/`basica_silver` por
  `sg_icao_origem`/`sg_icao_destino` = `base_icao`, sem precisar de mais
  um banco.
- Formaliza, via `SPEC-011`, uma tabela que já existia sem rastro
  documental.

### 5.2 Negativas

- **`SBQV` carrega o aeroporto fechado, não o atual** — decisão consciente
  (regra de desempate por maior `QT_OCORRENCIAS`, §2.d), mas quem esperar
  o aeroporto operante pode se confundir. `municipio_ourairports`/
  `pais_iso` ficam `NULL` para esse e mais 7 códigos (§2.f) — sinal visível
  de que são casos especiais, não erro de carga.
- **5 aeródromos observados nos microdados (`SEM_MATCH`) ficam de fora da
  dimensão** — quem cruzar `basica_raw`/`vra_raw` com esta tabela por
  `sg_icao_origem`/`destino` perde essas 5 linhas silenciosamente sem
  `LEFT JOIN` (`SPEC-011 §11`).
- **Dado de referência dentro do banco de um dataset específico** é uma
  pequena inconsistência se precisar ser cruzado com o VRA (banco
  separado, `DEC-004`) — exigiria `ATTACH DATABASE` ou duplicar a tabela.
  Aceito por ora (§4.1), revisitado se o custo virar recorrente.

### 5.3 O que esta decisão não resolve

- Não formaliza `data/aerodromos_enriquecido.csv`/`SRC_001_enriquecer_
  bases_aerodromos.py` com DEC/SPEC própria — dívida pré-existente,
  registrada, não fechada aqui.
- Não confirma se `SBQV` deveria, para as perguntas de análise futuras,
  representar o aeroporto fechado ou o atual — a tabela é um retrato
  único por ICAO, não captura reatribuição ao longo do tempo (`SPEC-011
  §11`).

## 6. Critérios de reavaliação

Esta decisão deve ser revisitada se:

- A dimensão precisar ser consultada com frequência a partir do
  `vra.sqlite` (reabre a alternativa 4.1: banco de referência dedicado, ou
  `ATTACH` recorrente).
- Mais tabelas de referência externas (não-ANAC) entrarem no projeto
  (mesma alternativa 4.1).
- Uma pergunta de análise precisar diferenciar aeroportos por período em
  vez de por ICAO estático (reabre o caso `SBQV`, §5.3).

## 7. Histórico

| Data | Evento |
|---|---|
| 2026-08-31 | DEC-009 v1 produzida em status `proposto`, retroativa. Formaliza a tabela `dim_airport_location_time_zone`, carregada em `anac_basica.sqlite` a partir do recorte de 283 linhas fornecido pelo autor. Aguardando aprovação do autor. |
| 2026-08-31 | Completada a pedido do autor: fonte trocada para `data/aerodromos_enriquecido.csv` (858 aeródromos, excluídos 5 `SEM_MATCH`). Três achados novos: fuso de meia hora (`utc_offset` corrigido de `INTEGER` para `REAL`), granularidade real da fonte (ICAO, IATA observado — 46 códigos duplicados, dedup por maior `QT_OCORRENCIAS`), e `SBQV` com reatribuição de ICAO entre dois aeroportos físicos. §1, §2, §4.3, §5, §6 atualizados. |
| 2026-08-31 | **Aprovada.** Autor revisou o lote (DEC-009 + SPEC-011) e aprovou explicitamente. |
| 2026-09-05 | **Correção pós-aprovação, decisão inalterada.** `rascunho/dim_airport_location_time_zone.csv` movido para `data/dim_airport_location_time_zone.csv` (`git mv`, histórico preservado) e declarado como exceção no `.gitignore`. Motivo: `rascunho/` é declarada descartável pelo `.gitignore`, e o recorte de 283 aeródromos é pesquisa externa não reproduzível por rede; trilha documental citada por peça aprovada não pode morar em pasta declarada descartável. As duas citações no corpo (§1, §4.3) passam a apontar para o caminho novo. Nenhuma decisão, fonte de carga ou schema muda: o recorte segue histórico, sem uso no pipeline. |

---

*Fim do documento.*
