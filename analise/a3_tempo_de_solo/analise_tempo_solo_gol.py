"""Tempo de solo (turnaround entre etapas) -- GOL, so passageiro (mesma
convencao do SPEC-013: PASSAGEIRO, exclui CARGUEIRO). Espelho estrutural de
analise_etapa_media_gol.py (a4_etapa_media), agora com tempo_solo_horas
como variavel de resposta em vez de nr_horas_voadas.

Fonte: fato_rotacao_aeronave_gol_azul (SPEC-012) -- tempo_solo_horas so
existe la (calculado por LAG de chegada por matricula), nao em
basica_curated_deep. ds_natureza_tipo_linha so existe em
basica_curated_deep -- trazida por mapeamento em pandas (id_basica ->
natureza), mesma tecnica de distribuicao_etapa_media_gol.py para evitar
JOIN sem indice.

Limpeza de dado: feita no banco, nao aqui. fl_solo_valido (DDL_005,
2026-09-02) exclui tempo_solo_horas negativo (fisicamente invalido),
continuidade de rotacao quebrada (fl_continuidade_ok=0) e > 72h (pernoite
+ fim de semana completo cabem ate' 72h -- limiar de julgamento de
dominio, medido antes: distribuicao 24-96h decai suave, sem quebra
natural que apontasse 72h sobre 48h/60h). GOL+Azul juntos: 7.919 linhas
de 2.743.531 (0,29%) ficam fl_solo_valido=0, nao sao deletadas, so' nao
entram aqui porque o WHERE filtra fl_solo_valido=1. Ver DDL_005 para a
medicao completa.

Roda com: conda run -n pesquisa-azul python analise/a3_tempo_de_solo/analise_tempo_solo_gol.py
"""

import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from iata_bases import aplicar_iata  # noqa: E402
from pareto_hub import selecionar_hub  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = REPO_ROOT / "db" / "anac_basica.sqlite"
FIG_DIR = REPO_ROOT / "analise" / "a3_tempo_de_solo" / "a3_figuras_gol"
FIG_DIR.mkdir(parents=True, exist_ok=True)

# Mesma paleta de analise_etapa_media_gol.py (consistencia visual entre
# linhas de analise GOL).
GOL_ORANGE = "#FF6900"
GOL_ORANGE_DARK = "#B34700"
NEUTRAL_GRAY = "#4d4d4d"
SEQ_ORANGE_CMAP = LinearSegmentedColormap.from_list("seq_orange", ["#ffe0c2", "#7a3300"])
PALETA_CATEGORICA = [
    "#2a78d6", "#eb6834", "#1baf7a", "#eda100",
    "#e87ba4", "#008300", "#4a3aa7", "#e34948",
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

JANELAS_FECHANDO = [
    ("2022-01-01", "2026-07-31", "2022_2026"),
    ("2023-01-01", "2026-07-31", "2023_2026"),
    ("2024-01-01", "2026-07-31", "2024_2026"),
    ("2025-01-01", "2026-07-31", "2025_2026"),
]


def load_data(dt_ini: str, dt_fim: str) -> pd.DataFrame:
    """Etapas PASSAGEIRO da GOL, dt_partida_real dentro da janela, com
    fl_solo_valido = 1 (DDL_005: exclui negativo, continuidade quebrada e
    > 72h -- ver sql/curated_deep/DDL_005_..._add_fl_solo_valido_sqlite.sql
    para a medicao completa e a justificativa do corte)."""
    con = sqlite3.connect(DB_PATH)
    natureza = pd.read_sql_query(
        "SELECT id_basica, ds_natureza_tipo_linha FROM basica_curated_deep "
        "WHERE sg_empresa_icao = 'GLO' AND ds_servico_tipo_linha = 'PASSAGEIRO'",
        con,
    ).set_index("id_basica")["ds_natureza_tipo_linha"]

    df = pd.read_sql_query(
        """
        SELECT id_basica, sg_equipamento_icao, sg_icao_origem, sg_icao_destino,
               dt_partida_real, km_distancia, tempo_solo_horas
        FROM fato_rotacao_aeronave_gol_azul
        WHERE sg_empresa_icao = 'GLO'
          AND fl_solo_valido = 1
          AND dt_partida_real BETWEEN ? AND ?
        """,
        con, params=(dt_ini, dt_fim), parse_dates=["dt_partida_real"],
    )
    con.close()

    df = df[df["id_basica"].isin(natureza.index)].copy()
    df["ds_natureza_tipo_linha"] = df["id_basica"].map(natureza)

    return aplicar_iata(df)


def fig_tempo_solo_medio_mensal(df: pd.DataFrame, suffix: str) -> None:
    mensal = (
        df.set_index("dt_partida_real")["tempo_solo_horas"]
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
    ax.set_title(f"GOL — Tempo de Solo Médio por Mês\n({suffix})")
    ax.set_ylabel("Tempo de Solo (h, média)")
    ax.set_xlabel("Mês")
    fig.tight_layout()
    fig.savefig(FIG_DIR / f"ana_01_tempo_solo_medio_mensal_{suffix}.png", dpi=150)
    plt.close(fig)


def fig_tempo_solo_medio_mensal_por_frota(df: pd.DataFrame, suffix: str, min_etapas: int = 1000) -> None:
    """Cores da PALETA_CATEGORICA, nao SEQ_ORANGE_CMAP -- achado desta
    rodada (2026-09-02): com 3+ linhas, tons de laranja monocromatico
    ficam quase indistinguiveis (B738/B38M/B737 pareciam a mesma cor).
    SEQ_ORANGE_CMAP fica reservado para onde ja fazia sentido (cor
    continua = valor, ex. top_bases_origem), nao para 1-linha-por-serie."""
    modelos = df["sg_equipamento_icao"].value_counts()
    modelos = modelos[modelos >= min_etapas].index.tolist()
    cores_modelo = {m: c for m, c in zip(modelos, PALETA_CATEGORICA)}

    fig, ax = plt.subplots(figsize=(11, 5))
    for modelo in modelos:
        sub = df[df["sg_equipamento_icao"] == modelo]
        mensal = sub.set_index("dt_partida_real")["tempo_solo_horas"].resample("MS").mean()
        ax.plot(mensal.index, mensal.values, linewidth=2, marker="o", markersize=3,
                label=modelo, color=cores_modelo[modelo])
    ax.set_title(f"GOL — Tempo de Solo Médio Mensal por Modelo de Aeronave\n({suffix})")
    ax.set_ylabel("Tempo de Solo (h, média)")
    ax.set_xlabel("Mês")
    ax.legend(frameon=True, edgecolor="#333333")
    fig.tight_layout()
    fig.savefig(FIG_DIR / f"ana_05_tempo_solo_medio_mensal_por_frota_{suffix}.png", dpi=150)
    plt.close(fig)


def fig_tempo_solo_medio_mensal_por_base(df: pd.DataFrame, suffix: str, max_bases: int = 6) -> None:
    hub = selecionar_hub(df["sg_iata_origem"].value_counts())
    bases = hub.index.tolist()[:max_bases]
    cores_base = {b: c for b, c in zip(bases, PALETA_CATEGORICA)}

    fig, ax = plt.subplots(figsize=(12, 5.5))
    for base in bases:
        sub = df[df["sg_iata_origem"] == base]
        mensal = sub.set_index("dt_partida_real")["tempo_solo_horas"].resample("MS").mean()
        ax.plot(mensal.index, mensal.values, linewidth=2, marker="o", markersize=3,
                label=base, color=cores_base[base])
        ax.annotate(
            base, xy=(mensal.index[-1], mensal.values[-1]),
            xytext=(6, 0), textcoords="offset points", va="center",
            color=cores_base[base], fontweight="bold", fontsize=9,
        )
    ax.set_title(f"GOL — Tempo de Solo Médio Mensal por Base (top {len(bases)} HUB)\n({suffix})")
    ax.set_ylabel("Tempo de Solo (h, média)")
    ax.set_xlabel("Mês")
    ax.margins(x=0.06)

    # Legenda adicional (pedido do autor, 2026-09-02): o rotulo direto na
    # ponta da linha (ja existia) fica ilegivel quando as 6 bases
    # convergem pro mesmo patamar no fim da serie (2022 em diante). Dentro
    # do grafico, canto superior direito -- area vazia (o pico de 8-10h so
    # acontece em 2021, no canto superior ESQUERDO), economiza espaco em
    # vez de empurrar a legenda para fora da area do grafico.
    ax.legend(title="Base", loc="upper right", frameon=True, edgecolor="#333333")

    fig.tight_layout()
    fig.savefig(FIG_DIR / f"ana_06_tempo_solo_medio_mensal_por_base_{suffix}.png", dpi=150)
    plt.close(fig)


def fig_tempo_solo_medio_por_frota(df: pd.DataFrame, suffix: str) -> None:
    agg = (
        df.groupby(["sg_equipamento_icao", "ds_natureza_tipo_linha"])["tempo_solo_horas"]
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
    ax.set_title(f"GOL — Tempo de Solo Médio por Modelo de Aeronave\n({suffix})")
    ax.set_ylabel("Tempo de Solo (h, média)")
    ax.set_xlabel("Modelo")
    ax.legend(frameon=True, edgecolor="#333333")
    fig.tight_layout()
    fig.savefig(FIG_DIR / f"ana_02_tempo_solo_medio_por_frota_{suffix}.png", dpi=150)
    plt.close(fig)



def fig_top_bases_origem(df: pd.DataFrame, suffix: str) -> None:
    agg_full = (
        df.groupby("sg_iata_origem")["tempo_solo_horas"]
        .agg(n_etapas="count", solo_medio="mean")
    )
    hub = selecionar_hub(agg_full["n_etapas"])
    agg = agg_full.loc[hub.index].sort_values("n_etapas")

    norm = plt.Normalize(agg["solo_medio"].min(), agg["solo_medio"].max())
    cores = SEQ_ORANGE_CMAP(norm(agg["solo_medio"]))

    fig, ax = plt.subplots(figsize=(9, 6))
    barras = ax.barh(agg.index, agg["n_etapas"], color=cores, edgecolor="#333333", linewidth=0.5)
    ax.bar_label(barras, fmt="%.0f", fontweight="bold", fontsize=8, padding=3)
    ax.margins(x=0.09)
    ax.set_title(f"GOL — Bases HUB de Origem (80% acumulado)\n(cor = tempo de solo médio, {suffix})")
    ax.set_xlabel("Nº de Etapas")
    sm = plt.cm.ScalarMappable(cmap=SEQ_ORANGE_CMAP, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax)
    cbar.set_label("Tempo de Solo Médio (h)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / f"ana_03_top_bases_origem_{suffix}.png", dpi=150)
    plt.close(fig)


def fig_top_bases_chegadas(df: pd.DataFrame, suffix: str) -> None:
    contagem_full = df["sg_iata_destino"].value_counts()
    contagem = selecionar_hub(contagem_full).sort_values()
    fig, ax = plt.subplots(figsize=(9, 6))
    barras = ax.barh(contagem.index, contagem.values, color=GOL_ORANGE, edgecolor="#333333", linewidth=0.5)
    ax.bar_label(barras, fmt="%.0f", fontweight="bold", fontsize=8, padding=3)
    ax.margins(x=0.09)
    ax.set_title(f"GOL — Bases HUB com Mais Chegadas (80% acumulado)\n({suffix})")
    ax.set_xlabel("Nº de Chegadas")
    fig.tight_layout()
    fig.savefig(FIG_DIR / f"ana_04_top_bases_chegadas_{suffix}.png", dpi=150)
    plt.close(fig)


def rodar_janela(dt_ini: str, dt_fim: str, suffix: str) -> pd.DataFrame:
    df = load_data(dt_ini, dt_fim)
    print(f"[{suffix}] {dt_ini} a {dt_fim}: {len(df):,} etapas".replace(",", "."))
    fig_tempo_solo_medio_mensal(df, suffix)
    fig_tempo_solo_medio_por_frota(df, suffix)
    fig_top_bases_origem(df, suffix)
    fig_top_bases_chegadas(df, suffix)
    return df


def main() -> None:
    df_full = rodar_janela(*WINDOW_FULL, "full_2021_2026")
    df_2026 = rodar_janela(*WINDOW_2026, "2026")

    dfs_fechando = {}
    for dt_ini, dt_fim, suffix in JANELAS_FECHANDO:
        df = load_data(dt_ini, dt_fim)
        print(f"[{suffix}] {dt_ini} a {dt_fim}: {len(df):,} etapas".replace(",", "."))
        fig_tempo_solo_medio_mensal(df, suffix)
        dfs_fechando[suffix] = df

    fig_tempo_solo_medio_mensal_por_frota(df_full, "full_2021_2026")
    fig_tempo_solo_medio_mensal_por_base(df_full, "full_2021_2026")
    fig_tempo_solo_medio_mensal_por_base(dfs_fechando["2025_2026"], "2025_2026")
    fig_tempo_solo_medio_mensal_por_base(df_2026, "2026")

    print(f"Figuras salvas em {FIG_DIR}")


if __name__ == "__main__":
    main()
