---
documento: SPEC-012
titulo: Curated Deep — Recorte GOL/Azul para Deep Dive
versao: v1
status: proposto
data: 2026-08-31
autor: Bruno Alexandre Serminaro
referencia: DEC-007
escopo: projeto
---

# SPEC-012 · Curated Deep — Recorte GOL/Azul para Deep Dive

> Documenta `basica_curated_deep` (`db/anac_basica.sqlite`) e
> `vra_curated_deep` (`db/anac_vra.sqlite`), já carregadas: recorte de
> `basica_silver`/`vra_silver` restrito a GOL (`GLO`) e Azul (`AZU`),
> 2021-01-01 até a última data disponível em cada fonte. Retroativa —
> construída a pedido direto do autor, sem SPEC prévia, mesmo padrão de
> regularização do `DEC-004`/`SPEC-011`.

---

## 1. Propósito

Dar às duas tabelas de recorte que alimentam o deep dive GOL/Azul
(`SPEC-004`) uma fonte de verdade sobre escopo (quem entra, qual janela,
quais colunas) e sobre os achados de qualidade de dado descobertos ao
medir a janela antes de materializar — não repetir a investigação toda
vez que alguém precisar confiar nessas tabelas.

## 2. Audiência

Reaproveita os papéis abstratos do `SPEC-002 §2` — nenhum papel novo.

## 3. Escopo

### 3.1 O que este SPEC entrega

1. Documentação de `basica_curated_deep`: fonte, filtro, colunas, janela
   real medida (§4-§6).
2. Documentação de `vra_curated_deep`: idem (§4-§6).
3. Achado de qualidade de dado no VRA bruto, descoberto durante a
   medição da janela, não documentado em `SPEC-009`/`SPEC-006` até agora
   (§6.2).

### 3.2 Fora de escopo

- Incluir `ACN` (Azul Conecta) — entidade/ICAO jurídico distinto do
  pedido literal "GOL e Azul"; fica de fora até decisão em contrário.
- Cálculo de métrica de atraso/pontualidade ou qualquer JOIN entre as
  duas tabelas — cada uma é um recorte vertical de uma fonte só, não um
  enriquecimento cruzado (isso seria escopo de uma camada `trusted`,
  desenhada e depois cancelada nesta mesma sessão de trabalho; o DDL
  chegou a ser escrito e depois excluído a pedido do autor, não fica
  rastro em `sql/` — só nesta SPEC e no histórico de conversa).
- Corrigir o achado do §6.2 na `vra_silver`/`vra_raw` — registrado aqui
  como achado, tratamento (se necessário) é decisão futura de quem for
  revisar `SPEC-009`.

## 4. Fonte e proveniência

```
basica_silver (SPEC-008, 112 colunas)
  → filtro sg_empresa_icao IN ('GLO','AZU') AND dt_partida_real >= '2021-01-01'
  → projeção das 29 colunas essenciais (SPEC-005 Sec.5)
  → sql/curated_deep/DDL_001_basica_curated_deep_create_table_sqlite.sql
  → basica_curated_deep (tabela, db/anac_basica.sqlite)

vra_silver (SPEC-009, 12 colunas)
  → filtro sg_empresa_icao IN ('GLO','AZU') AND dt_hr_partida_real >= '2021-01-01'
  → todas as 12 colunas (SPEC-006 Sec.5 -- ja compacto, nenhuma cortada)
  → sql/curated_deep/DDL_002_vra_curated_deep_create_table_sqlite.sql
  → vra_curated_deep (tabela, db/anac_vra.sqlite)
```

Ambas materializadas como **tabela**, não view — diferente do padrão
`_silver` (sempre view). Filtro sobre `basica_raw`/`vra_raw` sem índice
seria recalculado do zero a cada consulta; para uso repetido em análise
exploratória (o propósito desta camada), tabela materializada com índice
próprio (`sg_empresa_icao`, data) é o trade-off correto — mesmo raciocínio
de performance do `voo_trusted` cancelado, sem a complexidade de `ATTACH`
cross-banco porque cada tabela vem de uma fonte só.

## 5. Colunas

### 5.1 `basica_curated_deep` — 29 essenciais (`SPEC-005 §5`)

`id_basica`, `sg_empresa_icao`, `sg_empresa_iata`, `nr_voo`,
`dt_referencia`, `nr_etapa`, `ds_tipo_linha`, `ds_natureza_tipo_linha`,
`ds_servico_tipo_linha`, `ds_natureza_etapa`, `hr_partida_real`,
`dt_partida_real`, `hr_chegada_real`, `dt_chegada_real`,
`sg_icao_origem`, `sg_iata_origem`, `nm_municipio_origem`,
`sg_uf_origem`, `nm_pais_origem`, `sg_icao_destino`, `sg_iata_destino`,
`nm_municipio_destino`, `sg_uf_destino`, `nm_pais_destino`,
`sg_equipamento_icao`, `ds_modelo`, `ds_matricula`, `km_distancia`,
`nr_horas_voadas`. Confirmado por `PRAGMA table_info`: 29, mesmos nomes
de `basica_silver`, nenhuma coluna a mais ou a menos.

### 5.2 `vra_curated_deep` — todas as 12 (`SPEC-006 §5`)

`sg_empresa_icao`, `nr_voo`, `cd_autorizacao_di`, `cd_tipo_linha`,
`sg_icao_origem`, `sg_icao_destino`, `dt_hr_partida_prevista`,
`dt_hr_partida_real`, `dt_hr_chegada_prevista`, `dt_hr_chegada_real`,
`ds_situacao_voo`, `cd_justificativa`. Confirmado: 12, sem corte — o VRA
já era compacto o bastante (`SPEC-006 §5`).

## 6. Medição da janela e achados antes de materializar

### 6.1 Códigos ICAO confirmados

`GLO` = "GOL LINHAS AÉREAS S.A. (EX- VRG LINHAS AÉREAS S.A.)"; `AZU` =
"AZUL LINHAS AÉREAS BRASILEIRAS S/A" — confirmado contra `nm_empresa`
em `basica_raw`. `ACN` ("AZUL CONECTA LTDA., EX TWO TAXI AEREO LTDA")
existe como código distinto, deliberadamente fora do filtro (§3.2).

### 6.2 Achado: `vra_raw.dt_hr_partida_real` bruto não é seguro para
comparação de texto direta

Medindo `MAX(dt_hr_partida_real)` em `vra_raw` filtrado por `GLO`/`AZU` e
`dt_hr_partida_real >= '2021-01-01'` (comparação de texto, sem passar
pela normalização `GLOB`/`CASE` que `vra_silver` já aplica, achado 1 de
`DDL_004_vra_view_silver_sqlite.sql`), o resultado veio como o literal
`"null"` (string, não `NULL` de SQL) — evidência de que a coluna bruta
carrega valor textual `"null"` em pelo menos uma linha, provável resíduo
do parser JSON do dado de origem (mesma família de problema já visto no
SIROS, `SPEC-010 §6`, embora ali não fosse o literal `"null"`).

Investigando por que o filtro de texto (`>= '2021-01-01'`) não isolava
corretamente linhas de 2021+: confirmado que datas no formato antigo
`DD/MM/AAAA` (usado até 2018, achado 1 de `SPEC-009`) ordenam
lexicograficamente **acima** de `"2021-01-01"` sempre que o dia começa
com dígito ≥ 1 na segunda posição — ex. `"21/01/2010 00:00"` compara
maior que `"2021-01-01"` porque o segundo caractere (`'1'` vs `'0'`)
decide a ordem antes de qualquer coisa relacionada a ano real. Comparar
texto bruto sem normalizar produz janela errada silenciosamente.

**Tratamento**: `vra_curated_deep` foi construída a partir de
`vra_silver`, que já converte ambos os formatos para `datetime()`
canônico antes desta tabela filtrar — o filtro `>= '2021-01-01'` na
`vra_curated_deep` opera sobre dado já normalizado, seguro. `MAX`
resultante, limpo: `2026-07-01 03:22:00`.

### 6.3 Achado: mês de agosto/2026 fragmentário na Básica

`basica_curated_deep` tem `MAX(dt_partida_real) = 2026-08-01`, mas só 7
linhas nessa data (de 2.743.964 no total) — fora da cobertura que a
`SPEC-008 §7` confirma como completa (2010-01 a 2026-07). Incluídas
porque são dado real na fonte ("última data que temos" era o pedido
literal), mas registradas aqui como mês incompleto — qualquer agregação
mensal precisa excluir ou tratar `2026-08` separadamente.

## 7. Critérios de sucesso

- **C-01** — `basica_curated_deep` contém exatamente as 29 colunas
  essenciais de `SPEC-005 §5`, só `GLO`/`AZU`, `dt_partida_real >=
  2021-01-01`. **Cumprido**: 2.743.964 linhas (AZU 1.564.769, GLO
  1.179.195), 29 colunas confirmadas por `PRAGMA table_info`, zero linhas
  fora de `GLO`/`AZU` confirmado por contagem direta.
- **C-02** — `vra_curated_deep` contém as 12 colunas de `SPEC-006 §5`, só
  `GLO`/`AZU`, mesma janela, sem contaminação do formato de data duplo
  (§6.2). **Cumprido**: 2.697.490 linhas (AZU 1.541.051, GLO 1.156.439),
  12 colunas, `MIN`/`MAX` de `dt_hr_partida_real` dentro da janela
  esperada (2021-01-01 01:57:00 a 2026-07-01 03:22:00).
- **C-03** *(novo)* — Achado do §6.2 (valor literal `"null"` em
  `vra_raw.dt_hr_partida_real`) fica registrado para uma futura revisão
  de `SPEC-009`. **Cumprido nesta SPEC** (registro feito); tratamento na
  `vra_silver` em si é não-objetivo (§3.2).

## 8. Premissas e dependências

- Ambiente com `sqlite3` CLI disponível para rodar os DDLs de
  `sql/curated_deep/` — mesma premissa do `SPEC-002 §6`.
- Depende de `basica_silver`/`vra_silver` já carregadas e corretas
  (`SPEC-008`, `SPEC-009`) — esta SPEC não revalida o tratamento delas,
  só herda.
- `ACN` fora do escopo é premissa de leitura do pedido do autor ("GOL e
  Azul"), não confirmação formal de que Azul Conecta deveria ficar de
  fora de toda análise futura — reabre se o autor pedir o contrário.

## 9. Não-objetivos

- Não é objetivo enriquecer `basica_curated_deep` com dado do VRA (ou
  vice-versa) — isso é o desenho de `voo_trusted` (§3.2), não executado
  nesta sessão.
- Não é objetivo corrigir `vra_raw`/`vra_silver` para tratar o literal
  `"null"` do §6.2 — fica registrado, correção é decisão futura.
- Não é objetivo garantir que `2021-01-01` é o início "certo" da janela
  para toda pergunta de análise futura — foi o corte pedido pelo autor
  para este recorte, não uma validação de que é o período ideal.

## 10. Regras checáveis (R-COL)

| ID | Regra | Onde verificar | Severidade |
|---|---|---|---|
| **R-COL-26** *(novo)* | `basica_curated_deep` contém só `sg_empresa_icao IN ('GLO','AZU')`. | `SELECT COUNT(*) FROM basica_curated_deep WHERE sg_empresa_icao NOT IN ('GLO','AZU')` deve ser `0` | Alta |
| **R-COL-27** *(novo)* | `basica_curated_deep` tem exatamente as 29 colunas essenciais de `SPEC-005 §5`, mesmos nomes. | `PRAGMA table_info(basica_curated_deep)` × `SPEC-005 §5` | Alta |
| **R-COL-28** *(novo)* | `vra_curated_deep` contém só `sg_empresa_icao IN ('GLO','AZU')`, mesma janela de `basica_curated_deep` (`>= 2021-01-01`). | `SELECT COUNT(*) FROM vra_curated_deep WHERE sg_empresa_icao NOT IN ('GLO','AZU')` deve ser `0` | Alta |
| **R-COL-29** *(novo)* | `vra_curated_deep` tem as 12 colunas de `SPEC-006 §5`, sem corte. | `PRAGMA table_info(vra_curated_deep)` × `SPEC-006 §5` | Média |

## 11. Limitações conhecidas

- `2026-08` em `basica_curated_deep` é mês fragmentário (7 linhas, §6.3)
  — agregação mensal sem filtrar isso produz um ponto enganoso no fim da
  série.
- `basica_curated_deep` e `vra_curated_deep` não têm chave comum
  materializada entre si — comparar as duas exige `JOIN`/`ATTACH` manual
  pela chave hipotética de `SPEC-006 §6` (empresa+voo+data+hora+origem,
  medida nesta sessão: ~97% de correspondência, ver histórico de
  conversa, não persistido em nenhum artefato desta SPEC).
- Achado do §6.2 (`"null"` literal em `vra_raw`) não teve sua extensão
  medida além do necessário para explicar o `MAX` incorreto — não se sabe
  quantas linhas no total (fora de `GLO`/`AZU`, fora da janela) carregam
  o mesmo valor.
- A camada `trusted` (JOIN Básica × VRA enriquecendo pontualidade) foi
  desenhada por completo nesta sessão, com a chave de junção medida
  (~97% de correspondência, empresa+voo+data+hora+origem), mas nem a
  execução nem o DDL sobreviveram — build cancelado em andamento, arquivo
  excluído a pedido do autor. Quem retomar precisa redesenhar do zero ou
  recuperar do histórico de conversa, não há artefato em `sql/`.

## 12. Critérios de revisão

Revisitar esta SPEC quando:

- `basica_raw`/`vra_raw` forem recarregados — `basica_curated_deep`/
  `vra_curated_deep` são tabelas materializadas, não view, então não
  refletem a recarga automaticamente (precisam re-rodar os DDLs de
  `sql/curated_deep/`).
- O autor decidir incluir `ACN` no escopo de GOL/Azul.
- A camada `voo_trusted` (§3.2, cancelada) for retomada — nesse caso,
  revisar se `basica_curated_deep`/`vra_curated_deep` continuam fazendo
  sentido como camada separada ou se ficam supersedidas por ela.
- O achado do §6.2 for investigado a fundo e `SPEC-009`/`vra_silver`
  forem atualizadas para tratá-lo — esta SPEC deve then referenciar o
  tratamento, não só o achado.

## 13. Histórico

| Data | Evento |
|---|---|
| 2026-08-31 | SPEC-012 v1 produzida em status `proposto`, retroativa. Documenta `basica_curated_deep` (2.743.964 linhas, 29 colunas) e `vra_curated_deep` (2.697.490 linhas, 12 colunas), ambas já carregadas a pedido direto do autor. Achado novo registrado (§6.2): valor literal `"null"` em `vra_raw.dt_hr_partida_real` e risco de comparação de texto direta em data de formato duplo — não documentado em `SPEC-009`/`SPEC-006` até agora. Aguardando aprovação do autor. |

---

*Fim do documento.*
