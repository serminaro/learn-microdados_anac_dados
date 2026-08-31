---
documento: SPEC-009
titulo: Ingestão SQLite — VRA
versao: v2
status: aprovado
data: 2026-08-31
autor: Bruno Alexandre Serminaro
referencia: DEC-008, SPEC-006
escopo: projeto
---

# SPEC-009 · Ingestão SQLite — VRA

> SPEC de conteúdo, **implementada** (v2, 2026-08-31): a ingestão do VRA
> no caminho SQLite está em produção. Segue o padrão raw → silver fixado
> pela `DEC-008 §2.a`, usando o schema levantado em `SPEC-006`. A
> validação real revelou dois achados que a v1 (proposta) não previa:
> segunda mudança de formato de data no VRA (§4) e corrupção pontual de
> fonte em dois meses (§4) — os dois tratados na view, não escondidos.

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

1. DDL raw implementado (`vra_raw`), 12 colunas, nomes de `SPEC-006 §5`.
2. DDL silver implementado (`vra_silver`), casts sobre `vra_raw`, dois
   achados de qualidade de dado tratados (§4).
3. Plano de teste do `JOIN` com Básica (fecha `SPEC-006` C-02) — ainda não
   executado.

### 3.2 Fora de escopo

- Ingestão Snowflake — DEC futura (`DEC-008 §2.c`).
- SIROS — `SPEC-010`.
- Resolver a ausência de chave primária natural (§5) — registrada, não
  decidida.

## 4. Pipeline implementado

```
scripts/BASH_002_vra_download.sh (já existia)
  → data/anac/vra/*.csv (197 arquivos, 2010-01 a 2026-06)
  → sql/ingestao_sqlite/DDL_002_vra_create_table.sql
  → vra_raw (12 colunas TEXT, fiel ao CSV — linha 1 de metadado
       descartada na carga, linha 2 é o cabeçalho real)
  → src/ingestao_sqlite/SRC_002_vra_load_sqlite.py
      (carrega em db/anac_vra.sqlite, 17.459.155 linhas, ~25 min)
  → sql/tratamento/DDL_004_vra_view_silver_sqlite.sql
  → vra_silver (view, 12 colunas tipadas e organizadas)
```

### Achado 1: segunda mudança de formato de data (2026-08-31)

Validação de `vra_silver` revelou que o formato de horário do VRA muda
**de novo**, além do que `SPEC-006` tinha amostrado (só um mês, 2024-07):

| Período | Formato |
|---|---|
| 2010-01 a 2018-12 | `DD/MM/AAAA HH:MM` (sem segundos) |
| 2019-01 em diante (exceto §4 achado 2) | `AAAA-MM-DD HH:MM:SS` (ISO) |

`vra_silver` detecta o formato por padrão de caractere (`GLOB`) e converte
os dois para o mesmo `DATETIME` de saída — não assume ISO cegamente como
a v1 desta SPEC propunha.

### Achado 2: corrupção de fonte em 2020-02/2020-03

Os arquivos de fevereiro e março de 2020 (581.768 linhas) têm
`Microsoft.SqlServer.Dts.Pipeline.BlobColumn` como valor literal em
**5 colunas**: os 4 campos de horário e `ds_situacao_voo` — parece
vazamento de objeto interno de ferramenta ETL (SSIS) para dentro do
arquivo público da própria ANAC. Confirmado em `vra_raw`, não é erro de
carga. As demais colunas da mesma linha (empresa, voo, rota,
justificativa) estão intactas.

**Tratamento**: as 5 colunas viram `NULL` quando o valor bate com o
padrão da falha; a linha **não é descartada**, o resto do dado dela é
válido e seria perdido à toa se a linha inteira fosse excluída.

## 5. DDL raw implementado — `vra_raw`

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

## 6. DDL silver implementado — `vra_silver`

```sql
CREATE VIEW vra_silver AS
SELECT
    NULLIF(sg_empresa_icao, '') AS sg_empresa_icao,
    NULLIF(nr_voo, '') AS nr_voo,
    NULLIF(cd_autorizacao_di, '') AS cd_autorizacao_di,
    NULLIF(cd_tipo_linha, '') AS cd_tipo_linha,
    NULLIF(sg_icao_origem, '') AS sg_icao_origem,
    NULLIF(sg_icao_destino, '') AS sg_icao_destino,
    CASE
        WHEN dt_hr_partida_prevista GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]*'
            THEN datetime(dt_hr_partida_prevista)
        WHEN dt_hr_partida_prevista GLOB '[0-9][0-9]/[0-9][0-9]/[0-9][0-9][0-9][0-9]*'
            THEN datetime(substr(dt_hr_partida_prevista,7,4) || '-' || substr(dt_hr_partida_prevista,4,2)
                 || '-' || substr(dt_hr_partida_prevista,1,2) || ' ' || substr(dt_hr_partida_prevista,12,5) || ':00')
        ELSE NULL
    END AS dt_hr_partida_prevista,
    -- (mesma logica para dt_hr_partida_real, dt_hr_chegada_prevista, dt_hr_chegada_real)
    CASE
        WHEN ds_situacao_voo = '' OR ds_situacao_voo LIKE '%BlobColumn%' THEN NULL
        ELSE ds_situacao_voo
    END AS ds_situacao_voo,
    NULLIF(cd_justificativa, '') AS cd_justificativa
FROM vra_raw;
```

DDL completo em `sql/tratamento/DDL_004_vra_view_silver_sqlite.sql` (os 4
campos de horário repetem a mesma lógica `CASE`, omitidos aqui por
brevidade).

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

- **C-01** — DDL raw e silver implementados, batendo com o schema de
  `SPEC-006 §5`. **Cumprido.**
- **C-02** — Carga completa do VRA executada sem erro. **Cumprido**:
  17.459.155 linhas, 2010-01 a 2026-06, ~25 min.
- **C-03** — Teste de `JOIN` (§7) executado e reportado — fecha
  `SPEC-006` C-02. **Não cumprido ainda** — desenhado, não executado.
- **C-04** *(novo, v2)* — Achados de qualidade de dado (§4) tratados na
  view, não escondidos. **Cumprido**: formato de data duplo detectado por
  `GLOB`; corrupção de 2020-02/03 vira `NULL` nas 5 colunas afetadas, sem
  descartar a linha.

## 9. Premissas e dependências

- Estrutura de `VRA_20247.csv` (base de `SPEC-006`) generaliza quanto às
  12 colunas — **confirmado**; o formato de data dentro dessas colunas
  **não** generaliza (§4, achado 1) — corrigido na view, não na SPEC-006.
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
| **R-COL-18** *(novo, v2)* | Nenhum valor `Microsoft.SqlServer.Dts.Pipeline.BlobColumn` aparece em `vra_silver` — só em `vra_raw` (fiel à fonte, mesmo corrompida). | `SELECT COUNT(*) FROM vra_silver WHERE ... LIKE '%BlobColumn%'` deve ser 0, em qualquer coluna | Alta |
| **R-COL-19** *(novo, v2)* | Todo valor não-nulo em `vra_silver.dt_hr_partida_prevista`/`_real`/`dt_hr_chegada_*` está em formato `DATETIME` válido — nunca sobra `DD/MM/AAAA` sem converter. | Amostragem por ano, checar `typeof()`/formato | Alta |

## 12. Limitações conhecidas

- Chave primária candidata (§5) não testada quanto a duplicidade.
- As 5 colunas de 2020-02/03 (§4, achado 2) ficam `NULL` — quem precisar
  de horário programado exatamente nesses dois meses não tem como
  recuperar, o dado não existe em lugar nenhum da fonte.
- O padrão de detecção de formato de data (`GLOB`) assume só os dois
  formatos observados (§4); um terceiro formato futuro cairia no `ELSE
  NULL` silenciosamente, não travaria a carga — bom para não quebrar,
  ruim se ninguém perceber a perda.

## 13. Critérios de revisão

Revisitar esta SPEC quando:

- Um terceiro formato de data aparecer no VRA (§4, achado 1) — o `ELSE
  NULL` do `GLOB` esconderia a perda até alguém notar.
- O teste de `JOIN` (§7) for executado — atualizar com o resultado real.
- SIROS (`SPEC-010`) ou uma pergunta futura exigir cruzar VRA com um
  terceiro dataset, mudando a chave candidata da §5.

## 14. Histórico

| Data | Evento |
|---|---|
| 2026-08-31 | SPEC-009 v1 produzida em status `proposto`, prospectiva. DDL raw/typed propostos a partir de `SPEC-006`, plano de teste de `JOIN` com a Básica desenhado. Nada implementado ainda. Materializa a `DEC-008`. Aguardando aprovação do autor. |
| 2026-08-31 | **Aprovada.** Autor revisou o lote e aprovou explicitamente. |
| 2026-08-31 | **v2 — implementação real.** `vra_raw` e `vra_silver` (renomeado de `vra_typed`, pedido do autor) implementados e carregados: 17.459.155 linhas, 2010-2026. Dois achados na validação: (1) formato de data muda de novo entre 2018-12 e 2019-01 (`DD/MM/AAAA` → ISO), detectado por `GLOB` e convertido; (2) `2020-02`/`2020-03` (581.768 linhas) têm 5 colunas corrompidas na fonte (`BlobColumn`), tratadas como `NULL` sem descartar a linha. C-04, R-COL-18/19 adicionados. §1, §3, §4, §5, §6, §7-§13 atualizados. |

---

*Fim do documento.*
