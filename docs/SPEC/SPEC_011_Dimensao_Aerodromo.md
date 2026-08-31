---
documento: SPEC-011
titulo: Dimensão de Aeródromo — Localização e Fuso Horário
versao: v1
status: aprovado
data: 2026-08-31
autor: Bruno Alexandre Serminaro
referencia: DEC-009
escopo: projeto
---

# SPEC-011 · Dimensão de Aeródromo — Localização e Fuso Horário

> Documenta a tabela `dim_airport_location_time_zone`, já carregada em
> `db/anac_basica.sqlite`: de onde vem, o que foi descartado na carga, e
> as escolhas de limpeza. Materializa a `DEC-009`.

---

## 1. Propósito

Dar rastro formal a uma tabela de referência (não é dataset ANAC, é
dimensão de aeródromo) que entrou no projeto por pedido direto do autor,
sem o ciclo completo "SPEC antes de construir" que as três bases ANAC
tiveram — regularização no mesmo espírito do `DEC-004`.

## 2. Audiência

Reaproveita os papéis abstratos do `SPEC-002 §2` — nenhum papel novo.

## 3. Escopo

### 3.1 O que este SPEC entrega

Documentação da tabela `dim_airport_location_time_zone`: fonte, colunas,
critério de limpeza aplicado na carga, e o que ficou de fora.

### 3.2 Fora de escopo

- Formalizar `data/aerodromos_enriquecido.csv`/`SRC_001_enriquecer_
  bases_aerodromos.py` (o script que gerou o dado de origem) — dívida
  pré-existente, fora desta SPEC (`DEC-009 §5.3`).
- Resolver o caso `SBQV` (ICAO reatribuído entre dois aeroportos físicos
  ao longo do tempo) além de escolher uma linha canônica — incerteza
  registrada (§8), não resolvida aqui.
- Uso da dimensão em qualquer pergunta de análise (`DEC-007`) — quando
  acontecer, é a pergunta de análise que referencia esta SPEC, não o
  contrário.

## 4. Fonte e proveniência

```
data/aerodromos_enriquecido.csv (913 linhas na granularidade ICAO+IATA
  observado, OurAirports + tzdata, src/SRC_001_enriquecer_bases_
  aerodromos.py, 2026-08-25)
  → exclui 5 linhas _match = SEM_MATCH (sem coordenada)
  → dedup por BASE_ICAO, fica a linha de maior QT_OCORRENCIAS
       (858 ICAO únicos)
  → src/ingestao_sqlite/SRC_004_dim_airport_load_sqlite.py
  → sql/ingestao_sqlite/DDL_005_dim_airport_create_table.sql
  → dim_airport_location_time_zone (tabela, db/anac_basica.sqlite)
```

Primeira versão desta tabela (não aprovada, superada nesta mesma v1) veio
de `rascunho/dim_airport_location_time_zone.csv`, um recorte manual de
283 aeródromos cujo critério nunca foi confirmado. O autor pediu para
completar direto a partir da fonte primária — o recorte fica histórico,
sem uso no pipeline de carga atual.

## 5. Colunas carregadas e descartadas

| Coluna no CSV de origem | Entra na tabela? | Nome na tabela | Observação |
|---|---|---|---|
| `BASE_ICAO` | Sim | `base_icao` | Chave primária, único após dedup (§6) |
| `BASE_IATA` | Sim | `base_iata` | Vazio ou `"..."` (placeholder) tratado como `NULL`, ver §6 |
| `QT_OCORRENCIAS` | **Não** | — | usada só para escolher a linha canônica na dedup (§6), não persiste |
| `_match` | **Não** | — | usada só para excluir `SEM_MATCH` (§6), não persiste |
| `LATITUDE` | Sim | `latitude` | `REAL` |
| `LONGITUDE` | Sim | `longitude` | `REAL` |
| `TZ_IANA` | Sim | `tz_iana` | ex. `America/Sao_Paulo` |
| `UTC_OFFSET_PADRAO_H` | Sim | `utc_offset` | `REAL`, não `INTEGER` — existem fusos de meia hora (achado, §8) |
| `HORARIO_VERAO_ATUAL` | **Não** | — | descartada, pedido do autor (`DEC-009 §2.e`) |
| `JA_TEVE_HORARIO_VERAO` | **Não** | — | descartada, pedido do autor (`DEC-009 §2.e`) |
| `NOME_OURAIRPORTS` | Sim | `nome_ourairports` | Para os 8 aeródromos `MANUAL_KEYWORD`, carrega nota de resolução manual (ex. "fechado", "ident atual X"), não um nome comercial limpo |
| `MUNICIPIO_OURAIRPORTS` | Sim | `municipio_ourairports` | `NULL` para os 8 `MANUAL_KEYWORD` (§6) |
| `PAIS_ISO` | Sim | `pais_iso` | `NULL` para os 8 `MANUAL_KEYWORD` (§6) |
| `TIPO_OURAIRPORTS` | Sim | `tipo_ourairports` | `large_airport`/`medium_airport`/`small_airport` na maioria; para os 8 `MANUAL_KEYWORD` carrega texto de diagnóstico da fonte (ex. `"OurAirports id 5963, keyword-match"`), não uma categoria limpa |

As duas colunas de horário de verão não se perdem: continuam em
`data/aerodromos_enriquecido.csv`, só não entram nesta tabela.

## 6. Limpeza aplicada na carga

Medido no arquivo de origem (913 linhas, granularidade ICAO+IATA
observado):

- **5 linhas `_match = SEM_MATCH`** (`N/I`, `LGAT`, `SABG`, `MMTY`,
  `SBER`): sem `LATITUDE`/`LONGITUDE`/`TZ_IANA`. Excluídas — não servem
  como dimensão de localização. `MMTY` é achado documentado desde a
  geração original: código pesquisado supondo ser Monterrey, mas o ICAO
  real é `MMMY`.
- **46 códigos `BASE_ICAO` com mais de uma linha**: o arquivo de origem
  guarda uma linha por combinação (ICAO, IATA observado nos microdados),
  não uma linha por aeroporto. Resolvido com dedup: fica a linha de maior
  `QT_OCORRENCIAS`. Em 45 casos é só ruído de IATA (mesmo aeroporto,
  código IATA variante). Um caso é divergência real: **`SBQV`** teve o
  código reatribuído entre dois aeroportos físicos diferentes ao longo do
  tempo (o antigo, fechado — "Pedro Otacilio Figueiredo Airport" — e o
  atual, "Glauber de Andrade Rocha Airport", Vitória da Conquista). A
  regra de maior `QT_OCORRENCIAS` mantém o antigo (mais observações na
  janela dos microdados), coincidindo com a resolução manual já feita na
  geração original (`_match = MANUAL_KEYWORD`).
- **8 aeródromos `_match = MANUAL_KEYWORD`** (incluindo `SBQV`): fechados
  ou com ICAO reatribuído, resolvidos manualmente na geração original sem
  `MUNICIPIO_OURAIRPORTS`/`PAIS_ISO`. Ficam `NULL`, não string vazia.
- **`BASE_IATA` vazio ou `"..."` (placeholder, ex. `SBYS`/Campo
  Fontenelle)**: vira `NULL`, não o literal — mesmo critério de coerência
  que `basica_silver`/`vra_silver` já usam (`NULLIF`).

## 7. Critérios de sucesso

- **C-01** — Tabela criada a partir de `data/aerodromos_enriquecido.csv`,
  sem as duas colunas de horário de verão. **Cumprido**: 858 linhas,
  `PRAGMA table_info` sem `hor_verao_atual`/`ja_teve_horario_verao`.
- **C-02** — Nenhum valor placeholder (`"..."`) chega como `TEXT` real na
  tabela. **Cumprido**: `SBYS.base_iata` confirmado `NULL`.
- **C-03** — `base_icao` é único (serve de chave). **Cumprido**: dedup
  por `QT_OCORRENCIAS` aplicado antes da carga, 858 ICAO únicos.
- **C-04** *(novo)* — Nenhuma linha `SEM_MATCH` entra na tabela.
  **Cumprido**: 5 linhas excluídas antes da carga.
- **C-05** *(novo)* — `utc_offset` aceita fuso de meia hora sem truncar.
  **Cumprido**: `VCBI`/`VOMM`/`VIDP`/`VOHS`/`VABB` confirmados com
  `utc_offset = 5.5`.

## 8. Premissas e incertezas

- **Incerteza, não achado**: `SBQV` representa, nesta tabela, o aeroporto
  fechado (maior `QT_OCORRENCIAS` na janela observada), não o aeroporto
  atual que hoje usa o mesmo código ICAO. A tabela é um retrato único por
  ICAO — não captura reatribuição ao longo do tempo. Se uma pergunta de
  análise precisar diferenciar por período, este caso reabre (`DEC-009
  §6`).
- Ambiente `pesquisa-azul` (conda) disponível para rodar o script de
  carga — mesma premissa do `SPEC-002 §6`.

## 9. Não-objetivos

- Não é objetivo desta SPEC resolver o caso `SBQV` além de escolher uma
  linha canônica (§8) — se uma análise futura precisar do aeroporto
  atual, é ela que decide como tratar.
- Não é objetivo replicar esta tabela em `anac_vra.sqlite` — `DEC-009
  §5.2` já registra essa tensão como consequência aceita, não resolvida.
- Não é objetivo normalizar `nome_ourairports`/`tipo_ourairports` dos 8
  aeródromos `MANUAL_KEYWORD` para o mesmo formato dos demais — o texto
  de diagnóstico da fonte é preservado como está, não reescrito.

## 10. Regras checáveis (R-COL)

| ID | Regra | Onde verificar | Severidade |
|---|---|---|---|
| **R-COL-20** | `dim_airport_location_time_zone` não contém `hor_verao_atual` nem `ja_teve_horario_verao` — qualquer recarga que reintroduza essas colunas viola o pedido do `DEC-009 §2.e`. | `PRAGMA table_info(dim_airport_location_time_zone)` | Média |
| **R-COL-21** | Nenhuma linha de `dim_airport_location_time_zone` tem o literal `"..."` em `base_iata` (ou qualquer outra coluna `TEXT`) — placeholder de origem sempre vira `NULL`. | `SELECT * WHERE base_iata = '...'` deve retornar zero linhas | Média |
| **R-COL-22** *(novo)* | `base_icao` é único (858 linhas, uma por ICAO) — nenhuma recarga pode reintroduzir a granularidade (ICAO, IATA) da fonte sem dedup. | `SELECT base_icao, COUNT(*) GROUP BY base_icao HAVING COUNT(*) > 1` deve retornar zero linhas | Alta |
| **R-COL-23** *(novo)* | `utc_offset` é `REAL`, não `INTEGER` — recarga que trunque fuso de meia hora (`-3.5`, `3.5`, `4.5`, `5.5`) viola o schema. | `PRAGMA table_info` (tipo da coluna) e `SELECT DISTINCT utc_offset` | Média |

## 11. Limitações conhecidas

- **`SBQV` representa o aeroporto fechado, não o atual** (§8) — quem
  esperar sempre o aeroporto operante para um código ICAO precisa checar
  esse caso especificamente.
- **5 aeródromos observados nos microdados (`SEM_MATCH`) não estão na
  dimensão** — `JOIN` sem `LEFT JOIN` por `sg_icao_origem`/`destino` =
  `base_icao` perde essas linhas silenciosamente.
- Vive dentro de `anac_basica.sqlite`; cruzar com `anac_vra.sqlite`
  exige `ATTACH DATABASE` (`DEC-009 §5.2`).
- Horário de verão fica fora da tabela por decisão explícita — quem
  precisar dele consulta `data/aerodromos_enriquecido.csv` direto, não
  esta tabela.
- `nome_ourairports`/`tipo_ourairports` dos 8 aeródromos `MANUAL_KEYWORD`
  carregam texto de diagnóstico da fonte, não uma categoria/nome limpo
  (§5, §9).

## 12. Critérios de revisão

Revisitar esta SPEC quando:

- Uma pergunta de análise precisar diferenciar `SBQV` (ou caso
  equivalente) por período em vez de um retrato único por ICAO.
- A dimensão precisar ser consultada a partir do `vra.sqlite` com
  frequência (reabre `DEC-009 §4.1`).
- `data/aerodromos_enriquecido.csv` for atualizado ou ganhar DEC/SPEC
  própria.

## 13. Histórico

| Data | Evento |
|---|---|
| 2026-08-31 | SPEC-011 v1 produzida em status `proposto`, retroativa. Documenta `dim_airport_location_time_zone`, carregada em `anac_basica.sqlite` a partir do recorte de 283 linhas fornecido pelo autor. Materializa a `DEC-009`. Aguardando aprovação do autor. |
| 2026-08-31 | Completada a pedido do autor: fonte trocada para `data/aerodromos_enriquecido.csv` (858 aeródromos, 5 `SEM_MATCH` excluídos, dedup por maior `QT_OCORRENCIAS`). Achados novos: fuso de meia hora (`utc_offset` de `INTEGER` para `REAL`), 8 aeródromos `MANUAL_KEYWORD` sem município/país, e `SBQV` com ICAO reatribuído entre dois aeroportos físicos. §3.2, §4-§9, §10 (R-COL-22/23 novos), §11, §12 atualizados. |
| 2026-08-31 | **Aprovada.** Autor revisou o lote (DEC-009 + SPEC-011) e aprovou explicitamente. |

---

*Fim do documento.*
