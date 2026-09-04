---
documento: DEC-010
titulo: Relatórios derivados (IMRaD e Minto) versionados em relatorios/, fora da estrutura da SPEC-001 §5
versao: v1
status: aprovado
data: 2026-09-04
autor: Bruno Alexandre Serminaro
referencia: DEC-001, SPEC-001, SPEC-004, SPEC-017, GUIDE-005
escopo: projeto
---

# DEC-010 · Relatórios derivados em `relatorios/`

> Formaliza uma pasta nova na raiz do repositório. `SPEC-001 §5` fixa a
> estrutura documental (`docs/` por tipo) e delega `scripts/`, `src/`, `sql/`,
> `notebook/` e `r/` à convenção de código do `DEC-001 §6.6`. Os geradores de
> relatório não são nem uma coisa nem outra, e sem esta DEC seriam um
> diretório órfão para a próxima auditoria.

---

## 1. Contexto

A análise do deep dive GOL/Azul produziu, além das SPECs de linha, dois
documentos para leitura humana: um relatório em estrutura IMRaD, para quem
audita o método, e um comunicado em Pirâmide de Minto, para quem decide. Os
dois são gerados por script a partir de markdown e de figuras, e nasceram em
`learn-imrad-mintos`, repositório de estudo **sem git**.

Isso criava dois problemas. O primeiro é de preservação: documentos escritos à
mão, não regeneráveis, sem histórico nenhum. O segundo é de rastro: as peças
citam achados que vivem nas SPECs deste repositório, e a distância entre os
dois lados tornava a verificação manual.

A estrutura de pastas da `SPEC-001 §5` não previa esse tipo de ativo. Ela
separa documentação de governança (`docs/`, por tipo) de código e dado
(`scripts/`, `src/`, `sql/`, `notebook/`, `r/`). Um gerador de relatório é
código que produz documento, e cabe mal nas duas prateleiras.

## 2. Decisão

Criar `relatorios/` na raiz, contendo um subdiretório autocontido por peça
gerada:

```
relatorios/
├── gerador-imrad-microdados/    relatório IMRaD do deep dive GOL/Azul
└── gerador-minto-microdados/    comunicado de decisão, derivado do anterior por poda
```

Cada subdiretório carrega tudo o que precisa para rodar: `config.yml`,
`gerar_docx.py`, `modelo_de_escrita.docx`, `environment.yml`, o markdown de
cada seção, as figuras e a pasta `saida/`. Nenhum depende de arquivo fora de
si, salvo as referências textuais de procedência, que apontam para `docs/` e
`analise/` deste repositório.

`relatorios/` **não é peça SERMI**. Os arquivos lá dentro não têm frontmatter,
não recebem numeração `TIPO_NNN` e não entram nas regras `R-TAX-NN` da
`SPEC-001`. Governa-os a convenção de código do `DEC-001 §6.6`, como
`scripts/` e `src/`.

O guia de escrita das duas peças, esse sim, vira peça SERMI: `GUIDE-005`,
trazido do repositório de origem.

## 3. Origem ou rastro

- Peças copiadas de `learn-imrad-mintos/gerador-imrad-microdados` e
  `learn-imrad-mintos/gerador-minto-microdados` em 2026-09-04. As cópias de
  origem seguem lá, intactas; esta passa a ser a versão canônica.
- Guia metodológico copiado de `learn-imrad-mintos/docs/guia-metodologico.md`
  para `docs/GUIDE/GUIDE_005_Metodologia_IMRaD_e_Piramide_de_Minto.md`, com o
  texto das §1 a §5 inalterado.
- Achados reportados nas peças: `SPEC-013`, `SPEC-015`, `SPEC-016`, `SPEC-017`.
- Perguntas de análise que as peças respondem: `SPEC-004`, `DEC-007`.

## 4. Alternativas consideradas

| Alternativa | Por que não |
|---|---|
| Pôr as peças em `docs/REP/` como REP-002 | `docs/REP/` é para peça SERMI com frontmatter e numeração. Uma pasta de gerador com 41 figuras e um script Python não é isso. Cabe rever depois: o `.docx` produzido pode virar REP-002, com `relatorios/` continuando a ser a maquinaria que o gera. |
| Pôr em `notebook/` ou `src/` | Esconde documento dentro de código. Quem procura o relatório não procura em `src/`. |
| Deixar em `learn-imrad-mintos` e referenciar de longe | Mantém os documentos sem versionamento nenhum, que é o problema que motivou a mudança. |
| Não criar pasta e deixar cada gerador solto na raiz | Duas pastas hoje, e a próxima análise traz mais. `relatorios/` é o guarda-chuva que evita a proliferação. |

## 5. Consequências

**Ganhos.** Os documentos passam a ter histórico e a poder ser desfeitos. As
citações de achado ficam a uma distância verificável da SPEC que as sustenta.
As figuras das peças podem ser conferidas contra as originais de `analise/`
por `md5sum`, e a tabela de correspondência no README de cada gerador declara
o par.

**Custos.** As figuras das peças são cópias das de `analise/`, e passam a
existir duas vezes no mesmo repositório, cerca de 15MB. A duplicação é
deliberada: um gerador que apontasse para `../../analise/` deixaria de ser
autocontido e quebraria ao ser copiado para outro lugar. A tabela de
correspondência é o que impede que as duas versões divirjam em silêncio.

**Ambiente.** Os geradores declaram o ambiente conda `gov-sermi-perf`
(`python-docx`, `pyyaml`, `pillow`), diferente do `pesquisa-azul` usado pela
linha de análise (`SPEC-002 §6`). São dois ambientes no mesmo repositório, por
propósito diferente: um produz documento, o outro roda análise. Não se
misturam e não precisam ser unificados.

**Para a auditoria.** `relatorios/` deve ser lida como código, não como
documentação. Um `gov-check` que a trate como peça SERMI vai reportar falso
positivo.

## 6. Critérios de reavaliação

Revisitar esta DEC quando:

- Uma segunda análise produzir peças, e a estrutura de `relatorios/` precisar
  de subdivisão por tema em vez de por peça.
- O `.docx` gerado passar a ser distribuído fora do projeto, momento em que
  vale promovê-lo a `REP-002` com frontmatter, mantendo `relatorios/` como
  maquinaria.
- A duplicação de figuras passar de dezenas de MB, quando o custo de
  armazenamento supera o ganho de autocontenção.

## 7. Histórico

| Data | Evento |
|---|---|
| 2026-09-04 | DEC-010 v1, `aprovado`. Cria `relatorios/` e traz as duas peças do deep dive GOL/Azul, mais o guia metodológico como `GUIDE-005`. Motivo imediato: os documentos viviam num repositório sem git. |

---

*Fim do documento.*
