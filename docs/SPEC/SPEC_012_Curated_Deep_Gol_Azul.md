---
documento: SPEC-012
titulo: Curated Deep — Recorte GOL/Azul para Deep Dive
versao: v3
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
>
> **v2** acrescenta `fato_rotacao_aeronave_gol_azul` (mesmo banco de
> `basica_curated_deep`): fato de grão etapa, enriquecida com rotação por
> matrícula, validação temporal contra `nr_horas_voadas` e validação
> geodésica de `km_distancia` via `dim_airport` — nasceu de uma premissa
> do autor (usar `dim_airport` para normalizar fuso horário local) que a
> medição **refutou** antes de desenhar o DDL (§6.4).

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
4. *(v2)* Documentação de `fato_rotacao_aeronave_gol_azul`: desenho,
   achado que refutou a premissa original de normalização de fuso (§6.4),
   e os três blocos de validação medidos antes e depois de materializar
   (temporal, continuidade espacial, geodésica) (§4.2, §5.3, §6.4).

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
- *(v2)* Investigar a fundo as 3.759 linhas de continuidade quebrada
  (§6.4) ou o par `KMCN`/`KGUS` de `km_distancia` incorreto (§6.4) — os
  dois ficam registrados como achado, não resolvidos.
- *(v2)* Corrigir `km_distancia` na fonte (`basica_raw`/`basica_silver`)
  para o par `KMCN`/`KGUS` — a validação geodésica só sinaliza, não
  corrige o dado de origem.

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

### 4.2 `fato_rotacao_aeronave_gol_azul` *(v2)*

```
basica_curated_deep (esta SPEC, §4.1)
  ⨯ dim_airport_location_time_zone (SPEC-011, LEFT JOIN por ICAO origem
    e por ICAO destino — dois joins independentes, um por ponta da rota)
  → window functions (ROW_NUMBER/LAG) particionadas por ds_matricula,
    ordenadas por partida real
  → sql/curated_deep/DDL_003_fato_rotacao_aeronave_gol_azul_create_table_sqlite.sql
  → fato_rotacao_aeronave_gol_azul (tabela, db/anac_basica.sqlite)
```

Mesmo banco de `basica_curated_deep` e `dim_airport_location_time_zone`
— não precisa de `ATTACH`, os três objetos já vivem em
`anac_basica.sqlite`. Tabela materializada (não view): medido, o build
completo (window function + 2 joins geodésicos sobre 2.743.964 linhas)
levou 35,7s — uma view recalcularia isso a cada consulta, viável mas
mais lento que reutilizar a tabela já pronta para análise iterativa.

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

### 5.3 `fato_rotacao_aeronave_gol_azul` *(v2)* — herdadas + 9 derivadas

Herda de `basica_curated_deep`: `id_basica`, `sg_empresa_icao`, `nr_voo`,
`ds_matricula`, `sg_equipamento_icao`, `ds_modelo`, `sg_icao_origem`,
`sg_icao_destino`, `dt_partida_real`, `hr_partida_real`,
`dt_chegada_real`, `hr_chegada_real`, `km_distancia`, `nr_horas_voadas`
(14 colunas, subconjunto das 29 — as de referência de boletim/calendário
não entram, não fazem parte de nenhum cálculo desta fato).

Derivadas, três blocos:

| Bloco | Coluna | Cálculo |
|---|---|---|
| Rotação | `nr_sequencia_matricula` | `ROW_NUMBER() OVER (PARTITION BY ds_matricula ORDER BY partida)` |
| Rotação | `sg_icao_destino_anterior` | `LAG(sg_icao_destino)` na mesma partição/ordem |
| Rotação | `dt_chegada_anterior` | `LAG(datetime chegada)` idem |
| Rotação | `fl_continuidade_ok` | `1` se `sg_icao_origem = sg_icao_destino_anterior`, `0` se diverge, `NULL` na primeira etapa da matrícula na janela |
| Rotação | `tempo_solo_horas` | partida desta etapa − chegada da etapa anterior; `NULL` na primeira etapa |
| Validação temporal | `tempo_etapa_horas` | chegada − partida desta etapa |
| Validação temporal | `delta_horas_voadas` | `tempo_etapa_horas − nr_horas_voadas` |
| Validação geodésica | `km_distancia_geodesica` | Haversine (lei dos cossenos esféricos) via `latitude`/`longitude` do `dim_airport`, origem e destino |
| Validação geodésica | `delta_km_distancia` | `km_distancia − km_distancia_geodesica` |
| Validade de solo *(v3)* | `fl_solo_valido` | `1`/`0`/`NULL` — ver §6.5 |

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

### 6.4 *(v2)* `fato_rotacao_aeronave_gol_azul`: premissa refutada e três
validações medidas

**Achado que muda o desenho original.** A ideia inicial do autor era usar
`dim_airport` para normalizar fuso horário local antes de calcular a
duração de cada etapa (`hr_chegada_real − hr_partida_real`), partindo da
premissa de que esses horários são hora local de cada aeroporto — o
Brasil tem 3 fusos (`UTC-2` a `UTC-5`) e há destino internacional na base.
Testado **antes** de desenhar qualquer DDL: comparei a subtração ingênua
(sem nenhuma normalização) contra `nr_horas_voadas` em rotas de fuso
diferente e conhecido —

| Rota | Fusos (`dim_airport`) | Partida | Chegada | Diferença bruta | `nr_horas_voadas` |
|---|---|---|---|---|---|
| SBKP→KFLL (Miami) | UTC-3 → UTC-5 | 01:11 | 09:36 | 8,4167h | 8,41667 |
| SBKP→SBRB (Rio Branco) | UTC-3 → UTC-5 | 10:18 | 14:07 | 3,8167h | 3,81667 |

Bate exato mesmo cruzando 2h reais de diferença de fuso. **Conclusão: os
horários da Básica já estão num referencial único (provavelmente horário
de Brasília fixo), não hora local por aeroporto** — `dim_airport` não
serve para essa normalização porque ela não é necessária. Medido depois,
sobre as 2.743.964 linhas inteiras (não só a amostra): confirma-se por
completo (ver validação temporal abaixo).

**Papel revisado de `dim_airport`**: não normaliza fuso, mas (a)
enriquece a rotação com contexto geográfico e (b) valida `km_distancia`
por distância geodésica — uso novo, não coberto por nenhuma SPEC
anterior.

**Validação temporal** (`delta_horas_voadas`, toda a tabela): máximo
absoluto `0,0000333h` (~0,1 segundo) em 2.743.964 linhas — o achado da
amostra generaliza por completo, zero linha com delta relevante. Duas
linhas têm `tempo_etapa_horas = 0` (partida e chegada idênticas,
`nr_horas_voadas = 0.0` também — os dois concordam entre si, mas não
fazem sentido operacional; anomalia isolada, não tratada,
`id_basica` 30170801 e 30513522).

**Validação de continuidade** (`fl_continuidade_ok`, rotação por
`ds_matricula`): 433 matrículas distintas na janela; 2.743.531 linhas têm
etapa anterior (as demais são primeira etapa de sua matrícula dentro da
janela, efeito de borda, não falta de dado). Dessas, **99,86%**
(2.739.772) têm continuidade espacial (destino da etapa anterior =
origem desta); **0,14%** (3.759 linhas) quebrada — não investigado a
fundo, fica como achado (§11). 100% das linhas têm `ds_matricula`
preenchida neste recorte — melhor que os ~12% de nulo que `SPEC-005`
registra para o histórico completo da Básica (o gap parece concentrado
fora de GOL/Azul 2021+, não confirmado além disso).

**Validação geodésica** (`delta_km_distancia`): cobertura de
`dim_airport` é 100% (zero ICAO de origem/destino sem match, confirmado
antes de construir). Média de diferença: 0,03 km (30 metros) — ruído
normal entre rota real e linha geodésica. Distribuição: 2.743.962 linhas
(99,9999%) com diferença ≤10 km; só **2 linhas** com diferença >50 km —
ambas o mesmo par de aeroportos, `KMCN`↔`KGUS` (EUA, matrícula `AUC`),
`km_distancia = 6547` reportado contra `912,2` km geodésico real (delta
de 5.634,8 km). `tempo_etapa_horas` dessas duas linhas bate exato com
`nr_horas_voadas` (2,28h/1,67h) — consistente com voo real de
posicionamento/manutenção fora do Brasil, curto (≈900km reais), onde o
`km_distancia` da fonte ANAC está incorreto. Achado real de qualidade de
dado, isolado pela validação geodésica; não corrigido nesta SPEC (§3.2).

### 6.5 *(v3)* `fl_solo_valido` — flag de validade de `tempo_solo_horas`

Acrescentada em `fato_rotacao_aeronave_gol_azul` (`sql/curated_deep/DDL_005_...sql`,
2026-09-02) para uso pela linha de análise de tempo de solo (`SPEC-016`).
Mesmo espírito de `fl_continuidade_ok`/`fl_match_vra` (`SPEC-014`): flag,
não filtro destrutivo — nenhuma linha é apagada, a decisão de recorte
fica com quem consome.

`fl_solo_valido = 0` quando qualquer um dos três critérios (medidos
**antes** de aplicar, GOL+Azul juntos):

| Critério | Linhas | % |
|---|---|---|
| `tempo_solo_horas < 0` (fisicamente impossível) | 408 | 0,0149% |
| `fl_continuidade_ok = 0` (solo não mede turnaround real, aeroportos diferentes) | 3.759 | 0,14% |
| `tempo_solo_horas > 72` (acima de pernoite + fim de semana completo) | 4.142 | — |

União dos três: **7.919 linhas de 2.743.531 com solo não-nulo (0,2886%)**
recebem `fl_solo_valido = 0`; **2.735.612 restam com `fl_solo_valido = 1`**.
`fl_solo_valido = NULL` quando `tempo_solo_horas IS NULL` (433 linhas,
primeira etapa da matrícula na janela — ausência de medida, não
invalidez).

**O corte de 72h é julgamento de domínio, não achado estatístico** —
medido antes de fixar: a distribuição de `tempo_solo_horas` entre 24h e
96h decai suave, sem quebra natural que apontasse 72h sobre 48h/60h. 72h
foi escolhido por cobrir pernoite + fim de semana completo (sexta à noite
até segunda à noite); acima disso é lido como parada prolongada
(manutenção pesada, aeronave fora de operação), registrado como premissa
explícita, não como limiar objetivo.

**Amostra da causa raiz** (GOL isolado, medida antes de generalizar
GOL+Azul): dos casos negativos, 193/255 (76%) vêm de continuidade
quebrada (critério b já explica), 62/255 têm continuidade OK mesmo
negativo — erro de timestamp na própria Básica, não do pipeline de
rotação; não investigado a fundo.

**Efeito colateral que exigiu ação manual**: `fato_block_time_gol_azul`
(`SPEC-014`, `DDL_004`) foi construída com `f.*` a partir de
`fato_rotacao_aeronave_gol_azul` **antes** de `fl_solo_valido` existir —
não herda a coluna automaticamente. `DDL_004` foi rodada de novo depois
deste script, na mesma sessão, para sincronizar; se `fato_rotacao` for
alterada de novo no futuro, o mesmo re-run manual será necessário
(nenhuma automação de dependência entre as duas tabelas existe hoje).

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
- **C-04** *(novo, v2)* — `fato_rotacao_aeronave_gol_azul` calcula
  `tempo_etapa_horas` sem depender de `dim_airport` para fuso, e o
  resultado bate com `nr_horas_voadas`. **Cumprido**: delta máximo
  absoluto de 0,0000333h em 2.743.964 linhas (§6.4).
- **C-05** *(novo, v2)* — Rotação por `ds_matricula` reconstruída com
  taxa de continuidade espacial medida, não assumida. **Cumprido**:
  99,86% (2.739.772/2.743.531 com etapa anterior), 433 matrículas
  distintas, cobertura de `dim_airport` 100% (§6.4).
- **C-06** *(novo, v2)* — Validação geodésica de `km_distancia` via
  `dim_airport` (haversine) implementada e capaz de isolar achado real de
  qualidade de dado. **Cumprido**: par `KMCN`/`KGUS` isolado (delta
  5.634,8 km), 99,9999% das linhas dentro de 10 km de ruído normal
  (§6.4).

## 8. Premissas e dependências

- Ambiente com `sqlite3` CLI disponível para rodar os DDLs de
  `sql/curated_deep/` — mesma premissa do `SPEC-002 §6`.
- Depende de `basica_silver`/`vra_silver` já carregadas e corretas
  (`SPEC-008`, `SPEC-009`) — esta SPEC não revalida o tratamento delas,
  só herda.
- `ACN` fora do escopo é premissa de leitura do pedido do autor ("GOL e
  Azul"), não confirmação formal de que Azul Conecta deveria ficar de
  fora de toda análise futura — reabre se o autor pedir o contrário.
- *(v2)* `fato_rotacao_aeronave_gol_azul` assume que a hipótese "horário
  único, não local por aeroporto" (§6.4) generaliza para todo o histórico
  da Básica, não só para a janela GOL/Azul 2021+ testada — não confirmado
  para outras empresas nem para anos anteriores a 2021.
- *(v2)* Depende de `dim_airport_location_time_zone` (`SPEC-011`)
  continuar cobrindo 100% dos ICAO usados por GOL/Azul — se a frota ou as
  rotas mudarem para aeroportos fora dos 858 já carregados, a validação
  geodésica passa a ter `NULL`s silenciosos para essas linhas.

## 9. Não-objetivos

- Não é objetivo enriquecer `basica_curated_deep` com dado do VRA (ou
  vice-versa) — isso é o desenho de `voo_trusted` (§3.2), não executado
  nesta sessão.
- Não é objetivo corrigir `vra_raw`/`vra_silver` para tratar o literal
  `"null"` do §6.2 — fica registrado, correção é decisão futura.
- Não é objetivo garantir que `2021-01-01` é o início "certo" da janela
  para toda pergunta de análise futura — foi o corte pedido pelo autor
  para este recorte, não uma validação de que é o período ideal.
- *(v2)* Não é objetivo investigar as 3.759 linhas de continuidade
  quebrada (§6.4) uma a uma — ficam como população identificada, não
  como casos individualmente explicados.
- *(v2)* Não é objetivo corrigir `km_distancia` na fonte para o par
  `KMCN`/`KGUS` (§6.4) — a validação geodésica sinaliza, correção é
  decisão futura de quem revisar `basica_raw`/`basica_silver`.
- *(v2)* Não é objetivo generalizar a hipótese do §6.4 (horário único,
  não local) para outras empresas ou para o histórico anterior a 2021 —
  testado só para GOL/Azul dentro desta janela.

## 10. Regras checáveis (R-COL)

| ID | Regra | Onde verificar | Severidade |
|---|---|---|---|
| **R-COL-26** *(novo)* | `basica_curated_deep` contém só `sg_empresa_icao IN ('GLO','AZU')`. | `SELECT COUNT(*) FROM basica_curated_deep WHERE sg_empresa_icao NOT IN ('GLO','AZU')` deve ser `0` | Alta |
| **R-COL-27** *(novo)* | `basica_curated_deep` tem exatamente as 29 colunas essenciais de `SPEC-005 §5`, mesmos nomes. | `PRAGMA table_info(basica_curated_deep)` × `SPEC-005 §5` | Alta |
| **R-COL-28** *(novo)* | `vra_curated_deep` contém só `sg_empresa_icao IN ('GLO','AZU')`, mesma janela de `basica_curated_deep` (`>= 2021-01-01`). | `SELECT COUNT(*) FROM vra_curated_deep WHERE sg_empresa_icao NOT IN ('GLO','AZU')` deve ser `0` | Alta |
| **R-COL-29** *(novo)* | `vra_curated_deep` tem as 12 colunas de `SPEC-006 §5`, sem corte. | `PRAGMA table_info(vra_curated_deep)` × `SPEC-006 §5` | Média |
| **R-COL-30** *(novo, v2)* | `delta_horas_voadas` em `fato_rotacao_aeronave_gol_azul` nunca excede 0,01h (36s) em valor absoluto — se exceder, a hipótese do §6.4 (horário único) parou de valer para alguma linha nova (ex.: recarga futura, dado de outra empresa). | `SELECT MAX(ABS(delta_horas_voadas)) FROM fato_rotacao_aeronave_gol_azul` deve ser `< 0.01` | Alta |
| **R-COL-31** *(novo, v2)* | Nenhuma linha de `fato_rotacao_aeronave_gol_azul` tem `km_distancia_geodesica IS NULL` enquanto `dim_airport` cobrir 100% dos ICAO usados (§6.4) — `NULL` sinaliza aeroporto novo sem match na dimensão. | `SELECT COUNT(*) FROM fato_rotacao_aeronave_gol_azul WHERE km_distancia_geodesica IS NULL` deve ser `0` | Média |
| **R-COL-35** *(novo, v3)* | `fato_block_time_gol_azul` (`SPEC-014`) tem a coluna `fl_solo_valido` — se ausente, `fato_rotacao_aeronave_gol_azul` foi recarregada depois de `DDL_005` sem re-rodar `DDL_004` (§6.5), as duas tabelas dessincronizaram. | `PRAGMA table_info(fato_block_time_gol_azul)` deve listar `fl_solo_valido` | Média |

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
- *(v2)* `fato_rotacao_aeronave_gol_azul` tem 3.759 linhas de
  continuidade quebrada não investigadas (§6.4) — podem ser reposição de
  aeronave não capturada como etapa, troca de matrícula, ou erro de dado;
  causa não confirmada.
- *(v2)* `km_distancia` está confirmadamente errado para o par
  `KMCN`/`KGUS` (matrícula `AUC`, 2 linhas) — quem usar `km_distancia`
  direto de `basica_curated_deep` (não desta fato) herda o mesmo erro sem
  aviso, porque a validação geodésica só existe aqui.
- *(v2)* `fl_continuidade_ok`/`tempo_solo_horas` são `NULL` na primeira
  etapa de cada matrícula dentro da janela — efeito de borda (a aeronave
  pode ter voado antes de 2021, fora do recorte), não falta de dado real.

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
- *(v2)* Alguém investigar as 3.759 linhas de continuidade quebrada e
  encontrar causa sistemática (não caso a caso) — atualizar §6.4/§11 com
  o achado.
- *(v2)* `km_distancia` for corrigido na fonte para `KMCN`/`KGUS` —
  `delta_km_distancia` dessas duas linhas deixa de ser outlier,
  atualizar §6.4.

## 13. Histórico

| Data | Evento |
|---|---|
| 2026-08-31 | SPEC-012 v1 produzida em status `proposto`, retroativa. Documenta `basica_curated_deep` (2.743.964 linhas, 29 colunas) e `vra_curated_deep` (2.697.490 linhas, 12 colunas), ambas já carregadas a pedido direto do autor. Achado novo registrado (§6.2): valor literal `"null"` em `vra_raw.dt_hr_partida_real` e risco de comparação de texto direta em data de formato duplo — não documentado em `SPEC-009`/`SPEC-006` até agora. Aguardando aprovação do autor. |
| 2026-08-31 | **v2 — `fato_rotacao_aeronave_gol_azul` acrescentada.** Autor propôs usar `dim_airport` para normalizar fuso horário local antes de calcular duração de etapa; testado antes de desenhar o DDL e **refutado**: horários da Básica já estão num referencial único, não local por aeroporto (§6.4, evidência: subtração ingênua bate exato com `nr_horas_voadas` cruzando fusos reais de 2h). Papel de `dim_airport` redesenhado para rotação por matrícula (continuidade espacial, 99,86% medido) e validação geodésica de `km_distancia` (haversine) — isolou achado real: par `KMCN`/`KGUS` com `km_distancia` incorreto na fonte (delta 5.634,8 km, 2 linhas). `voo_trusted` (cancelada) citada em §3.2/§11 corrigida para refletir que o arquivo foi excluído, não só "cancelado". C-04/C-05/C-06, R-COL-30/31 novos. §3.1, §3.2, §4.2, §5.3, §6.4, §8, §9, §11, §12 atualizados. |
| 2026-09-03 | **v3 — correção retroativa (achado de auditoria documental): `fl_solo_valido` (`DDL_005`, 2026-09-02) documentada.** Coluna nova em `fato_rotacao_aeronave_gol_azul`, construída na mesma sessão que `SPEC-016` (análise de tempo de solo) já vinha consumindo sem que esta SPEC a registrasse — corrigido agora. Flag de validade (não filtro destrutivo): `0` quando `tempo_solo_horas<0` (408 linhas), `fl_continuidade_ok=0` (3.759) ou `>72h` (4.142, corte de julgamento de domínio, não achado estatístico) — união 7.919 de 2.743.531 linhas com solo não-nulo (0,2886%). `fato_block_time_gol_azul` (`SPEC-014`) precisou ser reconstruída para herdar a coluna (`DDL_004` roda com `f.*`, não automático). §5.3, §6.5 (novo), R-COL-35 novos. |

---

*Fim do documento.*
