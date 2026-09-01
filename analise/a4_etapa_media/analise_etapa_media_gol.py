"""Etapa media (duracao) -- GOL, so passageiro (SPEC-013).

Regra padrao deste recorte de analise (a menos que dito o contrario):
so etapas PASSAGEIRO, exclui CARGUEIRO.

Fonte: basica_curated_deep (db/anac_basica.sqlite), SPEC-012.
Roda com: conda run -n pesquisa-azul python analise/a4_etapa_media/analise_etapa_media_gol.py
"""

import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

REPO_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = REPO_ROOT / "db" / "anac_basica.sqlite"
FIG_DIR = REPO_ROOT / "analise" / "a4_etapa_media" / "a4_figuras_gol"
FIG_DIR.mkdir(parents=True, exist_ok=True)

# Paleta GOL (pedido do autor, 2026-09-01): laranja da marca. Aproximacao
# -- nao ha manual de marca oficial disponivel neste ambiente, ajustar o
# hex aqui se o autor tiver o valor exato. Estrutura de fundo/grid/titulo
# em negrito segue casada com rascunho/Deep_Dive_Gol_ANAC_1a_.docx (ver
# Historico da SPEC-013 v2); so a hue mudou de Set2 para laranja GOL.
GOL_ORANGE = "#FF6900"        # domestica / serie unica -- laranja GOL (aproximado)
GOL_ORANGE_DARK = "#B34700"       # internacional -- tom mais escuro da mesma familia
NEUTRAL_GRAY = "#4d4d4d"    # linha de media / anotacao -- cinza neutro, contraste contra o laranja
SEQ_ORANGE_CMAP = LinearSegmentedColormap.from_list("seq_orange", ["#ffe0c2", "#7a3300"])

# Paleta categorica "normal", colorida (pedido do autor, 2026-09-01): so
# para grafico de linha com mais de 3 series -- laranja monocromatico
# (SEQ_ORANGE_CMAP) fica pouco legivel alem disso, achado do §6.7 da
# SPEC-013 (linhas de nivel medio indistinguiveis so pela cor). Ordem
# fixa, validada (skill dataviz, references/palette.md) -- nao ciclar.
PALETA_CATEGORICA = [
    "#2a78d6",  # blue
    "#eb6834",  # orange
    "#1baf7a",  # aqua
    "#eda100",  # yellow
    "#e87ba4",  # magenta
    "#008300",  # green
    "#4a3aa7",  # violet
    "#e34948",  # red
]

GRID = "#d9d9d9"

plt.rcParams.update({
    "figure.facecolor": "#ffffff",
    "axes.facecolor": "#ffffff",
    "axes.edgecolor": "#333333",
    "axes.labelcolor": "#000000",
    "text.color": "#000000",
    "xtick.color": "#333333",
    "ytick.color": "#333333",
    "axes.grid": True,
    "grid.color": GRID,
    "grid.linewidth": 0.7,
    "axes.spines.top": True,
    "axes.spines.right": True,
    "axes.titleweight": "bold",
    "font.size": 10,
})

WINDOW_FULL = ("2021-01-01", "2026-07-31")
WINDOW_2026 = ("2026-01-01", "2026-07-31")

# Janelas fechando (pedido do autor, 2026-09-01): mesmo teto (2026-07-31),
# piso subindo ano a ano -- 2021_2026 (WINDOW_FULL) e 2026 (WINDOW_2026)
# ja cobertos acima, aqui so os intermediarios.
JANELAS_FECHANDO = [
    ("2022-01-01", "2026-07-31", "2022_2026"),
    ("2023-01-01", "2026-07-31", "2023_2026"),
    ("2024-01-01", "2026-07-31", "2024_2026"),
    ("2025-01-01", "2026-07-31", "2025_2026"),
]


def load_data(dt_ini: str, dt_fim: str) -> pd.DataFrame:
    """Etapas PASSAGEIRO da GOL, dt_partida_real dentro da janela [dt_ini, dt_fim]."""
    con = sqlite3.connect(DB_PATH)
    query = """
        SELECT
            dt_partida_real, sg_equipamento_icao, ds_natureza_tipo_linha,
            sg_icao_origem, sg_icao_destino, nr_horas_voadas, km_distancia
        FROM basica_curated_deep
        WHERE sg_empresa_icao = 'GLO'
          AND ds_servico_tipo_linha = 'PASSAGEIRO'
          AND dt_partida_real BETWEEN ? AND ?
    """
    df = pd.read_sql_query(query, con, params=(dt_ini, dt_fim), parse_dates=["dt_partida_real"])
    con.close()
    return df


def fig_duracao_media_mensal(df: pd.DataFrame, suffix: str) -> None:
    mensal = (
        df.set_index("dt_partida_real")["nr_horas_voadas"]
        .resample("MS")
        .mean()
    )
    media_geral = mensal.mean()

    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.plot(mensal.index, mensal.values, color=GOL_ORANGE, linewidth=2, marker="o", markersize=4)
    ax.axhline(media_geral, color=NEUTRAL_GRAY, linestyle="--", linewidth=1.3)
    ax.annotate(
        f"μ={media_geral:.2f}", xy=(mensal.index[0], media_geral),
        xytext=(4, 4), textcoords="offset points", color=NEUTRAL_GRAY, fontweight="bold", fontsize=9,
    )
    ax.set_title(f"GOL — Duração Média de Etapa por Mês\n({suffix})")
    ax.set_ylabel("Horas Voadas (média)")
    ax.set_xlabel("Mês")
    fig.tight_layout()
    fig.savefig(FIG_DIR / f"duracao_media_mensal_{suffix}.png", dpi=150)
    plt.close(fig)


def fig_duracao_media_mensal_por_frota(df: pd.DataFrame, suffix: str, min_etapas: int = 1000) -> None:
    """Cruzamento tempo x frota: uma linha por modelo com volume suficiente
    (>= min_etapas no periodo inteiro, nao por mes -- evita linha ruidosa
    de modelo residual)."""
    modelos = df["sg_equipamento_icao"].value_counts()
    modelos = modelos[modelos >= min_etapas].index.tolist()
    amostras_modelo = [0.25 + 0.7 * i / max(1, len(modelos) - 1) for i in range(len(modelos))]
    cores_modelo = {m: c for m, c in zip(modelos, SEQ_ORANGE_CMAP(amostras_modelo))}

    fig, ax = plt.subplots(figsize=(11, 5))
    for modelo in modelos:
        sub = df[df["sg_equipamento_icao"] == modelo]
        mensal = sub.set_index("dt_partida_real")["nr_horas_voadas"].resample("MS").mean()
        ax.plot(mensal.index, mensal.values, linewidth=2, marker="o", markersize=3,
                label=modelo, color=cores_modelo[modelo])
    ax.set_title(f"GOL — Duração Média Mensal por Modelo de Aeronave\n({suffix})")
    ax.set_ylabel("Horas Voadas (média)")
    ax.set_xlabel("Mês")
    ax.legend(frameon=True, edgecolor="#333333")
    fig.tight_layout()
    fig.savefig(FIG_DIR / f"duracao_media_mensal_por_frota_{suffix}.png", dpi=150)
    plt.close(fig)


def fig_duracao_media_mensal_por_base(df: pd.DataFrame, suffix: str, max_bases: int = 6) -> None:
    """Cruzamento tempo x base: uma linha por base HUB (80% acumulado,
    SPEC-013 Sec.6.5), limitado as max_bases de maior volume -- alem
    disso a legenda de uma linha fica ilegivel."""
    hub = selecionar_hub(df["sg_icao_origem"].value_counts())
    bases = hub.index.tolist()[:max_bases]
    cores_base = {b: c for b, c in zip(bases, PALETA_CATEGORICA)}

    fig, ax = plt.subplots(figsize=(12, 5.5))
    for base in bases:
        sub = df[df["sg_icao_origem"] == base]
        mensal = sub.set_index("dt_partida_real")["nr_horas_voadas"].resample("MS").mean()
        ax.plot(mensal.index, mensal.values, linewidth=2, marker="o", markersize=3,
                label=base, color=cores_base[base])
        # Rotulo direto no fim da linha -- com 6 series na mesma familia de
        # cor (laranja GOL), cores medianas ficam parecidas demais so pela
        # legenda (achado desta rodada); rotulo direto resolve.
        ax.annotate(
            base, xy=(mensal.index[-1], mensal.values[-1]),
            xytext=(6, 0), textcoords="offset points", va="center",
            color=cores_base[base], fontweight="bold", fontsize=9,
        )
    ax.set_title(f"GOL — Duração Média Mensal por Base (top {len(bases)} HUB)\n({suffix})")
    ax.set_ylabel("Horas Voadas (média)")
    ax.set_xlabel("Mês")
    ax.margins(x=0.06)
    fig.tight_layout()
    fig.savefig(FIG_DIR / f"duracao_media_mensal_por_base_{suffix}.png", dpi=150)
    plt.close(fig)


def fig_duracao_media_por_frota(df: pd.DataFrame, suffix: str) -> None:
    agg = (
        df.groupby(["sg_equipamento_icao", "ds_natureza_tipo_linha"])["nr_horas_voadas"]
        .agg(["mean", "count"])
        .reset_index()
    )
    agg = agg[agg["count"] >= 30]
    ordem = (
        agg.groupby("sg_equipamento_icao")["mean"].mean().sort_values(ascending=False).index
    )
    pivot = agg.pivot(index="sg_equipamento_icao", columns="ds_natureza_tipo_linha", values="mean")
    pivot = pivot.reindex(ordem)

    fig, ax = plt.subplots(figsize=(10, 5))
    x = range(len(pivot))
    largura = 0.38
    cores = {"DOMÉSTICA": GOL_ORANGE, "INTERNACIONAL": GOL_ORANGE_DARK}
    for i, coluna in enumerate(pivot.columns):
        deslocamento = (i - (len(pivot.columns) - 1) / 2) * largura
        barras = ax.bar(
            [xi + deslocamento for xi in x], pivot[coluna], width=largura,
            label=coluna.title(), color=cores.get(coluna, GOL_ORANGE),
        )
        ax.bar_label(barras, fmt="%.2f", fontweight="bold", fontsize=8, padding=2)
    ax.set_xticks(list(x))
    ax.set_xticklabels(pivot.index, rotation=0)
    ax.set_title(f"GOL — Duração Média por Modelo de Aeronave\n({suffix})")
    ax.set_ylabel("Horas Voadas (média)")
    ax.set_xlabel("Modelo")
    ax.legend(frameon=True, edgecolor="#333333")
    fig.tight_layout()
    fig.savefig(FIG_DIR / f"duracao_media_por_frota_{suffix}.png", dpi=150)
    plt.close(fig)


def selecionar_hub(contagens: pd.Series) -> pd.Series:
    """Filtra bases HUB pela regra de 80% acumulado (SPEC-013 Sec.6.5,
    mesma logica de gerar_pareto_bases_gol.py): HUB enquanto o acumulado
    ANTES da base for < 80%. Nao e mais corte fixo top-N."""
    ordenado = contagens.sort_values(ascending=False)
    pct = 100 * ordenado / ordenado.sum()
    pct_acum = pct.cumsum()
    pct_acum_antes = pct_acum - pct
    return ordenado[pct_acum_antes < 80]


def fig_top_bases_origem(df: pd.DataFrame, suffix: str) -> None:
    agg_full = (
        df.groupby("sg_icao_origem")["nr_horas_voadas"]
        .agg(n_etapas="count", duracao_media="mean")
    )
    hub = selecionar_hub(agg_full["n_etapas"])
    agg = agg_full.loc[hub.index].sort_values("n_etapas")

    norm = plt.Normalize(agg["duracao_media"].min(), agg["duracao_media"].max())
    cores = SEQ_ORANGE_CMAP(norm(agg["duracao_media"]))

    fig, ax = plt.subplots(figsize=(9, 6))
    barras = ax.barh(agg.index, agg["n_etapas"], color=cores, edgecolor="#333333", linewidth=0.5)
    ax.bar_label(barras, fmt="%.0f", fontweight="bold", fontsize=8, padding=3)
    ax.margins(x=0.09)
    ax.set_title(f"GOL — Bases HUB de Origem (80% acumulado)\n(cor = duração média, {suffix})")
    ax.set_xlabel("Nº de Etapas")
    sm = plt.cm.ScalarMappable(cmap=SEQ_ORANGE_CMAP, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax)
    cbar.set_label("Duração Média (h)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / f"top_bases_origem_{suffix}.png", dpi=150)
    plt.close(fig)


def fig_top_bases_chegadas(df: pd.DataFrame, suffix: str) -> None:
    contagem_full = df["sg_icao_destino"].value_counts()
    contagem = selecionar_hub(contagem_full).sort_values()
    fig, ax = plt.subplots(figsize=(9, 6))
    barras = ax.barh(contagem.index, contagem.values, color=GOL_ORANGE, edgecolor="#333333", linewidth=0.5)
    ax.bar_label(barras, fmt="%.0f", fontweight="bold", fontsize=8, padding=3)
    ax.margins(x=0.09)
    ax.set_title(f"GOL — Bases HUB com Mais Chegadas (80% acumulado)\n({suffix})")
    ax.set_xlabel("Nº de Chegadas")
    fig.tight_layout()
    fig.savefig(FIG_DIR / f"top_bases_chegadas_{suffix}.png", dpi=150)
    plt.close(fig)


def rodar_janela(dt_ini: str, dt_fim: str, suffix: str) -> pd.DataFrame:
    df = load_data(dt_ini, dt_fim)
    print(f"[{suffix}] {dt_ini} a {dt_fim}: {len(df):,} etapas".replace(",", "."))
    fig_duracao_media_mensal(df, suffix)
    fig_duracao_media_por_frota(df, suffix)
    fig_top_bases_origem(df, suffix)
    fig_top_bases_chegadas(df, suffix)
    return df


def main() -> None:
    df_full = rodar_janela(*WINDOW_FULL, "full_2021_2026")
    df_2026 = rodar_janela(*WINDOW_2026, "2026")

    # Janelas fechando -- so a linha mensal (o resto ja e coberto pelas
    # duas pontas full_2021_2026/2026 acima), exceto 2025_2026, guardada
    # para o cruzamento por base tambem (pedido do autor).
    dfs_fechando = {}
    for dt_ini, dt_fim, suffix in JANELAS_FECHANDO:
        df = load_data(dt_ini, dt_fim)
        print(f"[{suffix}] {dt_ini} a {dt_fim}: {len(df):,} etapas".replace(",", "."))
        fig_duracao_media_mensal(df, suffix)
        dfs_fechando[suffix] = df

    # Cruzamentos tempo x frota, tempo x base -- janela completa (mais
    # historico pra ver tendencia/sazonalidade por corte), mais o grafico
    # por base (colorido, PALETA_CATEGORICA) tambem para 2025_2026 e 2026
    # isolado (pedido do autor, 2026-09-01).
    fig_duracao_media_mensal_por_frota(df_full, "full_2021_2026")
    fig_duracao_media_mensal_por_base(df_full, "full_2021_2026")
    fig_duracao_media_mensal_por_base(dfs_fechando["2025_2026"], "2025_2026")
    fig_duracao_media_mensal_por_base(df_2026, "2026")

    print(f"Figuras salvas em {FIG_DIR}")


if __name__ == "__main__":
    main()
