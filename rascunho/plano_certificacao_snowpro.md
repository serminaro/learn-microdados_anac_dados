# Plano: preparação para a certificação SnowPro Core, usando o projeto ANAC como laboratório

> **Migrado para peça formal em 2026-08-30**: este conteúdo foi
> formalizado como `docs/GUIDE/GUIDE_001_Estudo_SnowPro_Core_via_Projeto_ANAC.md`.
> A lacuna de domínio da §3 foi fechada em `docs/plano_objetos_snowflake.md`
> no mesmo bloco de trabalho, e o ponto em aberto da §5 foi resolvido pela
> `docs/DEC/DEC_006_Escopo_Star_Schema_Basica_vs_VRA.md` (ambas ainda em
> `proposto`, aguardando revisão do autor). Este arquivo permanece como
> rascunho original, não é mais a fonte viva.
>
> Nota de status: rascunho informal, fora da taxonomia SERMI deste projeto
> (SPEC-001 §5/§2 tipa exaustivamente `docs/`, e um `plano_*.md` novo ali
> violaria a R-TAX-10, que isenta só os dois arquivos pré-existentes). Este
> documento vive em `rascunho/` pelo mesmo motivo dos outros três arquivos
> desta pasta: nota de trabalho pessoal, não peça formal. Migração para
> `docs/GUIDE/` é possível no futuro, por oportunidade, se o autor decidir
> formalizar (exigiria uma DEC de referência, R-TAX-06).
>
> Relacionado: `docs/plano_objetos_snowflake.md` (já assume explicitamente,
> desde a linha 3, o papel de veículo de estudo para o SnowPro Core — este
> documento complementa aquele, não substitui), `docs/plano_expansao_multidataset.md`,
> e `serminaro-governance/trabalho/contratos-trabalho/20-azul-analista-dados/okr/okr_carreira_estudo.md`
> (KR1.3, KR1.4, KR4.1).

---

## 1. Correção de contexto (2026-08-30)

O exame **COF-C02**, referenciado até agora no OKR de carreira, foi
**aposentado pela Snowflake em 14/05/2026**. A versão vigente é **COF-C03**
(mesma nota de corte aproximada, ~750/1000; custo US$ 175). Já corrigido em
`okr_carreira_estudo.md` (KR1.3). Este documento usa COF-C03 do início.

## 2. Domínios do exame (COF-C03)

Fonte terceira (certstud.com, open-exam-prep.com), consistente internamente
(soma 100%), mas **não confirmada contra o PDF oficial do exam guide** —
tratar como estimativa de estudo, não valor fechado:

| Domínio | Peso aprox. |
|---|---|
| Snowflake AI Data Cloud Features & Architecture | 25% |
| Account Access and Security | 17% |
| Data Transformations | 17% |
| Performance Concepts | 15% |
| Data Loading and Unloading | 15% |
| Data Protection and Data Sharing | 11% |

100 questões, 115 min.

## 3. Lacuna identificada no `plano_objetos_snowflake.md`

A tabela "Mapa objeto → domínio SnowPro Core" desse documento (linha 112-119)
cobre só 4 domínios (nomenclatura antiga, aproximada da COF-C02):

| Domínio coberto lá | Objetos já mapeados |
|---|---|
| Arquitetura da plataforma | Table, View, Dynamic Table, Warehouse |
| Carga e descarga de dados | Stage, File Format, Pipe, Stream |
| Transformação de dados | Task, Procedure, Function, Sequence |
| Proteção e compartilhamento de dados | Contact, API Integration, Git Repository |

**Faltam por completo**: *Account Access and Security* (17%) e
*Performance Concepts* (15%) — juntos, **32% da prova sem exercício
mapeado** neste projeto até agora. É a lacuna que a seção 4 fecha.

## 4. Exercícios complementares (o que o plano Snowflake não cobre)

| Domínio | Exercício no projeto ANAC | Onde registrar |
|---|---|---|
| **Account Access and Security** | Criar role customizada (ex. `ANAC_ANALYST`, só `SELECT` na camada ouro); aplicar uma masking policy num campo sensível (ex. matrícula de aeronave) ou uma row access policy por UF; testar com um segundo usuário de teste | Novo `DDL_00N` em `sql/ingestao_snowflake/` ou `sql/tratamento/`, mais uma seção nova no `plano_objetos_snowflake.md` (Camada 5 — Governança já existe, é o lugar natural) |
| **Performance Concepts** | Comparar Query Profile de uma agregação pesada com/sem clustering key na fact table; redimensionar `wh_anac` (X-Small → Small) e comparar tempo/crédito na mesma query; observar cache de resultado (rodar a mesma query 2x) | Registrar achados como nota empírica, no mesmo estilo das "Notas de consistência" do `README.md` |

Isso fecha os 6 domínios usando o mesmo projeto, sem inventar exercício
artificial — mesmo critério de honestidade que `plano_objetos_snowflake.md`
já usa ("onde um objeto não tem encaixe honesto, fica registrado como tal").

## 5. Ponto em aberto, não resolvido aqui: escopo VRA vs. Básica

O OKR de carreira (**KR4.1**, 12 meses) pede especificamente
"**ANAC VRA** → Snowflake → Power BI" com star schema (≥1 fato + ≥4
dimensões). Mas o `plano_objetos_snowflake.md` (Camada 3, Fase D) já
desenha esse mesmo star schema para o schema **`ANAC.BASICA`**, não VRA —
e VRA hoje só tem download bruto, sem extração/schema/carga implementados
(`README.md`, linha 110-112).

Duas leituras possíveis, **não decididas aqui**:
- (a) o star schema da Fase D serve para os dois datasets com adaptação
  mínima, e o KR4.1 pode ser satisfeito com Básica mesmo, atualizando o
  texto do KR; ou
- (b) VRA precisa do capítulo próprio que `plano_expansao_multidataset.md`
  já previu ("VRA e SIROS ganham capítulos equivalentes quando chegar a vez
  deles"), e o KR4.1 fica como está.

Recomendo resolver isso como uma decisão explícita (BAUR: **B**una
decisão pequena, mas vale registrar formalmente já que este projeto usa DEC
para decisão de arquitetura) antes da Fase D começar, não silenciosamente.

## 6. Cronograma (10-12 semanas a partir de 2026-08-30)

| Semana | Foco | Entrega verificável |
|---|---|---|
| 1 | Arquitetura + estrutura de dados (já em grande parte feito via Básica) | Revisão do que já existe, preencher lacunas de entendimento |
| 2 | Account Access & Security (seção 4) | Role + masking/row policy testadas |
| 3 | Data Loading & Unloading (Fase A/B já cobre parte) | Fase B do plano Snowflake (Procedure `sp_merge_basica`) concluída |
| 4 | Performance Concepts (seção 4) | Nota empírica de clustering key + warehouse sizing |
| 5-6 | Data Transformations (Fase C/D/E do plano Snowflake) | Stream+Task rodando; star schema resolvido (após decisão da seção 5) |
| 7 | Data Protection & Sharing (Fase F/G + Time Travel/clone) | Semantic View + demonstração de Time Travel/zero-copy clone |
| 8-9 | dbt (KR1.4) sobre o star schema já pronto | `dbt build` verde, ≥5 models, ≥8 tests |
| 10 | Power BI (KR4.1, fora do escopo do exame) | Dashboard com ≥6 measures DAX |
| 11-12 | Revisão + simulados (Snowflake University, Udemy Tom Bailey) | ≥2 simulados ≥80%, agendar e fazer a prova |

Prazo do KR1.3/1.4 é 6 meses a partir de 29/06/2026 (~dezembro/2026); este
cronograma cabe com folga.

## 7. Referências

- Snowflake, [Updated SnowPro Core Certification Announcement](https://www.snowflake.com/en/blog/updated-snowpro-core-exam-certification-announcement/)
- [SnowPro® Core Certification (COF-C03) — oficial](https://learn.snowflake.com/en/certifications/snowpro-core-c03/)
- Domínios/pesos (terceiros, a confirmar): [certstud.com](https://certstud.com/certifications/snowflake/snowpro-core/study-guide), [open-exam-prep.com](https://open-exam-prep.com/blog/snowpro-core-certification-exam-guide-2026)
