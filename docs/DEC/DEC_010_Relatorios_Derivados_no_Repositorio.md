---
documento: DEC-010
titulo: Relatórios derivados (IMRaD e Minto) versionados em relatorios/, fora da estrutura da SPEC-001 §5
versao: v1
status: proposto
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
└── report_microdados_v1/            uma pasta por versão do relatório
    ├── PROCEDENCIA_FIGURAS.md       procedência das figuras DESTA versão
    ├── gerador-imrad-microdados/    relatório IMRaD do deep dive GOL/Azul
    └── gerador-minto-microdados/    comunicado de decisão, derivado do anterior por poda
```

*(v2, 2026-09-05)* A camada de versão (`report_microdados_vN/`) foi
introduzida quando a segunda versão do relatório nasceu. Sem ela, uma versão
nova sobrescreveria a anterior ou obrigaria a renomear os dois geradores, e o
`.docx` publicado deixaria de ter uma origem identificável no repositório. O
`PROCEDENCIA_FIGURAS.md` desceu para dentro da versão pelo mesmo motivo que
os geradores são autocontidos (§5): quando as figuras de `v2` divergirem das
de `v1`, a tabela de procedência de cada uma tem que divergir junto.

Cada subdiretório carrega tudo o que precisa para rodar: `config.yml`,
`gerar_docx.py`, `modelo_de_escrita.docx`, `environment_report.yml`, o markdown de
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

- ~~Uma segunda análise produzir peças, e a estrutura de `relatorios/`
  precisar de subdivisão por tema em vez de por peça.~~ **Disparou em
  2026-09-05, com forma diferente da prevista:** a subdivisão que apareceu
  primeiro foi por *versão do mesmo relatório*, não por tema. A v1 previu a
  pressão certa e o eixo errado. Resolvido pela camada `report_microdados_vN/`
  do §2; subdivisão por tema continua em aberto, e cabe dentro da camada de
  versão se vier.
- O `.docx` gerado passar a ser distribuído fora do projeto, momento em que
  vale promovê-lo a `REP-002` com frontmatter, mantendo `relatorios/` como
  maquinaria.
- A duplicação de figuras passar de dezenas de MB, quando o custo de
  armazenamento supera o ganho de autocontenção. **No limiar em 2026-09-05:**
  10,4 MB de figura em `relatorios/` (82 arquivos, 2 versões), 21 MB de pasta
  total, contra 35,6 MB de original em `analise/` (272 arquivos). O custo
  agora é linear no número de versões, cerca de 11 MB por versão, não mais
  fixo. Reavaliar na v3, não antes: com duas versões o ganho de autocontenção
  ainda paga.

## 7. Histórico

| Data | Evento |
|---|---|
| 2026-09-04 | DEC-010 v1 redigida em status `proposto`, aguardando aprovação do autor. Cria `relatorios/` e traz as duas peças do deep dive GOL/Azul, mais o guia metodológico como `GUIDE-005`. Motivo imediato: os documentos viviam num repositório sem git. |
| 2026-09-05 | **v2, estrutura de `relatorios/` ganha camada de versão.** Os dois geradores desceram para `relatorios/report_microdados_v1/`, e `report_microdados_v2/` nasceu como cópia idêntica, a divergir a partir daqui (decisão do autor). `PROCEDENCIA_FIGURAS.md` desceu junto, um por versão, pelo mesmo princípio de autocontenção do §5. Movimentação feita com `mv` e registrada no git como 67 renomeações para `v1` (histórico preservado) mais 67 adições para `v2`. §2 e §6 atualizados; citações corrigidas em `README.md`, `GUIDE-005` e `INDEX_DEC`. **Verificado antes e depois:** os 67 arquivos batem byte a byte com o `HEAD`, e o teste de procedência do `PROCEDENCIA_FIGURAS.md` devolve o estado documentado (25 Classe A idênticas às originais de `analise/`, 16 Classe B sem original no repositório). Nenhum arquivo perdido, nenhuma figura alterada. |
| 2026-09-11 | **`environment.yml` renomeado para `environment_report.yml`** nos quatro geradores (`git mv`, histórico preservado), a pedido do autor. Motivo: o nome genérico colidia com o `environment_gov-sermi-perf.yml` da raiz, e os quatro arquivos declaravam `name: gov-sermi-perf`, o ambiente compartilhado do autor. Dois arquivos declarando o mesmo ambiente com conteúdos diferentes é defeito: quem rodasse `conda env create` a partir do gerador criaria um `gov-sermi-perf` com três pacotes, no lugar do ambiente completo. O ambiente dos geradores passa a se chamar `report-docx`, com as suas três dependências (`python-docx`, `pillow`, `pyyaml`), o que é a autocontenção do §5 aplicada ao ambiente e não só aos arquivos. Citações atualizadas nos dois `README.md` de minto e no §2 desta DEC. Decisão de ambiente do repositório: `DEC-011 §2.2`. |

---

*Fim do documento.*
