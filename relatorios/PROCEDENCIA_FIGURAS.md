# Procedência das figuras de `relatorios/`

As figuras usadas pelo relatório IMRaD e pelo comunicado Minto são cópias,
não referências: cada gerador precisa ser autocontido (`DEC-010 §5`). Este
documento é o que impede que as cópias divirjam em silêncio das originais.

## Método de verificação

```bash
# da raiz do repositório
python3 - <<'EOF'
import hashlib, pathlib, collections
md5 = lambda p: hashlib.md5(p.read_bytes()).hexdigest()
orig = collections.defaultdict(list)
for p in pathlib.Path('analise').rglob('*.png'): orig[md5(p)].append(str(p))
for p in sorted(pathlib.Path('relatorios').rglob('*.png')):
    print(('OK  ' if md5(p) in orig else 'DIFF'), p)
EOF
```

Resultado em 2026-09-04: **17 idênticas byte a byte**, **16 sem original neste repositório** (vêm do documento manual do autor) e **8 divergentes** (o gráfico existe em `analise/` sob outro nome, mas em versão diferente).

## Classe A — idênticas ao original (verificado por md5)

| Figura em `relatorios/` | Original em `analise/` |
|---|---|
| `imrad-microdados · 03-resultados · res_12_tempo_solo_forma_distribuicao_gol.png` | `a3_tempo_de_solo/a3_figuras_gol/dist_01_frequencia_densidade_boxplot_tempo_solo.png` |
| `imrad-microdados · 03-resultados · res_13_tempo_solo_violin_por_modelo_gol.png` | `a3_tempo_de_solo/a3_figuras_gol/dist_02_violin_tempo_solo_por_modelo.png` |
| `imrad-microdados · 03-resultados · res_16_tempo_solo_violin_por_modelo_gol_azul.png` | `a3_tempo_de_solo/a3_figuras_versus/v05_violin_por_modelo.png` |
| `imrad-microdados · 03-resultados · res_17_tempo_solo_lag_plot_gol_azul.png` | `a3_tempo_de_solo/a3_figuras_versus/v12_lag_plot.png` |
| `imrad-microdados · 03-resultados · res_18_etapa_media_forma_distribuicao_gol.png` | `a4_etapa_media/a4_figuras_gol/dist_01_frequencia_densidade_boxplot_etapa_media.png` |
| `imrad-microdados · 03-resultados · res_19_etapa_media_violin_por_modelo_gol.png` | `a4_etapa_media/a4_figuras_gol/dist_02_violin_etapa_media_por_modelo.png` |
| `imrad-microdados · 03-resultados · res_20_etapa_media_mensal_gol.png` | `a4_etapa_media/a4_figuras_gol/duracao_media_mensal_full_2021_2026.png` |
| `imrad-microdados · 03-resultados · res_21_etapa_media_mensal_por_frota_gol.png` | `a4_etapa_media/a4_figuras_gol/duracao_media_mensal_por_frota_full_2021_2026.png` |
| `imrad-microdados · 03-resultados · res_24_etapa_media_violin_por_modelo_gol_azul.png` | `a4_etapa_media/a4_figuras_versus/v05_violin_por_modelo.png` |
| `imrad-microdados · 03-resultados · res_25_etapa_media_mensal_gol_azul.png` | `a4_etapa_media/a4_figuras_versus/v01_duracao_media_mensal.png` |
| `imrad-microdados · 03-resultados · res_26_folga_forma_distribuicao_gol.png` | `a5_block_time/a5_figuras_gol/cerca_dist_01_frequencia_densidade_boxplot_folga.png` |
| `imrad-microdados · 03-resultados · res_27_folga_por_modelo_gol.png` | `a5_block_time/a5_figuras_gol/cerca_dist_08_folga_por_modelo.png` |
| `imrad-microdados · 03-resultados · res_29_atraso_recuperado_em_voo_gol.png` | `a5_block_time/a5_figuras_gol/cerca_dist_14_atraso_recuperado_em_voo.png` |
| `imrad-microdados · 03-resultados · res_30_folga_forma_gol_azul.png` | `a5_block_time/a5_figuras_versus/v02_folga_distribuicao_forma.png` |
| `imrad-microdados · 03-resultados · res_32_atraso_recuperado_em_voo_gol_azul.png` | `a5_block_time/a5_figuras_versus/v10_atraso_recuperado_em_voo.png` |
| `minto-microdados · 02-porques · p2b_etapa_media_por_modelo.png` | `a4_etapa_media/a4_figuras_gol/duracao_media_mensal_por_frota_full_2021_2026.png` |
| `minto-microdados · 02-porques · p3_tempo_solo_lag_plot.png` | `a3_tempo_de_solo/a3_figuras_versus/v12_lag_plot.png` |

## Classe B — sem original neste repositório

Extraídas de `Deep_Dive_Gol_ANAC_1a_bloco.docx`, o documento que o autor
escreveu à mão, que vive em `learn-imrad-mintos` e não é versionado. Cobrem
destinos, malha e frota, além das três figuras de tempo de solo com sufixo
`_docx` no nome. Não há o que reconciliar: a origem é externa.

- `imrad-microdados · 02-metodos · met_01_pareto_chegadas_por_base_hub_offhub.png`
- `imrad-microdados · 02-metodos · met_02_distribuicao_tempo_solo_corte_iqr.png`
- `imrad-microdados · 02-metodos · met_03_vies_match_vra_gol.png`
- `imrad-microdados · 03-resultados · res_01a_periodos_tipicos_destinos_gol.png`
- `imrad-microdados · 03-resultados · res_01b_periodos_tipicos_destinos_azul.png`
- `imrad-microdados · 03-resultados · res_02_destinos_media_semanal_por_ano.png`
- `imrad-microdados · 03-resultados · res_03_frequencia_periodos_destinos_gol.png`
- `imrad-microdados · 03-resultados · res_04_bases_ciclicas_destinos.png`
- `imrad-microdados · 03-resultados · res_05_distribuicao_modelos_frota_por_ano.png`
- `imrad-microdados · 03-resultados · res_06_primeira_aparicao_matricula_por_modelo.png`
- `imrad-microdados · 03-resultados · res_07_histograma_idade_em_servico.png`
- `imrad-microdados · 03-resultados · res_08_boxplot_idade_servico_por_modelo.png`
- `imrad-microdados · 03-resultados · res_09_tempo_solo_boxplot_por_modelo_docx.png`
- `imrad-microdados · 03-resultados · res_10_tempo_solo_quartis_por_modelo_docx.png`
- `imrad-microdados · 03-resultados · res_11_tempo_solo_medio_top_hubs_docx.png`
- `minto-microdados · 01-recomendacao · rec_tempo_solo_medio_top_hubs.png`

## Classe C — divergentes, a reconciliar

O mesmo gráfico existe em `analise/`, com outro nome, mas os bytes não batem.
A explicação provável é que as figuras de `analise/` foram regeradas depois de
copiadas para o relatório: `SPEC-016` registra duas correções de legibilidade
em 2026-09-02 (referência de média e mediana em violin plot, legenda de base
movida para dentro da área do gráfico). **Enquanto não reconciliadas, estas
figuras podem mostrar uma versão anterior do gráfico.** A reconciliação exige
olhar cada uma, porque algumas legendas do texto descrevem o que se vê.

- `imrad-microdados · 03-resultados · res_14_tempo_solo_mensal_por_base_gol.png`
- `imrad-microdados · 03-resultados · res_15_tempo_solo_por_hub_gol_azul.png`
- `imrad-microdados · 03-resultados · res_22_etapa_media_mensal_por_base_gol.png`
- `imrad-microdados · 03-resultados · res_23_etapa_media_top_bases_origem_gol.png`
- `imrad-microdados · 03-resultados · res_28_folga_por_hub_gol.png`
- `imrad-microdados · 03-resultados · res_31_folga_por_hub_gol_azul.png`
- `minto-microdados · 02-porques · p1_tempo_solo_mensal_por_base.png`
- `minto-microdados · 02-porques · p2a_etapa_media_por_base.png`

---

*Fim do documento.*