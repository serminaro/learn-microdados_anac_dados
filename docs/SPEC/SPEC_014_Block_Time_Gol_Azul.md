---
documento: SPEC-014
titulo: Block Time GOL/Azul — Sobra e Falta de Tempo (SPEC-004 §5.6)
versao: v1
status: proposto
data: 2026-09-01
autor: Bruno Alexandre Serminaro
referencia: DEC-007
escopo: projeto
---

# SPEC-014 · Block Time GOL/Azul — Sobra e Falta de Tempo (`SPEC-004 §5.6`)

> Documenta `fato_block_time_gol_azul` (`db/anac_basica.sqlite`), já
> carregada: destrava a pergunta 6 do `SPEC-004` ("Block time — sobra e
> estratégia"), bloqueada desde a v1 daquele documento por depender do
> VRA. Materializa o padrão de junção registrado em `DEC-007 §2.g`
> (corrigido para objeto único em `DEC-007 v4`/`SPEC-004 v4`, mesma
> sessão).

---

## 1. Propósito

Responder, com dado real, a pergunta que ficou registrada como desenho
sem implementação por várias versões do `SPEC-004`/`DEC-007`: comparando
o tempo programado (VRA) contra o tempo real de voo (Básica), onde GOL e
Azul têm sobra de tempo na malha e onde falta — e deixar claro, com
achado medido, o que essa comparação realmente mede (e o que não mede).

## 2. Audiência

Reaproveita os papéis abstratos do `SPEC-002 §2` — nenhum papel novo.

## 3. Escopo

### 3.1 O que este SPEC entrega

1. Documentação de `fato_block_time_gol_azul`: fonte, chave de junção
   medida antes de materializar, colunas, achados iniciais (§4-§7).
2. Achado que refina a leitura de "block time" nesta base de dados: o
   campo "real" do VRA não é tempo de bloco porta-a-porta, é
   estatisticamente idêntico ao tempo no ar (airborne) que a Básica já
   media (§6.2) — muda o que `folga_horas` de fato representa.
3. Fecha formalmente o bloqueio da pergunta 6 do `SPEC-004 §5.6`.

### 3.2 Fora de escopo

- Segmentação por frota, base, natureza de linha ou tempo (mensal,
  janelas fechando) — mesmo método já usado em `SPEC-013` para etapa
  média, ainda não aplicado aqui. Próxima rodada natural, não feita
  nesta versão.
- Separar, dentro de `folga_horas`, quanto é taxi estrutural (inevitável)
  e quanto é margem estratégica deliberada — não dá para separar com o
  dado disponível (§6.2, §11).
- Qualificar `tempo_solo_horas` (já em `fato_rotacao_aeronave_gol_azul`)
  contra o tempo de solo *previsto* implícito no VRA (chegada prevista da
  etapa anterior × partida prevista desta, mesma matrícula) — ideia
  registrada na sessão de trabalho, não construída nesta versão.
- Azul separado de GOL nos achados do §6 — reportados juntos nesta
  rodada; segmentar por empresa é extensão natural, não feita ainda.

## 4. Fonte e proveniência

```
fato_rotacao_aeronave_gol_azul (SPEC-012, 2.743.964 linhas, 23 colunas)
  LEFT JOIN vra_curated_deep (SPEC-012, 2.697.490 linhas)
  pela chave empresa+voo+data+HORA de partida+origem
  (DEC-007 Sec.2.g, refinada v4 -- medida abaixo, nao assumida)
  → sql/curated_deep/DDL_004_fato_block_time_gol_azul_create_table_sqlite.sql
  → fato_block_time_gol_azul (tabela, db/anac_basica.sqlite)
```

Cruza os dois bancos (`anac_basica.sqlite`, `anac_vra.sqlite`) via
`ATTACH DATABASE` confinado ao script de construção, `DETACH` implícito
ao fim da sessão — as bases continuam fisicamente separadas (`DEC-004`
intacta), só o resultado da junção vira objeto único, mesmo padrão já
usado (e depois descartado) na `voo_trusted` desta sessão. Tabela
materializada, não view — mesmo raciocínio de todas as `curated_deep`:
JOIN + window function sobre 2,7M linhas seria caro recalculado a cada
consulta.

Nome **único** (não um objeto por empresa) — correção pós-aprovação de
`DEC-007 v4`/`SPEC-004 v4` (`R-TAX-11`), alinhando com o padrão que
`curated_deep`/`fato_rotacao_aeronave_gol_azul` já fixaram: filtra por
`sg_empresa_icao`, não separa em tabelas.

## 5. Colunas

35 no total: 23 herdadas de `fato_rotacao_aeronave_gol_azul` (`SPEC-012
§5.3`, sem alteração) + 12 novas:

| Coluna | Cálculo | Papel |
|---|---|---|
| `dt_hr_partida_prevista` | VRA, direto | Horário programado de partida |
| `dt_hr_chegada_prevista` | VRA, direto | Horário programado de chegada |
| `dt_hr_partida_real_vra` | VRA, direto (renomeada p/ não colidir com `dt_partida_real`+`hr_partida_real` da Básica) | Partida real segundo o VRA |
| `dt_hr_chegada_real_vra` | VRA, direto (idem) | Chegada real segundo o VRA |
| `ds_situacao_voo` | VRA, direto | REALIZADO/CANCELADO/etc. — Básica não tem |
| `cd_justificativa` | VRA, direto | Motivo de atraso/cancelamento — Básica não tem |
| `fl_match_vra` | `1` se encontrou par no VRA pela chave, senão `0` | Não confundir "sem atraso calculado" com "sem par" |
| `tempo_previsto_horas` | `dt_hr_chegada_prevista − dt_hr_partida_prevista` | Bloco programado |
| `tempo_real_vra_horas` | `dt_hr_chegada_real_vra − dt_hr_partida_real_vra` | Bloco "real" segundo o VRA — achado §6.2: ≈ `nr_horas_voadas` |
| `atraso_partida_horas` | `dt_hr_partida_real_vra − dt_hr_partida_prevista` | Atraso na partida |
| `atraso_chegada_horas` | `dt_hr_chegada_real_vra − dt_hr_chegada_prevista` | Atraso na chegada |
| `folga_horas` | `tempo_previsto_horas − nr_horas_voadas` (Básica) | **Métrica central**: positivo = sobra, negativo = falta |

## 6. Medição da chave e achados antes/depois de materializar

### 6.1 Chave de junção: de hipótese a achado confirmado

`DEC-007 §2.g` registrava a chave como hipótese não confirmada
(empresa+voo+data+origem). Refinada nesta sessão (achado, não mais
hipótese): datas sem hora colidem quando o mesmo número de voo opera duas
vezes no mesmo dia calendário — medido antes em amostra 2025 GOL/Azul
(6.392 grupos duplicados sem hora, 13 com hora). Medido agora contra o
**par completo atual**, não mais amostra:

- `fato_rotacao_aeronave_gol_azul`: 2.743.964 linhas.
- `vra_curated_deep`: 2.697.490 linhas.
- Correspondência: **2.660.682 linhas (96,96%)**.
- Chaves duplicadas residuais: **10** (lado Básica), **12** (lado VRA) —
  de 2,7M linhas, ~0,0004%, essencialmente resolvido. Tratado por
  `ROW_NUMBER() OVER (... ORDER BY rowid)` no staging do VRA antes do
  `LEFT JOIN` — desempate determinístico, não descarte silencioso.

### 6.2 Achado que muda a leitura: `tempo_real_vra_horas` ≈ `nr_horas_voadas`

Medido depois de materializar, antes de reportar qualquer conclusão
sobre `folga_horas`: comparei `tempo_real_vra_horas` (VRA, chegada real −
partida real) contra `nr_horas_voadas` (Básica, tempo no ar) nas
2.660.682 linhas com par. **Delta médio: 0,0h. 99,9995% das linhas
(2.660.669 de 2.660.682) com diferença ≤1 minuto.**

**Conclusão**: o campo "real" do VRA não é tempo de bloco porta-a-porta
(gate a gate) — é estatisticamente a mesma medição que a Básica já fazia
(tempo no ar, airborne). O VRA só acrescenta dado novo no lado
**previsto** (horário programado) e em situação/justificativa — não no
lado real. Isso muda o que `folga_horas` representa: não é "bloco
programado menos bloco real", é **"bloco programado menos tempo no ar
real"**. Todo bloco programado publicado já embute taxi em solo (a
aeronave não decola no instante em que sai do portão) — uma folga
positiva de poucos minutos é esperada estruturalmente por esse motivo,
não é necessariamente margem estratégica deliberada da companhia. Não dá
para separar as duas coisas com o dado disponível (§3.2, §11).

### 6.3 Achado central: mais sobra que falta, mas quase um terço com falta

Medido nas 2.660.682 linhas com par no VRA:

| Métrica | Valor |
|---|---|
| `folga_horas` média | 0,0412h (~2,5 min) |
| `folga_horas` mediana (aprox.) | 0,05h (~3 min) |
| Etapas com falta de tempo (`folga_horas < 0`) | 873.831 (32,8%) |
| Etapas com sobra de tempo (`folga_horas > 0`) | 1.740.831 (65,4%) |
| Atraso médio de partida | 3,47 min |

Em média/mediana a folga fica perto de zero — não há evidência, no
agregado, de padding sistemático grande. Mas quase um terço das etapas
tem `folga_horas` negativa: tempo programado menor que o tempo no ar
real, situação que estrutural ou operacionalmente pressiona atraso.
Segmentar por frota/base/rota (não feito nesta versão, §3.2) é o próximo
passo natural para entender onde essa falta se concentra.

## 7. Critérios de sucesso

- **C-01** — Chave de junção medida contra o par completo de tabelas
  antes de fechar o DDL, não assumida. **Cumprido**: 96,96% de
  correspondência, duplicidade residual ~0,0004% (§6.1).
- **C-02** — `fato_block_time_gol_azul` criada com as 23 colunas
  herdadas de `fato_rotacao_aeronave_gol_azul` + 12 novas. **Cumprido**:
  35 colunas confirmadas por `PRAGMA table_info`, 2.743.964 linhas (igual
  à fonte, `LEFT JOIN` preserva todas).
- **C-03** *(achado, não critério planejado)* — Divergência real entre
  `tempo_real_vra_horas` e `nr_horas_voadas` medida antes de interpretar
  `folga_horas`. **Cumprido**: divergência é nula na prática (§6.2),
  achado registrado e usado para calibrar a leitura do §6.3.
- **C-04** — Pergunta 6 do `SPEC-004 §5.6` deixa de estar bloqueada.
  **Cumprido**: `folga_horas`/`atraso_partida_horas`/
  `atraso_chegada_horas` calculados e reportados (§6.3).

## 8. Premissas e dependências

- Depende de `fato_rotacao_aeronave_gol_azul` e `vra_curated_deep`
  (`SPEC-012`) já carregadas e corretas — esta SPEC não revalida o
  tratamento delas, só herda.
- Ambiente com `sqlite3` CLI disponível para rodar
  `sql/curated_deep/DDL_004_...` — mesma premissa do `SPEC-002 §6`.
- A chave de junção (§6.1) foi medida só para o par GOL/Azul, janela
  2021+ — não confirmado se generaliza para outras empresas ou período
  anterior a 2021.

## 9. Não-objetivos

- Não é objetivo separar taxi estrutural de margem estratégica dentro de
  `folga_horas` (§6.2) — limitação do dado disponível, não desta SPEC.
- Não é objetivo segmentar os achados do §6.3 por frota, base ou tempo —
  próxima rodada (§3.2).
- Não é objetivo qualificar `tempo_solo_horas` contra o tempo de solo
  previsto do VRA — ideia registrada, não construída (§3.2).

## 10. Regras checáveis (R-COL)

| ID | Regra | Onde verificar | Severidade |
|---|---|---|---|
| **R-COL-32** *(novo)* | `fato_block_time_gol_azul` tem exatamente 2.743.964 linhas (igual a `fato_rotacao_aeronave_gol_azul` — `LEFT JOIN` não pode perder nem duplicar linha da fonte). | `SELECT COUNT(*) FROM fato_block_time_gol_azul` × `SELECT COUNT(*) FROM fato_rotacao_aeronave_gol_azul` | Crítica |
| **R-COL-33** *(novo)* | `id_basica` é único em `fato_block_time_gol_azul` — nenhuma linha duplicada por fan-out do `LEFT JOIN`. | `SELECT id_basica, COUNT(*) FROM fato_block_time_gol_azul GROUP BY id_basica HAVING COUNT(*) > 1` deve ser vazio | Crítica |
| **R-COL-34** *(novo)* | `fl_match_vra = 1` em pelo menos 95% das linhas — se cair abaixo disso numa recarga futura, a chave de junção (§6.1) parou de generalizar. | `SELECT AVG(fl_match_vra) FROM fato_block_time_gol_azul` deve ser `>= 0.95` | Alta |

## 11. Limitações conhecidas

- **`folga_horas` mistura taxi estrutural com margem estratégica** (§6.2)
  — não é possível isolar as duas coisas com o dado disponível (VRA não
  publica tempo de bloco real, só tempo no ar real, idêntico ao da
  Básica).
- **3,04% das linhas sem par no VRA** (`fl_match_vra = 0`, 83.282 linhas)
  — não investigado por que (chave não bate, etapa sem registro
  correspondente no VRA, ou outro motivo); essas linhas ficam com as 12
  colunas novas em `NULL`, preservadas na tabela, não descartadas.
- Achado do §6.1 (chave revisada) validado só para GOL/Azul, 2021+ — não
  generalizado para outras empresas nem período anterior.
- Residual de 10-12 chaves duplicadas (§6.1) resolvido por desempate
  arbitrário (`rowid`), não por critério de negócio — registrado, não
  investigado a fundo.

## 12. Critérios de revisão

Revisitar esta SPEC quando:

- `fato_rotacao_aeronave_gol_azul` ou `vra_curated_deep` forem
  recarregados — `fato_block_time_gol_azul` é tabela materializada, não
  reflete a recarga automaticamente.
- Os achados do §6.3 forem segmentados por frota/base/tempo (§3.2) —
  **feito**: ver `SPEC-015` (análise exploratória completa, GOL+Azul+
  comparação, forma+cerca→run sequence→lag plot→segmentação).
- Alguém encontrar forma de isolar taxi estrutural de margem estratégica
  dentro de `folga_horas` (§6.2, §11).

## 13. Histórico

| Data | Evento |
|---|---|
| 2026-09-01 | SPEC-014 v1 produzida em status `proposto`, retroativa. Documenta `fato_block_time_gol_azul` (2.743.964 linhas, 35 colunas, 96,96% de correspondência com o VRA), destravando a pergunta 6 do `SPEC-004 §5.6`. Achado central (§6.2): `tempo_real_vra_horas` é estatisticamente idêntico a `nr_horas_voadas` da Básica (delta médio 0,0h) — o VRA não traz tempo de bloco real novo, só o previsto. Achado de negócio (§6.3): folga média/mediana perto de zero, mas 32,8% das etapas com falta de tempo programado. Aguardando aprovação do autor. |
| 2026-09-03 | Segmentação por frota/base/tempo (pendência do §12) resolvida em `SPEC-015` (documento novo, análise exploratória completa) — não incorporada aqui para manter a separação dado (esta SPEC) vs. análise (`SPEC-015`), mesmo padrão que `SPEC-012`/`SPEC-013` já estabeleceram para etapa média. Nenhuma coluna, critério de sucesso ou achado desta SPEC muda. |

---

*Fim do documento.*
