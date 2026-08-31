---
documento: SPEC-009
titulo: Ingestão SQLite — VRA
versao: v1
status: aprovado
data: 2026-08-31
autor: Bruno Alexandre Serminaro
referencia: DEC-008, SPEC-006
escopo: projeto
---

# SPEC-009 · Ingestão SQLite — VRA

> SPEC de conteúdo, **prospectiva**: desenha a ingestão do VRA no caminho
> SQLite — hoje só existe download bruto
> (`scripts/BASH_002_vra_download.sh`). Segue o padrão raw → typed fixado
> pela `DEC-008 §2.a`, usando o schema levantado em `SPEC-006`. Nada
> aqui está implementado ainda.

---

## 1. Propósito

Desenhar, antes de implementar, como o VRA entra em `vra.sqlite`
(`DEC-004`) seguindo o mesmo padrão já provado na Básica (`SPEC-008`),
respeitando as diferenças estruturais reais que `SPEC-006` já levantou
(12 colunas, `Partida Real`/`Chegada Real` como timestamp único, não
separado em data+hora).

## 2. Audiência

Reaproveita os papéis abstratos do `SPEC-002 §2` — nenhum papel novo.

## 3. Escopo

### 3.1 O que este SPEC entrega

1. DDL raw proposto (`vra_raw`), 12 colunas, nomes de `SPEC-006 §5`.
2. DDL typed proposto (`vra_typed`), casts sobre `vra_raw`.
3. Plano de teste do `JOIN` com Básica (fecha `SPEC-006` C-02).

### 3.2 Fora de escopo

- Implementação real (os scripts abaixo são propostos, não executados) —
  fica para quando o autor decidir rodar.
- Ingestão Snowflake — DEC futura (`DEC-008 §2.c`).
- SIROS — `SPEC-010`.

## 4. Pipeline proposto

```
scripts/BASH_002_vra_download.sh (já existe)
  → data/anac/vra/*.csv
  → DDL_NNN_vra_create_table.sql (proposto, sql/ingestao_sqlite/)
  → vra_raw (12 colunas TEXT, fiel ao CSV — linha 1 de metadado
       descartada na carga, linha 2 é o cabeçalho real)
  → SRC_NNN_vra_load_sqlite.py (proposto, src/ingestao_sqlite/)
  → sql/tratamento/DDL_NNN_vra_view_typed_sqlite.sql (proposto)
  → vra_typed (view, casts)
```

Números `NNN` reais decididos na implementação (`DEC-001 §6.6`), não
fixados aqui.

## 5. DDL raw proposto — `vra_raw`

```sql
CREATE TABLE IF NOT EXISTS vra_raw (
    "sg_empresa_icao" TEXT,
    "nr_voo" TEXT,
    "cd_autorizacao_di" TEXT,
    "cd_tipo_linha" TEXT,
    "sg_icao_origem" TEXT,
    "sg_icao_destino" TEXT,
    "dt_hr_partida_prevista" TEXT,
    "dt_hr_partida_real" TEXT,
    "dt_hr_chegada_prevista" TEXT,
    "dt_hr_chegada_real" TEXT,
    "ds_situacao_voo" TEXT,
    "cd_justificativa" TEXT
);
```

Sem chave primária natural óbvia (diferente de `basica_raw`, que tem
`id_basica`) — o VRA bruto não publica um identificador de linha; a
combinação `sg_empresa_icao + nr_voo + dt_hr_partida_real` é candidata,
mas não testada quanto a unicidade nesta versão.

## 6. DDL typed proposto — `vra_typed`

```sql
CREATE VIEW vra_typed AS
SELECT
    sg_empresa_icao,
    nr_voo,
    cd_autorizacao_di,
    cd_tipo_linha,
    sg_icao_origem,
    sg_icao_destino,
    datetime(dt_hr_partida_prevista) AS dt_hr_partida_prevista,
    datetime(dt_hr_partida_real)     AS dt_hr_partida_real,
    datetime(dt_hr_chegada_prevista) AS dt_hr_chegada_prevista,
    datetime(dt_hr_chegada_real)     AS dt_hr_chegada_real,
    ds_situacao_voo,
    cd_justificativa
FROM vra_raw;
```

**Decisão de design explícita, divergente da Básica**: mantém
`dt_hr_partida_real` como timestamp único (`DATETIME`), em vez de separar
em `dt_partida_real`+`hr_partida_real` como a Básica faz — porque o VRA já
publica assim, forçar a separação seria trabalho sem necessidade real
ainda. Se o `JOIN` com a Básica (§7) exigir separar para comparar,
revisitar aqui.

## 7. Plano de teste do `JOIN` com a Básica (fecha `SPEC-006` C-02)

1. Carregar um mês de VRA e o mês correspondente de Básica.
2. `JOIN` por `sg_empresa_icao + nr_voo + date(dt_hr_partida_real) +
   sg_icao_origem` (VRA) contra `sg_empresa_icao + nr_voo +
   dt_partida_real + sg_icao_origem` (Básica).
3. Medir taxa de correspondência (% de etapas da Básica que encontram par
   no VRA, e vice-versa).
4. Reportar como achado em `SPEC-006 §6` (transforma hipótese em achado
   confirmado ou refutado) — não é resultado desta SPEC, é entrega
   compartilhada.

## 8. Critérios de sucesso

- **C-01** — DDL raw e typed implementados, batendo com o schema de
  `SPEC-006 §5`.
- **C-02** — Carga de pelo menos um mês real de VRA executada sem erro.
- **C-03** — Teste de `JOIN` (§7) executado e reportado — fecha
  `SPEC-006` C-02.

## 9. Premissas e dependências

- Estrutura de `VRA_20247.csv` (base de `SPEC-006`) generaliza para
  outros meses — não testado.
- `scripts/BASH_002_vra_download.sh` já baixa os arquivos necessários —
  confirmado (`data/anac/vra/` já tem múltiplos arquivos).

## 10. Não-objetivos

- Não é objetivo resolver ausência de chave primária natural (§5) nesta
  versão — registrada como candidata, não decidida.
- Não é objetivo separar `dt_hr_partida_real` em data+hora — decisão
  explícita de manter como está (§6).

## 11. Regras checáveis (R-COL)

| ID | Regra | Onde verificar | Severidade |
|---|---|---|---|
| **R-COL-10** | `vra_raw` contém exatamente as 12 colunas de `SPEC-006 §5`, sem adição nem omissão silenciosa. | `PRAGMA table_info(vra_raw)` × SPEC-006 §5 | Alta |
| **R-COL-11** | O resultado do teste de `JOIN` (§7) fica registrado em `SPEC-006`, não só nesta SPEC — mantém achado num lugar só. | Inspeção de `SPEC-006` histórico | Média |

## 12. Limitações conhecidas

- Chave primária candidata (§5) não testada quanto a duplicidade.
- DDL desta SPEC é proposta — pode mudar na implementação real sem
  reabrir esta SPEC inteira, só atualizar §5/§6.

## 13. Critérios de revisão

Revisitar esta SPEC quando:

- A implementação real revelar que o schema proposto (§5-§6) precisa de
  ajuste.
- O teste de `JOIN` (§7) for executado — atualizar com o resultado real.
- SIROS (`SPEC-010`) ou uma pergunta futura exigir cruzar VRA com um
  terceiro dataset, mudando a chave candidata da §5.

## 14. Histórico

| Data | Evento |
|---|---|
| 2026-08-31 | SPEC-009 v1 produzida em status `proposto`, prospectiva. DDL raw/typed propostos a partir de `SPEC-006`, plano de teste de `JOIN` com a Básica desenhado. Nada implementado ainda. Materializa a `DEC-008`. Aguardando aprovação do autor. |
| 2026-08-31 | **Aprovada.** Autor revisou o lote e aprovou explicitamente. |

---

*Fim do documento.*
