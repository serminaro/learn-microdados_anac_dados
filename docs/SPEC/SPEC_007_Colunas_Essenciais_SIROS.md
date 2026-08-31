---
documento: SPEC-007
titulo: Colunas Essenciais — SIROS
versao: v1
status: aprovado
data: 2026-08-31
autor: Bruno Alexandre Serminaro
referencia: DEC-007
escopo: projeto
---

# SPEC-007 · Colunas Essenciais — SIROS

> Levantamento das colunas do dataset SIROS, a partir de arquivo real já
> baixado (`data/anac/siros/registros_2022-08-10.csv`) — não de
> documentação externa. Achado estrutural relevante: SIROS **não é** dado
> voo-por-data como Básica/VRA — é registro de **autorização de slot**,
> com padrão semanal e janela de validade. Isso muda o que "coluna
> essencial" significa aqui frente a `SPEC-005`/`SPEC-006`.

---

## 1. Propósito

Documentar a estrutura real do SIROS antes de desenhar sua ingestão
(`SPEC-010`, futura), e registrar formalmente o achado de que sua
granularidade é diferente de Básica/VRA — decisão que a `DEC-008`
(arquitetura de ingestão das 3 bases) precisa herdar, não resolver aqui.

## 2. Audiência

Reaproveita os papéis abstratos do `SPEC-002 §2` — nenhum papel novo.

## 3. Escopo

### 3.1 O que este SPEC entrega

1. Dicionário das 28 colunas brutas do SIROS (§5).
2. Registro do achado de granularidade (§6): autorização de slot, não voo
   por data.
3. Nome proposto de coluna, mesma convenção de prefixo do projeto.

### 3.2 Fora de escopo

- Ingestão real (DDL, scripts) — `SPEC-010`.
- Resolver como transformar "autorização por semana" em "voo por data"
  (se e quando isso for necessário para alguma pergunta de análise
  futura) — registrado como pergunta em aberto (§6), não resolvido.
- Confirmação contra o layout oficial do SIROS publicado pela ANAC.

## 4. Método

Inspeção direta de `data/anac/siros/registros_2022-08-10.csv`: linha 1 é
metadado de publicação (`"Atualizado em: 2022-08-12"`), linha 2 é o
cabeçalho real, delimitador `;`, valores entre aspas. Duas linhas de dado
inspecionadas.

## 5. Dicionário de colunas (SIROS bruto)

| Coluna bruta (CSV ANAC) | Nome proposto | Tipo inferido | Confiança | Comentário |
|---|---|---|---|---|
| `Cód  Empresa` | `CD_EMPRESA` | TEXT | alta confiança | Ex.: `AAL` — parece ICAO, mas nome da coluna não confirma isso explicitamente |
| `Empresa` | `NM_EMPRESA` | TEXT | alta confiança | Nome por extenso, ex.: `AMERICAN AIRLINES, INC.` |
| `Nº Voo` | `NR_VOO` | TEXT | alta confiança | |
| `Equip ` | `SG_EQUIPAMENTO_ICAO` | TEXT | alta confiança | Ex.: `B789`, `B772` |
| `Seg` | `FL_OPERA_SEGUNDA` | TEXT/NUMBER | inferido (padrão de nome) | Ver achado §6 — valor observado nas duas amostras é sempre `1`, não confirmado se marca presença/ausência |
| `Ter` | `FL_OPERA_TERCA` | TEXT/NUMBER | inferido (padrão de nome) | Valor observado: `2` |
| `Qua` | `FL_OPERA_QUARTA` | TEXT/NUMBER | inferido (padrão de nome) | Valor observado: `3` |
| `Qui` | `FL_OPERA_QUINTA` | TEXT/NUMBER | inferido (padrão de nome) | Valor observado: `4` |
| `Sex` | `FL_OPERA_SEXTA` | TEXT/NUMBER | inferido (padrão de nome) | Valor observado: `5` |
| `Sáb` | `FL_OPERA_SABADO` | TEXT/NUMBER | inferido (padrão de nome) | Valor observado: `6` |
| `Dom` | `FL_OPERA_DOMINGO` | TEXT/NUMBER | inferido (padrão de nome) | Valor observado: `7` |
| `Quant  Assentos` | `NR_ASSENTOS_OFERTADOS` | NUMBER | alta confiança | |
| `Nº SIROS` | `NR_SIROS` | TEXT | alta confiança | Chave do registro de autorização, ex.: `AAL-014694106` |
| `Situação SIROS` | `DS_SITUACAO_SIROS` | TEXT | alta confiança | Ex.: `Em Operação` |
| `Data Registro` | `DT_REGISTRO` | TIMESTAMP | alta confiança | Quando o registro foi criado no sistema — **não** é data de voo |
| `Início Operação` | `DT_INICIO_OPERACAO` | DATE | confirmado | Início da janela de validade da autorização |
| `Fim Operação` | `DT_FIM_OPERACAO` | DATE | confirmado | Fim da janela de validade |
| `Natureza Operação` | `DS_NATUREZA_OPERACAO` | TEXT | alta confiança | Ex.: `INTERNACIONAL` |
| `Nº Etapa` | `NR_ETAPA` | NUMBER | alta confiança | |
| `Cód  Origem` | `CD_ORIGEM` | TEXT | inferido (padrão de nome) | Ex.: `KDFW` — parece ICAO |
| `Arpt Origem` | `NM_AERODROMO_ORIGEM` | TEXT | alta confiança | Nome completo + cidade + país num só campo, ex.: `DALLAS-FORT WORTH INTERNATIONAL AIRPORT (DFW) - DALLAS & FORT WORTH, TEXAS - ESTADOS UNIDOS DA AMÉRICA` — precisaria parsing para separar aeroporto/cidade/país |
| `Cód Destino` | `CD_DESTINO` | TEXT | inferido (padrão de nome) | |
| `Arpt Destino` | `NM_AERODROMO_DESTINO` | TEXT | alta confiança | Mesmo formato composto de `Arpt Origem` |
| `Horário Partida` | `HR_PARTIDA` | TIME | confirmado | **Só hora**, sem data — é horário de template semanal, não de um voo específico |
| `Horário Chegada` | `HR_CHEGADA` | TIME | confirmado | Idem |
| `Tipo Serviço` | `DS_TIPO_SERVICO` | TEXT | alta confiança | Ex.: `REGULAR DE PASSAGEIROS` |
| `Objeto Transporte` | `DS_OBJETO_TRANSPORTE` | TEXT | alta confiança | Ex.: `PASSAGEIROS` |
| `Codeshare` | `DS_CODESHARE` | TEXT | incerto | Texto livre listando parceiros e janelas de validade, ex.: `GLO/6013 início: 18/05/2022 fim: 29/10/2022` — formato não estruturado, precisaria parsing próprio se for usado |

Todas as 28 colunas ficam marcadas como relevantes por ora — diferente da
Básica, não há ainda pergunta de análise que force um recorte "essencial"
menor (nenhuma das seis perguntas da `DEC-007` usa SIROS hoje).

## 6. Achado: SIROS é registro de autorização, não voo-por-data

**Hipótese que virou achado com esta amostra** (2 linhas, ambas com o
mesmo padrão — confiança moderada, não exaustiva): cada linha do SIROS
não é "um voo realizado num dia específico", é **uma autorização de slot**
— define que a empresa X pode operar o voo Y, nos dias da semana
marcados (`Seg`...`Dom`), dentro de uma janela de validade
(`Início Operação` a `Fim Operação`). Não existe coluna de data de voo
individual.

**Consequência de arquitetura, registrada aqui, não resolvida:**
transformar SIROS em "um voo por data" (para eventualmente cruzar com
Básica/VRA) exigiria expandir cada linha em N linhas — uma por data
dentro da janela de validade que caia num dia da semana marcado. Essa
expansão é trabalho de transformação, não de ingestão simples raw→typed
— fica registrada como pergunta em aberto para quando `SPEC-010`
(ingestão SIROS) for desenhada, e para `DEC-008` herdar como caso
especial, não resolver agora.

**Ainda não confirmado**: se as colunas `Seg`...`Dom` marcam presença
(valor = número do dia quando opera, vazio/0 quando não) ou se sempre
trazem os sete números independente de operar todo dia — as duas
amostras inspecionadas mostram os sete dias preenchidos em sequência
(`1` a `7`), o que não permite distinguir as duas hipóteses.

## 7. Critérios de sucesso

- **C-01** — As 28 colunas do SIROS documentadas com nome proposto.
- **C-02** — Achado de granularidade (§6) registrado e citado por
  `DEC-008` quando ela for redigida.
- **C-03** *(provisório)* — Hipótese sobre o padrão `Seg`...`Dom` (marca
  presença vs. sempre preenchido) resolvida contra uma amostra maior —
  não fechada nesta versão.

## 8. Premissas e dependências

- Baseado num único arquivo (`registros_2022-08-10.csv`, 2 linhas de
  amostra) — estrutura e o achado da §6 podem não generalizar para todo o
  histórico do SIROS (2019-11-presente, `SPEC-002 §3.2`).
- `Arpt Origem`/`Arpt Destino`/`Codeshare` são texto livre — parsing
  estruturado não tentado nesta versão.

## 9. Não-objetivos

- Não é objetivo implementar a expansão autorização→voo-por-data nesta
  versão — só registrar que ela seria necessária.
- Não é objetivo confirmar o significado de `Seg`...`Dom` além do que a
  amostra permite — fica como hipótese até `SPEC-010` trabalhar com mais
  dado.

## 10. Regras checáveis (R-COL)

| ID | Regra | Onde verificar | Severidade |
|---|---|---|---|
| **R-COL-07** | As 28 colunas desta SPEC batem com o cabeçalho real (linha 2) de qualquer arquivo `data/anac/siros/*.csv` amostrado. | `head -2` do arquivo × §5 | Alta |
| **R-COL-08** | Nenhum documento futuro trata SIROS como "voo por data" sem citar explicitamente a transformação de expansão da §6. | Inspeção de `DEC-008`/`SPEC-010` | Média |

## 11. Limitações conhecidas

- Amostra pequena (uma data de referência, 2 linhas) — domínio completo de
  valores categóricos (`Situação SIROS`, `Tipo Serviço`, etc.) não
  levantado.
- `Cód Empresa`/`Cód Origem`/`Cód Destino` "parecem" ICAO pela forma, mas
  o nome da coluna não confirma isso — marcado `inferido`, não
  `confirmado`.

## 12. Critérios de revisão

Revisitar esta SPEC quando:

- `SPEC-010` (ingestão SIROS) precisar decidir a expansão
  autorização→voo-por-data — essa decisão nasce lá, mas revisita o
  achado §6 aqui.
- Uma amostra maior confirmar ou refutar a hipótese sobre `Seg`...`Dom`.
- Alguma pergunta de análise futura precisar especificamente de colunas
  do SIROS — nesse momento, um recorte "essencial" real (como o da
  Básica) passa a fazer sentido.

## 13. Histórico

| Data | Evento |
|---|---|
| 2026-08-31 | SPEC-007 v1 produzida em status `proposto`, levantamento grounded em `data/anac/siros/registros_2022-08-10.csv` real. 28 colunas documentadas. Achado estrutural: SIROS é autorização de slot (padrão semanal + janela de validade), não voo-por-data — registrado para `DEC-008` herdar. Aguardando aprovação do autor. |
| 2026-08-31 | **Aprovada.** Autor revisou o lote e aprovou explicitamente. |

---

*Fim do documento.*
