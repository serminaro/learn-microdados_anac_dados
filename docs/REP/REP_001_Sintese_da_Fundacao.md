---
documento: REP-001
titulo: Síntese da Fundação — learn-microdados_anac_dados
versao: v1
status: aprovado
data: 2026-08-24
autor: Bruno Alexandre Serminaro
referencia: DEC-001
escopo: projeto
---

# REP-001 · Síntese da Fundação

> Consolida a base epistêmica que sustenta a fundação deste projeto sob
> SERMI: o que motivou, o que já se sabia antes desta sessão, o que se
> decidiu, o que é achado confirmado versus hipótese ainda não testada, e o
> que fica pendente para os blocos seguintes (DEC-002/SPEC-002,
> DEC-003/SPEC-003). Insumo direto de SPEC-002 e SPEC-003.

---

## 1. Contexto

`learn-microdados_anac_dados` existe desde antes desta fundação: pipeline
de consolidação da tabela Básica da ANAC (2024-2026) em SQLite, réplica no
Snowflake, dicionário de colunas, e um plano de objetos Snowflake em
andamento (`docs/plano_objetos_snowflake.md`, Fase A concluída em
2026-08-11). Repositório público no GitHub, licença MIT — peça de
portfólio, não só ferramenta pessoal.

Em 2026-08-24, numa única sessão, três coisas aconteceram em sequência: (1)
reorganização de `scripts/`/`sql/` por papel no pipeline; (2) expansão de
escopo de 1 dataset para 3 (Básica, VRA, SIROS) com dois caminhos de
produção paralelos; (3) o pedido explícito do autor para fundar o projeto
sob a governança documental SERMI. Este relatório sintetiza o estado que
resulta dessas três mudanças, no ponto em que a fundação (DEC-001, SPEC-001)
está pronta e antes de DEC-002/SPEC-002 formalizarem o escopo descritivo.

O estado anterior — decisões de arquitetura registradas em prosa dentro de
`docs/plano_*.md`, sem alternativa descartada nem critério de reavaliação
— é exatamente o que o DEC-001 (§1) identificou como o gatilho para fundar
agora, não depois.

---

## 2. Escopo

**Coberto por este relatório:** o histórico do projeto até esta fundação, a
base empírica que sustenta as decisões de escopo já tomadas informalmente
(D1-D7, §4), a separação entre achado confirmado e hipótese candidata sobre
as fontes de dado, e as premissas/vieses que devem calibrar o próximo
bloco (DEC-002/SPEC-002).

**Fora de escopo:** o conteúdo formal de SPEC-002 (critérios de sucesso
C-NN, não-objetivos) e SPEC-003 (papéis, cadência) — isso é DEC-002 e
DEC-003, que ainda não foram escritas. Também fora de escopo: detalhe
técnico de implementação de cada fase do plano Snowflake ou do plano de
expansão multidataset, já registrados nos respectivos documentos de plano
(`docs/plano_objetos_snowflake.md`, `docs/plano_expansao_multidataset.md`),
não repetidos aqui.

---

## 3. Base epistêmica

**Princípios que orientaram o trabalho desta sessão:**

- Realismo empírico sobre a fonte de dado: nenhuma afirmação de
  disponibilidade da ANAC (período coberto, cadência de publicação) foi
  aceita sem teste direto (requisição HTTP), mesmo quando a documentação ou
  a estrutura de pastas sugeria o contrário. Ver §5.
- Honestidade sobre limite: quando a fonte não sustenta o que se pediu
  (SIROS não tem histórico antes de 2019-11), isso foi registrado como
  limitação, não contornado nem escondido.
- Separação de decisão, descrição e narrativa: motivação direta da própria
  fundação SERMI (SPEC-001 §1).

**Pesquisa e referências:**

- Testes HTTP diretos contra `gov.br/anac/...` (Básica) e
  `sistemas.anac.gov.br/dadosabertos/...` (VRA, SIROS), 2026-08-24 — ver
  `docs/plano_expansao_multidataset.md` §1 para o detalhe completo por
  dataset.
- Precedente do ecossistema pessoal do autor: `learn-aviacao-cco-db`
  (projeto-irmão formalmente governado, fundação de cinco peças) e
  `serminaro-governance/_meta` (onde a fundação de sete peças foi fixada
  pela DEC-META-014, 2026-07-19) — usados para calibrar o que este projeto
  deveria/não deveria copiar (DEC-001 §3, §4.3).

---

## 4. Decisões iniciais

Decisões tomadas nesta sessão, antes ou durante a fundação. Cada uma remete
a uma DEC existente ou vira pendência de DEC futura (§7):

- **D1** — Consolidar 3 datasets ANAC (Básica, VRA, SIROS) em vez de 1.
  *Pendência de DEC*: candidata a `DEC-002` (decisão de escopo/descrição).
- **D2** — Dois caminhos de produção paralelos e igualmente investidos
  (Snowflake medalhão; SQLite+Python), não um principal e um secundário.
  *Pendência de DEC*: candidata a `DEC-002`.
- **D3** — Corte temporal 2010-presente para Básica/VRA (a fonte permite
  desde 2000, mas o projeto não usa o máximo); SIROS fixado em 2019-11+ por
  limite real da fonte, não escolha do projeto.
  *Pendência de DEC*: candidata a `DEC-002`.
- **D4** — Um banco SQLite por dataset; convenção de nomenclatura por
  prefixo de dataset nos scripts (não numeração sequencial linear).
  *Pendência de DEC*: decisão técnica/arquitetural, não de escopo — melhor
  candidata a uma DEC de conteúdo dedicada (`DEC-004` ou posterior, ver
  SPEC-001 §9), não a `DEC-002`, cujo papel é preencher o SPEC-002
  (descrição/escopo), não arquitetura de dado.
- **D5** — Adotar a taxonomia SERMI (fundação de sete peças, DEC-META-014)
  para este projeto a partir de 2026-08-24.
  *Formalizada*: `DEC-001`, aprovado.
- **D6** — Arquivo de código-fonte (shell, Python, SQL, Jupyter, R) não
  vira peça SERMI, mas adota a mesma mecânica de nome `TIPO_NNN_descricao`
  (BASH, SRC, DDL, DML, NOTE, R), prospectiva. R fica fora dos dois
  caminhos de produção, como ferramenta complementar de análise.
  *Formalizada*: `DEC-001 §6.6`.
- **D7** — Ingestão SQLite e Snowflake fisicamente separadas
  (`src/ingestao_sqlite/`, `src/ingestao_snowflake/`,
  `sql/ingestao_sqlite/`, `sql/ingestao_snowflake/`); download bruto e
  preparação comum continuam únicos, não duplicados por engine.
  *Pendência de DEC*: mesma natureza de D4 — arquitetural, candidata a DEC
  de conteúdo dedicada, não a `DEC-002`.

A relação D1-D3/D5 → `DEC-002` e D4/D7 → DEC de conteúdo futura (não
`DEC-002`) é, ela mesma, uma leitura deste relatório, não uma decisão
fechada — cabe ao autor confirmar ou corrigir no bloco de `DEC-002`.

---

## 5. Achados e hipóteses candidatas

### 5.1 Achados confirmados

Testados por requisição HTTP direta em 2026-08-24, não inferidos de
documentação:

- **Básica**: zip mensal real desde 2000-01 até 2026-06 (amostrado em
  2000, 2005, 2010, 2015, 2020, 2023, todos HTTP 200), no mesmo padrão de
  URL já usado em produção para 2024-2026.
- **VRA**: pastas de ano/mês confirmadas de 2000 a 2026 no portal de dados
  abertos; arquivo individual verificado em ao menos um mês (agosto/2024,
  `VRA_20248.csv` + `.json`).
- **SIROS**: publicado **diariamente** (`registros_AAAA-MM-DD.csv`), não
  mensalmente — verificado num mês completo real (janeiro/2020, 31 arquivos
  CSV + 31 JSON). Início real do lote em 2019-11 (pasta 2019 só contém
  Novembro e Dezembro).

### 5.2 Hipóteses candidatas (evidência insuficiente para inferência forte)

- **Estabilidade de schema ao longo do tempo**: assume-se que o cabeçalho
  (colunas) de Básica e VRA é estável entre 2010 e 2026, mas isso não foi
  testado — a validação atual (`src/02_extract_validate.py`) só cobre
  2024-2026. Com até 16 anos de histórico adicional, mudança de cabeçalho é
  plausível e não descartada. Já registrado como risco explícito em
  `docs/plano_expansao_multidataset.md` §5.
- **Volume estimado do SIROS** ("potencial de dezenas de milhões de linhas
  diárias ao longo dos anos", citado em `docs/plano_expansao_multidataset.md`
  §4): extrapolação a partir do volume observado num único mês amostrado,
  não uma contagem real sobre o histórico completo.
- **Classificação DDL/DML de `07`/`08`** (`sql/ingestao_snowflake/`) como
  predominantemente DML: leitura pelo propósito dominante do arquivo
  (carregar dado), não uma divisão que o conteúdo torna óbvio por si só —
  os dois arquivos também declaram infraestrutura (DDL). Já registrado como
  simplificação assumida em `DEC-001 §6.6`.

Nenhuma das três hipóteses acima é apresentada como conclusão em nenhum
documento deste projeto; onde aparecem fora deste REP, aparecem já
marcadas como risco ou simplificação, não como fato.

---

## 6. Premissas operacionais

- **P1** — O projeto já tem histórico real (commits, docs) anterior a esta
  fundação: a fundação formaliza a governança de um projeto em andamento,
  não cria um projeto do zero.
- **P2** — Os dois caminhos de produção compartilham a mesma etapa de
  download bruto (`scripts/`) e preparação comum (`src/02`, `src/03`),
  divergindo só a partir da ingestão específica de engine.
- **P3** — SIROS muda o desenho de download em relação a Básica/VRA
  (cadência diária, não mensal) e reabre a Fase G (Pipe/Snowpipe) do plano
  Snowflake, hoje registrada como opcional por não bater com a cadência
  mensal da Básica.

**Vieses a vigiar:**

- **Romantização de escopo**: o projeto cresceu de 1 para 3 datasets numa
  sessão só. Risco real de comprometer volume/prazo além do que o ritmo de
  trabalho solo sustenta. `DEC-002`/`SPEC-002` (critérios de sucesso) devem
  calibrar isso deliberadamente, não herdar o entusiasmo do momento da
  expansão sem questionar.
- **Viés de disponibilidade de fonte**: "a fonte tem dado desde 2000" não
  implica que processar 26 anos seja a escolha certa. O corte em 2010 (D3)
  já mitiga parcialmente, mas vale revisitar explicitamente em
  `SPEC-002`, não só aceitar o corte atual por inércia.

---

## 7. Recomendações por escala temporal

Projeto solo — dono operacional é o autor em todas as escalas.

| Escala | Recomendação |
|---|---|
| **Dias** | Revisar e aprovar SPEC-001 + REP-001 (este bloco); produzir DEC-002 + SPEC-002 em seguida. |
| **Semanas** | Fase B do plano Snowflake (Procedure `sp_merge_basica`); estender `scripts/01_download.sh` da Básica para 2010; primeira rodada do skill `gov-check` assim que a fundação completa (sete peças) existir. |
| **Meses** | Replicar o pipeline (os dois caminhos) para VRA; iniciar SIROS, com desenho de download específico para a cadência diária. |
| **Trimestres e além** | Os 3 datasets completos nos dois caminhos, camadas ouro, dashboards (Power BI/Looker Studio no caminho Snowflake, Streamlit no caminho SQLite). |

---

## 8. Pendências e próximos passos

- Produzir `DEC-002` (decisões de descrição) e `SPEC-002` (descrição do
  projeto: propósito, escopo, critérios de sucesso, não-objetivos), a
  partir do acúmulo de D1-D3/D5 deste relatório.
- Produzir `DEC-003` (decisão de participação) e `SPEC-003` (contrato de
  responsabilidade), registrando o modo solo e o freio compensatório
  (auditoria recorrente via `gov-check`).
- Avaliar, num momento futuro não determinado por esta fundação, se D4/D7
  (organização de dado, separação de ingestão) merecem uma DEC de conteúdo
  dedicada (`DEC-004`+) — ficou como leitura deste relatório, não decisão
  fechada (§4).
- Validar a hipótese candidata de estabilidade de schema (§5.2) quando o
  download da Básica for de fato estendido para 2010 — é nesse momento que
  a hipótese vira achado confirmado ou achado refutado.
- Migração (ou não) de `docs/plano_objetos_snowflake.md` e
  `docs/plano_expansao_multidataset.md` para peça formal SERMI — por
  oportunidade, sem prazo forçado (DEC-001 §5.3).
- Primeira auditoria de coerência (`gov-check`) assim que as sete peças da
  fundação existirem (Nível 2 de "Definição de Pronto",
  `rascunho/INSTRUCAO_DE_TRABALHO.txt` §6).

---

## 9. Histórico

| Data | Evento |
|---|---|
| 2026-08-24 | REP-001 v1 produzido e aprovado pelo autor, no mesmo bloco de trabalho de sua produção (junto com SPEC-001). O blueprint de REP não exige seção Histórico; nenhuma existia neste momento. |
| 2026-08-25 | Seção Histórico adicionada retroativamente, por achado do `gov-check` (`AUDIT-001`, R-CON-02 do SPEC-003: artefato `aprovado` precisa de registro de aprovação no próprio documento). Aprovador: Bruno Alexandre Serminaro. Sem revisão adicional da IA de apoio além da já registrada na produção original. |

---

*Fim do documento.*
