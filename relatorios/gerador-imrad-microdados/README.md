# Deep Dive GOL nos microdados da ANAC (relatório IMRaD)

Instância do `gerador_imrad` para uma análise específica: a operação da GOL nos microdados públicos da ANAC, 2021 a 2026, com a Azul como contraponto. O gerador genérico em `gerador_imrad`, em `learn-imrad-mintos`, é o template de onde esta pasta nasceu; aqui ela vive com o conteúdo preenchido.

Saída: `saida/deep_dive_gol_imrad.docx`.

## De onde vem cada parte

| Frente | Perguntas cobertas | Origem |
|---|---|---|
| Manual | Destinos e malha, distribuição da frota | `Deep_Dive_Gol_ANAC_1a_bloco.docx` (texto e figuras do autor, em `learn-imrad-mintos`, fora deste repositório) |
| Reprodutível | Tempo de solo, hub e off-hub, etapa média, block time | `learn-microdados_anac_dados`: SPEC-013 (etapa média), SPEC-015 (block time), SPEC-016 (tempo de solo), DEC-007 (arquitetura das perguntas) e as figuras de `analise/a3`, `a4` e `a5` |

As duas frentes usam a mesma fonte pública e a mesma janela, mas não o mesmo critério de limpeza. A divergência está declarada na seção Métodos (premissa 4 e Limitações), não escondida.

## Peça de decisão

Este documento é a peça de trabalho. A peça de decisão, em Pirâmide de Minto, responde às mesmas perguntas em outra densidade e vive em `../gerador-minto-microdados`. Ela deriva deste relatório por poda, e a metodologia das duas está em `../../docs/GUIDE/GUIDE_005_Metodologia_IMRaD_e_Piramide_de_Minto.md`.

## Figuras

As figuras já estão nas pastas `figuras/` de cada seção, com nome descritivo e prefixo que indica onde entram (`met_` em Métodos, `res_` em Resultados). Origem de cada uma:

- Destinos e frota: extraídas de `Deep_Dive_Gol_ANAC_1a_bloco.docx`.
- Tempo de solo: `analise/a3_tempo_de_solo/a3_figuras_gol` e `a3_figuras_versus`, mais três figuras do docx.
- Etapa média: `analise/a4_etapa_media/a4_figuras_gol` e `a4_figuras_versus`.
- Block time: `analise/a5_block_time/a5_figuras_gol` e `a5_figuras_versus`.

A correspondência figura a figura, verificada por `md5sum`, está em `../PROCEDENCIA_FIGURAS.md`, junto com o comando para refazer a verificação. Na conferência de 2026-09-04, 17 das 41 figuras dos dois geradores são idênticas às de `analise/`, 16 vêm do documento manual do autor e não têm original neste repositório, e 8 divergem e precisam ser reconciliadas.

As duas tabelas que no docx eram imagens EMF (destinos por ano, bases cíclicas) foram transcritas como tabelas de verdade no markdown de Resultados. A tabela de tempo de solo por hub também.

## Gerar o documento

```bash
conda activate gov-sermi-perf
python gerar_docx.py
```

## Convenções do markdown

Mesmas do `README do template, em `learn-imrad-mintos/gerador_imrad`. Duas limitações apareceram durante a escrita deste documento e foram corrigidas no gerador, não contornadas no texto: lista numerada agora continua através de linhas em branco e de comentários, e trecho entre crases vira monoespaçado em vez de sair literal.
