# Blueprints da fundação

Os sete JSON desta pasta descrevem **como cada peça da fundação de sete
peças devia ser construída**: seções obrigatórias, subtópicos, mínimos e
critérios auditáveis (campo `checar`). São a instância deste projeto,
derivada da `SPEC-META-001` (taxonomia) e da `DEC-META-002 §2.1` (conteúdo
das peças), não uma cópia genérica: cada arquivo nomeia a peça, sua posição
na ordem de produção, de quem depende e o que alimenta.

São 74 critérios `checar` no total.

| Blueprint | Peça | Seções | Critérios | Citado por |
|---|---|---|---|---|
| `DEC_001.json` | DEC-001 | 7 | 9 | `DEC-001 §6` |
| `SPEC_001.json` | SPEC-001 | 10 | 13 | — |
| `REP_001.json` | REP-001 | 8 | 9 | — |
| `DEC_002.json` | DEC-002 | 7 | 8 | `DEC-002 §6` |
| `SPEC_002.json` | SPEC-002 | 11 | 12 | — |
| `DEC_003.json` | DEC-003 | 7 | 9 | `DEC-003 §6` |
| `SPEC_003.json` | SPEC-003 | 12 | 14 | — |

A ordem da tabela é a ordem de produção decisão-primeiro fixada pela
`DEC-META-014`, não a alfabética.

Quatro deles não são citados por nenhuma peça. Isso não os torna
dispensáveis: são o contrato contra o qual `SPEC-001`, `REP-001`,
`SPEC-002` e `SPEC-003` foram validadas, e o que permite revalidá-las. A
ausência de citação diz que ninguém precisou apontar para eles no corpo do
texto, não que não foram usados.

## Por que ficam aqui

Viviam em `rascunho/contexto/blueprints/`, pasta que o `.gitignore` declara
descartável, embora os arquivos estivessem versionados e três peças
aprovadas os citassem. `SPEC-001 §5` já reservava `docs/assets/` para
"ativo a versionar", que é exatamente o que eles são: material legível por
máquina, de apoio à documentação, sem frontmatter e sem numeração
`TIPO_NNN`.

Não são peça SERMI. Não têm `status`, não entram nas regras `R-TAX-NN` e
não precisam de DEC para mudar.

## Duas referências mortas, deixadas de propósito

`DEC_001.json` declara `depende_de: ["rascunho/CONTEXTO_DO_PROJETO ou
contexto/", "rascunho/MEMORIA.txt"]`, e `REP_001.json` cita `MEMORIA.txt`.
Os três arquivos foram removidos do repositório em 2026-09-06, depois que
seu conteúdo essencial foi absorvido pelas peças (`DEC-001 §3` e `§5.2`,
`REP-001 §4`, `§6` e `§8.1`).

Os JSON **não foram editados**. Um blueprint é o contrato como foi escrito
na época; reescrevê-lo para esconder que uma dependência mudou de lugar
falsearia o registro. Quem for revalidar `DEC-001` ou `REP-001` contra o
blueprint deve ler essas duas entradas como "o insumo que hoje está dentro
da própria peça".

## O que não veio junto

A pasta antiga tinha `pesquisa/` e `relatorios/`, previstas para receber
material bruto de pesquisa. As duas ficaram vazias da criação até serem
removidas em 2026-09-06: o material que elas descreviam acabou entrando
direto nas peças. Foram removidas em vez de mantidas com `.gitkeep`, para
o repositório não declarar uma estrutura que nunca foi usada.
