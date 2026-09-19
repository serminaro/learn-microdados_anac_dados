"""Pontualidade A0/A14/D0/D14 -- GOL (pergunta a6).

Metricas (definicao fixada pelo autor, 2026-09-11):
    D0  = partidas com atraso <= 0 min   (saiu no horario ou antes)
    D14 = partidas com atraso <= 14 min  (equivale ao padrao "menos de 15")
    A0  = chegadas com atraso <= 0 min
    A14 = chegadas com atraso <= 14 min
atraso = real - previsto, em minutos.

Tres premissas decididas antes de calcular (2026-09-11):

1. DENOMINADOR: so voos REALIZADO, que e' o que vra_curated_deep contem.
   A taxa de CANCELAMENTO entra ao lado como metrica irma, medida em
   vra_silver, porque o vies tem direcao conhecida -- cancelar um voo que
   ia atrasar melhora as quatro taxas. Publicar pontualidade sem
   cancelamento ao lado esconde isso.

2. FRONTEIRA: <= 0 e <= 14, inclusive nos dois. Adiantado conta como no
   horario.

3. VIRADA DE DATA: atraso abaixo de -720 min ganha +1440 e atraso acima de
   +720 ganha -1440, quando a correcao traz o valor para dentro de +-720
   (partida 23:50 registrada como 00:10 do mesmo dia e' erro de data, nao
   antecipacao de um dia). O que continuar fora de +-720 depois disso sai
   do calculo e e' contado em [pont_03].

FUSO: os quatro carimbos do VRA estao numa referencia unica, verificado por
tres vias (GRU->MAO bate com o tempo voado da Basica; VCP<->MCO e' simetrico
nos dois sentidos; a mesma rota e' estavel de 2012 a 2026). Por isso
`real - previsto` dispensa conversao. A referencia PARECE ser horario de
Brasilia -- o toque de recolher de Congonhas aparece em 06h-22h no dado --
mas isso e' hipotese, nao achado, e so afeta o corte por hora do dia.

Fonte: vra_curated_deep (db/anac_vra.sqlite), SPEC-006/DEC-007.
Roda com: conda run -n gov-sermi-perf python analise/a6_pontualidade/analise_pontualidade_gol.py
"""

import sqlite3
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from iata_bases import aplicar_iata  # noqa: E402
from pareto_hub import selecionar_hub  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
DB_VRA = REPO_ROOT / "db" / "anac_vra.sqlite"
FIG_DIR = REPO_ROOT / "analise" / "a6_pontualidade" / "a6_figuras_gol"
FIG_DIR.mkdir(parents=True, exist_ok=True)

EMPRESA = "GLO"
ROTULO = "GOL"

GOL_ORANGE = "#FF6900"
GOL_ORANGE_DARK = "#B34700"
NEUTRAL_GRAY = "#4d4d4d"

# Uma cor fixa por metrica, nunca trocada entre figuras (skill dataviz).
COR_METRICA = {
    "D0": "#B34700",
    "D14": "#FF6900",
    "A0": "#4a3aa7",
    "A14": "#2a78d6",
}

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

LIMITE_ABSURDO_MIN = 720    # 12h: acima disso e' artefato, nao operacao
DIA_MIN = 1440
MIN_VOOS_BASE = 500         # base com menos que isso nao vira barra


def load_data(dt_ini: str, dt_fim: str) -> pd.DataFrame:
    """Voos realizados da empresa, com previsto de partida E de chegada."""
    con = sqlite3.connect(DB_VRA)
    query = """
        SELECT
            nr_voo, sg_icao_origem, sg_icao_destino,
            dt_hr_partida_prevista, dt_hr_partida_real,
            dt_hr_chegada_prevista, dt_hr_chegada_real
        FROM vra_curated_deep
        WHERE sg_empresa_icao = ?
          AND dt_hr_partida_prevista <> '' AND dt_hr_partida_prevista IS NOT NULL
          AND dt_hr_chegada_prevista <> '' AND dt_hr_chegada_prevista IS NOT NULL
          AND dt_hr_partida_real BETWEEN ? AND ?
    """
    df = pd.read_sql_query(
        query, con, params=(EMPRESA, dt_ini, dt_fim + " 23:59:59"),
        parse_dates=[
            "dt_hr_partida_prevista", "dt_hr_partida_real",
            "dt_hr_chegada_prevista", "dt_hr_chegada_real",
        ],
    )
    con.close()
    return aplicar_iata(df)


def serie_cancelamento_mensal(dt_ini: str, dt_fim: str) -> pd.Series:
    """% de cancelamento por mes de partida prevista (denominador = programados).

    Vem da silver, nao da curated: a curated filtra por data de partida REAL,
    que o voo cancelado nao tem, entao ela e' cega a cancelamento por
    construcao.
    """
    con = sqlite3.connect(DB_VRA)
    q = """
        SELECT substr(dt_hr_partida_prevista, 1, 7) AS mes,
               SUM(CASE WHEN ds_situacao_voo = 'CANCELADO' THEN 1 ELSE 0 END) AS cancelados,
               COUNT(*) AS programados
        FROM vra_silver
        WHERE sg_empresa_icao = ?
          AND dt_hr_partida_prevista BETWEEN ? AND ?
        GROUP BY 1 ORDER BY 1
    """
    d = pd.read_sql_query(q, con, params=(EMPRESA, dt_ini, dt_fim + " 23:59:59"))
    con.close()
    d["mes"] = pd.to_datetime(d["mes"] + "-01")
    d["pct"] = 100.0 * d["cancelados"] / d["programados"]
    return d.set_index("mes")["pct"]


def taxa_cancelamento(dt_ini: str, dt_fim: str) -> tuple[int, int, float]:
    """Metrica irma, medida na silver porque a curated nao guarda cancelado."""
    con = sqlite3.connect(DB_VRA)
    q = """
        SELECT ds_situacao_voo, COUNT(*) AS n
        FROM vra_silver
        WHERE sg_empresa_icao = ?
          AND dt_hr_partida_prevista BETWEEN ? AND ?
        GROUP BY 1
    """
    d = pd.read_sql_query(q, con, params=(EMPRESA, dt_ini, dt_fim + " 23:59:59"))
    con.close()
    por_sit = dict(zip(d["ds_situacao_voo"], d["n"]))
    realizado = int(por_sit.get("REALIZADO", 0))
    cancelado = int(por_sit.get("CANCELADO", 0))
    total = realizado + cancelado
    return realizado, cancelado, (100.0 * cancelado / total if total else float("nan"))


# ---------------------------------------------------------------------------
# P1/P2 -- premissas tratadas e testadas antes de qualquer figura
# ---------------------------------------------------------------------------

def corrigir_virada(atraso: pd.Series) -> pd.Series:
    """Devolve o atraso com a virada de data corrigida onde ela e' plausivel."""
    corr = atraso.copy()
    sobe = atraso < -LIMITE_ABSURDO_MIN
    desce = atraso > LIMITE_ABSURDO_MIN
    cand_sobe = atraso + DIA_MIN
    cand_desce = atraso - DIA_MIN
    corr[sobe & (cand_sobe.abs() <= LIMITE_ABSURDO_MIN)] = cand_sobe[sobe & (cand_sobe.abs() <= LIMITE_ABSURDO_MIN)]
    corr[desce & (cand_desce.abs() <= LIMITE_ABSURDO_MIN)] = cand_desce[desce & (cand_desce.abs() <= LIMITE_ABSURDO_MIN)]
    return corr


def preparar(df: pd.DataFrame, suffix: str) -> pd.DataFrame:
    """Calcula os atrasos, corrige virada, descarta absurdo e imprime as cercas."""
    n_bruto = len(df)
    df = df.copy()
    df["atraso_part"] = (df["dt_hr_partida_real"] - df["dt_hr_partida_prevista"]).dt.total_seconds() / 60.0
    df["atraso_cheg"] = (df["dt_hr_chegada_real"] - df["dt_hr_chegada_prevista"]).dt.total_seconds() / 60.0

    fora_antes = int(((df["atraso_part"].abs() > LIMITE_ABSURDO_MIN)
                      | (df["atraso_cheg"].abs() > LIMITE_ABSURDO_MIN)).sum())
    df["atraso_part"] = corrigir_virada(df["atraso_part"])
    df["atraso_cheg"] = corrigir_virada(df["atraso_cheg"])

    absurdo = (df["atraso_part"].abs() > LIMITE_ABSURDO_MIN) | (df["atraso_cheg"].abs() > LIMITE_ABSURDO_MIN)
    n_absurdo = int(absurdo.sum())
    df = df[~absurdo].copy()

    print(f"[pont_01] voos realizados com previsto, na janela: {n_bruto:,}".replace(",", "."))
    print(f"[pont_02] virada de data corrigida: {fora_antes - n_absurdo} voos")
    print(f"[pont_03] descartados por atraso absurdo (>{LIMITE_ABSURDO_MIN}min apos correcao): "
          f"{n_absurdo} ({100.0 * n_absurdo / n_bruto:.4f}%)")
    print(f"[pont_04] base de calculo final: {len(df):,}".replace(",", "."))
    return df


def _mascaras(df: pd.DataFrame) -> dict[str, pd.Series]:
    """As quatro fronteiras num lugar so.

    Taxa e contagem saem da MESMA mascara, de proposito: se a fronteira
    mudar, as duas mudam juntas. Duas definicoes paralelas acabariam
    divergindo, e um rotulo de contagem que nao fecha com a sua propria
    taxa e' pior que rotulo nenhum.
    """
    return {
        "D0": df["atraso_part"] <= 0,
        "D14": df["atraso_part"] <= 14,
        "A0": df["atraso_cheg"] <= 0,
        "A14": df["atraso_cheg"] <= 14,
    }


def metricas(df: pd.DataFrame) -> dict[str, float]:
    """% de voos que cumprem cada fronteira."""
    return {k: 100.0 * m.mean() for k, m in _mascaras(df).items()}


def contagens(df: pd.DataFrame) -> dict[str, int]:
    """Numero de voos que cumprem cada fronteira (numerador da taxa)."""
    return {k: int(m.sum()) for k, m in _mascaras(df).items()}


# ---------------------------------------------------------------------------
# P3/P4 -- nivel, evolucao, distribuicao e cortes
# ---------------------------------------------------------------------------

def fig_nivel(m: dict[str, float], canc_pct: float, suffix: str) -> None:
    """As quatro taxas, com o cancelamento ao lado como metrica irma."""
    fig, (ax, ax2) = plt.subplots(
        1, 2, figsize=(11, 4.6), gridspec_kw={"width_ratios": [3, 1]}
    )
    nomes = ["D0", "D14", "A0", "A14"]
    barras = ax.bar(nomes, [m[k] for k in nomes],
                    color=[COR_METRICA[k] for k in nomes], edgecolor="#333333", linewidth=0.5)
    ax.bar_label(barras, fmt="%.2f%%", fontweight="bold", fontsize=10, padding=3)
    ax.set_ylim(0, 100)
    ax.set_ylabel("% dos voos realizados")
    ax.set_title("Pontualidade (voos realizados)")

    b2 = ax2.bar(["cancelamento"], [canc_pct], color=NEUTRAL_GRAY,
                 edgecolor="#333333", linewidth=0.5)
    ax2.bar_label(b2, fmt="%.2f%%", fontweight="bold", fontsize=10, padding=3)
    ax2.set_ylim(0, 100)
    ax2.set_title("Métrica irmã\n(% dos programados)")

    fig.suptitle(f"{ROTULO} — A0 / A14 / D0 / D14\n({suffix})", fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG_DIR / f"nivel_pontualidade_{suffix}.png", dpi=150)
    plt.close(fig)


def fig_serie_mensal(df: pd.DataFrame, canc: pd.Series, suffix: str) -> pd.DataFrame:
    """Pontualidade e cancelamento no mesmo tempo, em dois paineis.

    Painel proprio para o cancelamento, e nao uma quinta linha: ele vive
    entre 1% e 3%, contra 60% a 90% das outras quatro, e na mesma escala
    viraria uma reta colada no zero. Eixo duplo esta descartado pela regra
    da SPEC-013 §4 (skill dataviz). Dois paineis empilhados com o mesmo
    eixo de tempo resolvem sem distorcer nenhuma das duas magnitudes.
    """
    mensal = (
        df.assign(mes=df["dt_hr_partida_real"].dt.to_period("M").dt.to_timestamp())
        .groupby("mes")
        .apply(lambda g: pd.Series(metricas(g)), include_groups=False)
    )

    fig, (ax, axc) = plt.subplots(
        2, 1, figsize=(11, 6.8), sharex=True,
        gridspec_kw={"height_ratios": [3, 1], "hspace": 0.12},
    )

    for k in ("D0", "D14", "A0", "A14"):
        ax.plot(mensal.index, mensal[k], linewidth=2, marker="o", markersize=3,
                color=COR_METRICA[k], label=k)
    ax.set_ylim(0, 100)
    ax.set_title(f"{ROTULO} — Pontualidade e Cancelamento por Mês\n({suffix})")
    ax.set_ylabel("% dos voos realizados")
    ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), frameon=True)

    canc = canc.reindex(mensal.index)
    axc.plot(canc.index, canc.values, linewidth=2, marker="o", markersize=3,
             color=NEUTRAL_GRAY)
    media_canc = canc.mean()
    axc.axhline(media_canc, color=NEUTRAL_GRAY, linestyle="--", linewidth=1.1)
    # Rotulo no canto vazio do painel, nao ancorado na serie: ancorado no
    # primeiro ponto ele caia em cima da propria linha.
    axc.text(0.995, 0.88, f"μ={media_canc:.2f}%", transform=axc.transAxes,
             ha="right", va="top", color=NEUTRAL_GRAY, fontweight="bold", fontsize=9)
    axc.set_ylim(0, max(5.0, float(canc.max()) * 1.2))
    # Sem legenda neste painel: ha uma serie so, e o eixo ja a nomeia. A
    # legenda fora do eixo era cortada pela largura reservada ao painel de cima.
    axc.set_ylabel("Cancelamento\n(% dos programados)")
    axc.set_xlabel("Mês")

    fig.tight_layout()
    fig.savefig(FIG_DIR / f"serie_mensal_{suffix}.png", dpi=150)
    plt.close(fig)

    pior = canc.idxmax()
    print(f"[pont_10] cancelamento mensal: media={media_canc:.2f}%  "
          f"min={canc.min():.2f}%  max={canc.max():.2f}% ({pior:%Y-%m})")
    return mensal


def fig_distribuicao_atraso(df: pd.DataFrame, suffix: str) -> None:
    """De onde as taxas saem: a distribuicao, com as duas fronteiras marcadas."""
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.6), sharey=True)
    for ax, col, cor, titulo in (
        (axes[0], "atraso_part", GOL_ORANGE, "Partida"),
        (axes[1], "atraso_cheg", GOL_ORANGE_DARK, "Chegada"),
    ):
        v = df[col].clip(-60, 180)
        ax.hist(v, bins=80, color=cor, edgecolor="none")
        ax.axvline(0, color=NEUTRAL_GRAY, linestyle="--", linewidth=1.4)
        ax.axvline(14, color=NEUTRAL_GRAY, linestyle=":", linewidth=1.6)
        ax.annotate("0", xy=(0, ax.get_ylim()[1] * 0.93), xytext=(3, 0),
                    textcoords="offset points", color=NEUTRAL_GRAY, fontweight="bold")
        ax.annotate("14", xy=(14, ax.get_ylim()[1] * 0.85), xytext=(3, 0),
                    textcoords="offset points", color=NEUTRAL_GRAY, fontweight="bold")
        mediana = df[col].median()
        ax.set_title(f"{titulo} (mediana={mediana:.1f} min)")
        ax.set_xlabel("Atraso (min, recorte -60 a +180)")
    axes[0].set_ylabel("Nº de Voos")
    fig.suptitle(
        f"{ROTULO} — Distribuição do Atraso e as Fronteiras das Métricas\n({suffix})",
        fontweight="bold",
    )
    fig.tight_layout()
    fig.savefig(FIG_DIR / f"distribuicao_atraso_{suffix}.png", dpi=150)
    plt.close(fig)


def fig_por_base(df: pd.DataFrame, suffix: str) -> None:
    """D14 por base HUB de origem (80% acumulado, pareto_hub)."""
    contagem = df["sg_iata_origem"].value_counts()
    hub = selecionar_hub(contagem)
    hub = hub[hub >= MIN_VOOS_BASE]
    agg = (
        df[df["sg_iata_origem"].isin(hub.index)]
        .groupby("sg_iata_origem")
        .apply(lambda g: pd.Series({"D14": metricas(g)["D14"], "voos": len(g)}),
               include_groups=False)
        .sort_values("D14")
    )
    fig, ax = plt.subplots(figsize=(9, 6))
    barras = ax.barh(agg.index, agg["D14"], color=GOL_ORANGE,
                     edgecolor="#333333", linewidth=0.5)
    ax.bar_label(barras, labels=[f"{v:.1f}%  (n={int(n):,})".replace(",", ".")
                                 for v, n in zip(agg["D14"], agg["voos"])],
                 fontweight="bold", fontsize=8, padding=3)
    ax.margins(x=0.22)
    ax.set_xlim(0, 100)
    ax.set_title(f"{ROTULO} — D14 por Base HUB de Origem\n(80% acumulado, {suffix})")
    ax.set_xlabel("D14 (% das partidas)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / f"d14_por_base_{suffix}.png", dpi=150)
    plt.close(fig)


def fig_por_hora(df: pd.DataFrame, suffix: str) -> None:
    """D14 e A14 por hora prevista de partida.

    A hora e' a do dado, numa referencia unica; a hipotese (nao confirmada)
    e' que seja horario de Brasilia. O titulo carrega a ressalva porque o
    eixo so faz sentido operacional se a hipotese valer.
    """
    h = df.assign(hora=df["dt_hr_partida_prevista"].dt.hour)
    agg = (
        h.groupby("hora")
        .apply(lambda g: pd.Series({**metricas(g), "voos": len(g)}), include_groups=False)
    )
    agg = agg[agg["voos"] >= MIN_VOOS_BASE]

    fig, ax = plt.subplots(figsize=(11, 4.8))
    for k in ("D14", "A14"):
        ax.plot(agg.index, agg[k], linewidth=2, marker="o", markersize=4,
                color=COR_METRICA[k], label=k)
    ax.set_ylim(0, 100)
    ax.set_title(
        f"{ROTULO} — Pontualidade por Hora Prevista de Partida\n"
        f"(hora na referência do dado, provavelmente Brasília — hipótese, {suffix})"
    )
    ax.set_ylabel("% dos voos")
    ax.set_xlabel("Hora prevista de partida")
    ax.set_xticks(list(agg.index))
    ax.legend(frameon=True)
    fig.tight_layout()
    fig.savefig(FIG_DIR / f"pontualidade_por_hora_{suffix}.png", dpi=150)
    plt.close(fig)


def rodar_janela(dt_ini: str, dt_fim: str, suffix: str, completo: bool = True) -> dict[str, float]:
    print(f"\n=== {ROTULO} | {suffix} | {dt_ini} a {dt_fim} ===")
    df = preparar(load_data(dt_ini, dt_fim), suffix)
    m = metricas(df)
    realizado, cancelado, canc_pct = taxa_cancelamento(dt_ini, dt_fim)
    print(f"[pont_05] D0={m['D0']:.2f}%  D14={m['D14']:.2f}%  "
          f"A0={m['A0']:.2f}%  A14={m['A14']:.2f}%")
    print(f"[pont_06] cancelamento: {cancelado:,} de {realizado + cancelado:,} programados "
          f"({canc_pct:.2f}%)".replace(",", "."))
    print(f"[pont_07] atraso mediano: partida={df['atraso_part'].median():.1f} min  "
          f"chegada={df['atraso_cheg'].median():.1f} min")

    fig_nivel(m, canc_pct, suffix)
    if completo:
        fig_serie_mensal(df, serie_cancelamento_mensal(dt_ini, dt_fim), suffix)
        fig_distribuicao_atraso(df, suffix)
        fig_por_base(df, suffix)
        fig_por_hora(df, suffix)
    return m


def main() -> None:
    resultados = {"full_2021_2026": rodar_janela(*WINDOW_FULL, "full_2021_2026")}
    resultados["2026"] = rodar_janela(*WINDOW_2026, "2026")

    for dt_ini, dt_fim, suffix in JANELAS_FECHANDO:
        resultados[suffix] = rodar_janela(dt_ini, dt_fim, suffix, completo=False)

    comp = pd.DataFrame(resultados)[
        ["full_2021_2026", "2022_2026", "2023_2026", "2024_2026", "2025_2026", "2026"]
    ]
    print("\n[pont_08] metrica em cada janela (%):")
    print(comp.round(2).to_string())
    print("\n[pont_09] amplitude entre janelas (pp) -- quanto maior, menos estavel:")
    print((comp.max(axis=1) - comp.min(axis=1)).round(2).to_string())

    print(f"\nFiguras salvas em {FIG_DIR}")


if __name__ == "__main__":
    main()
