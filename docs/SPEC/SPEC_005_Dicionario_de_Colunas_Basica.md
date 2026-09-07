---
documento: SPEC-005
titulo: Dicionário de Colunas — Básica
versao: v3
status: aprovado
data: 2026-08-31
autor: Bruno Alexandre Serminaro
referencia: DEC-007
escopo: projeto
---

# SPEC-005 · Dicionário de Colunas — Básica

> Documenta, de forma exaustiva, as colunas de `BASICA_RAW`/`basica_silver`
> — todas, não só as usadas em alguma análise — e marca quais são
> **essenciais** para as perguntas de análise da `DEC-007`. Consolida três
> fontes que faziam esse trabalho em paralelo: `QUERY-011-Dados_das_
> colunas_de_Trusted.csv` (conteúdo primário: categoria, confiança,
> comentário), `colunas.txt` (definição do flag essencial) e
> `docs/dicionario_colunas_basica.md` (dicionário informal pré-SERMI, que
> este documento supera). Primeira peça deste tipo no projeto.

---

## 1. Propósito

Dar ao projeto uma única fonte de verdade, versionada e citável, para "o
que cada coluna da Básica significa" — hoje espalhado entre um arquivo
`.md` sem frontmatter, um `.txt` de trabalho e um `.csv` de rascunho.
Nenhum dos três documentava sozinho as ~112 colunas com categoria dupla
(`CATEGORIA 1`/`CATEGORIA2`), confiança e marcação de essencialidade ao
mesmo tempo.

## 2. Audiência

Reaproveita os papéis abstratos do `SPEC-002 §2` (Autor, Par assistivo,
Autor futuro, Leitor do repositório) — nenhum papel novo. Uso principal:
qualquer SPEC ou script que precise citar "quais colunas existem" ou
"quais são essenciais" na Básica, sem reabrir o `.csv`/`.txt` de origem.

## 3. Escopo

### 3.1 O que este SPEC entrega

1. **Dicionário completo** das colunas de `BASICA_RAW` (§5): nome, tipo,
   categoria, confiança, comentário, flag de essencialidade.
2. **Definição formal de "essencial"**: as 29 colunas que a `trusted_
   essencial` (`DEC-007 §2.c`) usa para responder as perguntas de análise
   — cross-validado contra `rascunho/colunas.txt` antes de excluí-lo
   (mesmas 29, mesmos nomes).
3. **Superação** de `docs/dicionario_colunas_basica.md` como referência
   formal — o arquivo pode continuar existindo, mas deixa de ser citado.

### 3.2 Fora de escopo

- Colunas de VRA e SIROS — `SPEC-006` e `SPEC-007` (próximas peças).
- Confirmação contra o dicionário oficial da ANAC — as colunas marcadas
  "incerto" nesta SPEC continuam incertas; esta peça organiza o que já se
  sabe, não resolve o que não se sabe.
- Decidir se alguma coluna hoje não-essencial deveria entrar em
  `trusted_essencial` — isso é matéria de `DEC-007`, não desta SPEC.

## 4. Fontes e método de consolidação

- **`QUERY-011-Dados_das_colunas_de_Trusted.csv`** (112 linhas; removido do
  repositório em 2026-09-07, ver Histórico): fonte primária de conteúdo. Traz `CATEGORIA 1`/`CATEGORIA2` (taxonomia
  mais fina que `colunas.txt`), `CONFIANÇA`, `COMMENT`, e um flag `DEEP`
  que, cruzado, bate exatamente com as 29 colunas de `colunas.txt` —
  confirma que as duas fontes descrevem o mesmo recorte de essenciais,
  não recortes divergentes.
- **`colunas.txt`** (29 linhas; removido antes desta SPEC): definiu
  historicamente o recorte
  essencial; usado aqui só para validar o flag `DEEP` do CSV, não como
  fonte de conteúdo adicional (o CSV já contém tudo que o `.txt` tinha).
- **`docs/dicionario_colunas_basica.md`** (127 linhas, pré-SERMI): cobre
  as mesmas ~112 colunas em formato mais simples (`# | Coluna | Legenda |
  Confiança`), sem a categoria dupla nem o flag essencial. Não estava na
  lista de exceções do `SPEC-001 §5` (só `plano_objetos_snowflake.md` e
  `plano_expansao_multidataset.md` são isentos) — formalizar esta SPEC
  fecha essa lacuna latente da taxonomia, de brinde.

O CSV traz também flags `SURGIU`/`MORTA`/`FUND`/`REP` cujo significado
exato não está documentado na fonte — não uso esses flags aqui além de
manter `MORTA` como nome de categoria onde o CSV já a atribuía (uma
coluna, `NR_ESCALA_DESTINO`); não infiro os demais.

## 5. Dicionário completo de colunas

Legenda de confiança (herdada de `docs/dicionario_colunas_basica.md`):
**confirmado** (verificado em código/dado/DDL deste projeto), **alta
confiança** (padrão de nome inequívoco), **inferido** (leitura razoável,
tratar como hipótese), **incerto** (precisa do dicionário oficial ANAC).

112 colunas ao todo, 29 marcadas **essencial** (usadas em
`trusted_essencial`, `DEC-007 §2.c`).

#### ESSENCIAIS (5 colunas, 5 essenciais)

| Coluna | Tipo | Categoria 2 | Confiança | Essencial | Comentário |
|---|---|---|---|---|---|
| `ID_BASICA` | NUMBER | ESSENCIAL_VOO | confirmado | **sim** | Chave primária do registro (uma linha = uma etapa de voo realizada) |
| `SG_EMPRESA_ICAO` | TEXT | ESSENCIAL_VOO | alta confiança | **sim** | Código ICAO (3 letras) da empresa aérea, ex.: GLO, TAM, AZU |
| `SG_EMPRESA_IATA` | TEXT | ESSENCIAL_VOO | alta confiança | **sim** | Código IATA (2 caracteres) da empresa aérea, ex.: G3, JJ, AD |
| `NR_VOO` | TEXT | ESSENCIAL_VOO | alta confiança | **sim** | Número comercial do voo |
| `DT_REFERENCIA` | DATE | ESSENCIAL_VOO | alta confiança | **sim** | Data de referência do boletim (mês/ano de apuração) |

#### (sem categoria) (23 colunas, 1 essencial)

| Coluna | Tipo | Categoria 2 | Confiança | Essencial | Comentário |
|---|---|---|---|---|---|
| `ID_EMPRESA` | NUMBER | — | alta confiança | não | Identificador numérico da empresa aérea |
| `NM_EMPRESA` | TEXT | — | alta confiança | não | Nome/razão social da empresa aérea |
| `NM_PAIS` | TEXT | — | inferido (padrão de nome) | não | País de registro da empresa aérea |
| `DS_TIPO_EMPRESA` | TEXT | — | incerto — checar dicionário oficial ANAC | não | Classificação do tipo de empresa aérea (ex.: nacional regular) — categorias exatas não verificadas |
| `NR_SINGULAR` | NUMBER | — | incerto — checar dicionário oficial ANAC | não | Identificador numérico da etapa nos sistemas ANAC — termo "singular" não confirmado com precisão |
| `ID_DI` | NUMBER | — | incerto — checar dicionário oficial ANAC | não | Identificador do "DI" associado à etapa — sigla DI não confirmada com certeza (possível "Discriminação de Itinerário") |
| `CD_DI` | TEXT | — | incerto — checar dicionário oficial ANAC | não | Código do DI (ver ID_DI) |
| `DS_DI` | TEXT | — | incerto — checar dicionário oficial ANAC | não | Descrição textual do DI (ver ID_DI) |
| `DS_GRUPO_DI` | TEXT | — | incerto — checar dicionário oficial ANAC | não | Descrição do grupo/categoria a que o DI pertence |
| `NR_ANO_REFERENCIA` | NUMBER | — | alta confiança | não | Ano de referência |
| `NR_SEMESTRE_REFERENCIA` | NUMBER | — | alta confiança | não | Semestre de referência (1 ou 2) |
| `NM_SEMESTRE_REFERENCIA` | TEXT | — | alta confiança | não | Nome do semestre de referência (ex.: 1º Semestre) |
| `NR_TRIMESTRE_REFERENCIA` | NUMBER | — | alta confiança | não | Trimestre de referência (1 a 4) |
| `NM_TRIMESTRE_REFERENCIA` | TEXT | — | alta confiança | não | Nome do trimestre de referência |
| `NR_MES_REFERENCIA` | NUMBER | — | alta confiança | não | Mês de referência (1 a 12) |
| `NM_MES_REFERENCIA` | TEXT | — | alta confiança | não | Nome do mês de referência |
| `NR_SEMANA_REFERENCIA` | NUMBER | — | alta confiança | não | Número da semana no ano de referência |
| `NM_DIA_SEMANA_REFERENCIA` | TEXT | — | alta confiança | não | Nome do dia da semana de referência |
| `NR_DIA_REFERENCIA` | NUMBER | — | alta confiança | não | Dia do mês de referência |
| `NR_ANO_MES_REFERENCIA` | NUMBER | — | alta confiança | não | Ano-mês de referência, formato AAAAMM |
| `ID_TIPO_LINHA` | NUMBER | — | alta confiança | não | Identificador do tipo de linha aérea |
| `CD_TIPO_LINHA` | TEXT | — | alta confiança | não | Código do tipo de linha aérea |
| `NR_ETAPA` | NUMBER | ESSENCIAL_VOO | confirmado | **sim** | Número sequencial da etapa dentro do voo (voos com múltiplas escalas têm mais de uma etapa) |

#### CARAC_LINHA_ETAPA (4 colunas, 4 essenciais)

| Coluna | Tipo | Categoria 2 | Confiança | Essencial | Comentário |
|---|---|---|---|---|---|
| `DS_TIPO_LINHA` | TEXT | CARAC_LINHA | alta confiança | **sim** | Descrição do tipo de linha (ex.: doméstica mista, internacional mista, doméstica cargueira) |
| `DS_NATUREZA_TIPO_LINHA` | TEXT | CARAC_LINHA | inferido (padrão de nome) | **sim** | Natureza do tipo de linha (ex.: doméstica / internacional) |
| `DS_SERVICO_TIPO_LINHA` | TEXT | CARAC_LINHA | inferido (padrão de nome) | **sim** | Tipo de serviço prestado na linha (ex.: passageiro, carga) |
| `DS_NATUREZA_ETAPA` | TEXT | CARAC_ETAPA | inferido (padrão de nome) | **sim** | Natureza da etapa de voo (ex.: comercial, não comercial/posicionamento) |

#### BLOCK_TIME (26 colunas, 4 essenciais)

| Coluna | Tipo | Categoria 2 | Confiança | Essencial | Comentário |
|---|---|---|---|---|---|
| `HR_PARTIDA_REAL` | TIME | — | confirmado | **sim** | Hora real de partida (decolagem) |
| `DT_PARTIDA_REAL` | DATE | — | confirmado | **sim** | Data real de partida |
| `NR_ANO_PARTIDA_REAL` | NUMBER | — | alta confiança | não | Ano de partida real |
| `NR_SEMESTRE_PARTIDA_REAL` | NUMBER | — | alta confiança | não | Semestre de partida real (1 ou 2) |
| `NM_SEMESTRE_PARTIDA_REAL` | TEXT | — | alta confiança | não | Nome do semestre de partida real |
| `NR_TRIMESTRE_PARTIDA_REAL` | NUMBER | — | alta confiança | não | Trimestre de partida real (1 a 4) |
| `NM_TRIMESTRE_PARTIDA_REAL` | TEXT | — | alta confiança | não | Nome do trimestre de partida real |
| `NR_MES_PARTIDA_REAL` | NUMBER | — | alta confiança | não | Mês de partida real (1 a 12) |
| `NM_MES_PARTIDA_REAL` | TEXT | — | alta confiança | não | Nome do mês de partida real |
| `NR_SEMANA_PARTIDA_REAL` | NUMBER | — | alta confiança | não | Número da semana no ano de partida real |
| `NM_DIA_SEMANA_PARTIDA_REAL` | TEXT | — | alta confiança | não | Nome do dia da semana de partida real |
| `NR_DIA_PARTIDA_REAL` | NUMBER | — | alta confiança | não | Dia do mês de partida real |
| `NR_ANO_MES_PARTIDA_REAL` | NUMBER | — | alta confiança | não | Ano-mês de partida real, formato AAAAMM |
| `HR_CHEGADA_REAL` | TIME | — | confirmado | **sim** | Hora real de chegada (pouso) |
| `DT_CHEGADA_REAL` | DATE | — | confirmado | **sim** | Data real de chegada |
| `NR_ANO_CHEGADA_REAL` | NUMBER | — | alta confiança | não | Ano de chegada real |
| `NR_SEMESTRE_CHEGADA_REAL` | NUMBER | — | alta confiança | não | Semestre de chegada real (1 ou 2) |
| `NM_SEMESTRE_CHEGADA_REAL` | TEXT | — | alta confiança | não | Nome do semestre de chegada real |
| `NR_TRIMESTRE_CHEGADA_REAL` | NUMBER | — | alta confiança | não | Trimestre de chegada real (1 a 4) |
| `NM_TRIMESTRE_CHEGADA_REAL` | TEXT | — | alta confiança | não | Nome do trimestre de chegada real |
| `NR_MES_CHEGADA_REAL` | NUMBER | — | alta confiança | não | Mês de chegada real (1 a 12) |
| `NM_MES_CHEGADA_REAL` | TEXT | — | alta confiança | não | Nome do mês de chegada real |
| `NR_SEMANA_CHEGADA_REAL` | NUMBER | — | alta confiança | não | Número da semana no ano de chegada real |
| `NM_DIA_SEMANA_CHEGADA_REAL` | TEXT | — | alta confiança | não | Nome do dia da semana de chegada real |
| `NR_DIA_CHEGADA_REAL` | NUMBER | — | alta confiança | não | Dia do mês de chegada real |
| `NR_ANO_MES_CHEGADA_REAL` | NUMBER | — | alta confiança | não | Ano-mês de chegada real, formato AAAAMM |

#### DESTINOS (1 coluna, 0 essenciais)

| Coluna | Tipo | Categoria 2 | Confiança | Essencial | Comentário |
|---|---|---|---|---|---|
| `ID_AERODROMO_ORIGEM` | NUMBER | — | alta confiança | não | Identificador do aeródromo de origem |

#### TRECHOS (17 colunas, 10 essenciais)

| Coluna | Tipo | Categoria 2 | Confiança | Essencial | Comentário |
|---|---|---|---|---|---|
| `SG_ICAO_ORIGEM` | TEXT | ORIGEM | alta confiança | **sim** | Código ICAO do aeródromo de origem |
| `SG_IATA_ORIGEM` | TEXT | ORIGEM | confirmado | **sim** | Código IATA do aeródromo de origem |
| `NM_AERODROMO_ORIGEM` | TEXT | ORIGEM | alta confiança | não | Nome do aeródromo de origem |
| `NM_MUNICIPIO_ORIGEM` | TEXT | ORIGEM | alta confiança | **sim** | Município do aeródromo de origem |
| `SG_UF_ORIGEM` | TEXT | ORIGEM | alta confiança | **sim** | UF do aeródromo de origem |
| `NM_REGIAO_ORIGEM` | TEXT | ORIGEM | alta confiança | não | Região geográfica (Norte/Sul/etc.) do aeródromo de origem |
| `NM_PAIS_ORIGEM` | TEXT | ORIGEM | alta confiança | **sim** | País do aeródromo de origem |
| `NM_CONTINENTE_ORIGEM` | TEXT | ORIGEM | alta confiança | não | Continente do aeródromo de origem |
| `ID_AERODROMO_DESTINO` | NUMBER | DESTINOS | alta confiança | não | Identificador do aeródromo de destino |
| `SG_ICAO_DESTINO` | TEXT | DESTINOS | alta confiança | **sim** | Código ICAO do aeródromo de destino |
| `SG_IATA_DESTINO` | TEXT | DESTINOS | confirmado | **sim** | Código IATA do aeródromo de destino |
| `NM_AERODROMO_DESTINO` | TEXT | DESTINOS | alta confiança | não | Nome do aeródromo de destino |
| `NM_MUNICIPIO_DESTINO` | TEXT | DESTINOS | alta confiança | **sim** | Município do aeródromo de destino |
| `SG_UF_DESTINO` | TEXT | DESTINOS | alta confiança | **sim** | UF do aeródromo de destino |
| `NM_REGIAO_DESTINO` | TEXT | DESTINOS | alta confiança | não | Região geográfica do aeródromo de destino |
| `NM_PAIS_DESTINO` | TEXT | DESTINOS | alta confiança | **sim** | País do aeródromo de destino |
| `NM_CONTINENTE_DESTINO` | TEXT | DESTINOS | alta confiança | não | Continente do aeródromo de destino |

#### FROTA (4 colunas, 3 essenciais)

| Coluna | Tipo | Categoria 2 | Confiança | Essencial | Comentário |
|---|---|---|---|---|---|
| `ID_EQUIPAMENTO` | NUMBER | — | alta confiança | não | Identificador do tipo/modelo de aeronave (equipamento) |
| `SG_EQUIPAMENTO_ICAO` | TEXT | — | alta confiança | **sim** | Código ICAO do tipo de aeronave, ex.: A320, B738 |
| `DS_MODELO` | TEXT | — | alta confiança | **sim** | Descrição do modelo da aeronave |
| `DS_MATRICULA` | TEXT | — | confirmado | **sim** | Matrícula (prefixo de registro) da aeronave — vazia em ~12% das linhas quando a etapa não identifica a aeronave |

#### MORTA (1 coluna, 0 essenciais)

| Coluna | Tipo | Categoria 2 | Confiança | Essencial | Comentário |
|---|---|---|---|---|---|
| `NR_ESCALA_DESTINO` | NUMBER | MORTA | incerto — checar dicionário oficial ANAC | não | Posição/número da escala na rota até este destino — definição exata não verificada |

#### CARAC_DESPACHO (21 colunas, 2 essenciais)

| Coluna | Tipo | Categoria 2 | Confiança | Essencial | Comentário |
|---|---|---|---|---|---|
| `LT_COMBUSTIVEL` | NUMBER | PERF_DE_VOO | inferido (padrão de nome) | não | Combustível consumido ou embarcado na etapa, em litros |
| `NR_ASSENTOS_OFERTADOS` | NUMBER | — | confirmado | não | Número de assentos ofertados na etapa |
| `KG_PAYLOAD` | NUMBER | — | confirmado | não | Payload: capacidade de carga paga (passageiros + carga + correio), em kg |
| `KM_DISTANCIA` | NUMBER | PERF_DE_VOO | confirmado | **sim** | Distância voada na etapa, em km |
| `NR_PASSAG_PAGOS` | NUMBER | — | alta confiança | não | Número de passageiros pagantes transportados |
| `NR_PASSAG_GRATIS` | NUMBER | — | alta confiança | não | Número de passageiros em cortesia/gratuidade |
| `KG_BAGAGEM_LIVRE` | NUMBER | — | alta confiança | não | Peso de bagagem despachada dentro da franquia gratuita, em kg |
| `KG_BAGAGEM_EXCESSO` | NUMBER | — | alta confiança | não | Peso de bagagem despachada acima da franquia, paga pelo passageiro, em kg |
| `KG_CARGA_PAGA` | NUMBER | — | alta confiança | não | Peso de carga paga transportada, em kg |
| `KG_CARGA_GRATIS` | NUMBER | — | alta confiança | não | Peso de carga transportada gratuitamente, em kg |
| `KG_CORREIO` | NUMBER | — | alta confiança | não | Peso de correio (mala postal) transportado, em kg |
| `NR_DECOLAGEM` | NUMBER | PERF_DE_VOO | incerto — checar dicionário oficial ANAC | não | Contagem de decolagens da etapa (tipicamente 1) — uso exato não verificado |
| `NR_HORAS_VOADAS` | NUMBER | PERF_DE_VOO | confirmado | **sim** | Duração voada da etapa, em horas (decimal com vírgula no arquivo original) |
| `KG_PESO` | NUMBER | — | incerto — checar dicionário oficial ANAC | não | Peso associado à etapa, em kg — payload realizado, peso da aeronave ou outro, não verificado |
| `NR_VELOCIDADE_MEDIA` | NUMBER | PERF_DE_VOO | inferido (padrão de nome) | não | Velocidade média da etapa |
| `NR_PAX_GRATIS_KM` | NUMBER | — | inferido (padrão de nome) | não | Passageiros gratuitos × km voado (produção análoga ao RPK, para gratuidade) |
| `NR_CARGA_PAGA_KM` | NUMBER | — | inferido (padrão de nome) | não | Toneladas de carga paga × km voado |
| `NR_CARGA_GRATIS_KM` | NUMBER | — | inferido (padrão de nome) | não | Toneladas de carga gratuita × km voado |
| `NR_CORREIO_KM` | NUMBER | — | inferido (padrão de nome) | não | Toneladas de correio × km voado |
| `NR_BAGAGEM_PAGA_KM` | NUMBER | — | inferido (padrão de nome) | não | Toneladas de bagagem excedente (paga) × km voado |
| `NR_BAGAGEM_GRATIS_KM` | NUMBER | — | inferido (padrão de nome) | não | Toneladas de bagagem franqueada (gratuita) × km voado |

#### EQUITY (4 colunas, 0 essenciais)

| Coluna | Tipo | Categoria 2 | Confiança | Essencial | Comentário |
|---|---|---|---|---|---|
| `NR_ASK` | NUMBER | — | alta confiança | não | Available Seat-Kilometers — assentos ofertados × km voado; métrica-padrão da indústria para capacidade |
| `NR_RPK` | NUMBER | — | alta confiança | não | Revenue Passenger-Kilometers — passageiros pagos × km voado; métrica-padrão de demanda |
| `NR_ATK` | NUMBER | — | alta confiança | não | Available Ton-Kilometers — capacidade total ofertada (payload, toneladas) × km voado |
| `NR_RTK` | NUMBER | — | alta confiança | não | Revenue Ton-Kilometers — carga paga total transportada (toneladas) × km voado |

Nenhuma coluna `EQUITY` é essencial — decisão explícita (`SPEC-004 §3.2`,
2026-08-30): a etapa média usa só `KM_DISTANCIA`/`NR_HORAS_VOADAS`, ASK
fica fora de escopo por ora.

#### INTERNOS ANAC (6 colunas, 0 essenciais)

| Coluna | Tipo | Categoria 2 | Confiança | Essencial | Comentário |
|---|---|---|---|---|---|
| `ID_ARQUIVO` | NUMBER | — | alta confiança | não | Identificador do arquivo de origem do registro no sistema ANAC |
| `NM_ARQUIVO` | TEXT | — | alta confiança | não | Nome do arquivo de origem do registro |
| `NR_LINHA` | NUMBER | — | alta confiança | não | Número da linha do registro dentro do arquivo de origem |
| `DT_SISTEMA` | TIMESTAMP_NTZ | — | inferido (padrão de nome) | não | Data/timestamp de processamento do registro pelo sistema da ANAC |
| `NR_CHAVE` | TEXT | — | incerto (propósito) / **confirmado** (disponibilidade) | não | Chave técnica adicional do registro — propósito exato não verificado, mas disponibilidade **confirmada** (2026-08-31, `SPEC-008 v2`): só existe em registros com `NR_ANO_REFERENCIA >= 2020`; `NULL` para 2010-2019, a ANAC não publicava essa coluna antes — não é dado faltante por erro |
| `NR_ANO_MES_ARQUIVO` | TEXT | — | confirmado | não | Ano-mês (AAAA-MM) do arquivo de origem — coluna de proveniência ADICIONADA por este pipeline (`03_build_schema.py`), não pertence ao arquivo ANAC original |

## 6. Critérios de sucesso

- **C-01** — Todas as colunas de `BASICA_RAW` estão documentadas nesta
  SPEC, sem lacuna: 111 colunas fiéis ao arquivo ANAC
  (`DDL_001_basica_create_table.sql`) + 1 coluna de proveniência do
  pipeline (`NR_ANO_MES_ARQUIVO`) = 112, confirmado contra o DDL real.
- **C-02** — O conjunto de 29 essenciais desta SPEC é usado, sem alteração
  silenciosa, por `trusted_essencial` (`DEC-007 §2.c`, `SPEC-004 §4.1`).
- **C-03** — `docs/dicionario_colunas_basica.md` deixa de ser citado por
  qualquer documento SERMI novo a partir desta aprovação.

## 7. Premissas e dependências

- Divergência 111 vs. 112 **resolvida**: `sql/ingestao_sqlite/DDL_001_
  basica_create_table.sql` confirma 111 colunas TEXT fiéis ao arquivo
  ANAC original; a 112ª desta SPEC é `NR_ANO_MES_ARQUIVO`, que a própria
  tabela de §5 já marca como "ADICIONADA por este pipeline
  (`03_build_schema.py`), não pertence ao arquivo ANAC original" — não é
  divergência, é coluna de proveniência do pipeline, corretamente
  documentada.
- Confiança "incerto" continua incerta — esta SPEC organiza, não resolve.
- **`NR_CHAVE` (§5, categoria INTERNOS ANAC) tem disponibilidade temporal
  confirmada** (2026-08-31): só existe a partir de `NR_ANO_REFERENCIA >=
  2020`. Achado da carga real (`SPEC-008 §4`), não de inspeção de
  cabeçalho isolada — resolve a hipótese de estabilidade de schema do
  `SPEC-002 C-02` em achado confirmado (schema **não** é estável em
  2010-2026, divergência localizada nesta coluna).

## 8. Não-objetivos

- Não é objetivo confirmar contra o dicionário oficial da ANAC — fica
  como trabalho futuro, fora desta versão.
- Não é objetivo mudar o conjunto de 29 essenciais — isso é decisão da
  `DEC-007`, esta SPEC só documenta e valida consistência.

## 9. Regras checáveis (R-COL)

| ID | Regra | Onde verificar | Severidade |
|---|---|---|---|
| **R-COL-01** | O número de colunas documentadas nesta SPEC bate com `DESCRIBE TABLE BASICA_RAW` (Snowflake) ou `PRAGMA table_info(basica_raw)` (SQLite), a menos de divergência já registrada em §7. | Comparação schema real × §5 | Média |
| **R-COL-02** | O conjunto de colunas marcadas **sim** (essencial) nesta SPEC é idêntico ao conjunto usado por `trusted_essencial` nos dois caminhos. | `DESCRIBE VIEW`/`PRAGMA table_info` de `trusted_essencial` × §5 | Alta |
| **R-COL-03** | Nenhuma coluna essencial tem confiança `incerto` — todo campo usado em análise tem pelo menos leitura razoável do nome ou confirmação direta. | Inspeção de §5, coluna Confiança × Essencial | Alta |
| **R-COL-04** | Nenhum documento SERMI aprovado a partir desta peça cita `docs/dicionario_colunas_basica.md` ou `rascunho/colunas.txt` como referência formal. | Grep em `docs/DEC/`, `docs/SPEC/` | Baixa |

## 10. Limitações conhecidas

- Os flags `SURGIU`/`MORTA`/`FUND`/`REP` do CSV de origem não têm
  significado documentado — não usados nesta SPEC além do nome de
  categoria `MORTA` já atribuído pela fonte.
- Categorias como `(sem categoria)` e nomes como `MORTA`/`EQUITY` vêm
  literalmente da fonte — não renomeados, para preservar rastreabilidade
  com o CSV original.

## 11. Critérios de revisão

Revisitar esta SPEC quando:

- O schema real de `BASICA_RAW` divergir do que está documentado aqui
  (nova coluna, coluna removida pela ANAC).
- Alguma coluna "incerto" for confirmada contra o dicionário oficial —
  atualizar confiança, não reabrir a SPEC inteira.
- O conjunto de essenciais mudar por decisão de uma DEC de conteúdo
  futura (ex.: reabrir ASK para capacidade, `DEC-007 §6`).

## 12. Histórico

| Data | Evento |
|---|---|
| 2026-08-31 | SPEC-005 v1 produzida em status `proposto`, consolidando `QUERY-011-Dados_das_colunas_de_Trusted.csv`, `rascunho/colunas.txt` e `docs/dicionario_colunas_basica.md` num dicionário único, 112 colunas, 29 marcadas essenciais (cross-validado contra `colunas.txt`, mesmo recorte). Fecha lacuna latente do `SPEC-001 §5` (dicionário pré-SERMI não listado como exceção). Aguardando aprovação do autor. |
| 2026-08-31 | **Aprovada.** Autor revisou o lote (junto com os outros seis documentos desta rodada) e aprovou explicitamente. |
| 2026-08-31 | **v2 — correção pós-aprovação.** `NR_CHAVE` (§5) atualizada com achado real: disponível só a partir de `NR_ANO_REFERENCIA >= 2020`, confirmado na carga completa da Básica (`SPEC-008 §4`). Fecha `SPEC-002 C-02` em achado confirmado. §7 atualizada. |
| 2026-08-31 | **v3 — correção pós-aprovação, decisão inalterada (`R-TAX-11`).** Header stale corrigido: `basica_typed` (view retirada) → `basica_silver`, a view real hoje. Achado do `gov-check`, mesma rodada em que `R-TAX-11` foi formalizada no `SPEC-001`. |
| 2026-09-07 | **Correção de rastro, conteúdo inalterado.** As duas fontes primárias desta SPEC (`QUERY-011-Dados_das_colunas_de_Trusted.csv` e `colunas.txt`) viviam em `rascunho/`, pasta que o `.gitignore` declara descartável. O CSV foi removido do repositório nesta data, depois de conferida a absorção coluna a coluna: as 112 colunas do CSV aparecem todas nas 112 linhas da tabela de §5, e as 29 marcadas `DEEP` no CSV são as mesmas 29 marcadas essenciais aqui. Zero conteúdo único perdido. O `colunas.txt` já havia saído antes. §1 e §4 deixam de prefixar os dois com `rascunho/` e passam a dizer que não estão mais no repositório. Nenhuma coluna, categoria, confiança ou regra `R-COL-NN` muda. |

---

*Fim do documento.*
