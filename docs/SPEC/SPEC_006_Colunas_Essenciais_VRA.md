---
documento: SPEC-006
titulo: Colunas Essenciais — VRA
versao: v1
status: aprovado
data: 2026-08-31
autor: Bruno Alexandre Serminaro
referencia: DEC-007
escopo: projeto
---

# SPEC-006 · Colunas Essenciais — VRA

> Levantamento das colunas do dataset VRA, a partir de arquivo real já
> baixado (`data/anac/vra/VRA_20247.csv`) — não de documentação externa.
> Ao contrário da Básica (`SPEC-005`, 112 colunas, 29 essenciais), o VRA
> bruto já é compacto: 12 colunas, todas potencialmente relevantes. Insumo
> direto para a `DEC-008` (arquitetura de ingestão) e para desbloquear a
> pergunta 6 (block time) da `DEC-007 §2.g`.

---

## 1. Propósito

Documentar a estrutura real do VRA antes de desenhar sua ingestão
(`SPEC-009`, futura), e confirmar ou refutar a hipótese de chave de
junção com a Básica que a `DEC-007 §2.g` registrou sem dado real para
verificar.

## 2. Audiência

Reaproveita os papéis abstratos do `SPEC-002 §2` — nenhum papel novo.

## 3. Escopo

### 3.1 O que este SPEC entrega

1. Dicionário das 12 colunas brutas do VRA (§5).
2. Nome proposto de coluna, seguindo a convenção de prefixo já usada na
   Básica (`SG_`/`NR_`/`DT_`/`CD_`/`DS_`) — proposto, não implementado.
3. Confirmação (ou refutação) da hipótese de chave de junção Básica × VRA
   da `DEC-007 §2.g`.

### 3.2 Fora de escopo

- Ingestão real (DDL, scripts) — fica para `SPEC-009`.
- Confirmação contra o layout oficial do VRA publicado pela ANAC — este
  levantamento é sobre o arquivo real baixado, não sobre documentação
  externa.
- Colunas de metadado do arquivo (linha "Atualizado em: ..." no topo do
  CSV) — não é dado de voo, é cabeçalho de publicação.

## 4. Método

Inspeção direta de `data/anac/vra/VRA_20247.csv`: a linha 1 do arquivo é
metadado de publicação (`"Atualizado em: 2026-08-03"`), a linha 2 é o
cabeçalho real, delimitador `;`, valores entre aspas. Amostra de 2 linhas
de dado inspecionada para inferir tipo e formato.

## 5. Dicionário de colunas (VRA bruto)

| Coluna bruta (CSV ANAC) | Nome proposto | Tipo inferido | Confiança | Comentário |
|---|---|---|---|---|
| `ICAO Empresa Aérea` | `SG_EMPRESA_ICAO` | TEXT | alta confiança | Código ICAO, mesma convenção da Básica (ex.: `SKU`) |
| `Número Voo` | `NR_VOO` | TEXT | alta confiança | Número comercial do voo |
| `Código Autorização (DI)` | `CD_AUTORIZACAO_DI` | TEXT | incerto | Sigla "DI" não confirmada (mesma incerteza já registrada para `ID_DI` na Básica, `SPEC-005`); valor observado na amostra: `"0"` |
| `Código Tipo Linha` | `CD_TIPO_LINHA` | TEXT | inferido (padrão de nome) | Valor observado `"I"` na amostra — provavelmente Internacional/Doméstica, categorias exatas não confirmadas |
| `ICAO Aeródromo Origem` | `SG_ICAO_ORIGEM` | TEXT | alta confiança | Mesmo domínio de valores da Básica (ex.: `SBFL`) |
| `ICAO Aeródromo Destino` | `SG_ICAO_DESTINO` | TEXT | alta confiança | Idem |
| `Partida Prevista` | `DT_HR_PARTIDA_PREVISTA` | TIMESTAMP | confirmado | **Coluna que a Básica não tem** — resolve o bloqueio da pergunta 6 (`DEC-007 §2.g`). Formato `AAAA-MM-DD HH:MM:SS` observado, campo único (não separado em data/hora como na Básica) |
| `Partida Real` | `DT_HR_PARTIDA_REAL` | TIMESTAMP | confirmado | Idem formato; equivalente a `DT_PARTIDA_REAL`+`HR_PARTIDA_REAL` da Básica combinados num só campo |
| `Chegada Prevista` | `DT_HR_CHEGADA_PREVISTA` | TIMESTAMP | confirmado | Idem |
| `Chegada Real` | `DT_HR_CHEGADA_REAL` | TIMESTAMP | confirmado | Idem |
| `Situação Voo` | `DS_SITUACAO_VOO` | TEXT | inferido (padrão de nome) | Valor observado `"REALIZADO"` — outros valores possíveis (cancelado, etc.) não confirmados nesta amostra |
| `Código Justificativa` | `CD_JUSTIFICATIVA` | TEXT | incerto | Valor observado `"N/A"` — provável motivo de atraso/cancelamento quando aplicável, domínio de valores não levantado |

Todas as 12 colunas ficam marcadas **essenciais** por ora — o dataset
bruto já é compacto o bastante para não precisar de recorte, diferente da
Básica (`SPEC-005`).

## 6. Hipótese de chave de junção Básica × VRA (confirma `DEC-007 §2.g`)

Com as colunas reais em mãos, a chave proposta pela `DEC-007 §2.g`
(empresa + voo + data + origem) é **viável, ainda não testada**:

| Básica (`SPEC-005`) | VRA (esta SPEC) |
|---|---|
| `SG_EMPRESA_ICAO` | `SG_EMPRESA_ICAO` |
| `NR_VOO` | `NR_VOO` |
| `DT_PARTIDA_REAL` + `HR_PARTIDA_REAL` | `DT_HR_PARTIDA_REAL` (campo único, precisa separar data de hora para comparar) |
| `SG_ICAO_ORIGEM` | `SG_ICAO_ORIGEM` |

**Continua hipótese**, não achado: nomes e tipos batem na estrutura, mas
nenhum `JOIN` real foi executado ainda — cardinalidade, duplicidade de
`NR_VOO` por dia, ou pequenas divergências de horário entre as duas fontes
podem quebrar a chave na prática.

## 7. Critérios de sucesso

- **C-01** — As 12 colunas do VRA documentadas e com nome proposto de
  destino.
- **C-02** *(provisório)* — `JOIN` real entre uma amostra de Básica e VRA
  pela chave da §6 executado, com taxa de correspondência medida —
  transforma a hipótese em achado. Depende de `SPEC-009` (ingestão) para
  ter os dois lados carregados.

## 8. Premissas e dependências

- Baseado num único arquivo mensal (`VRA_20247.csv`) — estrutura pode
  variar entre meses/anos, não testado.
- `Partida Real`/`Chegada Real` do VRA podem divergir ligeiramente da
  Básica (fontes de apuração diferentes dentro da ANAC) — não testado.

## 9. Não-objetivos

- Não é objetivo implementar a ingestão nesta versão — `SPEC-009`.
- Não é objetivo confirmar o domínio completo de valores de `DS_SITUACAO_VOO`/`CD_JUSTIFICATIVA` — fica para quando a ingestão real expuser mais dado.

## 10. Regras checáveis (R-COL)

| ID | Regra | Onde verificar | Severidade |
|---|---|---|---|
| **R-COL-05** | As 12 colunas desta SPEC batem com o cabeçalho real (linha 2) de qualquer arquivo `data/anac/vra/*.csv` amostrado. | `head -2` do arquivo × §5 | Alta |
| **R-COL-06** | A chave de junção da §6 não é tratada como confirmada em nenhum documento até `C-02` (§7) ser fechado com `JOIN` real executado. | Inspeção de DEC/SPEC futuras que citem esta chave | Média |

## 11. Limitações conhecidas

- Amostra de uma linha de metadado + 2 linhas de dado — suficiente para
  estrutura, não para domínio completo de valores categóricos.
- Nomes propostos (§5) não são os nomes finais necessariamente — ficam
  sujeitos a ajuste quando `SPEC-009` desenhar o DDL real.

## 12. Critérios de revisão

Revisitar esta SPEC quando:

- `SPEC-009` (ingestão VRA) implementar o DDL real e os nomes propostos
  precisarem de ajuste.
- O `JOIN` real (C-02) revelar que a chave da §6 não é confiável — nesse
  caso, também revisitar `DEC-007 §2.g`.
- Outro arquivo mensal de VRA revelar coluna adicional ou divergência de
  formato frente a `VRA_20247.csv`.

## 13. Histórico

| Data | Evento |
|---|---|
| 2026-08-31 | SPEC-006 v1 produzida em status `proposto`, levantamento grounded em `data/anac/vra/VRA_20247.csv` real. 12 colunas documentadas, todas essenciais. Confirma estruturalmente (não empiricamente) a hipótese de chave de junção da `DEC-007 §2.g`. Aguardando aprovação do autor. |
| 2026-08-31 | **Aprovada.** Autor revisou o lote e aprovou explicitamente. |

---

*Fim do documento.*
