"""Distribuicao da frota -- GOL, so passageiro (pergunta a2, SPEC-004 §5.2).

Regra padrao deste recorte de analise (a menos que dito o contrario):
so etapas PASSAGEIRO, exclui CARGUEIRO (SPEC-013 §3.1, vale para a linha).

Unidade de observacao (decisao do autor, 2026-09-11): a ETAPA e a unidade
principal -- composicao percentual e "frota que voa", ponderada por uso --
com a contagem de MATRICULAS distintas ao lado, como segunda leitura
("frota que existe"). A diferenca entre as duas e' o proprio achado: um
modelo pode ter muitas caudas e pouca etapa, ou o contrario.

Dimensao temporal (decisao do autor, 2026-09-11): a janela da curated_deep
comeca em 2021-01-01, entao MAX(dt)-MIN(dt) por matricula NAO e' idade de
aeronave -- e' PERMANENCIA OBSERVADA NA JANELA, censurada nos dois lados.
Aeronave que ja voava antes de 2021 aparece truncada a esquerda; aeronave
que segue voando aparece truncada a direita. O script mede e imprime as
duas censuras ([frota_07]) em vez de esconde-las. Idade real exigiria o
RAB, fonte nao-ANAC, fora do escopo do projeto.

Fonte: basica_curated_deep (db/anac_basica.sqlite), SPEC-012.
Roda com: conda run -n gov-sermi-perf python analise/a2_frota/analise_frota_gol.py
"""

import sqlite3
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

REPO_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = REPO_ROOT / "db" / "anac_basica.sqlite"
FIG_DIR = REPO_ROOT / "analise" / "a2_frota" / "a2_figuras_gol"
FIG_DIR.mkdir(parents=True, exist_ok=True)

EMPRESA = "GLO"
ROTULO = "GOL"

# Paleta GOL -- mesma da linha a4 (SPEC-013 §4): laranja da marca,
# aproximado, sem manual de marca oficial neste ambiente.
GOL_ORANGE = "#FF6900"
GOL_ORANGE_DARK = "#B34700"
NEUTRAL_GRAY = "#4d4d4d"
SEQ_ORANGE_CMAP = LinearSegmentedColormap.from_list("seq_orange", ["#ffe0c2", "#7a3300"])

# Categorica validada (skill dataviz), ordem fixa -- so para linha com
# mais de 3 series, onde o laranja monocromatico deixa de ser legivel.
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

# Modelo com menos etapas que isso na janela nao entra nos graficos de
# distribuicao (entra nas contagens e nas cercas). Evita caixa de boxplot
# desenhada sobre 1 matricula, que parece achado e e' ruido.
MIN_ETAPAS_DIST = 1000


def load_data(dt_ini: str, dt_fim: str) -> pd.DataFrame:
    """Etapas PASSAGEIRO da empresa, dt_partida_real na janela [dt_ini, dt_fim]."""
    con = sqlite3.connect(DB_PATH)
    query = """
        SELECT
            dt_partida_real, ds_matricula, sg_equipamento_icao, ds_modelo
        FROM basica_curated_deep
        WHERE sg_empresa_icao = ?
          AND ds_servico_tipo_linha = 'PASSAGEIRO'
          AND dt_partida_real BETWEEN ? AND ?
    """
    df = pd.read_sql_query(
        query, con, params=(EMPRESA, dt_ini, dt_fim), parse_dates=["dt_partida_real"]
    )
    con.close()
    return df


# ---------------------------------------------------------------------------
# P1/P2 -- premissas testadas e perfil do dado, antes de qualquer figura
# ---------------------------------------------------------------------------

def perfil_do_dado(df: pd.DataFrame, suffix: str) -> pd.DataFrame:
    """Imprime as cercas de premissa e devolve a tabela modelo x metricas."""
    n = len(df)
    vazias = df["ds_matricula"].isna().sum() + (df["ds_matricula"].str.strip() == "").sum()
    print(f"[frota_01] etapas na janela: {n:,}".replace(",", "."))
    print(f"[frota_02] matricula vazia: {vazias} ({100.0 * vazias / n:.4f}%)")
    print(f"[frota_03] matriculas distintas: {df['ds_matricula'].nunique()}")
    print(f"[frota_04] modelos distintos: {df['sg_equipamento_icao'].nunique()}")

    # 1:1 entre codigo ICAO de equipamento e descricao de modelo? Se quebrar,
    # as duas colunas deixam de ser a mesma dimensao e o agrupamento muda.
    por_equip = df.groupby("sg_equipamento_icao")["ds_modelo"].nunique()
    quebras = int((por_equip > 1).sum())
    print(f"[frota_05] equipamentos com mais de um ds_modelo: {quebras}")

    tab = (
        df.groupby(["sg_equipamento_icao", "ds_modelo"])
        .agg(etapas=("ds_matricula", "size"), matriculas=("ds_matricula", "nunique"))
        .reset_index()
    )
    tab["pct_etapas"] = 100.0 * tab["etapas"] / tab["etapas"].sum()
    tab["pct_matriculas"] = 100.0 * tab["matriculas"] / tab["matriculas"].sum()
    tab["etapas_por_matricula"] = tab["etapas"] / tab["matriculas"]
    tab = tab.sort_values("etapas", ascending=False).reset_index(drop=True)

    print(f"[frota_06] composicao ({suffix}), por etapa e por matricula:")
    for _, r in tab.iterrows():
        print(
            f"           {r.sg_equipamento_icao:5s} {r.ds_modelo[:38]:38s} "
            f"etapas={r.etapas:>7,} ({r.pct_etapas:5.2f}%)  "
            f"matriculas={r.matriculas:>3} ({r.pct_matriculas:5.2f}%)  "
            f"etapas/matricula={r.etapas_por_matricula:7.1f}".replace(",", ".")
        )
    return tab


def permanencia(df: pd.DataFrame, dt_ini: str, dt_fim: str) -> pd.DataFrame:
    """Permanencia observada por matricula, com as duas censuras marcadas.

    Censura a esquerda: primeira aparicao no primeiro mes da janela -- a
    aeronave provavelmente ja voava antes, o valor e' um piso, nao a idade.
    Censura a direita: ultima aparicao no ultimo mes -- segue voando.
    """
    ini = pd.Timestamp(dt_ini)
    fim = pd.Timestamp(dt_fim)

    g = (
        df.groupby(["ds_matricula", "sg_equipamento_icao"])["dt_partida_real"]
        .agg(primeira="min", ultima="max", etapas="size")
        .reset_index()
    )
    g["permanencia_anos"] = (g["ultima"] - g["primeira"]).dt.days / 365.25
    g["censura_esq"] = g["primeira"] < (ini + pd.Timedelta("31D"))
    g["censura_dir"] = g["ultima"] > (fim - pd.Timedelta("31D"))
    g["censura"] = "nenhuma"
    g.loc[g["censura_esq"] & ~g["censura_dir"], "censura"] = "esquerda"
    g.loc[~g["censura_esq"] & g["censura_dir"], "censura"] = "direita"
    g.loc[g["censura_esq"] & g["censura_dir"], "censura"] = "ambas"

    n = len(g)
    print(
        f"[frota_07] censura da permanencia: "
        f"ambas={100.0 * (g['censura'] == 'ambas').sum() / n:.1f}%  "
        f"esquerda={100.0 * (g['censura'] == 'esquerda').sum() / n:.1f}%  "
        f"direita={100.0 * (g['censura'] == 'direita').sum() / n:.1f}%  "
        f"nenhuma={100.0 * (g['censura'] == 'nenhuma').sum() / n:.1f}%"
    )
    print(
        f"[frota_08] permanencia observada (anos): mediana={g['permanencia_anos'].median():.2f}  "
        f"q1={g['permanencia_anos'].quantile(0.25):.2f}  "
        f"q3={g['permanencia_anos'].quantile(0.75):.2f}  "
        f"max={g['permanencia_anos'].max():.2f}"
    )
    return g


# ---------------------------------------------------------------------------
# P3/P4 -- composicao, evolucao e distribuicao
# ---------------------------------------------------------------------------

def fig_composicao(tab: pd.DataFrame, suffix: str) -> None:
    """Duas leituras lado a lado: % de etapas e % de matriculas por modelo."""
    t = tab.sort_values("pct_etapas")
    y = range(len(t))

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), sharey=True)
    for ax, col, cor, titulo, unidade in (
        (axes[0], "pct_etapas", GOL_ORANGE, "Por Etapa (frota que voa)", "% das etapas"),
        (axes[1], "pct_matriculas", GOL_ORANGE_DARK, "Por Matrícula (frota que existe)", "% das matrículas"),
    ):
        barras = ax.barh(list(y), t[col], color=cor, edgecolor="#333333", linewidth=0.5)
        ax.bar_label(barras, fmt="%.1f%%", fontweight="bold", fontsize=8, padding=3)
        ax.margins(x=0.14)
        ax.set_title(titulo)
        ax.set_xlabel(unidade)
    axes[0].set_yticks(list(y))
    axes[0].set_yticklabels(t["sg_equipamento_icao"])
    fig.suptitle(f"{ROTULO} — Composição da Frota\n({suffix})", fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG_DIR / f"composicao_frota_{suffix}.png", dpi=150)
    plt.close(fig)


def fig_intensidade_uso(tab: pd.DataFrame, suffix: str) -> None:
    """Etapas por matricula: a ponte entre as duas unidades de observacao."""
    t = tab[tab["etapas"] >= MIN_ETAPAS_DIST].sort_values("etapas_por_matricula")
    norm = plt.Normalize(t["etapas_por_matricula"].min(), t["etapas_por_matricula"].max())
    cores = SEQ_ORANGE_CMAP(norm(t["etapas_por_matricula"]))

    fig, ax = plt.subplots(figsize=(9, 4.5))
    barras = ax.barh(t["sg_equipamento_icao"], t["etapas_por_matricula"],
                     color=cores, edgecolor="#333333", linewidth=0.5)
    ax.bar_label(barras, fmt="%.0f", fontweight="bold", fontsize=9, padding=3)
    ax.margins(x=0.12)
    ax.set_title(f"{ROTULO} — Intensidade de Uso por Modelo\n(etapas por matrícula, {suffix})")
    ax.set_xlabel("Etapas por Matrícula")
    fig.tight_layout()
    fig.savefig(FIG_DIR / f"intensidade_uso_{suffix}.png", dpi=150)
    plt.close(fig)


def fig_evolucao_share(df: pd.DataFrame, suffix: str) -> None:
    """Share mensal de etapas por modelo -- entrada e saida de tipo na operacao."""
    mensal = (
        df.assign(mes=df["dt_partida_real"].dt.to_period("M").dt.to_timestamp())
        .groupby(["mes", "sg_equipamento_icao"])
        .size()
        .unstack(fill_value=0)
    )
    share = 100.0 * mensal.div(mensal.sum(axis=1), axis=0)
    ordem = share.mean().sort_values(ascending=False).index
    share = share[ordem]

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.stackplot(
        share.index, [share[c] for c in share.columns],
        labels=list(share.columns),
        colors=PALETA_CATEGORICA[: len(share.columns)],
        edgecolor="white", linewidth=0.3,
    )
    ax.set_ylim(0, 100)
    ax.set_title(f"{ROTULO} — Evolução da Composição da Frota\n(% das etapas do mês, {suffix})")
    ax.set_ylabel("% das Etapas do Mês")
    ax.set_xlabel("Mês")
    ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), frameon=True)
    fig.tight_layout()
    fig.savefig(FIG_DIR / f"evolucao_share_frota_{suffix}.png", dpi=150)
    plt.close(fig)


def fig_frota_ativa_mensal(df: pd.DataFrame, suffix: str) -> None:
    """Matriculas distintas que voaram em cada mes, por modelo."""
    ativa = (
        df.assign(mes=df["dt_partida_real"].dt.to_period("M").dt.to_timestamp())
        .groupby(["mes", "sg_equipamento_icao"])["ds_matricula"]
        .nunique()
        .unstack(fill_value=0)
    )
    ordem = ativa.mean().sort_values(ascending=False).index
    ativa = ativa[ordem]

    fig, ax = plt.subplots(figsize=(11, 5))
    for i, col in enumerate(ativa.columns):
        ax.plot(ativa.index, ativa[col], linewidth=2, marker="o", markersize=3,
                color=PALETA_CATEGORICA[i % len(PALETA_CATEGORICA)], label=col)
    total = ativa.sum(axis=1)
    ax.plot(total.index, total, linewidth=2.2, linestyle="--", color=NEUTRAL_GRAY, label="total")
    ax.set_title(f"{ROTULO} — Frota Ativa por Mês\n(matrículas distintas que voaram, {suffix})")
    ax.set_ylabel("Matrículas Ativas")
    ax.set_xlabel("Mês")
    ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), frameon=True)
    fig.tight_layout()
    fig.savefig(FIG_DIR / f"frota_ativa_mensal_{suffix}.png", dpi=150)
    plt.close(fig)


def fig_permanencia(g: pd.DataFrame, tab: pd.DataFrame, suffix: str) -> None:
    """Distribuicao da permanencia observada por modelo, com a censura visivel."""
    modelos = tab[tab["etapas"] >= MIN_ETAPAS_DIST]["sg_equipamento_icao"].tolist()
    dados, rotulos = [], []
    for m in modelos:
        v = g.loc[g["sg_equipamento_icao"] == m, "permanencia_anos"]
        if len(v) >= 3:
            dados.append(v.values)
            pct_amb = 100.0 * (g.loc[g["sg_equipamento_icao"] == m, "censura"] == "ambas").mean()
            rotulos.append(f"{m}\n(n={len(v)}, {pct_amb:.0f}% cens.)")
    ordem = sorted(range(len(dados)), key=lambda i: pd.Series(dados[i]).median())
    dados = [dados[i] for i in ordem]
    rotulos = [rotulos[i] for i in ordem]

    fig, ax = plt.subplots(figsize=(9, 5))
    bp = ax.boxplot(dados, tick_labels=rotulos, patch_artist=True, widths=0.55)
    for caixa in bp["boxes"]:
        caixa.set(facecolor=GOL_ORANGE, edgecolor="#333333", linewidth=0.8)
    for elem in ("whiskers", "caps", "medians"):
        for art in bp[elem]:
            art.set(color=NEUTRAL_GRAY, linewidth=1.3)
    for fl in bp["fliers"]:
        fl.set(marker="o", markersize=3, markerfacecolor=GOL_ORANGE_DARK, markeredgecolor="none", alpha=0.5)
    ax.set_title(
        f"{ROTULO} — Permanência Observada na Janela, por Modelo\n"
        f"(NÃO é idade da aeronave: truncada nos dois lados, {suffix})"
    )
    ax.set_ylabel("Anos entre 1ª e última etapa na janela")
    fig.tight_layout()
    fig.savefig(FIG_DIR / f"permanencia_por_modelo_{suffix}.png", dpi=150)
    plt.close(fig)


def rodar_janela(dt_ini: str, dt_fim: str, suffix: str, completo: bool = True) -> pd.DataFrame:
    print(f"\n=== {ROTULO} | {suffix} | {dt_ini} a {dt_fim} ===")
    df = load_data(dt_ini, dt_fim)
    tab = perfil_do_dado(df, suffix)
    fig_composicao(tab, suffix)
    if completo:
        g = permanencia(df, dt_ini, dt_fim)
        fig_intensidade_uso(tab, suffix)
        fig_evolucao_share(df, suffix)
        fig_frota_ativa_mensal(df, suffix)
        fig_permanencia(g, tab, suffix)
    return tab


def main() -> None:
    tab_full = rodar_janela(*WINDOW_FULL, "full_2021_2026")
    rodar_janela(*WINDOW_2026, "2026")

    # Teste de robustez: a composicao sobrevive ao estreitamento da janela?
    shares = {"full_2021_2026": tab_full.set_index("sg_equipamento_icao")["pct_etapas"]}
    for dt_ini, dt_fim, suffix in JANELAS_FECHANDO:
        tab = rodar_janela(dt_ini, dt_fim, suffix, completo=False)
        shares[suffix] = tab.set_index("sg_equipamento_icao")["pct_etapas"]

    comp = pd.DataFrame(shares).fillna(0.0)
    print("\n[frota_09] share de etapas por modelo em cada janela (%):")
    print(comp.round(2).to_string())
    amplitude = (comp.max(axis=1) - comp.min(axis=1)).sort_values(ascending=False)
    print("\n[frota_10] amplitude do share entre janelas (pp) -- quanto maior, menos estavel:")
    print(amplitude.round(2).to_string())

    print(f"\nFiguras salvas em {FIG_DIR}")


if __name__ == "__main__":
    main()
