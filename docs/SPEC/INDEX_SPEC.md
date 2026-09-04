# Índice de SPECs — learn-microdados_anac_dados

Registro de todas as SPECs do projeto. Numeração local, sequencial,
**nunca reutilizada**. Convenção e estrutura em `SPEC-001 §4` (deste
projeto). Criado ao cruzar o limiar de ~10 documentos que a própria
`SPEC-001 §5` sinalizava como gatilho para este índice existir
(2026-08-31, na aprovação da `SPEC-005`–`SPEC-010`).

## SPECs de fundação (status `aprovado`)

| Nº | Título | Data | Descrição curta |
|---|---|---|---|
| [SPEC-001](SPEC_001_Taxonomia_Documental.md) | Taxonomia Documental do Projeto | 2026-08-24 | Define os seis tipos de documento SERMI, frontmatter, convenção de nomes/pastas, dez regras `R-TAX-NN`. |
| [SPEC-002](SPEC_002_Descricao_do_Projeto.md) | Descrição do Projeto | 2026-08-24 | Propósito, audiência, escopo (3 datasets, 2 caminhos, corte 2010), decomposição, critérios de sucesso, oito regras `R-FUN-NN`. |
| [SPEC-003](SPEC_003_Contrato_de_Responsabilidade.md) | Contrato de Responsabilidade | 2026-08-24 | Atribuição papel-pessoa, fluxo de aprovação, fronteiras de autonomia, sete regras `R-CON-NN`. Ainda em `proposto`. |

## SPECs de conteúdo (status `aprovado`)

| Nº | Título | Data | Descrição curta |
|---|---|---|---|
| [SPEC-004](SPEC_004_Perguntas_de_Analise_Deep_Dive_Gol_Azul.md) | Perguntas de Análise — Deep Dive GOL e Azul | 2026-08-31 | Seis perguntas de análise, genéricas e dual-path (Snowflake, SQLite+Python); perguntas 3-4 detalhadas por completo com SQL de referência. Primeira SPEC de conteúdo do projeto. Seis regras `R-ANL-NN`. |
| [SPEC-005](SPEC_005_Dicionario_de_Colunas_Basica.md) | Dicionário de Colunas — Básica | 2026-08-31 | Documenta as 112 colunas de `BASICA_RAW`, 29 marcadas essenciais; consolida `QUERY-011.csv`, `colunas.txt` e supera `dicionario_colunas_basica.md`. |
| [SPEC-006](SPEC_006_Colunas_Essenciais_VRA.md) | Colunas Essenciais — VRA | 2026-08-31 | Levantamento das 12 colunas do VRA, grounded em arquivo real; confirma estruturalmente a hipótese de chave de junção com a Básica (`DEC-007 §2.g`). |
| [SPEC-007](SPEC_007_Colunas_Essenciais_SIROS.md) | Colunas Essenciais — SIROS | 2026-08-31 | Levantamento das 28 colunas do SIROS, grounded em arquivo real; achado de que é registro de autorização de slot, não voo-por-data. |
| [SPEC-008](SPEC_008_Ingestao_SQLite_Basica.md) | Ingestão SQLite — Básica | 2026-08-31 | Retroativa: documenta o pipeline de ingestão da Básica já implementado (raw → silver, 112 colunas). |
| [SPEC-009](SPEC_009_Ingestao_SQLite_VRA.md) | Ingestão SQLite — VRA | 2026-08-31 | Implementada: `vra_raw`/`vra_silver` carregados (17.459.155 linhas, 2010-2026); dois achados de qualidade de dado (formato de data, corrupção BlobColumn) documentados e tratados. |
| [SPEC-010](SPEC_010_Ingestao_SQLite_SIROS.md) | Ingestão SQLite — SIROS | 2026-08-31 | `siros_raw`/`siros_silver` implementados (10.677.382 linhas); achado de formato duplo de data (`dt_registro`, análogo ao VRA, direção oposta) tratado antes de materializar. Expansão autorização→voo-por-data fora de escopo. |
| [SPEC-011](SPEC_011_Dimensao_Aerodromo.md) | Dimensão de Aeródromo — Localização e Fuso Horário | 2026-08-31 | Retroativa: documenta `dim_airport_location_time_zone` (858 aeródromos, sem colunas de horário de verão), carregada em `anac_basica.sqlite`. Materializa `DEC-009`. |

## SPECs de conteúdo (status `proposto`)

| Nº | Título | Data | Descrição curta |
|---|---|---|---|
| [SPEC-012](SPEC_012_Curated_Deep_Gol_Azul.md) | Curated Deep — Recorte GOL/Azul para Deep Dive | 2026-08-31 | Retroativa (v2): `basica_curated_deep`, `vra_curated_deep` e `fato_rotacao_aeronave_gol_azul` (rotação por matrícula, validação temporal e geodésica via `dim_airport`); refuta premissa de fuso local e isola erro real de `km_distancia` (par `KMCN`/`KGUS`). |
| [SPEC-013](SPEC_013_Analise_Etapa_Media_Gol_Azul.md) | Análise Exploratória — Etapa Média GOL/Azul | 2026-09-04 | Documento vivo, cresce por rodada. GOL (rodadas 1-8): sazonalidade recorrente da duração média, ordenação estável de frota, achado de B737 quase saindo do internacional em 2026, bases do nordeste puxando duração sem puxar volume. Azul + comparação + notebook didático (v9): replicação confirmatória, autocorrelação diária maior na Azul, 21 gráficos de comparação. |
| [SPEC-014](SPEC_014_Block_Time_Gol_Azul.md) | Block Time GOL/Azul — Sobra e Falta de Tempo | 2026-09-01 | Destrava a pergunta 6 do SPEC-004: `fato_block_time_gol_azul`, chave de junção medida (96,96% correspondência), achado de que o "real" do VRA ≈ tempo no ar da Básica (não é bloco porta-a-porta), 32,8% das etapas com falta de tempo programado. |
| [SPEC-015](SPEC_015_Analise_Block_Time_Gol_Azul.md) | Análise Exploratória — Block Time GOL/Azul (Folga e Atrasos) | 2026-09-03 | Documento vivo, cresce por rodada. Rodada 1 (GOL+Azul+versus): bug de filtro PASSAGEIRO não herdado, garbage de timestamp em atraso, VRA atrasado um mês (janela ajustada), atraso de partida/chegada quase redundantes (métrica nova "Δ atraso em voo"), viés de match VRA cresce a partir de 2024 em GOL **e** Azul (refuta hipótese GOL-específica), corte fixo ±60min substituindo cerca de Tukey. |
| [SPEC-016](SPEC_016_Analise_Tempo_de_Solo_Gol_Azul.md) | Análise Exploratória — Tempo de Solo GOL/Azul (Turnaround) | 2026-09-04 | Documento vivo, retroativo (linha de análise já concluída sem registro). Cauda longa até o teto de validade de 72h (pernoite legítimo lido como outlier por Tukey), autocorrelação diária maior na Azul, corte único `CORTE_HORAS=3h` generalizado para os 12 gráficos de comparação. |
| [SPEC-017](SPEC_017_Autocorrelacao_como_Indicador_Operacional.md) | Autocorrelação como Indicador Operacional — GOL/Azul | 2026-09-04 | Documento vivo, sem medição nova: relê o achado de autocorrelação de `SPEC-013 §6.8`/`SPEC-016 §6.2`, que parecia contradizer a leitura de operação homogênea. Separa amplitude, periodicidade e memória; converte `r` em meia-vida de distúrbio e tamanho de amostra efetivo; nomeia três fatores de confusão mecânicos com teste especificado; especifica autocorrelação **por base** como diagnóstico de restrição de capacidade nos sete hubs da GOL. Nove extensões de pesquisa em anexo. |

## SPECs superseded

| Nº | Título | Substituída por |
|---|---|---|
| — | — | `docs/dicionario_colunas_basica.md` e `rascunho/colunas.txt` não são SPECs numeradas, mas ficam superados por `SPEC-005` a partir da aprovação dela. |

---

*Fim do documento.*
