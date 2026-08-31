---
documento: GUIDE-001
titulo: Estudo para a certificação SnowPro Core (COF-C03) usando o projeto ANAC como laboratório
versao: v1
status: aprovado
data: 2026-08-30
autor: Bruno Alexandre Serminaro
referencia: DEC-002, DEC-006
escopo: projeto
---

# GUIDE-001 · Estudo para o SnowPro Core (COF-C03) via projeto ANAC

> Formaliza, como peça SERMI, o plano de estudo que vivia em
> `rascunho/plano_certificacao_snowpro.md` (nota de trabalho pessoal,
> fora da taxonomia documental). Descreve como operar o projeto
> `learn-microdados_anac_dados` como veículo de estudo para os seis
> domínios do exame **SnowPro Core (COF-C03)**, cobrindo lacuna de
> domínio, cronograma e o ponto de escopo que a DEC-006 resolveu.
> Complementa `docs/plano_objetos_snowflake.md` (que já assume, desde a
> origem, o papel de veículo de estudo, e cujo mapa objeto→domínio foi
> atualizado para COF-C03 no mesmo bloco de trabalho que produziu este
> GUIDE), não o substitui.

---

## 1. Propósito

`SPEC-002 §1` já declara competência em Snowflake/SnowPro Core como parte
do propósito deste projeto. Este documento opera esse propósito: como usar
o pipeline ANAC já em construção para cobrir, com exercício honesto (não
forçado), os seis domínios do exame vigente.

## 2. Correção de contexto

O exame **COF-C02**, referenciado em versões anteriores do OKR de
carreira, foi **aposentado pela Snowflake em 14/05/2026**. A versão
vigente é **COF-C03** (nota de corte aproximada ~750/1000; custo
US$ 175). Este documento e o `plano_objetos_snowflake.md` usam COF-C03.

## 3. Domínios do exame (COF-C03)

Fonte terceira (certstud.com, open-exam-prep.com), consistente
internamente (soma 100%), mas **não confirmada contra o PDF oficial do
exam guide** — tratar como estimativa de estudo, não valor fechado.

| Domínio | Peso aprox. |
|---|---|
| Snowflake AI Data Cloud Features & Architecture | 25% |
| Account Access and Security | 17% |
| Data Transformations | 17% |
| Performance Concepts | 15% |
| Data Loading and Unloading | 15% |
| Data Protection and Data Sharing | 11% |

100 questões, 115 min.

## 4. Mapeamento objeto/exercício por domínio

Cobertura completa dos seis domínios, mantida em
`docs/plano_objetos_snowflake.md` ("Mapa objeto → domínio SnowPro Core
(COF-C03)"), com o exercício honesto por domínio:

| Domínio | Onde é praticado |
|---|---|
| Arquitetura da plataforma | Table, View, Dynamic Table, Warehouse (Camadas 1, 3) |
| Account Access and Security | Role `ANAC_ANALYST`, Masking Policy, Row Access Policy (Camada 5) |
| Data Transformations | Task, Procedure, Function, Sequence (Camada 2, 3) |
| Performance Concepts | Clustering key, warehouse sizing, cache de resultado — nota empírica, sem objeto dedicado |
| Data Loading and Unloading | Stage, File Format, Pipe, Stream (Camada 0, 1) |
| Data Protection and Data Sharing | Contact, API Integration, Git Repository, Time Travel/zero-copy clone (Camada 5) |

Antes de 2026-08-30, o mapa cobria só 4 domínios na nomenclatura antiga da
COF-C02, deixando 32% da prova (Account Access and Security + Performance
Concepts) sem exercício mapeado. Fechado no mesmo bloco de trabalho que
produziu este GUIDE.

## 5. Escopo do star schema (KR4.1): resolvido pela DEC-006

O OKR de carreira (KR4.1, 12 meses) lista, na coluna de ação estratégica,
"ANAC VRA → Snowflake → Power BI". O `plano_objetos_snowflake.md` (Fase D)
desenha o star schema sobre `ANAC.BASICA`, não VRA — que ainda só tem
download bruto implementado (`SPEC-002 §4.1`). A `DEC-006` resolveu essa
tensão: o critério verificável do KR4.1 não nomeia dataset, e Básica
satisfaz esse critério via a Fase D já desenhada. VRA permanece "a
implementar", sem prazo vinculado a este KR (`plano_expansao_multidataset.md`).

## 6. Cronograma (10-12 semanas a partir de 2026-08-30)

| Semana | Foco | Entrega verificável |
|---|---|---|
| 1 | Arquitetura + estrutura de dados (já em grande parte feito via Básica) | Revisão do que já existe, preencher lacunas de entendimento |
| 2 | Account Access & Security (`plano_objetos_snowflake.md`, Camada 5) | Role + masking/row access policy testadas |
| 3 | Data Loading & Unloading (Fase A/B já cobre parte) | Fase B do plano Snowflake (Procedure `sp_merge_basica`) concluída |
| 4 | Performance Concepts | Nota empírica de clustering key + warehouse sizing |
| 5-6 | Data Transformations (Fase C/D/E do plano Snowflake) | Stream+Task rodando; star schema sobre Básica (DEC-006) |
| 7 | Data Protection & Sharing (Fase F/G + Time Travel/clone) | Semantic View + demonstração de Time Travel/zero-copy clone |
| 8-9 | dbt (KR1.4) sobre o star schema já pronto | `dbt build` verde, ≥5 models, ≥8 tests |
| 10 | Power BI (KR4.1, fora do escopo do exame) | Dashboard com ≥6 measures DAX |
| 11-12 | Revisão + simulados (Snowflake University, Udemy Tom Bailey) | ≥2 simulados ≥80%, agendar e fazer a prova |

Prazo do KR1.3/1.4 é 6 meses a partir de 29/06/2026 (~dezembro/2026); este
cronograma cabe com folga.

## 7. Limitações conhecidas

- Pesos de domínio são de fonte terceira, não confirmados contra o exam
  guide oficial da Snowflake.
- O cronograma da §6 é estimativa de ritmo, não compromisso com data fixa
  — sujeito ao mesmo critério de sucesso incremental do `DEC-002 §6.2`.
- A edição do `okr_carreira_estudo.md` (fora deste repositório, coluna de
  ação estratégica do KR4.1) é pendência do autor, não executada por esta
  peça nem pela DEC-006 que a motivou.

## 8. Referências

- Snowflake, [Updated SnowPro Core Certification Announcement](https://www.snowflake.com/en/blog/updated-snowpro-core-exam-certification-announcement/)
- [SnowPro® Core Certification (COF-C03) — oficial](https://learn.snowflake.com/en/certifications/snowpro-core-c03/)
- Domínios/pesos (terceiros, a confirmar): [certstud.com](https://certstud.com/certifications/snowflake/snowpro-core/study-guide), [open-exam-prep.com](https://open-exam-prep.com/blog/snowpro-core-certification-exam-guide-2026)

## 9. Histórico

| Data | Evento |
|---|---|
| 2026-08-30 | GUIDE-001 produzido em status `proposto`, migrando `rascunho/plano_certificacao_snowpro.md` para peça SERMI formal, no mesmo bloco de trabalho que corrigiu o mapa de domínios em `plano_objetos_snowflake.md` e produziu a `DEC-006` (resolve §5). Aguardando revisão do autor. |
| 2026-08-31 | **Aprovada.** Frontmatter com `referencia: DEC-002, DEC-006` coerente com R-TAX-06 (ambas as DECs motivadoras citadas). Autor revisou o resumo (quadro "Aprovações ANAC") e aprovou explicitamente. Primeira peça `GUIDE` do projeto a ser aprovada. |

---

*Fim do documento.*
