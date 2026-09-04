"""Block time -- GOL e Azul, sobra e falta de tempo (SPEC-014).

Fonte: fato_block_time_gol_azul (db/anac_basica.sqlite). Grao ja herda o
filtro PASSAGEIRO de basica_curated_deep -> fato_rotacao_aeronave_gol_azul
(regra padrao da linha de analise: so passageiro, salvo dito o contrario).

folga_horas = tempo_previsto_horas (VRA) - nr_horas_voadas (Basica,
tempo no ar). Achado ja registrado (SPEC-014 Sec.6.2): tempo_real_vra_horas
e estatisticamente identico a nr_horas_voadas -- folga_horas mede bloco
programado menos tempo no ar real, nao bloco menos bloco. Uma folga
positiva pequena e esperada estruturalmente (todo bloco programado
inclui taxi); nao dividir isso em "taxi" vs "margem estrategica" sem
dado novo.

Roda com: conda run -n pesquisa-azul python analise/a5_block_time/analise_block_time_gol_azul.py
"""

import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import pandas as pd

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from iata_bases import aplicar_iata  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = REPO_ROOT / "db" / "anac_basica.sqlite"
FIG_DIR = REPO_ROOT / "analise" / "a5_block_time" / "a5_figuras_block_time"
CSV_PATH = REPO_ROOT / "analise" / "a5_block_time" / "dados_block_time_gol_azul.csv"
FIG_DIR.mkdir(parents=True, exist_ok=True)

# Cores por empresa -- aproximacao de marca (sem manual oficial
# disponivel neste ambiente, mesmo aviso ja registrado para GOL_ORANGE em
# analise_etapa_media_gol.py; AZUL_BLUE e nova aproximacao, ajustar se
# houver hex oficial). Paleta categorica validada para graficos com mais
# de 2-3 series (mesma logica da SPEC-013 Sec.6.7/v7).
GOL_ORANGE = "#FF6900"
AZUL_BLUE = "#0039A6"
NEUTRAL_GRAY = "#4d4d4d"
COR_SOBRA = "#1baf7a"   # verde -- folga positiva
COR_FALTA = "#e34948"   # vermelho -- folga negativa
PALETA_CATEGORICA = [
    "#2a78d6", "#eb6834", "#1baf7a", "#eda100",
    "#e87ba4", "#008300", "#4a3aa7", "#e34948",
]
# Extensao da categorica para graficos com mais series que a paleta base
# cobre (fig_folga_por_frota, 12 modelos) -- 4 tons adicionais bem
# separados dos 8 originais e do verde/vermelho ja reservados para
# sobra/falta (COR_SOBRA/COR_FALTA).
PALETA_MODELO = PALETA_CATEGORICA + ["#8b4513", "#00bcd4", "#9c27b0", "#607d8b"]
COR_GERAL = "#4a3aa7"  # roxo -- so' para agregados GOL+Azul combinados (nao e' cor de nenhuma empresa)
CORES_EMPRESA = {"GLO": GOL_ORANGE, "AZU": AZUL_BLUE}
NOME_EMPRESA = {"GLO": "GOL", "AZU": "Azul"}

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


def load_data() -> pd.DataFrame:
    """fato_block_time_gol_azul nao carrega ds_natureza_tipo_linha (herda
    de fato_rotacao_aeronave_gol_azul, que nao tem essa coluna -- so'
    existe em basica_curated_deep). Trazida por mapeamento id_basica ->
    natureza em pandas, mesma tecnica ja usada em analise_tempo_solo_gol.py
    e distribuicao_etapa_media_gol.py (bug real, achado ao rodar o
    script pela primeira vez ate' o fim nesta sessao, 2026-09-02 --
    fig_folga_por_natureza nunca tinha completado antes)."""
    con = sqlite3.connect(DB_PATH)
    natureza = pd.read_sql_query(
        "SELECT id_basica, ds_natureza_tipo_linha FROM basica_curated_deep",
        con,
    ).set_index("id_basica")["ds_natureza_tipo_linha"]

    df = pd.read_sql_query(
        "SELECT * FROM fato_block_time_gol_azul", con,
        parse_dates=["dt_partida_real", "dt_chegada_real"],
    )
    con.close()

    df["ds_natureza_tipo_linha"] = df["id_basica"].map(natureza)
    return aplicar_iata(df)


def selecionar_hub(contagens: pd.Series) -> pd.Series:
    """Mesma regra de 80% acumulado da SPEC-013 Sec.6.5."""
    ordenado = contagens.sort_values(ascending=False)
    pct = 100 * ordenado / ordenado.sum()
    pct_acum = pct.cumsum()
    return ordenado[(pct_acum - pct) < 80]


def fig_distribuicao_folga(df: pd.DataFrame) -> None:
    """Populacao combinada GOL+Azul -- usa COR_GERAL (roxo), nao a cor de
    nenhuma empresa isolada (laranja/azul ja tem significado especifico
    nos outros graficos desta pasta, usar aqui seria enganoso)."""
    sub = df[df["fl_match_vra"] == 1]["folga_horas"].dropna()
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(sub.clip(-2, 2), bins=80, color=COR_GERAL, edgecolor="none")
    ax.axvline(0, color=NEUTRAL_GRAY, linestyle="--", linewidth=1.3)
    ax.set_title("GOL + Azul — Distribuição de folga_horas\n(recortado em ±2h para legibilidade)")
    ax.set_xlabel("folga_horas (positivo = sobra, negativo = falta)")
    ax.set_ylabel("Nº de etapas")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "distribuicao_folga_horas.png", dpi=150)
    plt.close(fig)


def fig_folga_por_empresa(df: pd.DataFrame) -> None:
    sub = df[df["fl_match_vra"] == 1]
    agg = sub.groupby("sg_empresa_icao")["folga_horas"].agg(["mean", "median", "count"])
    fig, ax = plt.subplots(figsize=(7, 5))
    x = range(len(agg))
    cores = [CORES_EMPRESA[e] for e in agg.index]
    barras = ax.bar(x, agg["mean"], color=cores)
    ax.bar_label(barras, fmt="%.3f", fontweight="bold", padding=3)
    ax.axhline(0, color=NEUTRAL_GRAY, linewidth=1)
    ax.set_xticks(list(x))
    ax.set_xticklabels([NOME_EMPRESA[e] for e in agg.index])
    ax.set_title("Folga Média por Empresa\n(GOL + Azul)")
    ax.set_ylabel("folga_horas (média)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "folga_media_por_empresa.png", dpi=150)
    plt.close(fig)


def fig_folga_por_frota(df: pd.DataFrame, min_etapas: int = 1000) -> None:
    """12 modelos, so' 2 cores por empresa achatava a distincao entre
    modelos (achado desta rodada, 2026-09-02). Agora: cor distinta por
    MODELO (PALETA_MODELO), textura (hatch) por EMPRESA -- nao perde
    nenhuma das duas informacoes, so' separa os dois canais visuais."""
    sub = df[df["fl_match_vra"] == 1]
    agg = (
        sub.groupby(["sg_equipamento_icao", "sg_empresa_icao"])["folga_horas"]
        .agg(["mean", "count"]).reset_index()
    )
    agg = agg[agg["count"] >= min_etapas]
    pivot = agg.pivot(index="sg_equipamento_icao", columns="sg_empresa_icao", values="mean")
    ordem = agg.groupby("sg_equipamento_icao")["mean"].mean().sort_values(ascending=False).index
    pivot = pivot.reindex(ordem)

    cores_modelo = {m: c for m, c in zip(pivot.index, PALETA_MODELO)}
    hatch_empresa = {"GLO": "", "AZU": "///"}

    fig, ax = plt.subplots(figsize=(12, 5.5))
    x = range(len(pivot))
    largura = 0.38
    for i, empresa in enumerate(pivot.columns):
        deslocamento = (i - (len(pivot.columns) - 1) / 2) * largura
        cores = [cores_modelo[m] for m in pivot.index]
        barras = ax.bar(
            [xi + deslocamento for xi in x], pivot[empresa], width=largura,
            color=cores, edgecolor="#222222", linewidth=0.6, hatch=hatch_empresa.get(empresa, ""),
        )
        ax.bar_label(barras, fmt="%.2f", fontsize=7, fontweight="bold", padding=2)
    ax.axhline(0, color=NEUTRAL_GRAY, linewidth=1)
    ax.set_xticks(list(x))
    ax.set_xticklabels(pivot.index, rotation=45, ha="right")
    ax.set_title(f"Folga Média por Modelo de Aeronave\n(GOL + Azul, modelos com ≥{min_etapas} etapas)")
    ax.set_ylabel("folga_horas (média)")

    legenda = [
        Patch(facecolor="#bbbbbb", edgecolor="#222222", label="GOL"),
        Patch(facecolor="#bbbbbb", edgecolor="#222222", hatch="///", label="Azul"),
    ]
    ax.legend(handles=legenda, title="Empresa (textura)", frameon=True, edgecolor="#333333")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "folga_media_por_frota.png", dpi=150)
    plt.close(fig)


def fig_folga_mensal_por_empresa(df: pd.DataFrame) -> None:
    sub = df[df["fl_match_vra"] == 1]
    fig, ax = plt.subplots(figsize=(11, 5))
    for empresa in ["GLO", "AZU"]:
        s = sub[sub["sg_empresa_icao"] == empresa]
        mensal = s.set_index("dt_partida_real")["folga_horas"].resample("MS").mean()
        ax.plot(mensal.index, mensal.values, linewidth=2, marker="o", markersize=3,
                label=NOME_EMPRESA[empresa], color=CORES_EMPRESA[empresa])
    ax.axhline(0, color=NEUTRAL_GRAY, linestyle="--", linewidth=1)
    ax.set_title("Folga Média Mensal por Empresa\n(GOL + Azul, 2021-2026)")
    ax.set_ylabel("folga_horas (média)")
    ax.set_xlabel("Mês")
    ax.legend(frameon=True, edgecolor="#333333")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "folga_mensal_por_empresa.png", dpi=150)
    plt.close(fig)


def fig_atraso_partida_por_empresa(df: pd.DataFrame) -> None:
    sub = df[df["fl_match_vra"] == 1].copy()
    sub["atraso_partida_min"] = sub["atraso_partida_horas"] * 60
    fig, ax = plt.subplots(figsize=(10, 5))
    for empresa, cor in CORES_EMPRESA.items():
        s = sub[sub["sg_empresa_icao"] == empresa]["atraso_partida_min"].clip(-30, 60)
        ax.hist(s, bins=60, alpha=0.6, label=NOME_EMPRESA[empresa], color=cor)
    ax.axvline(0, color=NEUTRAL_GRAY, linestyle="--", linewidth=1.3)
    ax.set_title("Distribuição do Atraso de Partida por Empresa\n(recortado em -30/+60 min para legibilidade)")
    ax.set_xlabel("Atraso de partida (minutos)")
    ax.set_ylabel("Nº de etapas")
    ax.legend(frameon=True, edgecolor="#333333")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "distribuicao_atraso_partida.png", dpi=150)
    plt.close(fig)


def fig_top_bases_folga(df: pd.DataFrame, empresa: str, top_n: int = 10) -> None:
    sub = df[(df["sg_empresa_icao"] == empresa) & (df["fl_match_vra"] == 1)]
    hub = selecionar_hub(sub["sg_iata_origem"].value_counts())
    bases = hub.index.tolist()[:top_n]
    agg = sub[sub["sg_iata_origem"].isin(bases)].groupby("sg_iata_origem")["folga_horas"].mean()
    agg = agg.reindex(bases).sort_values()
    cores = [COR_SOBRA if v >= 0 else COR_FALTA for v in agg.values]

    fig, ax = plt.subplots(figsize=(9, 6))
    barras = ax.barh(agg.index, agg.values, color=cores, edgecolor="#333333", linewidth=0.5)
    ax.bar_label(barras, fmt="%.3f", fontweight="bold", fontsize=8, padding=3)
    ax.axvline(0, color=NEUTRAL_GRAY, linewidth=1)
    ax.set_title(f"{NOME_EMPRESA[empresa]} — Folga Média por Base HUB\n(80% acumulado, verde=sobra, vermelho=falta)")
    ax.set_xlabel("folga_horas (média)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / f"folga_por_base_{empresa.lower()}.png", dpi=150)
    plt.close(fig)


def fig_folga_por_natureza(df: pd.DataFrame) -> None:
    sub = df[df["fl_match_vra"] == 1]
    agg = sub.groupby(["ds_natureza_tipo_linha", "sg_empresa_icao"])["folga_horas"].mean().unstack()
    fig, ax = plt.subplots(figsize=(8, 5))
    x = range(len(agg))
    largura = 0.38
    for i, empresa in enumerate(agg.columns):
        deslocamento = (i - (len(agg.columns) - 1) / 2) * largura
        barras = ax.bar([xi + deslocamento for xi in x], agg[empresa], width=largura,
                         label=NOME_EMPRESA.get(empresa, empresa), color=CORES_EMPRESA.get(empresa, GOL_ORANGE))
        ax.bar_label(barras, fmt="%.3f", fontweight="bold", padding=2)
    ax.axhline(0, color=NEUTRAL_GRAY, linewidth=1)
    ax.set_xticks(list(x))
    ax.set_xticklabels([s.title() for s in agg.index])
    ax.set_title("Folga Média por Natureza da Linha\n(GOL + Azul)")
    ax.set_ylabel("folga_horas (média)")
    ax.legend(frameon=True, edgecolor="#333333")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "folga_por_natureza.png", dpi=150)
    plt.close(fig)


def fig_continuidade_x_folga(df: pd.DataFrame) -> None:
    sub = df[df["fl_match_vra"] == 1].copy()
    sub["grupo_continuidade"] = sub["fl_continuidade_ok"].map(
        {1: "Continuidade OK", 0: "Continuidade quebrada"}
    ).fillna("Primeira etapa (sem anterior)")
    agg = sub.groupby("grupo_continuidade")["folga_horas"].agg(["mean", "count"])
    ordem = ["Continuidade OK", "Continuidade quebrada", "Primeira etapa (sem anterior)"]
    agg = agg.reindex(ordem)

    fig, ax = plt.subplots(figsize=(9, 5))
    cores = [PALETA_CATEGORICA[0], PALETA_CATEGORICA[7], PALETA_CATEGORICA[3]]
    barras = ax.bar(agg.index, agg["mean"], color=cores)
    ax.bar_label(barras, fmt="%.3f", fontweight="bold", padding=3)
    for i, (_, row) in enumerate(agg.iterrows()):
        ax.annotate(f"n={int(row['count']):,}".replace(",", "."), xy=(i, 0),
                     xytext=(0, -14), textcoords="offset points", ha="center", fontsize=8, color=NEUTRAL_GRAY)
    ax.axhline(0, color=NEUTRAL_GRAY, linewidth=1)
    ax.set_title("Folga Média vs. Continuidade da Rotação\n(GOL + Azul)")
    ax.set_ylabel("folga_horas (média)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "continuidade_x_folga.png", dpi=150)
    plt.close(fig)


def main() -> None:
    df = load_data()
    print(f"Linhas carregadas: {len(df):,}".replace(",", "."))

    df.to_csv(CSV_PATH, index=False)
    print(f"CSV exportado: {CSV_PATH} ({CSV_PATH.stat().st_size / 1e6:.1f} MB)")

    fig_distribuicao_folga(df)
    fig_folga_por_empresa(df)
    fig_folga_por_frota(df)
    fig_folga_mensal_por_empresa(df)
    fig_atraso_partida_por_empresa(df)
    fig_top_bases_folga(df, "GLO")
    fig_top_bases_folga(df, "AZU")
    fig_folga_por_natureza(df)
    fig_continuidade_x_folga(df)

    print(f"Figuras salvas em {FIG_DIR}")


if __name__ == "__main__":
    main()
