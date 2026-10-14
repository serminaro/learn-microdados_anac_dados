"""Distribuicao do tempo de solo -- Azul, so passageiro. Espelho de
distribuicao_tempo_solo_gol.py, agora para a Azul (AZU).

Fonte: fato_rotacao_aeronave_gol_azul (SPEC-012) + basica_curated_deep so
para filtrar PASSAGEIRO (mesma tecnica de load_data em pandas .isin, nao
JOIN em SQL sem indice).

Limpeza de dado: feita no banco (fl_solo_valido, DDL_005, 2026-09-02),
nao em pandas -- exclui negativo, continuidade de rotacao quebrada e
> 72h (medido para GOL+Azul juntos, ver DDL_005). load_data() so filtra
fl_solo_valido = 1.

Roda com: conda run -n gov-sermi-perf python analise/a3_tempo_de_solo/distribuicao_tempo_solo_azul.py
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
from pareto_hub import selecionar_hub  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = REPO_ROOT / "db" / "anac_basica.sqlite"
FIG_DIR = REPO_ROOT / "analise" / "a3_tempo_de_solo" / "a3_figuras_azul"
FIG_DIR.mkdir(parents=True, exist_ok=True)

WINDOW_FULL = ("2021-01-01", "2026-07-31")

AZUL_BLUE = "#0039A6"
NEUTRAL_GRAY = "#4d4d4d"
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
    """Etapas PASSAGEIRO da Azul, dt_partida_real dentro de WINDOW_FULL,
    com fl_solo_valido = 1 (DDL_005: exclui negativo, continuidade
    quebrada e > 72h -- ver sql/curated_deep/DDL_005_..._sqlite.sql)."""
    con = sqlite3.connect(DB_PATH)
    ids_passageiro = pd.read_sql_query(
        "SELECT id_basica FROM basica_curated_deep "
        "WHERE sg_empresa_icao = 'AZU' AND ds_servico_tipo_linha = 'PASSAGEIRO'",
        con,
    )["id_basica"]

    df = pd.read_sql_query(
        """
        SELECT id_basica, ds_matricula, sg_equipamento_icao,
               sg_icao_origem, sg_icao_destino, dt_partida_real, hr_partida_real,
               km_distancia, nr_horas_voadas, tempo_solo_horas
        FROM fato_rotacao_aeronave_gol_azul
        WHERE sg_empresa_icao = 'AZU'
          AND fl_solo_valido = 1
          AND dt_partida_real BETWEEN ? AND ?
        """,
        con, params=WINDOW_FULL, parse_dates=["dt_partida_real"],
    )
    con.close()

    df = df[df["id_basica"].isin(ids_passageiro)].reset_index(drop=True)

    hr = df["hr_partida_real"].str.split(":", expand=True).astype(int)
    df["hora_partida_decimal"] = hr[0] + hr[1] / 60 + hr[2] / 3600

    return aplicar_iata(df)


def calcular_corte_outlier(serie: pd.Series) -> tuple[float, float]:
    """Cerca de Tukey (1.5x IQR). Mesma convencao do espelho GOL: aqui
    'outlier' cobre desde pernoite legitimo ate parada de manutencao,
    nao separa um do outro."""
    q1, q3 = serie.quantile([0.25, 0.75])
    iqr = q3 - q1
    return q1 - 1.5 * iqr, q3 + 1.5 * iqr



def fig_dist_01_frequencia_densidade_boxplot(df: pd.DataFrame) -> tuple[float, float]:
    solo = df["tempo_solo_horas"]
    inferior, superior = calcular_corte_outlier(solo)
    inferior_valido = max(inferior, 0.0)
    n_outliers = int(((solo < inferior_valido) | (solo > superior)).sum())
    pct_outliers = 100 * n_outliers / len(solo)

    # eixo/binagem recortados (mesma tecnica do espelho GOL): bins de
    # sns.histplot sao calculados sobre o range dos dados ANTES de
    # qualquer set_xlim, entao filtra os dados de visualizacao antes.
    p99 = solo.quantile(0.99)
    xlim_max = max(superior * 1.8, p99)
    solo_vis = solo[solo <= xlim_max]

    fig, (ax_hist, ax_box) = plt.subplots(
        2, 1, figsize=(10, 6.5), sharex=True,
        gridspec_kw={"height_ratios": [3, 1], "hspace": 0.06},
    )

    sns.histplot(solo_vis, bins=80, binrange=(0, xlim_max), color=AZUL_BLUE, stat="count", ax=ax_hist,
                 edgecolor="white", linewidth=0.3, alpha=0.85)
    ax_hist.set_ylabel("Frequência (nº de etapas)")

    ax_dens = ax_hist.twinx()
    sns.kdeplot(solo_vis, color=NEUTRAL_GRAY, linewidth=2, ax=ax_dens, clip=(0, xlim_max))
    ax_dens.set_ylabel("Densidade")
    ax_dens.grid(False)

    for corte in (inferior_valido, superior):
        ax_hist.axvline(corte, color=NEUTRAL_GRAY, linestyle="--", linewidth=1.3)
        ax_box.axvline(corte, color=NEUTRAL_GRAY, linestyle="--", linewidth=1.3)

    n_outliers_fmt = f"{n_outliers:,}".replace(",", ".")
    max_fmt = f"{solo.max():,.0f}".replace(",", ".")
    ax_hist.set_title(
        "Azul — Distribuição de Tempo de Solo (frequência + densidade)\n"
        f"corte de outlier (Tukey, 1,5×IQR): [{inferior_valido:.2f}h, {superior:.2f}h] "
        f"— {n_outliers_fmt} etapas fora ({pct_outliers:.2f}%) — inclui pernoite legítimo\n"
        f"(eixo recortado em {xlim_max:.1f}h; máximo real observado: {max_fmt}h)"
    )
    ax_hist.set_xlim(0, xlim_max)

    sns.boxplot(x=solo, color=AZUL_BLUE, ax=ax_box, fliersize=2, linewidth=1)
    ax_box.set_xlabel("Tempo de solo (h)")
    ax_box.set_yticks([])

    fig.savefig(FIG_DIR / "dist_01_frequencia_densidade_boxplot_tempo_solo.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    print(
        f"[dist_01] corte outlier Tukey: inferior={inferior:.3f}h (usado {inferior_valido:.3f}h; "
        f"nao pode ser negativo) | superior={superior:.3f}h | "
        f"{n_outliers_fmt} etapas fora ({pct_outliers:.2f}%) | máximo observado: {solo.max():.1f}h"
    )
    return inferior_valido, superior


def fig_dist_02_violin_por_modelo(df: pd.DataFrame, superior: float, min_etapas: int = 1000) -> None:
    """Painel unico -- df ja chega truncado em <= superior (main() aplica
    isso uma vez, logo apos dist_01)."""
    contagem = df["sg_equipamento_icao"].value_counts()
    modelos = contagem[contagem >= min_etapas].index.tolist()[:len(PALETA_CATEGORICA)]
    sub = df[df["sg_equipamento_icao"].isin(modelos)]
    ordem = (
        sub.groupby("sg_equipamento_icao")["tempo_solo_horas"]
        .median().sort_values(ascending=False).index.tolist()
    )
    n_fmt = f"{len(sub):,}".replace(",", ".")

    fig, ax = plt.subplots(figsize=(10, 6.5))
    sns.violinplot(
        data=sub, x="sg_equipamento_icao", y="tempo_solo_horas", order=ordem,
        hue="sg_equipamento_icao", hue_order=ordem, palette=PALETA_CATEGORICA[:len(ordem)],
        legend=False, cut=0, ax=ax,
    )

    meia_largura = 0.4
    for i, modelo in enumerate(ordem):
        valores = sub.loc[sub["sg_equipamento_icao"] == modelo, "tempo_solo_horas"]
        media, mediana = valores.mean(), valores.median()
        ax.hlines(media, i - meia_largura, i + meia_largura, color="#2a78d6", linewidth=2, zorder=5)
        ax.hlines(mediana, i - meia_largura, i + meia_largura, color=NEUTRAL_GRAY, linewidth=2,
                  linestyle="--", zorder=5)
        ax.text(i + meia_largura + 0.03, media, f"μ={media:.2f}h", color="#2a78d6",
                fontsize=8, fontweight="bold", va="center")
        ax.text(i + meia_largura + 0.03, mediana, f"md={mediana:.2f}h", color=NEUTRAL_GRAY,
                fontsize=8, fontweight="bold", va="center")

    legenda_ref = [
        Line2D([0], [0], color="#2a78d6", linewidth=2, label="Média"),
        Line2D([0], [0], color=NEUTRAL_GRAY, linewidth=2, linestyle="--", label="Mediana"),
    ]
    ax.legend(handles=legenda_ref, loc="upper left", frameon=True, edgecolor="#333333")

    ax.set_xlabel("Modelo")
    ax.set_ylabel("Tempo de solo (h)")
    ax.tick_params(axis="x", rotation=30)
    ax.margins(x=0.12)
    ax.set_title(
        f"Azul — Distribuição de Tempo de Solo por Modelo (≥{min_etapas} etapas)\n"
        f"(truncado em ≤{superior:.2f}h, cerca de Tukey de dist_01, n={n_fmt})"
    )
    fig.tight_layout()
    fig.savefig(FIG_DIR / "dist_02_violin_tempo_solo_por_modelo.png", dpi=150)
    plt.close(fig)


def fig_dist_03_dispersao_tempo_solo_etapa_media(df: pd.DataFrame, min_etapas: int = 30) -> None:
    """1 ponto = 1 matricula (media de solo e de etapa no periodo)."""
    por_matricula = (
        df.groupby("ds_matricula")
        .agg(
            tempo_solo_medio=("tempo_solo_horas", "mean"),
            etapa_media=("nr_horas_voadas", "mean"),
            n_etapas=("nr_horas_voadas", "count"),
            modelo=("sg_equipamento_icao", lambda s: s.mode().iat[0]),
        )
    )
    por_matricula = por_matricula[por_matricula["n_etapas"] >= min_etapas]

    modelos = por_matricula["modelo"].value_counts().index.tolist()[:len(PALETA_CATEGORICA)]
    cores = {m: c for m, c in zip(modelos, PALETA_CATEGORICA)}
    por_matricula = por_matricula[por_matricula["modelo"].isin(modelos)]

    fig, ax = plt.subplots(figsize=(9, 6.5))
    for modelo in modelos:
        sub = por_matricula[por_matricula["modelo"] == modelo]
        ax.scatter(
            sub["etapa_media"], sub["tempo_solo_medio"],
            color=cores[modelo], label=modelo, s=42, alpha=0.8,
            edgecolor="white", linewidth=0.5,
        )
    ax.set_title(
        "Azul — Tempo de Solo x Etapa Média, por Aeronave\n"
        f"(1 ponto = 1 matrícula, ≥{min_etapas} etapas no período)"
    )
    ax.set_xlabel("Etapa média (h)")
    ax.set_ylabel("Tempo de solo médio (h)")
    ax.legend(title="Modelo", frameon=True, edgecolor="#333333")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "dist_03_dispersao_tempo_solo_etapa_media_por_matricula.png", dpi=150)
    plt.close(fig)


def fig_dist_04_dispersao_tempo_solo_distancia(df: pd.DataFrame, min_etapas: int = 1000,
                                                amostra: int = 30_000, seed: int = 42) -> None:
    """Tempo de solo depende da distancia da PROXIMA etapa (a que ele antecede)?"""
    contagem = df["sg_equipamento_icao"].value_counts()
    modelos = contagem[contagem >= min_etapas].index.tolist()
    sub = df[df["sg_equipamento_icao"].isin(modelos)].dropna(subset=["km_distancia"])
    if len(sub) > amostra:
        sub = sub.sample(amostra, random_state=seed)

    fig, ax = plt.subplots(figsize=(9, 6.5))
    sns.scatterplot(
        data=sub, x="km_distancia", y="tempo_solo_horas",
        hue="sg_equipamento_icao", palette=PALETA_CATEGORICA[:len(modelos)],
        s=18, alpha=0.5, edgecolor="none", ax=ax,
    )
    n_amostra_fmt = f"{len(sub):,}".replace(",", ".")
    ax.set_title(f"Azul — Tempo de Solo x Distância (da etapa seguinte), por Modelo\n(amostra de {n_amostra_fmt} etapas)")
    ax.set_xlabel("Distância da etapa seguinte (km)")
    ax.set_ylabel("Tempo de solo (h)")
    ax.legend(title="Modelo", frameon=True, edgecolor="#333333")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "dist_04_dispersao_tempo_solo_distancia_por_modelo.png", dpi=150)
    plt.close(fig)


def fig_dist_05_distribuicao_por_hub(df: pd.DataFrame, max_bases: int = 8) -> None:
    hub = selecionar_hub(df["sg_iata_origem"].value_counts())
    bases = hub.index.tolist()[:max_bases]
    sub = df[df["sg_iata_origem"].isin(bases)]
    ordem = sub.groupby("sg_iata_origem")["tempo_solo_horas"].median().sort_values(ascending=False).index.tolist()

    fig, ax = plt.subplots(figsize=(11, 6))
    sns.boxplot(
        data=sub, x="sg_iata_origem", y="tempo_solo_horas", order=ordem,
        hue="sg_iata_origem", hue_order=ordem, palette=PALETA_CATEGORICA[:len(ordem)], legend=False,
        fliersize=2, linewidth=1, ax=ax,
    )
    ax.set_title(f"Azul — Distribuição de Tempo de Solo por Base HUB de Origem\n(top {len(bases)}, 80% acumulado)")
    ax.set_xlabel("Base de origem")
    ax.set_ylabel("Tempo de solo (h)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "dist_05_distribuicao_tempo_solo_por_hub.png", dpi=150)
    plt.close(fig)


def fig_dist_06_distribuicao_por_destino(df: pd.DataFrame, max_destinos: int = 8) -> None:
    hub_destino = selecionar_hub(df["sg_iata_destino"].value_counts())
    destinos = hub_destino.index.tolist()[:max_destinos]
    sub = df[df["sg_iata_destino"].isin(destinos)]
    ordem = sub.groupby("sg_iata_destino")["tempo_solo_horas"].median().sort_values(ascending=False).index.tolist()

    fig, ax = plt.subplots(figsize=(11, 6))
    sns.boxplot(
        data=sub, x="sg_iata_destino", y="tempo_solo_horas", order=ordem,
        hue="sg_iata_destino", hue_order=ordem, palette=PALETA_CATEGORICA[:len(ordem)], legend=False,
        fliersize=2, linewidth=1, ax=ax,
    )
    ax.set_title(f"Azul — Distribuição de Tempo de Solo por Destino\n(top {len(destinos)}, 80% acumulado)")
    ax.set_xlabel("Destino")
    ax.set_ylabel("Tempo de solo (h)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "dist_06_distribuicao_tempo_solo_por_destino.png", dpi=150)
    plt.close(fig)


def fig_dist_07_correlacao(df: pd.DataFrame, superior: float) -> None:
    """Painel unico -- mesma razao do dist_02: df ja chega truncado."""
    cols = {
        "tempo_solo_horas": "Tempo de solo (h)",
        "nr_horas_voadas": "Etapa média (h)",
        "km_distancia": "Distância (km)",
    }
    n_fmt = f"{len(df):,}".replace(",", ".")
    corr = df[list(cols)].rename(columns=cols).corr(method="pearson")

    fig, ax = plt.subplots(figsize=(6, 5.2))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", vmin=-1, vmax=1,
                square=True, cbar_kws={"label": "Correlação de Pearson"}, ax=ax)
    ax.set_title(
        "Azul — Correlação entre Tempo de Solo, Etapa Média e Distância\n"
        f"(truncado em ≤{superior:.2f}h, n={n_fmt})"
    )
    fig.tight_layout()
    fig.savefig(FIG_DIR / "dist_07_correlacao_tempo_solo_etapa_distancia.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def fig_dist_08_violin_sem_outlier_referencias(df: pd.DataFrame, superior: float) -> None:
    """df ja chega truncado em <= superior -- sem filtro interno, so usa
    a coluna direto."""
    sub = df["tempo_solo_horas"]
    media = sub.mean()
    mediana = sub.median()
    q1, q3 = sub.quantile([0.25, 0.75])
    n_fmt = f"{len(sub):,}".replace(",", ".")

    fig, ax = plt.subplots(figsize=(6.5, 7))
    sns.violinplot(y=sub, color=AZUL_BLUE, cut=0, inner="quartile", ax=ax)

    referencias = [
        (media, "Média", "#2a78d6", "-"),
        (mediana, "Mediana (Q2)", NEUTRAL_GRAY, "--"),
        (q1, "Q1", "#4a3aa7", ":"),
        (q3, "Q3", "#008300", ":"),
    ]
    for valor, rotulo, cor, estilo in referencias:
        ax.axhline(valor, color=cor, linestyle=estilo, linewidth=1.6, zorder=5)
        ax.text(
            0.62, valor, f"{rotulo} = {valor:.2f}h", transform=ax.get_yaxis_transform(),
            color=cor, fontweight="bold", fontsize=9, va="center", zorder=6,
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.85, "pad": 1.5},
        )

    ax.set_title(
        f"Azul — Distribuição de Tempo de Solo, Sem Outlier\n"
        f"(truncado em ≤{superior:.2f}h, cerca de Tukey de dist_01, n={n_fmt})"
    )
    ax.set_ylabel("Tempo de solo (h)")
    ax.set_xticks([])
    ax.set_xlim(-0.5, 1.3)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "dist_08_violin_sem_outlier_referencias.png", dpi=150)
    plt.close(fig)


def fig_dist_09_tempo_solo_x_horario_partida(df: pd.DataFrame, superior: float) -> None:
    """Hexbin -- tempo de solo no X, horario no Y. df ja chega truncado em <= superior."""
    fig, ax = plt.subplots(figsize=(9, 8))
    hb = ax.hexbin(
        df["tempo_solo_horas"], df["hora_partida_decimal"],
        gridsize=60, cmap="YlOrBr", mincnt=1,
    )
    cbar = fig.colorbar(hb, ax=ax)
    cbar.set_label("Nº de etapas (por célula)")

    ax.set_ylim(0, 24)
    ax.set_yticks(range(0, 25, 3))
    ax.set_yticklabels([f"{h:02d}:00" for h in range(0, 25, 3)])
    ax.set_title(f"Azul — Tempo de Solo x Horário de Partida (da etapa seguinte)\n"
                 f"(hexbin, truncado em ≤{superior:.2f}h)")
    ax.set_xlabel("Tempo de solo (h)")
    ax.set_ylabel("Horário de partida")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "dist_09_tempo_solo_x_horario_partida.png", dpi=150)
    plt.close(fig)


def fig_dist_10_hexbin_por_hub_individual(df: pd.DataFrame, top_n: int = 10) -> list[str]:
    """df ja chega truncado em <= superior. Tempo de solo no X, horario no Y."""
    top_bases = df["sg_iata_origem"].value_counts().head(top_n).index.tolist()

    for base in top_bases:
        sub = df[df["sg_iata_origem"] == base]
        n_fmt = f"{len(sub):,}".replace(",", ".")

        fig, ax = plt.subplots(figsize=(7, 6.5))
        hb = ax.hexbin(sub["tempo_solo_horas"], sub["hora_partida_decimal"],
                        gridsize=40, cmap="YlOrBr", mincnt=1)
        cbar = fig.colorbar(hb, ax=ax)
        cbar.set_label("Nº de etapas (por célula)")

        ax.set_ylim(0, 24)
        ax.set_yticks(range(0, 25, 3))
        ax.set_yticklabels([f"{h:02d}:00" for h in range(0, 25, 3)])
        ax.set_title(f"Azul — Tempo de Solo x Horário de Partida — {base}\n(hexbin, n={n_fmt})")
        ax.set_xlabel("Tempo de solo (h)")
        ax.set_ylabel("Horário de partida")
        fig.tight_layout()
        fig.savefig(FIG_DIR / f"dist_10_hexbin_horario_partida_{base}.png", dpi=150)
        plt.close(fig)

    return top_bases


def fig_dist_11_12_hexbin_grid_top6(df: pd.DataFrame, top6: list[str]) -> None:
    """df ja chega truncado em <= superior. Tempo de solo no X, horario no Y."""
    layouts = [
        ("dist_11_hexbin_grid_top6_2x3.png", 2, 3),
        ("dist_12_hexbin_grid_top6_3x2.png", 3, 2),
    ]
    for fname, nrows, ncols in layouts:
        fig, axes = plt.subplots(nrows, ncols, figsize=(5.2 * ncols, 4.4 * nrows),
                                  sharex=True, sharey=True)
        axes_flat = axes.flatten()
        hbs = []
        for ax, base in zip(axes_flat, top6):
            sub = df[df["sg_iata_origem"] == base]
            hb = ax.hexbin(sub["tempo_solo_horas"], sub["hora_partida_decimal"],
                            gridsize=32, cmap="YlOrBr", mincnt=1)
            hbs.append(hb)
            n_fmt = f"{len(sub):,}".replace(",", ".")
            ax.set_title(f"{base} (n={n_fmt})", fontweight="bold", fontsize=10)
            ax.set_ylim(0, 24)
            ax.set_yticks(range(0, 25, 6))
            ax.set_yticklabels([f"{h:02d}:00" for h in range(0, 25, 6)])

        vmax_global = max(hb.get_array().max() for hb in hbs)
        for hb in hbs:
            hb.set_clim(0, vmax_global)

        fig.supxlabel("Tempo de solo (h)")
        fig.supylabel("Horário de partida")
        cbar = fig.colorbar(hbs[0], ax=axes_flat, shrink=0.85)
        cbar.set_label("Nº de etapas por célula (escala compartilhada entre os 6 painéis)")
        fig.suptitle(f"Azul — Tempo de Solo x Horário de Partida, Top 6 Bases ({nrows}x{ncols})",
                     fontweight="bold")
        fig.savefig(FIG_DIR / fname, dpi=150, bbox_inches="tight")
        plt.close(fig)


def fig_dist_13_run_sequence(df: pd.DataFrame) -> pd.Series:
    diario = df.set_index("dt_partida_real")["tempo_solo_horas"].resample("D").mean().dropna()
    media_geral = diario.mean()

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(diario.index, diario.values, color=AZUL_BLUE, linewidth=0.8, alpha=0.85)
    ax.axhline(media_geral, color=NEUTRAL_GRAY, linestyle="--", linewidth=1.3)
    ax.annotate(f"média geral = {media_geral:.2f}h", xy=(diario.index[0], media_geral),
                xytext=(4, 6), textcoords="offset points", color=NEUTRAL_GRAY, fontweight="bold")
    ax.set_title("Azul — Run Sequence Plot: Tempo de Solo Médio Diário (2021-2026)")
    ax.set_xlabel("Data (ordem cronológica)")
    ax.set_ylabel("Tempo de solo médio do dia (h)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "dist_13_run_sequence_tempo_solo_diario.png", dpi=150)
    plt.close(fig)
    return diario


def fig_dist_14_lag_plot(diario: pd.Series) -> float:
    anterior = diario.iloc[:-1].to_numpy()
    atual = diario.iloc[1:].to_numpy()
    r = float(np.corrcoef(anterior, atual)[0, 1])

    fig, ax = plt.subplots(figsize=(6.5, 6.5))
    ax.scatter(anterior, atual, color=AZUL_BLUE, s=14, alpha=0.5, edgecolor="none")
    lims = [min(anterior.min(), atual.min()), max(anterior.max(), atual.max())]
    ax.plot(lims, lims, color=NEUTRAL_GRAY, linestyle="--", linewidth=1.2)
    ax.set_xlim(lims)
    ax.set_ylim(lims)
    ax.set_title(f"Azul — Lag Plot (lag 1 dia): Tempo de Solo Médio Diário\nr = {r:.3f}")
    ax.set_xlabel("Tempo de solo médio em t-1 (h)")
    ax.set_ylabel("Tempo de solo médio em t (h)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "dist_14_lag_plot_tempo_solo_diario.png", dpi=150)
    plt.close(fig)
    return r


def fig_dist_15_mix_frota_temporal(df: pd.DataFrame, min_etapas: int = 1000) -> pd.DataFrame:
    contagem = df["sg_equipamento_icao"].value_counts()
    modelos = contagem[contagem >= min_etapas].index.tolist()
    sub = df[df["sg_equipamento_icao"].isin(modelos)]

    mensal_contagem = (
        sub.set_index("dt_partida_real")
        .groupby("sg_equipamento_icao")["tempo_solo_horas"]
        .resample("MS").count()
        .unstack(0)
        .fillna(0)
    )
    ordem = mensal_contagem.sum().sort_values(ascending=False).index.tolist()
    share = mensal_contagem[ordem].div(mensal_contagem[ordem].sum(axis=1), axis=0) * 100

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.stackplot(share.index, [share[m] for m in ordem], labels=ordem,
                 colors=PALETA_CATEGORICA[:len(ordem)], alpha=0.9)
    ax.set_ylim(0, 100)
    ax.set_title("Azul — Composição da Frota por Mês (% de etapas)")
    ax.set_xlabel("Mês")
    ax.set_ylabel("% de etapas do mês")
    ax.legend(title="Modelo", loc="upper left", frameon=True, edgecolor="#333333")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "dist_15_mix_frota_temporal.png", dpi=150)
    plt.close(fig)

    return mensal_contagem


def fig_dist_16_decomposicao_mix_vs_intramodelo(df: pd.DataFrame, mensal_contagem: pd.DataFrame,
                                                 ano_base: str = "2021") -> None:
    modelos = mensal_contagem.columns.tolist()
    sub = df[df["sg_equipamento_icao"].isin(modelos)]

    duracao_mensal = (
        sub.set_index("dt_partida_real")
        .groupby("sg_equipamento_icao")["tempo_solo_horas"]
        .resample("MS").mean()
        .unstack(0)
    )
    share_mensal = mensal_contagem.div(mensal_contagem.sum(axis=1), axis=0)
    share_base = share_mensal.loc[ano_base].mean()

    real = (share_mensal[modelos] * duracao_mensal[modelos]).sum(axis=1)
    contrafactual = (duracao_mensal[modelos] * share_base[modelos]).sum(axis=1)

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(real.index, real.values, color=AZUL_BLUE, linewidth=2, marker="o", markersize=3,
             label="Real (mix de frota variando no tempo)")
    ax.plot(contrafactual.index, contrafactual.values, color=NEUTRAL_GRAY, linewidth=2,
             linestyle="--", label=f"Contrafactual (mix travado em {ano_base})")
    ax.set_title(f"Azul — Tempo de Solo: Real x Contrafactual com Mix de Frota Travado em {ano_base}")
    ax.set_xlabel("Mês")
    ax.set_ylabel("Tempo de solo médio (h)")
    ax.legend(frameon=True, edgecolor="#333333")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "dist_16_decomposicao_mix_vs_intramodelo.png", dpi=150)
    plt.close(fig)


def main() -> None:
    df = load_data()
    print(f"{len(df):,} etapas carregadas ({df['ds_matricula'].nunique()} matrículas)".replace(",", "."))

    inferior, superior = fig_dist_01_frequencia_densidade_boxplot(df)

    df_truncado = df[df["tempo_solo_horas"] <= superior].reset_index(drop=True)
    n_fmt = f"{len(df_truncado):,}".replace(",", ".")
    n_total_fmt = f"{len(df):,}".replace(",", ".")
    print(f"[main] dados truncados em <= {superior:.2f}h para dist_02 em diante: "
          f"{n_fmt} de {n_total_fmt} etapas")

    fig_dist_02_violin_por_modelo(df_truncado, superior)
    fig_dist_03_dispersao_tempo_solo_etapa_media(df_truncado)
    fig_dist_04_dispersao_tempo_solo_distancia(df_truncado)
    fig_dist_05_distribuicao_por_hub(df_truncado)
    fig_dist_06_distribuicao_por_destino(df_truncado)
    fig_dist_07_correlacao(df_truncado, superior)
    fig_dist_08_violin_sem_outlier_referencias(df_truncado, superior)
    fig_dist_09_tempo_solo_x_horario_partida(df_truncado, superior)

    top10 = fig_dist_10_hexbin_por_hub_individual(df_truncado)
    print(f"[dist_10] top 10 bases: {', '.join(top10)}")
    fig_dist_11_12_hexbin_grid_top6(df_truncado, top10[:6])

    diario = fig_dist_13_run_sequence(df_truncado)
    r_lag1 = fig_dist_14_lag_plot(diario)
    print(f"[dist_14] autocorrelação lag-1 (tempo de solo médio diário): r = {r_lag1:.3f}")

    mensal_contagem = fig_dist_15_mix_frota_temporal(df_truncado)
    fig_dist_16_decomposicao_mix_vs_intramodelo(df_truncado, mensal_contagem)

    print(f"Figuras salvas em {FIG_DIR}")


if __name__ == "__main__":
    main()
