"""Block time -- GOL, so passageiro (SPEC-014). Primeira rodada aplicando
o metodo completo (forma + cerca de Tukey + run sequence + lag plot)
ANTES de qualquer segmentacao por frota/hub -- ordem discutida e
combinada com o autor, 2026-09-02, corrigindo a sequencia que usamos por
engano em a3_tempo_de_solo/a4_etapa_media (la' so fizemos run sequence e
lag plot depois, quando pedido; aqui e' desde o inicio).

Fonte: fato_block_time_gol_azul (db/anac_basica.sqlite) + basica_curated_deep
so' para filtrar PASSAGEIRO. Achado desta rodada: o docstring do script
antigo (analise_block_time_gol_azul.py) afirmava que o filtro PASSAGEIRO
"ja vem herdado" de fato_rotacao_aeronave_gol_azul -- medido agora, NAO
e' verdade (fato_rotacao herda basica_curated_deep inteira, cargueiro
incluso, mesma situacao ja encontrada e corrigida em a3_tempo_de_solo).
22.239 etapas de CARGUEIRO (1,9% do total GOL) estavam misturadas no
script antigo sem ninguem perceber. Corrigido aqui via mapeamento
id_basica -> ds_servico_tipo_linha (mesma tecnica de sempre).

Limpeza pontual em atraso_partida_horas/atraso_chegada_horas (NAO e'
cerca de Tukey, e' garbage de dado): 71 linhas (0,0064% de 1,1M com
match VRA) com |atraso_partida_horas| > 24h, chegando a -8748h (quase 1
ano) -- claramente timestamp VRA corrompido, todas marcadas
REALIZADO/justificativa N/A. folga_horas NAO e' afetada por esse
problema (usa nr_horas_voadas da Basica, nao os timestamps "reais" do
VRA) -- por isso dist_01/02/03 nao precisam desse filtro, so'
dist_04/05/06 precisam. Filtro local (nao DDL): a escala (0,0064%) e'
pequena demais para justificar uma coluna de validade no banco, ao
contrario do que fizemos para tempo_solo_horas (DDL_005, 0,29%).

Roda com: conda run -n pesquisa-azul python analise/a5_block_time/distribuicao_block_time_gol.py
"""

from pathlib import Path
import sqlite3

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import seaborn as sns

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from iata_bases import aplicar_iata  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = REPO_ROOT / "db" / "anac_basica.sqlite"
FIG_DIR = REPO_ROOT / "analise" / "a5_block_time" / "a5_figuras_gol"
FIG_DIR.mkdir(parents=True, exist_ok=True)

# Teto ajustado para 2026-06-30 (nao 07-31 como em a3/a4) -- achado do
# dist_07 (2026-09-02): o VRA (fonte do "previsto") so' tem dado ate'
# 2026-07-01 03:22, contra 2026-08-01 da Basica. Julho/2026 ficava com
# ~100% das etapas sem match VRA por atraso de publicacao da fonte, nao
# por operacao real -- excluido da janela em vez de aparecer como pico
# artificial em qualquer grafico mensal.
WINDOW_FULL = ("2021-01-01", "2026-06-30")

GOL_ORANGE = "#FF6900"
NEUTRAL_GRAY = "#4d4d4d"
COR_SOBRA = "#1baf7a"
COR_FALTA = "#e34948"
PALETA_CATEGORICA = [
    "#2a78d6", "#eb6834", "#1baf7a", "#eda100",
    "#e87ba4", "#008300", "#4a3aa7", "#e34948",
]

sns.set_theme(style="whitegrid")
plt.rcParams.update({
    "figure.facecolor": "#ffffff",
    "axes.facecolor": "#ffffff",
    "axes.titleweight": "bold",
    "font.size": 10,
})


def load_data() -> pd.DataFrame:
    """Etapas PASSAGEIRO da GOL, dt_partida_real dentro de WINDOW_FULL.
    fato_block_time_gol_azul nao filtra servico nem traz natureza
    (achados desta rodada) -- os dois vem por mapeamento id_basica,
    mesma tecnica de a3_tempo_de_solo."""
    con = sqlite3.connect(DB_PATH)
    passageiro = pd.read_sql_query(
        "SELECT id_basica, ds_natureza_tipo_linha FROM basica_curated_deep "
        "WHERE sg_empresa_icao = 'GLO' AND ds_servico_tipo_linha = 'PASSAGEIRO'",
        con,
    ).set_index("id_basica")

    df = pd.read_sql_query(
        """
        SELECT id_basica, dt_partida_real, sg_icao_origem, sg_icao_destino,
               sg_equipamento_icao, fl_continuidade_ok, folga_horas,
               atraso_partida_horas, atraso_chegada_horas, fl_match_vra
        FROM fato_block_time_gol_azul
        WHERE sg_empresa_icao = 'GLO'
          AND dt_partida_real BETWEEN ? AND ?
        """,
        con, params=WINDOW_FULL, parse_dates=["dt_partida_real"],
    )
    con.close()

    n_antes = len(df)
    df = df[df["id_basica"].isin(passageiro.index)].reset_index(drop=True)
    df["ds_natureza_tipo_linha"] = df["id_basica"].map(passageiro["ds_natureza_tipo_linha"])
    n_fmt = f"{len(df):,}".replace(",", ".")
    n_antes_fmt = f"{n_antes:,}".replace(",", ".")
    n_removido_fmt = f"{n_antes - len(df):,}".replace(",", ".")
    print(f"[load_data] filtro PASSAGEIRO: {n_fmt} de {n_antes_fmt} etapas "
          f"({n_removido_fmt} de CARGUEIRO removidas -- docstring do script antigo estava errado)")

    return aplicar_iata(df)


def calcular_corte_outlier(serie: pd.Series) -> tuple[float, float]:
    """Cerca de Tukey (1.5x IQR). folga_horas e atraso_partida_horas
    tem valor negativo com sentido proprio (falta de tempo / chegada
    adiantada) -- nao ha piso em 0 aqui, ao contrario de tempo_solo_horas."""
    q1, q3 = serie.quantile([0.25, 0.75])
    iqr = q3 - q1
    return q1 - 1.5 * iqr, q3 + 1.5 * iqr


def selecionar_hub(contagens: pd.Series) -> pd.Series:
    """HUB enquanto o acumulado ANTES da base for < 80% (mesma regra ja usada nesta linha de analise)."""
    ordenado = contagens.sort_values(ascending=False)
    pct = 100 * ordenado / ordenado.sum()
    pct_acum = pct.cumsum()
    pct_acum_antes = pct_acum - pct
    return ordenado[pct_acum_antes < 80]


def fig_dist_01_frequencia_densidade_boxplot_folga(df: pd.DataFrame) -> tuple[float, float]:
    sub = df[df["fl_match_vra"] == 1]
    folga = sub["folga_horas"].dropna()
    inferior, superior = calcular_corte_outlier(folga)
    n_outliers = int(((folga < inferior) | (folga > superior)).sum())
    pct_outliers = 100 * n_outliers / len(folga)

    fig, (ax_hist, ax_box) = plt.subplots(
        2, 1, figsize=(10, 6.5), sharex=True,
        gridspec_kw={"height_ratios": [3, 1], "hspace": 0.06},
    )

    sns.histplot(folga, bins=80, color=GOL_ORANGE, stat="count", ax=ax_hist,
                 edgecolor="white", linewidth=0.3, alpha=0.85)
    ax_hist.set_ylabel("Frequência (nº de etapas)")

    ax_dens = ax_hist.twinx()
    sns.kdeplot(folga, color=NEUTRAL_GRAY, linewidth=2, ax=ax_dens)
    ax_dens.set_ylabel("Densidade")
    ax_dens.grid(False)

    for corte in (inferior, superior):
        ax_hist.axvline(corte, color=NEUTRAL_GRAY, linestyle="--", linewidth=1.3)
        ax_box.axvline(corte, color=NEUTRAL_GRAY, linestyle="--", linewidth=1.3)
    ax_hist.axvline(0, color="#333333", linestyle=":", linewidth=1.3)
    ax_box.axvline(0, color="#333333", linestyle=":", linewidth=1.3)

    n_outliers_fmt = f"{n_outliers:,}".replace(",", ".")
    ax_hist.set_title(
        "GOL — Distribuição de Folga (frequência + densidade)\n"
        f"corte de outlier (Tukey, 1,5×IQR): [{inferior:.2f}h, {superior:.2f}h] "
        f"— {n_outliers_fmt} etapas fora ({pct_outliers:.2f}%) — linha pontilhada = 0 (nem sobra, nem falta)"
    )

    sns.boxplot(x=folga, color=GOL_ORANGE, ax=ax_box, fliersize=2, linewidth=1)
    ax_box.set_xlabel("folga_horas (positivo = sobra, negativo = falta)")
    ax_box.set_yticks([])

    fig.savefig(FIG_DIR / "dist_01_frequencia_densidade_boxplot_folga.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    print(
        f"[dist_01] corte outlier Tukey (folga): [{inferior:.3f}h, {superior:.3f}h] | "
        f"{n_outliers_fmt} etapas fora ({pct_outliers:.2f}%)"
    )
    return inferior, superior


def fig_dist_02_run_sequence_folga(df: pd.DataFrame) -> pd.Series:
    sub = df[df["fl_match_vra"] == 1]
    diario = sub.set_index("dt_partida_real")["folga_horas"].resample("D").mean().dropna()
    media_geral = diario.mean()

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(diario.index, diario.values, color=GOL_ORANGE, linewidth=0.8, alpha=0.85)
    ax.axhline(media_geral, color=NEUTRAL_GRAY, linestyle="--", linewidth=1.3)
    ax.axhline(0, color="#333333", linestyle=":", linewidth=1.1)
    ax.annotate(f"média geral = {media_geral:.3f}h", xy=(diario.index[0], media_geral),
                xytext=(4, 6), textcoords="offset points", color=NEUTRAL_GRAY, fontweight="bold")
    ax.set_title("GOL — Run Sequence Plot: Folga Média Diária (2021-2026)")
    ax.set_xlabel("Data (ordem cronológica)")
    ax.set_ylabel("Folga média do dia (h)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "dist_02_run_sequence_folga.png", dpi=150)
    plt.close(fig)
    return diario


def fig_dist_03_lag_plot_folga(diario: pd.Series) -> float:
    anterior = diario.iloc[:-1].to_numpy()
    atual = diario.iloc[1:].to_numpy()
    r = float(np.corrcoef(anterior, atual)[0, 1])

    fig, ax = plt.subplots(figsize=(6.5, 6.5))
    ax.scatter(anterior, atual, color=GOL_ORANGE, s=14, alpha=0.5, edgecolor="none")
    lims = [min(anterior.min(), atual.min()), max(anterior.max(), atual.max())]
    ax.plot(lims, lims, color=NEUTRAL_GRAY, linestyle="--", linewidth=1.2)
    ax.set_xlim(lims)
    ax.set_ylim(lims)
    ax.set_title(f"GOL — Lag Plot (lag 1 dia): Folga Média Diária\nr = {r:.3f}")
    ax.set_xlabel("Folga média em t-1 (h)")
    ax.set_ylabel("Folga média em t (h)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "dist_03_lag_plot_folga.png", dpi=150)
    plt.close(fig)
    return r


def fig_dist_04_frequencia_densidade_boxplot_atraso(df: pd.DataFrame,
                                                      limite_valido: float = 24.0) -> tuple[float, float, pd.DataFrame]:
    """limite_valido: filtro pontual de garbage de dado (ver docstring do
    modulo), nao cerca de Tukey -- aplicado ANTES da cerca."""
    sub = df[df["fl_match_vra"] == 1].dropna(subset=["atraso_partida_horas"]).copy()
    n_antes = len(sub)
    extremos = sub[sub["atraso_partida_horas"].abs() > limite_valido]
    if len(extremos):
        print(f"[dist_04] removidas {len(extremos)} etapas com |atraso_partida_horas| > {limite_valido:.0f}h "
              f"(timestamp VRA corrompido, max observado {extremos['atraso_partida_horas'].abs().max():.0f}h)")
    sub = sub[sub["atraso_partida_horas"].abs() <= limite_valido]

    atraso = sub["atraso_partida_horas"]
    inferior, superior = calcular_corte_outlier(atraso)
    n_outliers = int(((atraso < inferior) | (atraso > superior)).sum())
    pct_outliers = 100 * n_outliers / len(atraso)

    # A cerca de Tukey e' calculada sobre TODA a serie (acima), mas o
    # eixo visual e' recortado nos percentis 0,1%-99,9%: sem isso os
    # outliers legitimos ate' ±24h (raros, mas reais) esticam o eixo e
    # escondem a forma real da distribuicao, que vive dentro de ±0,5h.
    xlim_min, xlim_max = atraso.quantile(0.001), atraso.quantile(0.999)
    atraso_plot = atraso[(atraso >= xlim_min) & (atraso <= xlim_max)]

    fig, (ax_hist, ax_box) = plt.subplots(
        2, 1, figsize=(10, 6.5), sharex=True,
        gridspec_kw={"height_ratios": [3, 1], "hspace": 0.06},
    )

    sns.histplot(atraso_plot, bins=80, color=GOL_ORANGE, stat="count", ax=ax_hist,
                 edgecolor="white", linewidth=0.3, alpha=0.85, binrange=(xlim_min, xlim_max))
    ax_hist.set_ylabel("Frequência (nº de etapas)")

    ax_dens = ax_hist.twinx()
    sns.kdeplot(atraso_plot, color=NEUTRAL_GRAY, linewidth=2, ax=ax_dens)
    ax_dens.set_ylabel("Densidade")
    ax_dens.grid(False)

    for corte in (inferior, superior):
        ax_hist.axvline(corte, color=NEUTRAL_GRAY, linestyle="--", linewidth=1.3)
        ax_box.axvline(corte, color=NEUTRAL_GRAY, linestyle="--", linewidth=1.3)
    ax_hist.axvline(0, color="#333333", linestyle=":", linewidth=1.3)
    ax_box.axvline(0, color="#333333", linestyle=":", linewidth=1.3)

    n_outliers_fmt = f"{n_outliers:,}".replace(",", ".")
    n_fmt = f"{len(sub):,}".replace(",", ".")
    ax_hist.set_title(
        "GOL — Distribuição de Atraso de Partida (frequência + densidade)\n"
        f"corte de outlier (Tukey, 1,5×IQR): [{inferior:.2f}h, {superior:.2f}h] "
        f"— {n_outliers_fmt} etapas fora ({pct_outliers:.2f}%), n={n_fmt}\n"
        f"(já sem as {len(extremos)} etapas com |atraso| > {limite_valido:.0f}h; "
        "eixo recortado nos percentis 0,1%-99,9% p/ legibilidade)"
    )

    sns.boxplot(x=atraso, color=GOL_ORANGE, ax=ax_box, fliersize=2, linewidth=1)
    ax_box.set_xlim(xlim_min, xlim_max)
    ax_box.set_xlabel("Atraso de partida (h, positivo = atrasou, negativo = saiu adiantado)")
    ax_box.set_yticks([])

    fig.savefig(FIG_DIR / "dist_04_frequencia_densidade_boxplot_atraso.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    print(
        f"[dist_04] corte outlier Tukey (atraso): [{inferior:.3f}h, {superior:.3f}h] | "
        f"{n_outliers_fmt} etapas fora ({pct_outliers:.2f}%)"
    )
    return inferior, superior, sub


def fig_dist_05_run_sequence_atraso(sub: pd.DataFrame) -> pd.Series:
    diario = sub.set_index("dt_partida_real")["atraso_partida_horas"].resample("D").mean().dropna()
    media_geral = diario.mean()

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(diario.index, diario.values, color=GOL_ORANGE, linewidth=0.8, alpha=0.85)
    ax.axhline(media_geral, color=NEUTRAL_GRAY, linestyle="--", linewidth=1.3)
    ax.axhline(0, color="#333333", linestyle=":", linewidth=1.1)
    ax.annotate(f"média geral = {media_geral:.3f}h", xy=(diario.index[0], media_geral),
                xytext=(4, 6), textcoords="offset points", color=NEUTRAL_GRAY, fontweight="bold")
    ax.set_title("GOL — Run Sequence Plot: Atraso de Partida Médio Diário (2021-2026)")
    ax.set_xlabel("Data (ordem cronológica)")
    ax.set_ylabel("Atraso médio do dia (h)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "dist_05_run_sequence_atraso.png", dpi=150)
    plt.close(fig)
    return diario


def fig_dist_06_lag_plot_atraso(diario: pd.Series) -> float:
    anterior = diario.iloc[:-1].to_numpy()
    atual = diario.iloc[1:].to_numpy()
    r = float(np.corrcoef(anterior, atual)[0, 1])

    fig, ax = plt.subplots(figsize=(6.5, 6.5))
    ax.scatter(anterior, atual, color=GOL_ORANGE, s=14, alpha=0.5, edgecolor="none")
    lims = [min(anterior.min(), atual.min()), max(anterior.max(), atual.max())]
    ax.plot(lims, lims, color=NEUTRAL_GRAY, linestyle="--", linewidth=1.2)
    ax.set_xlim(lims)
    ax.set_ylim(lims)
    ax.set_title(f"GOL — Lag Plot (lag 1 dia): Atraso de Partida Médio Diário\nr = {r:.3f}")
    ax.set_xlabel("Atraso médio em t-1 (h)")
    ax.set_ylabel("Atraso médio em t (h)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "dist_06_lag_plot_atraso.png", dpi=150)
    plt.close(fig)
    return r


def fig_dist_07_vies_match_vra(df: pd.DataFrame, top_n: int = 10, min_etapas: int = 1000) -> None:
    """Pergunta: as etapas sem match VRA (fl_match_vra=0) sao aleatorias,
    ou concentradas por mes/base/modelo? Se concentradas, os achados de
    folga_horas (calculados so' onde ha match) podem estar levemente
    enviesados nesse recorte -- checar ANTES de interpretar qualquer
    media."""
    pct_geral = 100 * (df["fl_match_vra"] == 0).mean()

    fig, axes = plt.subplots(1, 3, figsize=(17, 5.5))

    mensal = (
        df.set_index("dt_partida_real")["fl_match_vra"]
        .resample("MS").apply(lambda s: 100 * (s == 0).mean())
    )
    axes[0].plot(mensal.index, mensal.values, color=GOL_ORANGE, linewidth=2, marker="o", markersize=3)
    axes[0].axhline(pct_geral, color=NEUTRAL_GRAY, linestyle="--", linewidth=1.2)
    axes[0].set_title("Por mês")
    axes[0].set_ylabel("% de etapas sem match VRA")
    axes[0].set_xlabel("Mês")

    top_bases = selecionar_hub(df["sg_iata_origem"].value_counts()).index.tolist()[:top_n]
    pct_base = (
        df[df["sg_iata_origem"].isin(top_bases)]
        .groupby("sg_iata_origem")["fl_match_vra"]
        .apply(lambda s: 100 * (s == 0).mean())
        .sort_values(ascending=False)
    )
    cores_base = PALETA_CATEGORICA[:len(pct_base)] if len(pct_base) <= len(PALETA_CATEGORICA) else GOL_ORANGE
    axes[1].bar(pct_base.index, pct_base.values, color=cores_base)
    axes[1].axhline(pct_geral, color=NEUTRAL_GRAY, linestyle="--", linewidth=1.2)
    axes[1].set_title(f"Por base HUB de origem (top {top_n})")
    axes[1].tick_params(axis="x", rotation=45)

    modelos = df["sg_equipamento_icao"].value_counts()
    modelos = modelos[modelos >= min_etapas].index.tolist()
    pct_modelo = (
        df[df["sg_equipamento_icao"].isin(modelos)]
        .groupby("sg_equipamento_icao")["fl_match_vra"]
        .apply(lambda s: 100 * (s == 0).mean())
        .sort_values(ascending=False)
    )
    cores_modelo = PALETA_CATEGORICA[:len(pct_modelo)] if len(pct_modelo) <= len(PALETA_CATEGORICA) else GOL_ORANGE
    axes[2].bar(pct_modelo.index, pct_modelo.values, color=cores_modelo)
    axes[2].axhline(pct_geral, color=NEUTRAL_GRAY, linestyle="--", linewidth=1.2)
    axes[2].set_title(f"Por modelo (≥{min_etapas} etapas)")

    fig.suptitle(f"GOL — Viés do Match VRA (linha cinza = média geral, {pct_geral:.2f}% sem match)",
                 fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "dist_07_vies_match_vra.png", dpi=150)
    plt.close(fig)

    print(f"[dist_07] % geral sem match VRA: {pct_geral:.2f}% | "
          f"faixa por mês: [{mensal.min():.2f}%, {mensal.max():.2f}%] | "
          f"faixa por base: [{pct_base.min():.2f}%, {pct_base.max():.2f}%] | "
          f"faixa por modelo: [{pct_modelo.min():.2f}%, {pct_modelo.max():.2f}%]")


def fig_dist_08_folga_por_modelo(df: pd.DataFrame, inferior: float, superior: float,
                                  min_etapas: int = 1000) -> None:
    """Segmentacao por frota -- so' agora, depois de ja confirmar (dist_01-03)
    que folga_horas tem deriva temporal real. Truncado na cerca de Tukey
    de dist_01 -- mesma logica ja usada em a3/a4: segmentar em cima da
    visao 'sem outlier', nao da bruta."""
    sub = df[(df["fl_match_vra"] == 1) & df["folga_horas"].between(inferior, superior)]
    contagem = sub["sg_equipamento_icao"].value_counts()
    modelos = contagem[contagem >= min_etapas].index.tolist()
    sub = sub[sub["sg_equipamento_icao"].isin(modelos)]
    ordem = sub.groupby("sg_equipamento_icao")["folga_horas"].median().sort_values(ascending=False).index.tolist()

    fig, ax = plt.subplots(figsize=(9, 6.5))
    sns.violinplot(data=sub, x="sg_equipamento_icao", y="folga_horas", order=ordem,
                    hue="sg_equipamento_icao", hue_order=ordem, palette=PALETA_CATEGORICA[:len(ordem)],
                    legend=False, cut=0, ax=ax)
    ax.axhline(0, color="#333333", linestyle=":", linewidth=1.2)

    # Media e mediana ficam muito proximas aqui (folga_horas tem IQR
    # pequeno) -- achado desta rodada: com as duas linhas separadas por
    # menos de ~4% do range do eixo, os dois rotulos de texto colidem
    # visualmente (ficam ilegiveis, "md=0i067h"). Funde num rotulo so'
    # quando isso acontece, em vez de brigar por posicionamento.
    meia_largura = 0.4
    span_eixo = superior - inferior
    limiar_proximidade = span_eixo * 0.04
    for i, modelo in enumerate(ordem):
        valores = sub.loc[sub["sg_equipamento_icao"] == modelo, "folga_horas"]
        media, mediana = valores.mean(), valores.median()
        ax.hlines(media, i - meia_largura, i + meia_largura, color="#2a78d6", linewidth=2, zorder=5)
        ax.hlines(mediana, i - meia_largura, i + meia_largura, color=NEUTRAL_GRAY, linewidth=2,
                  linestyle="--", zorder=5)
        caixa = dict(facecolor="white", alpha=0.8, edgecolor="none", pad=1.5)
        if abs(media - mediana) < limiar_proximidade:
            y_texto = (media + mediana) / 2
            ax.text(i + meia_largura + 0.03, y_texto, f"μ={media:.3f}h / md={mediana:.3f}h",
                    color="#333333", fontsize=8, fontweight="bold", va="center", bbox=caixa, zorder=6)
        else:
            ax.text(i + meia_largura + 0.03, media, f"μ={media:.3f}h", color="#2a78d6",
                    fontsize=8, fontweight="bold", va="center", bbox=caixa, zorder=6)
            ax.text(i + meia_largura + 0.03, mediana, f"md={mediana:.3f}h", color=NEUTRAL_GRAY,
                    fontsize=8, fontweight="bold", va="center", bbox=caixa, zorder=6)

    legenda_ref = [
        Line2D([0], [0], color="#2a78d6", linewidth=2, label="Média"),
        Line2D([0], [0], color=NEUTRAL_GRAY, linewidth=2, linestyle="--", label="Mediana"),
    ]
    ax.legend(handles=legenda_ref, loc="upper right", frameon=True, edgecolor="#333333")

    ax.set_xlabel("Modelo")
    ax.set_ylabel("folga_horas")
    ax.margins(x=0.12)
    n_fmt = f"{len(sub):,}".replace(",", ".")
    ax.set_title(
        f"GOL — Folga por Modelo de Aeronave (≥{min_etapas} etapas)\n"
        f"(truncado em cerca de Tukey [{inferior:.2f}h, {superior:.2f}h], n={n_fmt})"
    )
    fig.tight_layout()
    fig.savefig(FIG_DIR / "dist_08_folga_por_modelo.png", dpi=150)
    plt.close(fig)


def fig_dist_09_folga_por_hub(df: pd.DataFrame, inferior: float, superior: float, max_bases: int = 8) -> None:
    sub = df[(df["fl_match_vra"] == 1) & df["folga_horas"].between(inferior, superior)]
    hub = selecionar_hub(sub["sg_iata_origem"].value_counts())
    bases = hub.index.tolist()[:max_bases]
    sub = sub[sub["sg_iata_origem"].isin(bases)]
    ordem = sub.groupby("sg_iata_origem")["folga_horas"].median().sort_values(ascending=False).index.tolist()

    fig, ax = plt.subplots(figsize=(11, 6))
    sns.boxplot(data=sub, x="sg_iata_origem", y="folga_horas", order=ordem,
                hue="sg_iata_origem", hue_order=ordem, palette=PALETA_CATEGORICA[:len(ordem)],
                legend=False, fliersize=2, linewidth=1, ax=ax)
    ax.axhline(0, color="#333333", linestyle=":", linewidth=1.2)
    ax.set_title(f"GOL — Folga por Base HUB de Origem\n(top {len(bases)}, 80% acumulado)")
    ax.set_xlabel("Base de origem")
    ax.set_ylabel("folga_horas")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "dist_09_folga_por_hub.png", dpi=150)
    plt.close(fig)


def fig_dist_10_folga_por_natureza(df: pd.DataFrame, inferior: float, superior: float) -> None:
    sub = df[(df["fl_match_vra"] == 1) & df["folga_horas"].between(inferior, superior)]
    agg = sub.groupby("ds_natureza_tipo_linha")["folga_horas"].agg(["mean", "count"])

    fig, ax = plt.subplots(figsize=(7, 5.5))
    barras = ax.bar([s.title() for s in agg.index], agg["mean"], color=PALETA_CATEGORICA[:len(agg)])
    ax.bar_label(barras, fmt="%.3f", fontweight="bold", padding=3)
    ax.axhline(0, color="#333333", linestyle=":", linewidth=1.2)
    # n= dentro da barra -- mesmo ajuste do dist_11 (colado no eixo X
    # colidia com o rotulo das categorias).
    y_rotulo = agg["mean"].max() * 0.05
    for i, (_, row) in enumerate(agg.iterrows()):
        n_fmt = f"{int(row['count']):,}".replace(",", ".")
        ax.text(i, y_rotulo, f"n={n_fmt}", ha="center", va="bottom",
                fontsize=8, color="white", fontweight="bold")
    ax.set_title("GOL — Folga Média por Natureza da Linha")
    ax.set_ylabel("folga_horas (média)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "dist_10_folga_por_natureza.png", dpi=150)
    plt.close(fig)


def fig_dist_11_folga_por_continuidade(df: pd.DataFrame, inferior: float, superior: float) -> None:
    """fl_continuidade_ok=0 significa que a origem desta etapa nao bate
    com o destino da etapa anterior da mesma matricula (SPEC-012) --
    checa se essa quebra de rotacao vem acompanhada de folga anormal."""
    sub = df[(df["fl_match_vra"] == 1) & df["folga_horas"].between(inferior, superior)].copy()
    sub["grupo"] = sub["fl_continuidade_ok"].map(
        {1: "Continuidade OK", 0: "Continuidade quebrada"}
    ).fillna("Primeira etapa (sem anterior)")
    ordem = ["Continuidade OK", "Continuidade quebrada", "Primeira etapa (sem anterior)"]
    agg = sub.groupby("grupo")["folga_horas"].agg(["mean", "count"]).reindex(ordem)

    fig, ax = plt.subplots(figsize=(9, 5.5))
    cores = [PALETA_CATEGORICA[0], PALETA_CATEGORICA[7], PALETA_CATEGORICA[3]]
    barras = ax.bar(agg.index, agg["mean"], color=cores)
    ax.bar_label(barras, fmt="%.3f", fontweight="bold", padding=3)
    ax.axhline(0, color="#333333", linestyle=":", linewidth=1.2)
    # n= dentro da barra, perto da base -- colado no eixo X (fora da
    # barra) colidia com o rotulo das categorias (achado desta rodada).
    y_rotulo = agg["mean"].max() * 0.05
    for i, (_, row) in enumerate(agg.iterrows()):
        n_fmt = f"{int(row['count']):,}".replace(",", ".")
        ax.text(i, y_rotulo, f"n={n_fmt}", ha="center", va="bottom",
                fontsize=8, color="white", fontweight="bold")
    ax.set_title("GOL — Folga Média vs. Continuidade da Rotação")
    ax.set_ylabel("folga_horas (média)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "dist_11_folga_por_continuidade.png", dpi=150)
    plt.close(fig)


def fig_dist_12_atraso_por_modelo(sub_atraso: pd.DataFrame, inferior: float, superior: float,
                                   min_etapas: int = 1000) -> None:
    """Mesmo tratamento de dist_08, agora para atraso_partida_horas --
    sub_atraso ja vem sem os 71 registros de timestamp corrompido
    (filtrados em dist_04)."""
    sub = sub_atraso[sub_atraso["atraso_partida_horas"].between(inferior, superior)]
    contagem = sub["sg_equipamento_icao"].value_counts()
    modelos = contagem[contagem >= min_etapas].index.tolist()
    sub = sub[sub["sg_equipamento_icao"].isin(modelos)]
    ordem = sub.groupby("sg_equipamento_icao")["atraso_partida_horas"].median().sort_values(ascending=False).index.tolist()

    fig, ax = plt.subplots(figsize=(9, 6.5))
    sns.violinplot(data=sub, x="sg_equipamento_icao", y="atraso_partida_horas", order=ordem,
                    hue="sg_equipamento_icao", hue_order=ordem, palette=PALETA_CATEGORICA[:len(ordem)],
                    legend=False, cut=0, ax=ax)
    ax.axhline(0, color="#333333", linestyle=":", linewidth=1.2)

    # Mesmo ajuste do dist_08: funde os dois rotulos quando media e
    # mediana ficam proximas demais pra caber em duas linhas legiveis.
    meia_largura = 0.4
    span_eixo = superior - inferior
    limiar_proximidade = span_eixo * 0.04
    for i, modelo in enumerate(ordem):
        valores = sub.loc[sub["sg_equipamento_icao"] == modelo, "atraso_partida_horas"]
        media, mediana = valores.mean(), valores.median()
        ax.hlines(media, i - meia_largura, i + meia_largura, color="#2a78d6", linewidth=2, zorder=5)
        ax.hlines(mediana, i - meia_largura, i + meia_largura, color=NEUTRAL_GRAY, linewidth=2,
                  linestyle="--", zorder=5)
        caixa = dict(facecolor="white", alpha=0.8, edgecolor="none", pad=1.5)
        if abs(media - mediana) < limiar_proximidade:
            y_texto = (media + mediana) / 2
            ax.text(i + meia_largura + 0.03, y_texto,
                    f"μ={media * 60:.1f}min / md={mediana * 60:.1f}min",
                    color="#333333", fontsize=8, fontweight="bold", va="center", bbox=caixa, zorder=6)
        else:
            ax.text(i + meia_largura + 0.03, media, f"μ={media * 60:.1f}min", color="#2a78d6",
                    fontsize=8, fontweight="bold", va="center", bbox=caixa, zorder=6)
            ax.text(i + meia_largura + 0.03, mediana, f"md={mediana * 60:.1f}min", color=NEUTRAL_GRAY,
                    fontsize=8, fontweight="bold", va="center", bbox=caixa, zorder=6)

    legenda_ref = [
        Line2D([0], [0], color="#2a78d6", linewidth=2, label="Média"),
        Line2D([0], [0], color=NEUTRAL_GRAY, linewidth=2, linestyle="--", label="Mediana"),
    ]
    ax.legend(handles=legenda_ref, loc="upper right", frameon=True, edgecolor="#333333")

    ax.set_xlabel("Modelo")
    ax.set_ylabel("Atraso de partida (h)")
    ax.margins(x=0.12)
    n_fmt = f"{len(sub):,}".replace(",", ".")
    ax.set_title(
        f"GOL — Atraso de Partida por Modelo de Aeronave (≥{min_etapas} etapas)\n"
        f"(truncado em cerca de Tukey [{inferior:.2f}h, {superior:.2f}h], n={n_fmt})"
    )
    fig.tight_layout()
    fig.savefig(FIG_DIR / "dist_12_atraso_por_modelo.png", dpi=150)
    plt.close(fig)


def fig_dist_13_top_bases_sem_match(df: pd.DataFrame, top_n: int = 10) -> None:
    """Complementa o dist_07: la' o painel de base ja vinha pre-filtrado
    pelas top N bases por VOLUME (selecionar_hub), so' depois mostrando a
    taxa. Aqui a selecao e' direto pelo numero ABSOLUTO de etapas sem
    match -- uma base grande pode acumular muitas linhas sem match so'
    por volume, mesmo com taxa baixa; olhar as duas visoes juntas (numero
    absoluto e % normalizado pela mesma base) separa esses dois casos."""
    grouped = df.groupby("sg_iata_origem")["fl_match_vra"]
    n_total = grouped.count()
    n_sem_match = grouped.apply(lambda s: int((s == 0).sum()))
    pct_sem_match = 100 * n_sem_match / n_total
    pct_geral = 100 * (df["fl_match_vra"] == 0).mean()

    agg = pd.DataFrame({"n_sem_match": n_sem_match, "n_total": n_total, "pct_sem_match": pct_sem_match})
    top = agg.sort_values("n_sem_match", ascending=True).tail(top_n)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    barras1 = ax1.barh(top.index, top["n_sem_match"], color=GOL_ORANGE, edgecolor="#333333", linewidth=0.5)
    ax1.bar_label(barras1, fmt="%.0f", fontweight="bold", fontsize=8, padding=3)
    ax1.margins(x=0.12)
    ax1.set_title(f"Top {top_n} bases — nº absoluto de etapas sem match")
    ax1.set_xlabel("Nº de etapas sem match VRA")

    barras2 = ax2.barh(top.index, top["pct_sem_match"], color=GOL_ORANGE, edgecolor="#333333", linewidth=0.5)
    ax2.bar_label(barras2, fmt="%.2f%%", fontweight="bold", fontsize=8, padding=3)
    ax2.axvline(pct_geral, color=NEUTRAL_GRAY, linestyle="--", linewidth=1.2)
    ax2.margins(x=0.12)
    ax2.set_title("Mesmas bases — % sem match\n(normalizado pelo total da própria base)")
    ax2.set_xlabel("% de etapas sem match VRA")

    fig.suptitle("GOL — Bases com Mais Etapas sem Match VRA: Absoluto x Normalizado", fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "dist_13_top_bases_sem_match.png", dpi=150)
    plt.close(fig)

    maior_absoluto = top.index[-1]
    print(f"[dist_13] maior em nº absoluto: {maior_absoluto} "
          f"({int(top['n_sem_match'].iloc[-1]):,} etapas sem match, "
          f"{top['pct_sem_match'].iloc[-1]:.2f}% dessa base)".replace(",", "."))


def fig_dist_14_atraso_recuperado_em_voo(sub: pd.DataFrame, limite_valido: float = 24.0) -> None:
    """atraso_partida e atraso_chegada tem r=0,98 (quase redundantes) --
    por isso nao replicamos os 4 graficos do atraso_partida para chegada.
    O conteudo novo e' a DIFERENCA: atraso_chegada - atraso_partida, que
    mede quanto de atraso foi recuperado (negativo) ou ganho (positivo)
    durante o voo. `sub` ja vem filtrado do garbage de atraso_partida
    (ver fig_dist_04); aqui aplicamos o mesmo filtro pontual a
    atraso_chegada antes de calcular a diferenca."""
    dados = sub.dropna(subset=["atraso_chegada_horas"]).copy()
    extremos = dados[dados["atraso_chegada_horas"].abs() > limite_valido]
    if len(extremos):
        print(f"[dist_14] removidas {len(extremos)} etapas com |atraso_chegada_horas| > {limite_valido:.0f}h "
              f"(mesmo tipo de timestamp VRA corrompido do dist_04)")
    dados = dados[dados["atraso_chegada_horas"].abs() <= limite_valido]

    diff = dados["atraso_chegada_horas"] - dados["atraso_partida_horas"]
    r = dados["atraso_partida_horas"].corr(dados["atraso_chegada_horas"])
    media, mediana = diff.mean(), diff.median()
    inferior, superior = calcular_corte_outlier(diff)
    n_outliers = int(((diff < inferior) | (diff > superior)).sum())
    pct_outliers = 100 * n_outliers / len(diff)

    fig, (ax_hist, ax_box) = plt.subplots(
        2, 1, figsize=(10, 6.5), sharex=True,
        gridspec_kw={"height_ratios": [3, 1], "hspace": 0.06},
    )

    xlim_min, xlim_max = diff.quantile(0.001), diff.quantile(0.999)
    diff_plot = diff[(diff >= xlim_min) & (diff <= xlim_max)]

    sns.histplot(diff_plot, bins=80, color=GOL_ORANGE, stat="count", ax=ax_hist,
                 edgecolor="white", linewidth=0.3, alpha=0.85, binrange=(xlim_min, xlim_max))
    ax_hist.set_ylabel("Frequência (nº de etapas)")

    ax_dens = ax_hist.twinx()
    sns.kdeplot(diff_plot, color=NEUTRAL_GRAY, linewidth=2, ax=ax_dens)
    ax_dens.set_ylabel("Densidade")
    ax_dens.grid(False)

    ax_hist.axvline(0, color="#333333", linestyle=":", linewidth=1.3)
    ax_hist.axvline(media, color="#2a78d6", linestyle="--", linewidth=1.3)
    ax_hist.annotate(f"média = {media*60:.1f}min / mediana = {mediana*60:.1f}min",
                      xy=(media, ax_hist.get_ylim()[1] * 0.9), xytext=(6, 0),
                      textcoords="offset points", color="#2a78d6", fontweight="bold", fontsize=9)

    n_fmt = f"{len(diff):,}".replace(",", ".")
    ax_hist.set_title(
        "GOL — Atraso Recuperado (ou Ganho) em Voo: Δ = Atraso Chegada − Atraso Partida\n"
        f"corr(atraso_partida, atraso_chegada) = {r:.3f} — negativo indica recuperação em voo, n={n_fmt}\n"
        f"cerca de Tukey: [{inferior:.2f}h, {superior:.2f}h], {pct_outliers:.2f}% fora "
        "(eixo recortado nos percentis 0,1%-99,9% p/ legibilidade)"
    )

    sns.boxplot(x=diff, color=GOL_ORANGE, ax=ax_box, fliersize=2, linewidth=1)
    ax_box.set_xlim(xlim_min, xlim_max)
    ax_box.set_xlabel("Δ atraso em voo (h, negativo = recuperou atraso, positivo = piorou em voo)")
    ax_box.set_yticks([])

    fig.savefig(FIG_DIR / "dist_14_atraso_recuperado_em_voo.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    print(f"[dist_14] Δ atraso em voo: média={media*60:.1f}min, mediana={mediana*60:.1f}min "
          f"(negativo=recuperou), corr(partida,chegada)={r:.3f}")


def fig_dist_15_frequencia_densidade_boxplot_atraso_chegada(df: pd.DataFrame,
                                                              limite_valido: float = 24.0
                                                              ) -> tuple[float, float, pd.DataFrame]:
    """Mesmo tratamento do dist_04, agora para atraso_chegada_horas.
    Replicado por pedido explicito mesmo sabendo que corr(partida,chegada)
    = 0,976 (ver dist_14) -- o formato desta distribuicao e' quase
    identico ao de dist_04, o que e' o proprio ponto de checar."""
    sub = df[df["fl_match_vra"] == 1].dropna(subset=["atraso_chegada_horas"]).copy()
    extremos = sub[sub["atraso_chegada_horas"].abs() > limite_valido]
    if len(extremos):
        print(f"[dist_15] removidas {len(extremos)} etapas com |atraso_chegada_horas| > {limite_valido:.0f}h "
              f"(timestamp VRA corrompido, max observado {extremos['atraso_chegada_horas'].abs().max():.0f}h)")
    sub = sub[sub["atraso_chegada_horas"].abs() <= limite_valido]

    atraso = sub["atraso_chegada_horas"]
    inferior, superior = calcular_corte_outlier(atraso)
    n_outliers = int(((atraso < inferior) | (atraso > superior)).sum())
    pct_outliers = 100 * n_outliers / len(atraso)

    xlim_min, xlim_max = atraso.quantile(0.001), atraso.quantile(0.999)
    atraso_plot = atraso[(atraso >= xlim_min) & (atraso <= xlim_max)]

    fig, (ax_hist, ax_box) = plt.subplots(
        2, 1, figsize=(10, 6.5), sharex=True,
        gridspec_kw={"height_ratios": [3, 1], "hspace": 0.06},
    )

    sns.histplot(atraso_plot, bins=80, color=GOL_ORANGE, stat="count", ax=ax_hist,
                 edgecolor="white", linewidth=0.3, alpha=0.85, binrange=(xlim_min, xlim_max))
    ax_hist.set_ylabel("Frequência (nº de etapas)")

    ax_dens = ax_hist.twinx()
    sns.kdeplot(atraso_plot, color=NEUTRAL_GRAY, linewidth=2, ax=ax_dens)
    ax_dens.set_ylabel("Densidade")
    ax_dens.grid(False)

    for corte in (inferior, superior):
        ax_hist.axvline(corte, color=NEUTRAL_GRAY, linestyle="--", linewidth=1.3)
        ax_box.axvline(corte, color=NEUTRAL_GRAY, linestyle="--", linewidth=1.3)
    ax_hist.axvline(0, color="#333333", linestyle=":", linewidth=1.3)
    ax_box.axvline(0, color="#333333", linestyle=":", linewidth=1.3)

    n_outliers_fmt = f"{n_outliers:,}".replace(",", ".")
    n_fmt = f"{len(sub):,}".replace(",", ".")
    ax_hist.set_title(
        "GOL — Distribuição de Atraso de Chegada (frequência + densidade)\n"
        f"corte de outlier (Tukey, 1,5×IQR): [{inferior:.2f}h, {superior:.2f}h] "
        f"— {n_outliers_fmt} etapas fora ({pct_outliers:.2f}%), n={n_fmt}\n"
        f"(já sem as {len(extremos)} etapas com |atraso| > {limite_valido:.0f}h; "
        "eixo recortado nos percentis 0,1%-99,9% p/ legibilidade)"
    )

    sns.boxplot(x=atraso, color=GOL_ORANGE, ax=ax_box, fliersize=2, linewidth=1)
    ax_box.set_xlim(xlim_min, xlim_max)
    ax_box.set_xlabel("Atraso de chegada (h, positivo = atrasou, negativo = chegou adiantado)")
    ax_box.set_yticks([])

    fig.savefig(FIG_DIR / "dist_15_frequencia_densidade_boxplot_atraso_chegada.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    print(
        f"[dist_15] corte outlier Tukey (atraso chegada): [{inferior:.3f}h, {superior:.3f}h] | "
        f"{n_outliers_fmt} etapas fora ({pct_outliers:.2f}%)"
    )
    return inferior, superior, sub


def fig_dist_16_run_sequence_atraso_chegada(sub: pd.DataFrame) -> pd.Series:
    diario = sub.set_index("dt_partida_real")["atraso_chegada_horas"].resample("D").mean().dropna()
    media_geral = diario.mean()

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(diario.index, diario.values, color=GOL_ORANGE, linewidth=0.8, alpha=0.85)
    ax.axhline(media_geral, color=NEUTRAL_GRAY, linestyle="--", linewidth=1.3)
    ax.axhline(0, color="#333333", linestyle=":", linewidth=1.1)
    ax.annotate(f"média geral = {media_geral:.3f}h", xy=(diario.index[0], media_geral),
                xytext=(4, 6), textcoords="offset points", color=NEUTRAL_GRAY, fontweight="bold")
    ax.set_title("GOL — Run Sequence Plot: Atraso de Chegada Médio Diário (2021-2026)")
    ax.set_xlabel("Data (ordem cronológica)")
    ax.set_ylabel("Atraso médio do dia (h)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "dist_16_run_sequence_atraso_chegada.png", dpi=150)
    plt.close(fig)
    return diario


def fig_dist_17_lag_plot_atraso_chegada(diario: pd.Series) -> float:
    anterior = diario.iloc[:-1].to_numpy()
    atual = diario.iloc[1:].to_numpy()
    r = float(np.corrcoef(anterior, atual)[0, 1])

    fig, ax = plt.subplots(figsize=(6.5, 6.5))
    ax.scatter(anterior, atual, color=GOL_ORANGE, s=14, alpha=0.5, edgecolor="none")
    lims = [min(anterior.min(), atual.min()), max(anterior.max(), atual.max())]
    ax.plot(lims, lims, color=NEUTRAL_GRAY, linestyle="--", linewidth=1.2)
    ax.set_xlim(lims)
    ax.set_ylim(lims)
    ax.set_title(f"GOL — Lag Plot (lag 1 dia): Atraso de Chegada Médio Diário\nr = {r:.3f}")
    ax.set_xlabel("Atraso médio em t-1 (h)")
    ax.set_ylabel("Atraso médio em t (h)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "dist_17_lag_plot_atraso_chegada.png", dpi=150)
    plt.close(fig)
    return r


def fig_dist_18_atraso_chegada_por_modelo(sub_atraso_chegada: pd.DataFrame, inferior: float, superior: float,
                                           min_etapas: int = 1000) -> None:
    """Mesmo tratamento de dist_12, agora para atraso_chegada_horas."""
    sub = sub_atraso_chegada[sub_atraso_chegada["atraso_chegada_horas"].between(inferior, superior)]
    contagem = sub["sg_equipamento_icao"].value_counts()
    modelos = contagem[contagem >= min_etapas].index.tolist()
    sub = sub[sub["sg_equipamento_icao"].isin(modelos)]
    ordem = sub.groupby("sg_equipamento_icao")["atraso_chegada_horas"].median().sort_values(ascending=False).index.tolist()

    fig, ax = plt.subplots(figsize=(9, 6.5))
    sns.violinplot(data=sub, x="sg_equipamento_icao", y="atraso_chegada_horas", order=ordem,
                    hue="sg_equipamento_icao", hue_order=ordem, palette=PALETA_CATEGORICA[:len(ordem)],
                    legend=False, cut=0, ax=ax)
    ax.axhline(0, color="#333333", linestyle=":", linewidth=1.2)

    meia_largura = 0.4
    span_eixo = superior - inferior
    limiar_proximidade = span_eixo * 0.04
    for i, modelo in enumerate(ordem):
        valores = sub.loc[sub["sg_equipamento_icao"] == modelo, "atraso_chegada_horas"]
        media, mediana = valores.mean(), valores.median()
        ax.hlines(media, i - meia_largura, i + meia_largura, color="#2a78d6", linewidth=2, zorder=5)
        ax.hlines(mediana, i - meia_largura, i + meia_largura, color=NEUTRAL_GRAY, linewidth=2,
                  linestyle="--", zorder=5)
        caixa = dict(facecolor="white", alpha=0.8, edgecolor="none", pad=1.5)
        if abs(media - mediana) < limiar_proximidade:
            y_texto = (media + mediana) / 2
            ax.text(i + meia_largura + 0.03, y_texto,
                    f"μ={media * 60:.1f}min / md={mediana * 60:.1f}min",
                    color="#333333", fontsize=8, fontweight="bold", va="center", bbox=caixa, zorder=6)
        else:
            ax.text(i + meia_largura + 0.03, media, f"μ={media * 60:.1f}min", color="#2a78d6",
                    fontsize=8, fontweight="bold", va="center", bbox=caixa, zorder=6)
            ax.text(i + meia_largura + 0.03, mediana, f"md={mediana * 60:.1f}min", color=NEUTRAL_GRAY,
                    fontsize=8, fontweight="bold", va="center", bbox=caixa, zorder=6)

    legenda_ref = [
        Line2D([0], [0], color="#2a78d6", linewidth=2, label="Média"),
        Line2D([0], [0], color=NEUTRAL_GRAY, linewidth=2, linestyle="--", label="Mediana"),
    ]
    ax.legend(handles=legenda_ref, loc="upper right", frameon=True, edgecolor="#333333")

    ax.set_xlabel("Modelo")
    ax.set_ylabel("Atraso de chegada (h)")
    ax.margins(x=0.12)
    n_fmt = f"{len(sub):,}".replace(",", ".")
    ax.set_title(
        f"GOL — Atraso de Chegada por Modelo de Aeronave (≥{min_etapas} etapas)\n"
        f"(truncado em cerca de Tukey [{inferior:.2f}h, {superior:.2f}h], n={n_fmt})"
    )
    fig.tight_layout()
    fig.savefig(FIG_DIR / "dist_18_atraso_chegada_por_modelo.png", dpi=150)
    plt.close(fig)


# ============================================================================
# Familia "cerca_" -- pedido explicito do usuario (2026-09-03): em vez da
# cerca de Tukey (que varia por variavel e por corte, ex.: [-0.51h,0.49h]
# em dist_04 vs [-0.68h,0.59h] em dist_15), usar um corte FIXO e redondo de
# +-60 minutos (+-1h) para folga_horas, atraso_partida_horas e
# atraso_chegada_horas, com todas as unidades exibidas em minutos (mais
# legivel que horas fracionarias numa faixa tao estreita). +-60min e' mais
# estrito que o filtro de garbage de timestamp (|atraso|>24h usado em
# dist_04/15) -- esse corte fixo ja cobre aquele caso, sem precisar repetir
# o filtro. So' existe equivalente cerca_ para os graficos que de fato
# truncam uma dessas 3 variaveis (dist_01-06, 08-12, 14-18); dist_07 (vies
# de match) e dist_13 (bases sem match) nao truncam, entao ficam sem par.
# ============================================================================

LIMITE_CERCA_MIN = 60.0  # +-60 minutos = +-1h -- valor fixo pedido pelo usuario, nao Tukey


def _cerca_hist_box(dados_horas: pd.Series, titulo: str, xlabel_base: str, filename: str) -> None:
    # folga_horas/atraso_*_horas sao todas granularidade de minuto inteiro na
    # fonte (VRA/Basica), so' com ruido de ponto flutuante da divisao por 60
    # (achado desta rodada). 80 bins sobre 120min = 1,5min/bin, desalinhado
    # do minuto -- produz um serrilhado artificial (bins alternando 1 e 2
    # valores inteiros). Arredonda pro minuto e usa bin de largura 1,
    # centralizado em cada inteiro.
    dados_min = (dados_horas * 60).round()
    fig, (ax_hist, ax_box) = plt.subplots(
        2, 1, figsize=(10, 6.5), sharex=True,
        gridspec_kw={"height_ratios": [3, 1], "hspace": 0.06},
    )
    sns.histplot(dados_min, binwidth=1, binrange=(-LIMITE_CERCA_MIN - 0.5, LIMITE_CERCA_MIN + 0.5),
                 color=GOL_ORANGE, stat="count", ax=ax_hist,
                 edgecolor="white", linewidth=0.3, alpha=0.85)
    ax_hist.set_ylabel("Frequência (nº de etapas)")

    ax_dens = ax_hist.twinx()
    sns.kdeplot(dados_min, color=NEUTRAL_GRAY, linewidth=2, ax=ax_dens)
    ax_dens.set_ylabel("Densidade")
    ax_dens.grid(False)

    ax_hist.axvline(0, color="#333333", linestyle=":", linewidth=1.3)
    ax_box.axvline(0, color="#333333", linestyle=":", linewidth=1.3)

    n_fmt = f"{len(dados_min):,}".replace(",", ".")
    media, mediana = dados_min.mean(), dados_min.median()
    ax_hist.set_title(
        f"{titulo}\n"
        f"corte fixo: [-{LIMITE_CERCA_MIN:.0f}min, +{LIMITE_CERCA_MIN:.0f}min] — "
        f"média={media:.1f}min, mediana={mediana:.1f}min, n={n_fmt}"
    )

    sns.boxplot(x=dados_min, color=GOL_ORANGE, ax=ax_box, fliersize=2, linewidth=1)
    ax_box.set_xlabel(f"{xlabel_base} (min)")
    ax_box.set_yticks([])

    fig.savefig(FIG_DIR / filename, dpi=150, bbox_inches="tight")
    plt.close(fig)


def _cerca_run_sequence(sub_truncado: pd.DataFrame, coluna: str, titulo: str,
                         ylabel_base: str, filename: str) -> pd.Series:
    diario_min = sub_truncado.set_index("dt_partida_real")[coluna].resample("D").mean().dropna() * 60
    media_geral = diario_min.mean()

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(diario_min.index, diario_min.values, color=GOL_ORANGE, linewidth=0.8, alpha=0.85)
    ax.axhline(media_geral, color=NEUTRAL_GRAY, linestyle="--", linewidth=1.3)
    ax.axhline(0, color="#333333", linestyle=":", linewidth=1.1)
    ax.annotate(f"média geral = {media_geral:.1f}min", xy=(diario_min.index[0], media_geral),
                xytext=(4, 6), textcoords="offset points", color=NEUTRAL_GRAY, fontweight="bold")
    ax.set_title(titulo)
    ax.set_xlabel("Data (ordem cronológica)")
    ax.set_ylabel(f"{ylabel_base} (min)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / filename, dpi=150)
    plt.close(fig)
    return diario_min


def _cerca_lag_plot(diario_min: pd.Series, titulo: str, xlabel_base: str,
                     ylabel_base: str, filename: str) -> float:
    anterior = diario_min.iloc[:-1].to_numpy()
    atual = diario_min.iloc[1:].to_numpy()
    r = float(np.corrcoef(anterior, atual)[0, 1])

    fig, ax = plt.subplots(figsize=(6.5, 6.5))
    ax.scatter(anterior, atual, color=GOL_ORANGE, s=14, alpha=0.5, edgecolor="none")
    lims = [min(anterior.min(), atual.min()), max(anterior.max(), atual.max())]
    ax.plot(lims, lims, color=NEUTRAL_GRAY, linestyle="--", linewidth=1.2)
    ax.set_xlim(lims)
    ax.set_ylim(lims)
    # Titulo longo demais pra largura fixa do lag plot (6.5in) -- quebra
    # "(cerca_)" em linha propria em vez de deixar cortar.
    titulo_wrap = titulo.replace(" (cerca_)", "\n(cerca_)")
    ax.set_title(f"{titulo_wrap}\nr = {r:.3f}")
    ax.set_xlabel(f"{xlabel_base} em t-1 (min)")
    ax.set_ylabel(f"{ylabel_base} em t (min)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / filename, dpi=150)
    plt.close(fig)
    return r


def _cerca_violin_por_modelo(sub_truncado: pd.DataFrame, coluna: str, titulo: str,
                              ylabel_base: str, filename: str, min_etapas: int = 1000) -> None:
    sub = sub_truncado.copy()
    sub["_valor_min"] = sub[coluna] * 60
    contagem = sub["sg_equipamento_icao"].value_counts()
    modelos = contagem[contagem >= min_etapas].index.tolist()
    sub = sub[sub["sg_equipamento_icao"].isin(modelos)]
    ordem = sub.groupby("sg_equipamento_icao")["_valor_min"].median().sort_values(ascending=False).index.tolist()

    # Largura da figura escala com o nº de modelos -- achado ao replicar
    # para a Azul (ate' 7 modelos, contra 3 da GOL): com largura fixa os
    # rotulos ao lado de cada violino invadiam o vizinho.
    fig, ax = plt.subplots(figsize=(max(9.0, 1.5 * len(ordem)), 6.5))
    sns.violinplot(data=sub, x="sg_equipamento_icao", y="_valor_min", order=ordem,
                    hue="sg_equipamento_icao", hue_order=ordem, palette=PALETA_CATEGORICA[:len(ordem)],
                    legend=False, cut=0, ax=ax)
    ax.axhline(0, color="#333333", linestyle=":", linewidth=1.2)

    # Rotulos centralizados numa faixa ACIMA de cada violino (nao mais ao
    # lado) -- cada rotulo fica confinado a coluna do seu proprio modelo,
    # sem competir por espaco horizontal com o vizinho.
    meia_largura = 0.4
    y_min, y_max = ax.get_ylim()
    folga_topo = (y_max - y_min) * 0.18
    ax.set_ylim(y_min, y_max + folga_topo)
    y_texto = y_max + folga_topo * 0.15
    for i, modelo in enumerate(ordem):
        valores = sub.loc[sub["sg_equipamento_icao"] == modelo, "_valor_min"]
        media, mediana = valores.mean(), valores.median()
        ax.hlines(media, i - meia_largura, i + meia_largura, color="#2a78d6", linewidth=2, zorder=5)
        ax.hlines(mediana, i - meia_largura, i + meia_largura, color=NEUTRAL_GRAY, linewidth=2,
                  linestyle="--", zorder=5)
        ax.text(i, y_texto, f"μ={media:.1f}min\nmd={mediana:.1f}min",
                color="#333333", fontsize=8, fontweight="bold", ha="center", va="bottom", zorder=6)

    # Legenda no canto inferior direito -- os rotulos de media/mediana agora
    # ficam numa faixa acima dos violinos, entao "upper right" colidia com
    # a ultima categoria (achado desta rodada, replicacao Azul).
    legenda_ref = [
        Line2D([0], [0], color="#2a78d6", linewidth=2, label="Média"),
        Line2D([0], [0], color=NEUTRAL_GRAY, linewidth=2, linestyle="--", label="Mediana"),
    ]
    ax.legend(handles=legenda_ref, loc="lower right", frameon=True, edgecolor="#333333")

    ax.set_xlabel("Modelo")
    ax.set_ylabel(f"{ylabel_base} (min)")
    ax.margins(x=0.12)
    n_fmt = f"{len(sub):,}".replace(",", ".")
    ax.set_title(
        f"{titulo}\n(corte fixo [-{LIMITE_CERCA_MIN:.0f}min, +{LIMITE_CERCA_MIN:.0f}min], n={n_fmt})"
    )
    fig.tight_layout()
    fig.savefig(FIG_DIR / filename, dpi=150)
    plt.close(fig)


def _cerca_bar_media_por_grupo(sub_truncado: pd.DataFrame, coluna_valor: str, coluna_grupo: str,
                                ordem_grupo, cores, titulo: str, ylabel_base: str, filename: str) -> None:
    dados = sub_truncado.copy()
    dados["_valor_min"] = dados[coluna_valor] * 60
    agg = dados.groupby(coluna_grupo)["_valor_min"].agg(["mean", "count"])
    if ordem_grupo is not None:
        agg = agg.reindex(ordem_grupo)

    fig, ax = plt.subplots(figsize=(7 if len(agg) <= 2 else 9, 5.5))
    barras = ax.bar(agg.index.astype(str), agg["mean"], color=cores[:len(agg)])
    ax.bar_label(barras, fmt="%.1f", fontweight="bold", padding=3)
    ax.axhline(0, color="#333333", linestyle=":", linewidth=1.2)
    y_rotulo = agg["mean"].max() * 0.05
    for i, (_, row) in enumerate(agg.iterrows()):
        n_fmt = f"{int(row['count']):,}".replace(",", ".")
        ax.text(i, y_rotulo, f"n={n_fmt}", ha="center", va="bottom",
                fontsize=8, color="white", fontweight="bold")
    ax.set_title(titulo)
    ax.set_ylabel(f"{ylabel_base} (média, min)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / filename, dpi=150)
    plt.close(fig)


def cerca_dist_01_03_folga(df: pd.DataFrame) -> pd.DataFrame:
    """cerca_01 (hist+box), cerca_02 (run sequence), cerca_03 (lag plot) --
    folga_horas truncada no corte fixo +-60min. Retorna o subconjunto (em
    horas) para reuso nos graficos de segmentacao cerca_08-11."""
    sub = df[df["fl_match_vra"] == 1].dropna(subset=["folga_horas"]).copy()
    n_antes = len(sub)
    limite_h = LIMITE_CERCA_MIN / 60
    sub = sub[sub["folga_horas"].between(-limite_h, limite_h)]
    n_fora = n_antes - len(sub)
    print(f"[cerca_01] corte fixo ±{LIMITE_CERCA_MIN:.0f}min (folga): "
          f"{n_fora:,} etapas fora ({100 * n_fora / n_antes:.2f}%)".replace(",", "."))

    _cerca_hist_box(sub["folga_horas"], "GOL — Distribuição de Folga (cerca_)",
                     "Folga", "cerca_dist_01_frequencia_densidade_boxplot_folga.png")
    diario_min = _cerca_run_sequence(
        sub, "folga_horas", "GOL — Run Sequence Plot: Folga Média Diária (cerca_)",
        "Folga média do dia", "cerca_dist_02_run_sequence_folga.png",
    )
    r = _cerca_lag_plot(
        diario_min, "GOL — Lag Plot (lag 1 dia): Folga Média Diária (cerca_)",
        "Folga média", "Folga média", "cerca_dist_03_lag_plot_folga.png",
    )
    print(f"[cerca_03] autocorrelação lag-1 (folga diária, corte fixo): r = {r:.3f}")
    return sub


def cerca_dist_04_06_atraso_partida(df: pd.DataFrame) -> pd.DataFrame:
    """Mesmo tratamento de cerca_dist_01_03, para atraso_partida_horas.
    +-60min e' mais estrito que o filtro de garbage |atraso|>24h usado em
    dist_04 -- ja fica coberto automaticamente, sem precisar repetir."""
    sub = df[df["fl_match_vra"] == 1].dropna(subset=["atraso_partida_horas"]).copy()
    n_antes = len(sub)
    limite_h = LIMITE_CERCA_MIN / 60
    sub = sub[sub["atraso_partida_horas"].between(-limite_h, limite_h)]
    n_fora = n_antes - len(sub)
    print(f"[cerca_04] corte fixo ±{LIMITE_CERCA_MIN:.0f}min (atraso partida): "
          f"{n_fora:,} etapas fora ({100 * n_fora / n_antes:.2f}%)".replace(",", "."))

    _cerca_hist_box(sub["atraso_partida_horas"], "GOL — Distribuição de Atraso de Partida (cerca_)",
                     "Atraso de partida", "cerca_dist_04_frequencia_densidade_boxplot_atraso.png")
    diario_min = _cerca_run_sequence(
        sub, "atraso_partida_horas",
        "GOL — Run Sequence Plot: Atraso de Partida Médio Diário (cerca_)",
        "Atraso médio do dia", "cerca_dist_05_run_sequence_atraso.png",
    )
    r = _cerca_lag_plot(
        diario_min, "GOL — Lag Plot (lag 1 dia): Atraso de Partida Médio Diário (cerca_)",
        "Atraso médio", "Atraso médio", "cerca_dist_06_lag_plot_atraso.png",
    )
    print(f"[cerca_06] autocorrelação lag-1 (atraso partida diário, corte fixo): r = {r:.3f}")
    return sub


def cerca_dist_15_17_atraso_chegada(df: pd.DataFrame) -> pd.DataFrame:
    """Mesmo tratamento de cerca_dist_01_03, para atraso_chegada_horas."""
    sub = df[df["fl_match_vra"] == 1].dropna(subset=["atraso_chegada_horas"]).copy()
    n_antes = len(sub)
    limite_h = LIMITE_CERCA_MIN / 60
    sub = sub[sub["atraso_chegada_horas"].between(-limite_h, limite_h)]
    n_fora = n_antes - len(sub)
    print(f"[cerca_15] corte fixo ±{LIMITE_CERCA_MIN:.0f}min (atraso chegada): "
          f"{n_fora:,} etapas fora ({100 * n_fora / n_antes:.2f}%)".replace(",", "."))

    _cerca_hist_box(sub["atraso_chegada_horas"], "GOL — Distribuição de Atraso de Chegada (cerca_)",
                     "Atraso de chegada", "cerca_dist_15_frequencia_densidade_boxplot_atraso_chegada.png")
    diario_min = _cerca_run_sequence(
        sub, "atraso_chegada_horas",
        "GOL — Run Sequence Plot: Atraso de Chegada Médio Diário (cerca_)",
        "Atraso médio do dia", "cerca_dist_16_run_sequence_atraso_chegada.png",
    )
    r = _cerca_lag_plot(
        diario_min, "GOL — Lag Plot (lag 1 dia): Atraso de Chegada Médio Diário (cerca_)",
        "Atraso médio", "Atraso médio", "cerca_dist_17_lag_plot_atraso_chegada.png",
    )
    print(f"[cerca_17] autocorrelação lag-1 (atraso chegada diário, corte fixo): r = {r:.3f}")
    return sub


def cerca_dist_08_folga_por_modelo(sub_folga: pd.DataFrame) -> None:
    _cerca_violin_por_modelo(
        sub_folga, "folga_horas", "GOL — Folga por Modelo de Aeronave (cerca_)",
        "Folga", "cerca_dist_08_folga_por_modelo.png",
    )


def cerca_dist_09_folga_por_hub(sub_folga: pd.DataFrame, max_bases: int = 8) -> None:
    sub = sub_folga.copy()
    sub["_valor_min"] = sub["folga_horas"] * 60
    hub = selecionar_hub(sub["sg_iata_origem"].value_counts())
    bases = hub.index.tolist()[:max_bases]
    sub = sub[sub["sg_iata_origem"].isin(bases)]
    ordem = sub.groupby("sg_iata_origem")["_valor_min"].median().sort_values(ascending=False).index.tolist()

    fig, ax = plt.subplots(figsize=(11, 6))
    sns.boxplot(data=sub, x="sg_iata_origem", y="_valor_min", order=ordem,
                hue="sg_iata_origem", hue_order=ordem, palette=PALETA_CATEGORICA[:len(ordem)],
                legend=False, fliersize=2, linewidth=1, ax=ax)
    ax.axhline(0, color="#333333", linestyle=":", linewidth=1.2)
    ax.set_title(f"GOL — Folga por Base HUB de Origem (cerca_)\n(top {len(bases)}, 80% acumulado)")
    ax.set_xlabel("Base de origem")
    ax.set_ylabel("Folga (min)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "cerca_dist_09_folga_por_hub.png", dpi=150)
    plt.close(fig)


def cerca_dist_10_folga_por_natureza(sub_folga: pd.DataFrame) -> None:
    sub = sub_folga.copy()
    sub["grupo"] = sub["ds_natureza_tipo_linha"].str.title()
    _cerca_bar_media_por_grupo(
        sub, "folga_horas", "grupo", None, PALETA_CATEGORICA,
        "GOL — Folga Média por Natureza da Linha (cerca_)",
        "Folga", "cerca_dist_10_folga_por_natureza.png",
    )


def cerca_dist_11_folga_por_continuidade(sub_folga: pd.DataFrame) -> None:
    sub = sub_folga.copy()
    sub["grupo"] = sub["fl_continuidade_ok"].map(
        {1: "Continuidade OK", 0: "Continuidade quebrada"}
    ).fillna("Primeira etapa (sem anterior)")
    ordem = ["Continuidade OK", "Continuidade quebrada", "Primeira etapa (sem anterior)"]
    cores = [PALETA_CATEGORICA[0], PALETA_CATEGORICA[7], PALETA_CATEGORICA[3]]
    _cerca_bar_media_por_grupo(
        sub, "folga_horas", "grupo", ordem, cores,
        "GOL — Folga Média vs. Continuidade da Rotação (cerca_)",
        "Folga", "cerca_dist_11_folga_por_continuidade.png",
    )


def cerca_dist_12_atraso_por_modelo(sub_atraso_partida: pd.DataFrame) -> None:
    _cerca_violin_por_modelo(
        sub_atraso_partida, "atraso_partida_horas",
        "GOL — Atraso de Partida por Modelo de Aeronave (cerca_)",
        "Atraso de partida", "cerca_dist_12_atraso_por_modelo.png",
    )


def cerca_dist_18_atraso_chegada_por_modelo(sub_atraso_chegada: pd.DataFrame) -> None:
    _cerca_violin_por_modelo(
        sub_atraso_chegada, "atraso_chegada_horas",
        "GOL — Atraso de Chegada por Modelo de Aeronave (cerca_)",
        "Atraso de chegada", "cerca_dist_18_atraso_chegada_por_modelo.png",
    )


def cerca_dist_14_atraso_recuperado_em_voo(df: pd.DataFrame, limite_valido: float = 24.0) -> None:
    """Mesma pergunta do dist_14 (Δ = atraso_chegada - atraso_partida), mas
    aqui a propria diferenca e' truncada no corte fixo +-60min, em vez do
    recorte por percentil usado no dist_14 original."""
    sub = df[df["fl_match_vra"] == 1].dropna(subset=["atraso_partida_horas", "atraso_chegada_horas"]).copy()
    sub = sub[(sub["atraso_partida_horas"].abs() <= limite_valido) &
              (sub["atraso_chegada_horas"].abs() <= limite_valido)]
    diff_horas = sub["atraso_chegada_horas"] - sub["atraso_partida_horas"]

    n_antes = len(diff_horas)
    limite_h = LIMITE_CERCA_MIN / 60
    diff_horas = diff_horas[diff_horas.between(-limite_h, limite_h)]
    n_fora = n_antes - len(diff_horas)
    print(f"[cerca_14] corte fixo ±{LIMITE_CERCA_MIN:.0f}min (Δ atraso em voo): "
          f"{n_fora:,} etapas fora ({100 * n_fora / n_antes:.2f}%)".replace(",", "."))

    _cerca_hist_box(
        diff_horas, "GOL — Δ Atraso em Voo: Atraso Chegada − Atraso Partida (cerca_)",
        "Δ atraso em voo", "cerca_dist_14_atraso_recuperado_em_voo.png",
    )
    media_min, mediana_min = diff_horas.mean() * 60, diff_horas.median() * 60
    print(f"[cerca_14] Δ atraso em voo (corte fixo): média={media_min:.1f}min, mediana={mediana_min:.1f}min "
          "(negativo=recuperou)")


def main() -> None:
    df = load_data()
    print(f"{len(df):,} etapas carregadas".replace(",", "."))

    inferior_folga, superior_folga = fig_dist_01_frequencia_densidade_boxplot_folga(df)
    diario_folga = fig_dist_02_run_sequence_folga(df)
    r_folga = fig_dist_03_lag_plot_folga(diario_folga)
    print(f"[dist_03] autocorrelação lag-1 (folga diária): r = {r_folga:.3f}")

    inferior_atraso, superior_atraso, sub_atraso = fig_dist_04_frequencia_densidade_boxplot_atraso(df)
    diario_atraso = fig_dist_05_run_sequence_atraso(sub_atraso)
    r_atraso = fig_dist_06_lag_plot_atraso(diario_atraso)
    print(f"[dist_06] autocorrelação lag-1 (atraso diário): r = {r_atraso:.3f}")

    fig_dist_07_vies_match_vra(df)

    # Segmentacao -- so' agora, depois de confirmar forma, estabilidade
    # temporal e viés de match (dist_01-07). Truncado na cerca de Tukey
    # de cada variavel.
    fig_dist_08_folga_por_modelo(df, inferior_folga, superior_folga)
    fig_dist_09_folga_por_hub(df, inferior_folga, superior_folga)
    fig_dist_10_folga_por_natureza(df, inferior_folga, superior_folga)
    fig_dist_11_folga_por_continuidade(df, inferior_folga, superior_folga)
    fig_dist_12_atraso_por_modelo(sub_atraso, inferior_atraso, superior_atraso)
    fig_dist_13_top_bases_sem_match(df)
    fig_dist_14_atraso_recuperado_em_voo(sub_atraso)

    inferior_chegada, superior_chegada, sub_atraso_chegada = fig_dist_15_frequencia_densidade_boxplot_atraso_chegada(df)
    diario_chegada = fig_dist_16_run_sequence_atraso_chegada(sub_atraso_chegada)
    r_chegada = fig_dist_17_lag_plot_atraso_chegada(diario_chegada)
    print(f"[dist_17] autocorrelação lag-1 (atraso chegada diário): r = {r_chegada:.3f}")
    fig_dist_18_atraso_chegada_por_modelo(sub_atraso_chegada, inferior_chegada, superior_chegada)

    # Familia cerca_ -- corte fixo +-60min, unidades em minutos (ver docstring
    # da secao acima). So' cobre os graficos que truncam folga/atraso.
    sub_cerca_folga = cerca_dist_01_03_folga(df)
    cerca_dist_08_folga_por_modelo(sub_cerca_folga)
    cerca_dist_09_folga_por_hub(sub_cerca_folga)
    cerca_dist_10_folga_por_natureza(sub_cerca_folga)
    cerca_dist_11_folga_por_continuidade(sub_cerca_folga)

    sub_cerca_atraso_partida = cerca_dist_04_06_atraso_partida(df)
    cerca_dist_12_atraso_por_modelo(sub_cerca_atraso_partida)

    cerca_dist_14_atraso_recuperado_em_voo(df)

    sub_cerca_atraso_chegada = cerca_dist_15_17_atraso_chegada(df)
    cerca_dist_18_atraso_chegada_por_modelo(sub_cerca_atraso_chegada)

    print(f"Figuras salvas em {FIG_DIR}")


if __name__ == "__main__":
    main()
