---
documento: SPEC-010
titulo: Ingestão SQLite — SIROS
versao: v5
status: aprovado
data: 2026-08-31
autor: Bruno Alexandre Serminaro
referencia: DEC-008, SPEC-007
escopo: projeto
---

# SPEC-010 · Ingestão SQLite — SIROS

> SPEC de conteúdo, **implementada** (v3, 2026-08-31): a ingestão do SIROS
> no caminho SQLite compõe incrementalmente `siros_raw` a partir de dois
> formatos de origem (CSV até meados de 2024, JSON depois — §4), na mesma
> tabela, com o mesmo loader. Segue o padrão raw → typed fixado pela
> `DEC-008 §2.a`/§2.d, usando o schema levantado em `SPEC-007`, com
> amostragem **semanal** (não diária) como padrão de carga.
>
> **Nota de numeração**: este número (`SPEC-010`) coincide, por
> coincidência de contagem entre repositórios, com o nome de um rascunho
> externo já removido deste projeto
> (`rascunho/SPEC-010-ANAC-Perguntas_Analise-Deep_Dive-Gol.md`, excluído
> em 2026-08-31). Sem relação alguma entre os dois — numeração deste
> projeto é local e sequencial (`SPEC-001 §4`).

---

## 1. Propósito

Como o SIROS entra em `siros.sqlite` (`DEC-004`) como carga **raw fiel**
ao dado de origem — CSV (até meados de 2024) e JSON (depois, §4), os dois
compostos na mesma tabela — sem tentar resolver, nesta SPEC, a
transformação de autorização-de-slot para voo-por-data que `SPEC-007 §6`
identificou como necessária para qualquer uso analítico futuro
(`DEC-008 §2.d` já registrou isso como fora de escopo aqui).

## 2. Audiência

Reaproveita os papéis abstratos do `SPEC-002 §2` — nenhum papel novo.

## 3. Escopo

### 3.1 O que este SPEC entrega

1. DDL raw proposto (`siros_raw`), 28 colunas, nomes de `SPEC-007 §5`.
2. DDL silver proposto (`siros_silver`, renomeado de `siros_typed` em
   2026-08-31 por consistência com `basica_silver`/`vra_silver`), casts
   básicos — sem expandir
   autorização em voo-por-data.
3. Registro explícito de que a expansão fica fora de escopo (§9).

### 3.2 Fora de escopo

- Expansão "autorização → voo por data" (`SPEC-007 §6`) — camada seguinte
  hipotética, só entra em pauta quando uma pergunta de análise precisar
  dela (`DEC-008 §2.d`).
- Parsing estruturado de `Arpt Origem`/`Arpt Destino`/`Codeshare` (texto
  livre, `SPEC-007 §5`) — mantidos como TEXT bruto.
- Implementação real, Snowflake — mesmas exclusões de `SPEC-009 §3.2`.

## 4. Pipeline implementado

```
scripts/BASH_003_siros_download.sh (já existia; disparado de novo em
     2026-08-31 para cobrir até a data corrente)
  → data/anac/siros/registros_AAAA-MM-DD.csv (nome sempre .csv, conteúdo
       CSV até meados de 2024, JSON depois — §4, mesmo nome de arquivo)
  → sql/ingestao_sqlite/DDL_003_siros_create_table.sql
  → siros_raw (28 colunas TEXT + dt_arquivo TEXT NOT NULL de
       proveniência; uma linha de origem = uma linha na tabela, sem
       expansão, formato de origem detectado por conteúdo, não extensão)
  → src/ingestao_sqlite/SRC_003_siros_load_sqlite.py
       (parse_csv + parse_json, mesma tabela de destino)
  → sql/tratamento/DDL_NNN_siros_view_silver_sqlite.sql (ainda proposto,
       não implementado — ver §6)
  → siros_silver (view, casts básicos)
```

### Achado que mudou a política de carga (2026-08-31)

Teste com um mês completo, diário (agosto/2022, 31 arquivos): **1.543.629
linhas**, mas só **578.333 `nr_siros` distintos** — cada autorização
aparece em média 2,7× dentro do mês. Confirma que cada arquivo diário é
um **snapshot completo** das autorizações ativas naquele dia, não um
incremento. Extrapolado para o histórico inteiro (1.775 arquivos):
**~37 GB**, **~3h** de carga.

**Decisão do autor**: manter fidelidade diária não valia o custo —
adotada **amostragem semanal** (1 arquivo por semana, sempre de
segunda-feira) como política padrão de "raw" para este dataset. Reduz o
volume em ~7× sem inventar dado, só reduz a frequência de snapshot
mantida. `SRC_003_siros_load_sqlite.py` aceita `--diario` para forçar
fidelidade diária completa, se algum dia for necessário — não é a opção
padrão.

**Isso é uma exceção deliberada à fidelidade estrita** que `basica_raw`/
`vra_raw` seguem (fiéis linha a linha ao arquivo de origem, sem recorte).
Justificada pela natureza específica do SIROS (snapshot redundante, não
evento novo por dia) — não é precedente para reduzir fidelidade das
outras duas bases.

### Segundo achado: mudança de formato CSV → JSON (2026-08-31)

Durante a carga completa, o loader travou em `registros_2024-06-17.csv`:
o arquivo não é CSV, é um array JSON (`[{"Cod_Empresa":"AAL",...}]`). A
transição não é uma virada limpa — alterna entre CSV e JSON por algumas
semanas (`2024-06-17` já é JSON, `2024-06-24` volta a ser CSV) antes de
se fixar em JSON a partir de `2024-09-16` em diante.

**Correção em duas etapas**: primeiro (mesma sessão) o loader passou a
detectar o formato de cada arquivo e pular o que não sabia processar, sem
abortar a carga inteira. Depois (pedido do autor, mesma sessão), ganhou
um **parser JSON de verdade** (`parse_json`, `SIROS_JSON_KEYS` no
script): os mesmos 28 campos, chaves em inglês sem acento em vez do
cabeçalho em português do CSV, mapeados um a um para as mesmas colunas de
`siros_raw` — sem mudança de schema, mesma tabela, mesma política de
amostragem semanal, mesma idempotência por `dt_arquivo`.

**Consequência**: `siros_raw` agora compõe os dois formatos numa tabela
só, de forma incremental — a mesma execução de `SRC_003` cobre semanas em
CSV e semanas em JSON sem distinção para quem consome os dados depois.

## 5. DDL raw implementado — `siros_raw`

```sql
CREATE TABLE IF NOT EXISTS siros_raw (
    "cd_empresa" TEXT,
    "nm_empresa" TEXT,
    "nr_voo" TEXT,
    "sg_equipamento_icao" TEXT,
    "fl_opera_segunda" TEXT,
    "fl_opera_terca" TEXT,
    "fl_opera_quarta" TEXT,
    "fl_opera_quinta" TEXT,
    "fl_opera_sexta" TEXT,
    "fl_opera_sabado" TEXT,
    "fl_opera_domingo" TEXT,
    "nr_assentos_ofertados" TEXT,
    "nr_siros" TEXT,
    "ds_situacao_siros" TEXT,
    "dt_registro" TEXT,
    "dt_inicio_operacao" TEXT,
    "dt_fim_operacao" TEXT,
    "ds_natureza_operacao" TEXT,
    "nr_etapa" TEXT,
    "cd_origem" TEXT,
    "nm_aerodromo_origem" TEXT,
    "cd_destino" TEXT,
    "nm_aerodromo_destino" TEXT,
    "hr_partida" TEXT,
    "hr_chegada" TEXT,
    "ds_tipo_servico" TEXT,
    "ds_objeto_transporte" TEXT,
    "ds_codeshare" TEXT,
    dt_arquivo TEXT NOT NULL
);
```

`dt_arquivo` (adicionada na implementação, ausente da v1 desta SPEC): data
do arquivo de origem (`registros_AAAA-MM-DD.csv`), coluna de proveniência
— mesmo papel que `nr_ano_mes_arquivo` cumpre em `basica_raw`/`vra_raw`,
e usada pelo loader para idempotência (pula arquivo já carregado).

Sem chave primária natural única confirmada — `nr_siros` parece candidato
(`SPEC-007 §5`, ex. `AAL-014694106`), mas unicidade não testada (repete
entre semanas por natureza, ver §4).

## 6. DDL silver implementado — `siros_silver`

Implementada em 2026-08-31 (`sql/tratamento/DDL_005_siros_view_silver_
sqlite.sql`). Antes de materializar, medido contra `siros_raw` inteiro:

### Achado: `dt_registro` tem a mesma quebra de formato do VRA, direção oposta

O DDL originalmente proposto (v4 desta SPEC) usava `datetime(dt_registro)`
incondicional — teria devolvido `NULL` silencioso para mais da metade da
tabela. Medido: **4.851.007 linhas em ISO** (`AAAA-MM-DD HH:MM:SS`, era
CSV, até meados de 2024) e **5.826.375 em `DD/MM/AAAA HH:MM:SS`** (era
JSON, a partir de meados de 2024) — zero linhas em terceiro formato.
Mesmo padrão do `SPEC-009` achado 1 (VRA), mas invertido: lá a mudança foi
`DD/MM`→ISO ao longo do tempo; aqui é ISO→`DD/MM`. Detectado e convertido
por `GLOB`, mesma técnica.

`dt_inicio_operacao`/`dt_fim_operacao` **não** têm esse problema — sempre
ISO, só mudam de granularidade (datetime completo na era CSV, ex.
`"2020-03-08 00:00:00"`; só data na era JSON, ex. `"2024-04-01"`) —
`date()` trata os dois sem `CASE` extra (medido, zero divergência real
depois de descontar a diferença de granularidade).

```sql
CREATE VIEW siros_silver AS
SELECT
    NULLIF(cd_empresa, '') AS cd_empresa, NULLIF(nm_empresa, '') AS nm_empresa,
    NULLIF(nr_voo, '') AS nr_voo, NULLIF(sg_equipamento_icao, '') AS sg_equipamento_icao,
    fl_opera_segunda, fl_opera_terca, fl_opera_quarta, fl_opera_quinta,
    fl_opera_sexta, fl_opera_sabado, fl_opera_domingo,
    CAST(NULLIF(nr_assentos_ofertados, '') AS INTEGER) AS nr_assentos_ofertados,
    NULLIF(nr_siros, '') AS nr_siros, NULLIF(ds_situacao_siros, '') AS ds_situacao_siros,
    CASE
        WHEN dt_registro GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]*'
            THEN datetime(dt_registro)
        WHEN dt_registro GLOB '[0-9][0-9]/[0-9][0-9]/[0-9][0-9][0-9][0-9]*'
            THEN datetime(substr(dt_registro,7,4) || '-' || substr(dt_registro,4,2)
                 || '-' || substr(dt_registro,1,2) || ' ' || substr(dt_registro,12,8))
        ELSE NULL
    END AS dt_registro,
    date(dt_inicio_operacao) AS dt_inicio_operacao, date(dt_fim_operacao) AS dt_fim_operacao,
    NULLIF(ds_natureza_operacao, '') AS ds_natureza_operacao,
    CAST(NULLIF(nr_etapa, '') AS INTEGER) AS nr_etapa,
    NULLIF(cd_origem, '') AS cd_origem, NULLIF(nm_aerodromo_origem, '') AS nm_aerodromo_origem,
    NULLIF(cd_destino, '') AS cd_destino, NULLIF(nm_aerodromo_destino, '') AS nm_aerodromo_destino,
    time(hr_partida) AS hr_partida, time(hr_chegada) AS hr_chegada,
    NULLIF(ds_tipo_servico, '') AS ds_tipo_servico,
    NULLIF(ds_objeto_transporte, '') AS ds_objeto_transporte,
    NULLIF(ds_codeshare, '') AS ds_codeshare, date(dt_arquivo) AS dt_arquivo
FROM siros_raw;
```

`fl_opera_*` continuam `TEXT` sem `NULLIF` — não confirmado se vazio é
significativo (§ premissa abaixo) — e sem cast para booleano, mesmo
motivo que a v4 já registrava.

Validado: 10.677.382 linhas (igual a `siros_raw`), 29 colunas
(`PRAGMA table_info`), **zero `NULL` em `dt_registro`** — os dois formatos
convertem, nenhum terceiro formato passou despercebido.

`fl_opera_*` ficam como `TEXT`, sem cast para booleano — a `SPEC-007 §6`
ainda não confirmou se o valor marca presença ou vem sempre preenchido;
tipar como booleano agora seria decidir algo que não está confirmado.

## 7. Critérios de sucesso

- **C-01** — DDL raw implementado, batendo com o schema de `SPEC-007 §5`
  + `dt_arquivo` de proveniência. **Cumprido.**
- **C-02** — Carga de pelo menos um arquivo real de SIROS executada sem
  erro. **Cumprido** (teste de agosto/2022, depois recarregado sob a
  política semanal).
- **C-03** — Nenhuma expansão autorização→voo-por-data implementada nesta
  versão (critério negativo). **Cumprido.**
- **C-04** — Carga semanal do histórico completo (CSV + JSON) executada,
  idempotente, sem erro. **Cumprido, cobertura máxima disponível na
  fonte**: 2019-11-11 a 2025-02-10 (254 semanas, 10.677.382 linhas) — a
  ANAC não publica SIROS além de 2025-02-14 (confirmado, §4); não é
  lacuna de download, é o que existe.
- **C-05** *(novo, v5)* — `siros_silver` criada com as 29 colunas
  (`SPEC-007` + `dt_arquivo`), formato de data duplo tratado sem `NULL`
  silencioso. **Cumprido**: 10.677.382 linhas, zero `NULL` em
  `dt_registro` (§6).

## 8. Premissas e dependências

- Estrutura de `registros_2022-08-10.csv` (base de `SPEC-007`) generalizou
  para o mês inteiro testado — **confirmado**, não mais premissa.
- Volume real do SIROS: **medido** (§4) — ~1,54M linhas/mês em carga
  diária, ~37 GB para o histórico diário completo. Resolve a hipótese
  candidata do `REP-001 §5.2` em achado confirmado.
- `scripts/BASH_003_siros_download.sh` já baixa os arquivos necessários —
  confirmado; disparado de novo (2026-08-31) para cobrir 2025-02-15 até a
  data corrente. **Resultado: 0 arquivos novos, todos 404** — a ANAC
  simplesmente não publicou SIROS além de 2025-02-14 até o momento desta
  carga (confirmado inspecionando a listagem real da pasta `2025/02 -
  Fevereiro/`: os arquivos param em `registros_2025-02-14`, tanto `.csv`
  quanto `.json` — não é problema de padrão de URL, é ausência real na
  fonte). Achado extra: a partir de algum ponto a ANAC passou a publicar
  **os dois formatos lado a lado** (`registros_AAAA-MM-DD.csv` **e**
  `.json`), não só o `.csv` com conteúdo JSON disfarçado — útil se a
  ingestão futura quiser preferir o `.json` explícito em vez de
  detectar por conteúdo.

## 9. Não-objetivos

- Não é objetivo resolver a expansão autorização→voo-por-data
  (`SPEC-007 §6`) — permanece registrada, não implementada, até uma
  pergunta de análise real precisar dela.
- Não é objetivo parsear `nm_aerodromo_origem`/`destino` (texto composto)
  em aeroporto/cidade/país separados — fica como texto bruto.
- Não é objetivo confirmar unicidade de `nr_siros` como chave primária
  nesta versão.
- Não é objetivo tipar `fl_opera_*` como booleano (§6) — a `SPEC-007 §6`
  ainda não confirmou se vazio é significativo.

## 10. Regras checáveis (R-COL)

| ID | Regra | Onde verificar | Severidade |
|---|---|---|---|
| **R-COL-12** | `siros_raw` contém exatamente as 28 colunas de `SPEC-007 §5` + `dt_arquivo`; uma linha do arquivo carregado = uma linha na tabela (sem expansão). | `PRAGMA table_info(siros_raw)` × `SELECT COUNT(*)` vs. linhas do arquivo | Alta |
| **R-COL-13** | Nenhum script desta SPEC implementa expansão autorização→voo-por-data — violação sinalizaria escopo não respeitado (§9). | Leitura dos scripts de carga | Alta |
| **R-COL-14** *(novo, v2)* | Carga padrão (`SRC_003` sem `--diario`) só processa arquivos de segunda-feira — `SELECT dt_arquivo` distintos em `siros_raw` caem todos num só dia da semana, a menos que `--diario` tenha sido usado explicitamente. | `strftime('%w', dt_arquivo)` em `siros_raw` — deve ser sempre `'1'` | Média |
| **R-COL-15** *(v3, redefinida)* | `MAX(dt_arquivo)` em `siros_raw` nunca ultrapassa a data mais recente já baixada em `data/anac/siros/` — carga não pode estar "à frente" do download. | `SELECT MAX(dt_arquivo) FROM siros_raw` × arquivos mais recentes em disco | Alta |
| **R-COL-17** *(novo, v3)* | Uma mesma semana (`dt_arquivo`) nunca tem linhas de origem CSV e JSON misturadas — cada `dt_arquivo` veio de um único arquivo, logo de um único formato. | Não verificável direto por coluna (formato de origem não é persistido); inferir por auditoria pontual do script de carga | Baixa |
| **R-COL-24** *(novo, v5)* | `siros_silver` contém exatamente as 29 colunas (`SPEC-007` + `dt_arquivo`). | `PRAGMA table_info(siros_silver)` | Alta |
| **R-COL-25** *(novo, v5)* | Nenhum valor não-nulo de `dt_registro` em `siros_raw` produz `NULL` em `siros_silver` — os dois formatos conhecidos (ISO, `DD/MM/AAAA`) precisam sempre converter; um terceiro formato futuro cairia em `NULL` sem aviso (mesma limitação do VRA, `SPEC-009 §12`). | `SELECT COUNT(*) FROM siros_silver WHERE dt_registro IS NULL` deve ser `0` | Alta |

## 11. Limitações conhecidas

- **Amostragem semanal perde eventos intra-semana**: uma autorização
  criada e encerrada entre duas segundas-feiras nunca aparece em
  `siros_raw` sob a política padrão — trade-off aceito pela decisão do
  autor (§4), não um bug.
- Cobertura de `siros_raw` (2019-11-11 a 2025-02-10) é o **máximo
  disponível na fonte** hoje, não um recorte por escolha — confirmado por
  inspeção direta da pasta remota (§4). Revisitar quando a ANAC publicar
  mais.
- Formato de origem (CSV/JSON) não é persistido em `siros_raw` — quem
  quiser saber de qual formato uma semana veio precisa inferir pela data
  (`< 2024-06-17` é CSV, `>= 2024-09-16` é JSON, entre as duas é
  ambíguo sem checar o arquivo).
- O `GLOB` de `dt_registro` (§6) só cobre os dois formatos conhecidos — um
  terceiro formato futuro cairia em `NULL` sem aviso, mesma limitação já
  registrada para o VRA (`SPEC-009 §12`).
- `fl_opera_*` seguem `TEXT`, sem `NULLIF` nem cast para booleano (§6, §9)
  — vazio pode ou não ser significativo, não confirmado.

## 12. Critérios de revisão

Revisitar esta SPEC quando:

- A implementação real revelar que o schema proposto (§5-§6) precisa de
  ajuste.
- Alguma pergunta de análise exigir a expansão autorização→voo-por-data —
  aciona `DEC-008 §2.d`, não só esta SPEC.
- Alguma pergunta de análise precisar de granularidade diária real —
  reabre a decisão de amostragem semanal do §4 (rodar com `--diario`).
- A ANAC publicar SIROS além de 2025-02-14 — rodar
  `scripts/BASH_003_siros_download.sh` e depois `SRC_003` de novo
  (idempotente, sem retrabalho).
- A ANAC mudar o formato de novo (terceira vez) — o padrão já estabelecido
  aqui (detectar por conteúdo, não por extensão, mapear para o schema
  existente) deve se repetir, não reabrir do zero.

## 13. Histórico

| Data | Evento |
|---|---|
| 2026-08-31 | SPEC-010 v1 produzida em status `proposto`, prospectiva. DDL raw/typed propostos a partir de `SPEC-007`, expansão autorização→voo-por-data explicitamente fora de escopo. Nada implementado ainda. Materializa a `DEC-008`. Aguardando aprovação do autor. |
| 2026-08-31 | **Aprovada.** Autor revisou o lote e aprovou explicitamente. |
| 2026-08-31 | **v2 — implementação real.** `DDL_003_siros_create_table.sql` e `SRC_003_siros_load_sqlite.py` criados; `dt_arquivo` adicionada como coluna de proveniência (ausente da v1). Teste diário de um mês (ago/2022) mediu volume real do SIROS (~1,54M linhas/mês, ~37 GB/~3h para o histórico diário completo) — resolve hipótese candidata do `REP-001 §5.2`. Decisão do autor: amostragem semanal (segundas-feiras) como política padrão de carga, reduzindo ~7× o volume; `--diario` disponível para forçar fidelidade completa. Banco de teste recriado sob a nova política. C-04 adicionado. §4-§12 atualizados. |
| 2026-08-31 | Carga completa executada (com uma interrupção externa no meio, retomada sem perda — idempotente). Achado: a ANAC muda o formato do SIROS de CSV para JSON, com transição irregular a partir de 2024-06-17, fixando-se em JSON a partir de 2024-09-16. Loader corrigido para detectar e pular formato não suportado em vez de abortar a carga inteira. Resultado parcial: `siros_raw` com 9.490.568 linhas, 231 semanas, até 2024-09-09. R-COL-15 adicionado. |
| 2026-08-31 | **v3 — parser JSON implementado.** A pedido do autor, `SRC_003_siros_load_sqlite.py` ganhou `parse_json`/`SIROS_JSON_KEYS`: mapeia os 28 campos do formato novo (chaves em inglês) para as mesmas colunas de `siros_raw`, na mesma tabela, mesma política semanal, mesma idempotência — não é mais "não suportado", é um segundo formato de entrada tratado pelo mesmo loader. Carregadas as 23 semanas JSON já baixadas: +1.186.814 linhas, total 10.677.382. Download disparado de novo para cobrir 2025-02-15 até a data corrente — **resultado: 0 arquivos, todos 404**, confirmado por inspeção direta que a ANAC não publica SIROS além de 2025-02-14 (não é lacuna de download, é o que existe na fonte hoje). Achado extra: a partir de certo ponto a ANAC passa a publicar `.csv` e `.json` lado a lado, não só `.csv` com conteúdo JSON. Cobertura final desta versão: 2019-11-11 a 2025-02-10, 254 semanas, 10.677.382 linhas — máximo disponível. C-04, §8, §9, §10 (R-COL-15 redefinida, R-COL-17 novo), §11, §12 atualizados. |
| 2026-08-31 | **v4 — renomeação de camada.** `siros_typed` renomeado para `siros_silver` em todo o documento (§3.1, §4, §6, §7, §9), sem mudança de conteúdo — consistência com `basica_silver`/`vra_silver`, já implementados e nomeados assim a pedido do autor. Segue proposto, não implementado. |
| 2026-08-31 | **v5 — `siros_silver` implementado.** Antes de materializar, achado: `dt_registro` tem a mesma quebra de formato do VRA (`SPEC-009` achado 1), direção oposta (ISO→`DD/MM/AAAA`, não `DD/MM`→ISO) — o DDL da v4 teria produzido `NULL` silencioso em 5.826.375 das 10.677.382 linhas. Corrigido por `GLOB`, mesma técnica do VRA. `dt_inicio_operacao`/`dt_fim_operacao` confirmados sem esse problema, só mudam de granularidade entre eras. Validado: 10.677.382 linhas, 29 colunas, zero `NULL` em `dt_registro`. `sql/tratamento/DDL_005_siros_view_silver_sqlite.sql`. C-05, R-COL-24/25 adicionados. §6, §7, §9, §10, §11 atualizados. |

---

*Fim do documento.*
