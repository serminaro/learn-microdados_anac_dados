"""Distribuicao da etapa media -- Azul, so passageiro (espelho de
distribuicao_etapa_media_gol.py, mesma convencao do SPEC-013).

Complementa analise_etapa_media_azul.py: aquele script olha media/mediana ao
longo do tempo e por corte; este olha a FORMA da distribuicao em si (forma,
outliers, dispersao, correlacao).

Fonte: fato_rotacao_aeronave_gol_azul (SPEC-012) + basica_curated_deep so
para filtrar PASSAGEIRO (fato_rotacao nao carrega essa coluna -- e' fato
por etapa da Basica inteira, cargueiro incluso). Filtro feito em pandas
(.isin) e nao em SQL porque nenhuma das duas tabelas tem indice em
id_basica -- o JOIN direto no SQLite ficou lento (testado, abortado, ver
distribuicao_etapa_media_gol.py).

Roda com: conda run -n gov-sermi-perf python analise/a4_etapa_media/distribuicao_etapa_media_azul.py
"""

from pathlib import Path
import sqlite3

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from iata_bases import aplicar_iata  # noqa: E402
from pareto_hub import selecionar_hub  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = REPO_ROOT / "db" / "anac_basica.sqlite"
FIG_DIR = REPO_ROOT / "analise" / "a4_etapa_media" / "a4_figuras_azul"
FIG_DIR.mkdir(parents=True, exist_ok=True)

WINDOW_FULL = ("2021-01-01", "2026-07-31")

# Azul da marca (aproximacao, mesmo hex ja usado em
# analise/a5_block_time/analise_block_time_gol_azul.py -- nao inventar
# uma segunda aproximacao do mesmo azul).
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
    """Etapas PASSAGEIRO da Azul, dt_partida_real dentro de WINDOW_FULL.

    fato_rotacao_aeronave_gol_azul cobre GOL+Azul, passageiro+cargueiro
    (herda tudo de basica_curated_deep sem filtro). Filtra por empresa no
    SQL (indice existe), traz id_basica, e so depois filtra PASSAGEIRO em
    pandas contra a lista de id_basica validos -- evita o JOIN sem indice.
    """
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
    """Cerca de Tukey (1.5x IQR) -- convencao padrao para 'valor de corte de outlier'."""
    q1, q3 = serie.quantile([0.25, 0.75])
    iqr = q3 - q1
    return q1 - 1.5 * iqr, q3 + 1.5 * iqr



def fig_dist_01_frequencia_densidade_boxplot(df: pd.DataFrame) -> tuple[float, float]:
    """Frequencia (contagem), densidade (KDE) e boxplot na mesma figura,
    eixos separados para frequencia x densidade -- nao sao a mesma escala,
    sobrepor as duas na mesma escala (truque comum do seaborn) distorce
    uma das duas."""
    horas = df["nr_horas_voadas"]
    inferior, superior = calcular_corte_outlier(horas)
    inferior_valido = max(inferior, 0.0)
    n_outliers = int(((horas < inferior_valido) | (horas > superior)).sum())
    pct_outliers = 100 * n_outliers / len(horas)

    fig, (ax_hist, ax_box) = plt.subplots(
        2, 1, figsize=(10, 6.5), sharex=True,
        gridspec_kw={"height_ratios": [3, 1], "hspace": 0.06},
    )

    sns.histplot(horas, bins=80, color=AZUL_BLUE, stat="count", ax=ax_hist,
                 edgecolor="white", linewidth=0.3, alpha=0.85)
    ax_hist.set_ylabel("Frequência (nº de etapas)")

    ax_dens = ax_hist.twinx()
    sns.kdeplot(horas, color=NEUTRAL_GRAY, linewidth=2, ax=ax_dens)
    ax_dens.set_ylabel("Densidade")
    ax_dens.grid(False)

    for corte in (inferior_valido, superior):
        ax_hist.axvline(corte, color=NEUTRAL_GRAY, linestyle="--", linewidth=1.3)
        ax_box.axvline(corte, color=NEUTRAL_GRAY, linestyle="--", linewidth=1.3)

    n_outliers_fmt = f"{n_outliers:,}".replace(",", ".")
    ax_hist.set_title(
        "Azul — Distribuição de Etapa Média (frequência + densidade)\n"
        f"corte de outlier (Tukey, 1,5×IQR): [{inferior_valido:.2f}h, {superior:.2f}h] "
        f"— {n_outliers_fmt} etapas fora ({pct_outliers:.2f}%)"
    )

    sns.boxplot(x=horas, color=AZUL_BLUE, ax=ax_box, fliersize=2, linewidth=1)
    ax_box.set_xlabel("Horas voadas (etapa)")
    ax_box.set_yticks([])

    fig.savefig(FIG_DIR / "dist_01_frequencia_densidade_boxplot_etapa_media.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    print(
        f"[dist_01] corte outlier Tukey: inferior={inferior:.3f}h (usado {inferior_valido:.3f}h; "
        f"nao pode ser negativo) | superior={superior:.3f}h | "
        f"{n_outliers_fmt} etapas fora ({pct_outliers:.2f}%)"
    )
    return inferior_valido, superior


def fig_dist_02_violin_por_modelo(df: pd.DataFrame, inferior: float, superior: float,
                                   min_etapas: int = 1000) -> None:
    contagem = df["sg_equipamento_icao"].value_counts()
    modelos = contagem[contagem >= min_etapas].index.tolist()
    sub = df[df["sg_equipamento_icao"].isin(modelos)]
    ordem = (
        sub.groupby("sg_equipamento_icao")["nr_horas_voadas"]
        .median().sort_values(ascending=False).index.tolist()
    )
    sub_com_corte = sub[sub["nr_horas_voadas"].between(inferior, superior)]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
    for ax, dados, rotulo in ((ax1, sub, "Sem corte"), (ax2, sub_com_corte, "Com corte de outlier")):
        sns.violinplot(
            data=dados, x="sg_equipamento_icao", y="nr_horas_voadas", order=ordem,
            hue="sg_equipamento_icao", hue_order=ordem, palette=PALETA_CATEGORICA[:len(ordem)],
            legend=False, cut=0, ax=ax,
        )
        ax.set_title(f"{rotulo} (n={len(dados):,})".replace(",", "."))
        ax.set_xlabel("Modelo")
        ax.tick_params(axis="x", rotation=30)
    ax1.set_ylabel("Horas voadas (etapa)")
    ax2.set_ylabel("")

    fig.suptitle(f"Azul — Distribuição de Etapa Média por Modelo (≥{min_etapas} etapas)", fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "dist_02_violin_etapa_media_por_modelo.png", dpi=150)
    plt.close(fig)


def fig_dist_03_dispersao_etapa_media_tempo_solo(df: pd.DataFrame, min_etapas: int = 30) -> None:
    """1 ponto = 1 matricula (media de etapa e de tempo de solo no periodo).

    Nota: tempo_solo_horas tem cauda longa (pernoite/manutencao misturado
    com solo entre voos do dia) -- a media por matricula pode ser puxada
    por poucos pernoites longos. Nao tratado aqui (agregacao simples,
    mesma decisao do espelho GOL); se a leitura ficar estranha, mediana
    e' o proximo passo, nao a media.
    """
    por_matricula = (
        df.dropna(subset=["tempo_solo_horas"])
        .groupby("ds_matricula")
        .agg(
            etapa_media=("nr_horas_voadas", "mean"),
            tempo_solo_medio=("tempo_solo_horas", "mean"),
            n_etapas=("nr_horas_voadas", "count"),
            modelo=("sg_equipamento_icao", lambda s: s.mode().iat[0]),
        )
    )
    por_matricula = por_matricula[por_matricula["n_etapas"] >= min_etapas]

    # Cap no tamanho da paleta -- zip() truncaria silenciosamente e faria
    # o loop abaixo estourar KeyError se houver mais modelos que cores
    # (Azul tem bem mais tipos de aeronave que a GOL: widebody
    # internacional, ATR, Embraer).
    modelos = por_matricula["modelo"].value_counts().index.tolist()[:len(PALETA_CATEGORICA)]
    cores = {m: c for m, c in zip(modelos, PALETA_CATEGORICA)}
    por_matricula = por_matricula[por_matricula["modelo"].isin(modelos)]

    fig, ax = plt.subplots(figsize=(9, 6.5))
    for modelo in modelos:
        sub = por_matricula[por_matricula["modelo"] == modelo]
        ax.scatter(
            sub["tempo_solo_medio"], sub["etapa_media"],
            color=cores[modelo], label=modelo, s=42, alpha=0.8,
            edgecolor="white", linewidth=0.5,
        )
    ax.set_title(
        "Azul — Etapa Média x Tempo de Solo, por Aeronave\n"
        f"(1 ponto = 1 matrícula, ≥{min_etapas} etapas no período)"
    )
    ax.set_xlabel("Tempo de solo médio (h)")
    ax.set_ylabel("Etapa média (h)")
    ax.legend(title="Modelo", frameon=True, edgecolor="#333333")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "dist_03_dispersao_etapa_media_tempo_solo_por_matricula.png", dpi=150)
    plt.close(fig)


def fig_dist_04_dispersao_etapa_media_distancia(df: pd.DataFrame, min_etapas: int = 1000,
                                                 amostra: int = 30_000, seed: int = 42) -> None:
    """Correlacao com frota: etapa media (tempo) x km_distancia, por modelo.

    Amostra fixa (30k, seed fixa) so para legibilidade do grafico -- 1M+
    pontos sobrepostos vira uma mancha solida. Estatisticas de outras
    figuras usam a base inteira, so esta usa amostra.
    """
    contagem = df["sg_equipamento_icao"].value_counts()
    modelos = contagem[contagem >= min_etapas].index.tolist()
    sub = df[df["sg_equipamento_icao"].isin(modelos)].dropna(subset=["km_distancia"])
    if len(sub) > amostra:
        sub = sub.sample(amostra, random_state=seed)

    fig, ax = plt.subplots(figsize=(9, 6.5))
    sns.scatterplot(
        data=sub, x="km_distancia", y="nr_horas_voadas",
        hue="sg_equipamento_icao", palette=PALETA_CATEGORICA[:len(modelos)],
        s=18, alpha=0.5, edgecolor="none", ax=ax,
    )
    n_amostra_fmt = f"{len(sub):,}".replace(",", ".")
    ax.set_title(f"Azul — Etapa Média x Distância, por Modelo\n(amostra de {n_amostra_fmt} etapas)")
    ax.set_xlabel("Distância (km)")
    ax.set_ylabel("Etapa média (h)")
    ax.legend(title="Modelo", frameon=True, edgecolor="#333333")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "dist_04_dispersao_etapa_media_distancia_por_modelo.png", dpi=150)
    plt.close(fig)


def fig_dist_05_distribuicao_por_hub(df: pd.DataFrame, max_bases: int = 8) -> None:
    hub = selecionar_hub(df["sg_iata_origem"].value_counts())
    bases = hub.index.tolist()[:max_bases]
    sub = df[df["sg_iata_origem"].isin(bases)]
    ordem = sub.groupby("sg_iata_origem")["nr_horas_voadas"].median().sort_values(ascending=False).index.tolist()

    fig, ax = plt.subplots(figsize=(11, 6))
    sns.boxplot(
        data=sub, x="sg_iata_origem", y="nr_horas_voadas", order=ordem,
        hue="sg_iata_origem", hue_order=ordem, palette=PALETA_CATEGORICA[:len(ordem)], legend=False,
        fliersize=2, linewidth=1, ax=ax,
    )
    ax.set_title(f"Azul — Distribuição de Etapa Média por Base HUB de Origem\n(top {len(bases)}, 80% acumulado)")
    ax.set_xlabel("Base de origem")
    ax.set_ylabel("Horas voadas (etapa)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "dist_05_distribuicao_etapa_media_por_hub.png", dpi=150)
    plt.close(fig)


def fig_dist_06_distribuicao_por_destino(df: pd.DataFrame, max_destinos: int = 8) -> None:
    hub_destino = selecionar_hub(df["sg_iata_destino"].value_counts())
    destinos = hub_destino.index.tolist()[:max_destinos]
    sub = df[df["sg_iata_destino"].isin(destinos)]
    ordem = sub.groupby("sg_iata_destino")["nr_horas_voadas"].median().sort_values(ascending=False).index.tolist()

    fig, ax = plt.subplots(figsize=(11, 6))
    sns.boxplot(
        data=sub, x="sg_iata_destino", y="nr_horas_voadas", order=ordem,
        hue="sg_iata_destino", hue_order=ordem, palette=PALETA_CATEGORICA[:len(ordem)], legend=False,
        fliersize=2, linewidth=1, ax=ax,
    )
    ax.set_title(f"Azul — Distribuição de Etapa Média por Destino\n(top {len(destinos)}, 80% acumulado)")
    ax.set_xlabel("Destino")
    ax.set_ylabel("Horas voadas (etapa)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "dist_06_distribuicao_etapa_media_por_destino.png", dpi=150)
    plt.close(fig)


def fig_dist_07_correlacao(df: pd.DataFrame, inferior: float, superior: float) -> None:
    """Sem corte x com corte (cerca de Tukey, 1,5x IQR, aplicada em
    nr_horas_voadas -- mesma regra de dist_01/02/08). Pearson e sensivel a
    outlier (nao e' robusto como a mediana), entao vale ver se os
    coeficientes mudam quando os extremos de etapa media saem da conta."""
    cols = {
        "nr_horas_voadas": "Etapa média (h)",
        "km_distancia": "Distância (km)",
        "tempo_solo_horas": "Tempo de solo (h)",
    }
    sub_com_corte = df[df["nr_horas_voadas"].between(inferior, superior)]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.5, 5.5))
    for ax, dados, rotulo in ((ax1, df, "Sem corte"), (ax2, sub_com_corte, "Com corte de outlier")):
        corr = dados[list(cols)].rename(columns=cols).corr(method="pearson")
        n_fmt = f"{len(dados):,}".replace(",", ".")
        sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", vmin=-1, vmax=1,
                    square=True, cbar_kws={"label": "Correlação de Pearson"}, ax=ax)
        ax.set_title(f"{rotulo} (n={n_fmt})")

    fig.suptitle("Azul — Correlação entre Etapa Média, Distância e Tempo de Solo", fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "dist_07_correlacao_etapa_media_distancia_solo.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def fig_dist_08_violin_sem_outlier_referencias(df: pd.DataFrame, inferior: float, superior: float) -> None:
    """Violin unico (sem quebra por modelo/hub), so dados dentro do corte
    Tukey de dist_01, com media/mediana/Q1/Q3 marcados. Mediana e Q2 sao a
    mesma coisa por definicao -- rotulado assim para deixar isso explicito."""
    sub = df.loc[df["nr_horas_voadas"].between(inferior, superior), "nr_horas_voadas"]
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
        f"Azul — Distribuição de Etapa Média, Sem Outlier\n"
        f"(corte Tukey [{inferior:.2f}h, {superior:.2f}h], n={n_fmt})"
    )
    ax.set_ylabel("Horas voadas (etapa)")
    ax.set_xticks([])
    ax.set_xlim(-0.5, 1.3)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "dist_08_violin_sem_outlier_referencias.png", dpi=150)
    plt.close(fig)


def fig_dist_09_etapa_media_x_horario_partida(df: pd.DataFrame) -> None:
    """Hexbin (nao scatter) -- volume grande demais para scatter marcador
    por marcador; hexbin usa a base inteira sem amostrar, e mostra
    densidade real por celula."""
    fig, ax = plt.subplots(figsize=(10, 7))
    hb = ax.hexbin(
        df["nr_horas_voadas"], df["hora_partida_decimal"],
        gridsize=60, cmap="YlOrBr", mincnt=1,
    )
    cbar = fig.colorbar(hb, ax=ax)
    cbar.set_label("Nº de etapas (por célula)")

    ax.set_ylim(0, 24)
    ax.set_yticks(range(0, 25, 3))
    ax.set_yticklabels([f"{h:02d}:00" for h in range(0, 25, 3)])
    ax.set_title("Azul — Etapa Média x Horário de Partida\n(hexbin, base completa)")
    ax.set_xlabel("Horas voadas (etapa)")
    ax.set_ylabel("Horário de partida")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "dist_09_etapa_media_x_horario_partida.png", dpi=150)
    plt.close(fig)


def fig_dist_10_hexbin_por_hub_individual(df: pd.DataFrame, top_n: int = 10) -> list[str]:
    """Top N bruto por volume (nao a regra 80% acumulado de dist_05/06 --
    pedido explicito foi 'top 10 hub', nao 'HUB Pareto')."""
    top_bases = df["sg_iata_origem"].value_counts().head(top_n).index.tolist()

    for base in top_bases:
        sub = df[df["sg_iata_origem"] == base]
        n_fmt = f"{len(sub):,}".replace(",", ".")

        fig, ax = plt.subplots(figsize=(8, 6))
        hb = ax.hexbin(sub["nr_horas_voadas"], sub["hora_partida_decimal"],
                        gridsize=40, cmap="YlOrBr", mincnt=1)
        cbar = fig.colorbar(hb, ax=ax)
        cbar.set_label("Nº de etapas (por célula)")

        ax.set_ylim(0, 24)
        ax.set_yticks(range(0, 25, 3))
        ax.set_yticklabels([f"{h:02d}:00" for h in range(0, 25, 3)])
        ax.set_title(f"Azul — Etapa Média x Horário de Partida — {base}\n(hexbin, n={n_fmt})")
        ax.set_xlabel("Horas voadas (etapa)")
        ax.set_ylabel("Horário de partida")
        fig.tight_layout()
        fig.savefig(FIG_DIR / f"dist_10_hexbin_horario_partida_{base}.png", dpi=150)
        plt.close(fig)

    return top_bases


def fig_dist_11_12_hexbin_grid_top6(df: pd.DataFrame, top6: list[str]) -> None:
    """Mesmos 6 hexbins, dois layouts (2x3 e 3x2) -- escala de cor
    COMPARTILHADA entre os 6 paineis (nao e' o default do hexbin, que
    normalizaria cada painel sozinho e faria base pequena parecer tao
    'quente' quanto a maior base so por causa da escala local)."""
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
            hb = ax.hexbin(sub["nr_horas_voadas"], sub["hora_partida_decimal"],
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

        fig.supxlabel("Horas voadas (etapa)")
        fig.supylabel("Horário de partida")
        cbar = fig.colorbar(hbs[0], ax=axes_flat, shrink=0.85)
        cbar.set_label("Nº de etapas por célula (escala compartilhada entre os 6 painéis)")
        fig.suptitle(f"Azul — Etapa Média x Horário de Partida, Top 6 Bases ({nrows}x{ncols})",
                     fontweight="bold")
        fig.savefig(FIG_DIR / fname, dpi=150, bbox_inches="tight")
        plt.close(fig)


def fig_dist_13_run_sequence(df: pd.DataFrame) -> pd.Series:
    """Run sequence plot (NIST/SEMATECH, secao 3): valor x ORDEM de coleta.
    Agregado por dia (media diaria) -- a serie bruta (centenas de milhares
    de etapas de dezenas de aeronaves voando em paralelo) nao tem uma unica
    ordem de processo fisicamente significativa; o dia calendario e' a
    unidade onde 'ordem cronologica' volta a fazer sentido como eixo unico."""
    diario = df.set_index("dt_partida_real")["nr_horas_voadas"].resample("D").mean().dropna()
    media_geral = diario.mean()

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(diario.index, diario.values, color=AZUL_BLUE, linewidth=0.8, alpha=0.85)
    ax.axhline(media_geral, color=NEUTRAL_GRAY, linestyle="--", linewidth=1.3)
    ax.annotate(f"média geral = {media_geral:.2f}h", xy=(diario.index[0], media_geral),
                xytext=(4, 6), textcoords="offset points", color=NEUTRAL_GRAY, fontweight="bold")
    ax.set_title("Azul — Run Sequence Plot: Etapa Média Diária (2021-2026)")
    ax.set_xlabel("Data (ordem cronológica)")
    ax.set_ylabel("Etapa média do dia (h)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "dist_13_run_sequence_etapa_media_diaria.png", dpi=150)
    plt.close(fig)
    return diario


def fig_dist_14_lag_plot(diario: pd.Series) -> float:
    """Lag plot (lag 1): valor(t) x valor(t-1). Mesma serie diaria de dist_13."""
    anterior = diario.iloc[:-1].to_numpy()
    atual = diario.iloc[1:].to_numpy()
    r = float(np.corrcoef(anterior, atual)[0, 1])

    fig, ax = plt.subplots(figsize=(6.5, 6.5))
    ax.scatter(anterior, atual, color=AZUL_BLUE, s=14, alpha=0.5, edgecolor="none")
    lims = [min(anterior.min(), atual.min()), max(anterior.max(), atual.max())]
    ax.plot(lims, lims, color=NEUTRAL_GRAY, linestyle="--", linewidth=1.2)
    ax.set_xlim(lims)
    ax.set_ylim(lims)
    ax.set_title(f"Azul — Lag Plot (lag 1 dia): Etapa Média Diária\nr = {r:.3f}")
    ax.set_xlabel("Etapa média em t-1 (h)")
    ax.set_ylabel("Etapa média em t (h)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "dist_14_lag_plot_etapa_media_diaria.png", dpi=150)
    plt.close(fig)
    return r


def fig_dist_15_mix_frota_temporal(df: pd.DataFrame, min_etapas: int = 1000) -> pd.DataFrame:
    """Participacao percentual de cada modelo no volume de etapas, por mes.
    Mesma investigacao do espelho GOL: a deriva do run sequence (dist_13)
    e' composicao de frota mudando, ou duracao mudando por aeronave?"""
    contagem = df["sg_equipamento_icao"].value_counts()
    modelos = contagem[contagem >= min_etapas].index.tolist()
    sub = df[df["sg_equipamento_icao"].isin(modelos)]

    mensal_contagem = (
        sub.set_index("dt_partida_real")
        .groupby("sg_equipamento_icao")["nr_horas_voadas"]
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
    """Decomposicao tipo shift-share: real (mix variando no tempo) x
    contrafactual (mix travado no ano_base, so a duracao por modelo varia).
    Se o contrafactual ficar achatado enquanto o real sobe, a deriva e'
    efeito de composicao de frota, nao de duracao mudando por aeronave."""
    modelos = mensal_contagem.columns.tolist()
    sub = df[df["sg_equipamento_icao"].isin(modelos)]

    duracao_mensal = (
        sub.set_index("dt_partida_real")
        .groupby("sg_equipamento_icao")["nr_horas_voadas"]
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
    ax.set_title(f"Azul — Etapa Média: Real x Contrafactual com Mix de Frota Travado em {ano_base}")
    ax.set_xlabel("Mês")
    ax.set_ylabel("Etapa média (h)")
    ax.legend(frameon=True, edgecolor="#333333")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "dist_16_decomposicao_mix_vs_intramodelo.png", dpi=150)
    plt.close(fig)


def main() -> None:
    df = load_data()
    print(f"{len(df):,} etapas carregadas ({df['ds_matricula'].nunique()} matrículas)".replace(",", "."))

    inferior, superior = fig_dist_01_frequencia_densidade_boxplot(df)
    fig_dist_02_violin_por_modelo(df, inferior, superior)
    fig_dist_03_dispersao_etapa_media_tempo_solo(df)
    fig_dist_04_dispersao_etapa_media_distancia(df)
    fig_dist_05_distribuicao_por_hub(df)
    fig_dist_06_distribuicao_por_destino(df)
    fig_dist_07_correlacao(df, inferior, superior)
    fig_dist_08_violin_sem_outlier_referencias(df, inferior, superior)
    fig_dist_09_etapa_media_x_horario_partida(df)

    top10 = fig_dist_10_hexbin_por_hub_individual(df)
    print(f"[dist_10] top 10 bases: {', '.join(top10)}")
    fig_dist_11_12_hexbin_grid_top6(df, top10[:6])

    diario = fig_dist_13_run_sequence(df)
    r_lag1 = fig_dist_14_lag_plot(diario)
    print(f"[dist_14] autocorrelação lag-1 (etapa média diária): r = {r_lag1:.3f}")

    mensal_contagem = fig_dist_15_mix_frota_temporal(df)
    fig_dist_16_decomposicao_mix_vs_intramodelo(df, mensal_contagem)

    print(f"Figuras salvas em {FIG_DIR}")


if __name__ == "__main__":
    main()
