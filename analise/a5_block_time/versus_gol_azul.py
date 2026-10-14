"""GOL x Azul lado a lado -- block time (folga, atraso de partida, atraso de
chegada), mesmo grafico, dois paineis, mesma escala sempre que a comparacao
pedir isso. Espelho de a3_tempo_de_solo/versus_gol_azul.py e
a4_etapa_media/versus_gol_azul.py: nao reimplementa a query, importa
distribuicao_block_time_gol.py e distribuicao_block_time_azul.py como
modulos e reusa load_data()/selecionar_hub()/PALETA_CATEGORICA de cada um.

"Mesmo olhar do problema" traduzido, grafico a grafico, do mesmo jeito que
nos espelhos de a3/a4:
  (a) mesmo eixo Y ou X compartilhado -- quando a pergunta e' "quem e' maior".
  (b) densidade (nao contagem bruta) nos histogramas -- Azul tem mais
      etapas que GOL mesmo depois do truncamento.
  (c) mesma cerca de corte para as duas empresas, aplicada por variavel
      (nao uma unica vez pra tudo, como em a3, porque aqui ha' 3 variaveis
      distintas: folga_horas, atraso_partida_horas, atraso_chegada_horas).

Corte de truncagem: CORTE_MIN = 60 minutos (+-1h) fixo para as duas
empresas e todos os graficos que dependem de folga/atraso -- pedido do
autor, 2026-09-03, mesma politica ja validada e usada em ambos os scripts
individuais (familia "cerca_"). Unidades em minutos, nao horas, mesmo
motivo (mais legivel numa faixa estreita).

Roda com: conda run -n pesquisa-azul python analise/a5_block_time/versus_gol_azul.py
"""

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import distribuicao_block_time_gol as dg
import distribuicao_block_time_azul as da

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from iata_bases import aplicar_iata  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
FIG_DIR = REPO_ROOT / "analise" / "a5_block_time" / "a5_figuras_versus"
FIG_DIR.mkdir(parents=True, exist_ok=True)

GOL_ORANGE = "#FF6900"
AZUL_BLUE = "#0039A6"
NEUTRAL_GRAY = "#4d4d4d"

# Corte fixo unico para as duas empresas, aplicado por variavel (folga,
# atraso partida, atraso chegada) -- mesma politica da familia "cerca_" em
# distribuicao_block_time_gol.py/_azul.py.
CORTE_MIN = 60.0

sns.set_theme(style="whitegrid")
plt.rcParams.update({
    "figure.facecolor": "#ffffff",
    "axes.facecolor": "#ffffff",
    "axes.titleweight": "bold",
    "font.size": 10,
})


def fmt_milhar(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def truncar_cerca(df: pd.DataFrame, coluna: str, limite_min: float = CORTE_MIN) -> pd.DataFrame:
    """fl_match_vra==1 (folga/atraso so' fazem sentido onde ha' match) +
    corte fixo +-limite_min, mesma regra da familia cerca_ dos scripts
    individuais."""
    limite_h = limite_min / 60
    sub = df[df["fl_match_vra"] == 1].dropna(subset=[coluna]).copy()
    return sub[sub[coluna].between(-limite_h, limite_h)]


def _preparar_diff(df: pd.DataFrame, limite_valido: float = 24.0) -> pd.Series:
    """Δ = atraso_chegada - atraso_partida, com o mesmo filtro de garbage
    de timestamp (|atraso|>24h) usado nos scripts individuais antes de
    truncar no corte fixo."""
    sub = df[df["fl_match_vra"] == 1].dropna(subset=["atraso_partida_horas", "atraso_chegada_horas"]).copy()
    sub = sub[(sub["atraso_partida_horas"].abs() <= limite_valido) &
              (sub["atraso_chegada_horas"].abs() <= limite_valido)]
    diff = sub["atraso_chegada_horas"] - sub["atraso_partida_horas"]
    limite_h = CORTE_MIN / 60
    return diff[diff.between(-limite_h, limite_h)]


def v01_folga_run_sequence_diaria(sub_g: pd.DataFrame, sub_a: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    diario_g = sub_g.set_index("dt_partida_real")["folga_horas"].resample("D").mean().dropna() * 60
    diario_a = sub_a.set_index("dt_partida_real")["folga_horas"].resample("D").mean().dropna() * 60

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7.5), sharex=True, sharey=True)
    for ax, diario, cor, nome in ((ax1, diario_g, GOL_ORANGE, "GOL"), (ax2, diario_a, AZUL_BLUE, "Azul")):
        ax.plot(diario.index, diario.values, color=cor, linewidth=0.8, alpha=0.85)
        ax.axhline(diario.mean(), color=NEUTRAL_GRAY, linestyle="--", linewidth=1.2)
        ax.axhline(0, color="#333333", linestyle=":", linewidth=1.0)
        ax.set_title(f"{nome} (média geral = {diario.mean():.1f}min)")
        ax.set_ylabel("Folga média do dia (min)")
    ax2.set_xlabel("Data (ordem cronológica)")
    fig.suptitle(
        f"GOL x Azul — Run Sequence Plot: Folga Média Diária "
        f"(corte fixo ±{CORTE_MIN:.0f}min, eixo Y compartilhado)",
        fontweight="bold",
    )
    fig.tight_layout()
    fig.savefig(FIG_DIR / "v01_folga_run_sequence_diaria.png", dpi=150)
    plt.close(fig)
    return diario_g, diario_a


def _distribuicao_forma(sub_g: pd.DataFrame, sub_a: pd.DataFrame, coluna: str,
                         titulo_var: str, filename: str) -> None:
    xlim = (-CORTE_MIN, CORTE_MIN)
    fig, axes = plt.subplots(2, 2, figsize=(13, 7), sharex="col",
                              gridspec_kw={"height_ratios": [3, 1], "hspace": 0.08, "wspace": 0.15})
    axes[0, 1].sharey(axes[0, 0])
    for col, (sub, cor, nome) in enumerate(((sub_g, GOL_ORANGE, "GOL"), (sub_a, AZUL_BLUE, "Azul"))):
        ax_hist, ax_box = axes[0, col], axes[1, col]
        # Granularidade de minuto inteiro (achado da rodada GOL) -- bin de
        # largura 1, alinhado ao inteiro, senao cria serrilhado artificial.
        valores_min = (sub[coluna] * 60).round()
        sns.histplot(valores_min, binwidth=1, binrange=(xlim[0] - 0.5, xlim[1] + 0.5), color=cor, stat="density",
                     ax=ax_hist, edgecolor="white", linewidth=0.3, alpha=0.85)
        sns.kdeplot(valores_min, color=NEUTRAL_GRAY, linewidth=2, ax=ax_hist, clip=xlim)
        ax_hist.axvline(0, color="#333333", linestyle=":", linewidth=1.0)
        ax_hist.set_title(f"{nome} (n={fmt_milhar(len(valores_min))})")
        ax_hist.set_xlim(xlim)
        ax_hist.set_ylabel("Densidade" if col == 0 else "")

        sns.boxplot(x=valores_min, color=cor, ax=ax_box, fliersize=2, linewidth=1)
        ax_box.set_xlim(xlim)
        ax_box.set_xlabel(f"{titulo_var} (min)")
        ax_box.set_yticks([])

    fig.suptitle(
        f"GOL x Azul — Forma da Distribuição de {titulo_var} "
        f"(densidade, corte fixo ±{CORTE_MIN:.0f}min)",
        fontweight="bold",
    )
    fig.savefig(FIG_DIR / filename, dpi=150, bbox_inches="tight")
    plt.close(fig)


def v02_folga_distribuicao_forma(sub_g: pd.DataFrame, sub_a: pd.DataFrame) -> None:
    _distribuicao_forma(sub_g, sub_a, "folga_horas", "Folga", "v02_folga_distribuicao_forma.png")


def v03_atraso_partida_distribuicao_forma(sub_g: pd.DataFrame, sub_a: pd.DataFrame) -> None:
    _distribuicao_forma(sub_g, sub_a, "atraso_partida_horas", "Atraso de Partida",
                         "v03_atraso_partida_distribuicao_forma.png")


def v04_atraso_chegada_distribuicao_forma(sub_g: pd.DataFrame, sub_a: pd.DataFrame) -> None:
    _distribuicao_forma(sub_g, sub_a, "atraso_chegada_horas", "Atraso de Chegada",
                         "v04_atraso_chegada_distribuicao_forma.png")


def _violin_por_modelo(sub_g: pd.DataFrame, sub_a: pd.DataFrame, coluna: str,
                        titulo_var: str, filename: str, min_etapas: int = 1000) -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6.5), sharey=True)
    for ax, sub, nome in ((ax1, sub_g, "GOL"), (ax2, sub_a, "Azul")):
        s = sub.copy()
        s["_valor_min"] = s[coluna] * 60
        contagem = s["sg_equipamento_icao"].value_counts()
        modelos = contagem[contagem >= min_etapas].index.tolist()
        s = s[s["sg_equipamento_icao"].isin(modelos)]
        ordem = s.groupby("sg_equipamento_icao")["_valor_min"].median().sort_values(ascending=False).index.tolist()
        sns.violinplot(data=s, x="sg_equipamento_icao", y="_valor_min", order=ordem,
                        hue="sg_equipamento_icao", hue_order=ordem,
                        palette=dg.PALETA_CATEGORICA[:len(ordem)], legend=False, cut=0, ax=ax)
        ax.axhline(0, color="#333333", linestyle=":", linewidth=1.0)
        ax.set_title(f"{nome} (n={fmt_milhar(len(s))})")
        ax.set_xlabel("Modelo")
        ax.tick_params(axis="x", rotation=30)
    ax1.set_ylabel(f"{titulo_var} (min)")
    ax2.set_ylabel("")
    ax1.set_ylim(-CORTE_MIN, CORTE_MIN)
    fig.suptitle(
        f"GOL x Azul — {titulo_var} por Modelo (corte fixo ±{CORTE_MIN:.0f}min, eixo Y compartilhado)",
        fontweight="bold",
    )
    fig.tight_layout()
    fig.savefig(FIG_DIR / filename, dpi=150)
    plt.close(fig)


def v05_folga_violin_por_modelo(sub_g: pd.DataFrame, sub_a: pd.DataFrame) -> None:
    _violin_por_modelo(sub_g, sub_a, "folga_horas", "Folga", "v05_folga_violin_por_modelo.png")


def v06_atraso_partida_violin_por_modelo(sub_g: pd.DataFrame, sub_a: pd.DataFrame) -> None:
    _violin_por_modelo(sub_g, sub_a, "atraso_partida_horas", "Atraso de Partida",
                        "v06_atraso_partida_violin_por_modelo.png")


def v07_atraso_chegada_violin_por_modelo(sub_g: pd.DataFrame, sub_a: pd.DataFrame) -> None:
    _violin_por_modelo(sub_g, sub_a, "atraso_chegada_horas", "Atraso de Chegada",
                        "v07_atraso_chegada_violin_por_modelo.png")


def v08_folga_por_hub(sub_g: pd.DataFrame, sub_a: pd.DataFrame, max_bases: int = 8) -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
    for ax, sub, selecionar_hub, nome in (
        (ax1, sub_g, dg.selecionar_hub, "GOL"), (ax2, sub_a, da.selecionar_hub, "Azul"),
    ):
        s = sub.copy()
        s["_valor_min"] = s["folga_horas"] * 60
        hub = selecionar_hub(s["sg_iata_origem"].value_counts())
        bases = hub.index.tolist()[:max_bases]
        s = s[s["sg_iata_origem"].isin(bases)]
        ordem = s.groupby("sg_iata_origem")["_valor_min"].median().sort_values(ascending=False).index.tolist()
        sns.boxplot(data=s, x="sg_iata_origem", y="_valor_min", order=ordem,
                    hue="sg_iata_origem", hue_order=ordem, palette=dg.PALETA_CATEGORICA[:len(ordem)],
                    legend=False, fliersize=2, linewidth=1, ax=ax)
        ax.axhline(0, color="#333333", linestyle=":", linewidth=1.0)
        ax.set_title(nome)
        ax.set_xlabel("Base de origem (top HUB, 80% acumulado)")
    ax1.set_ylabel("Folga (min)")
    ax2.set_ylabel("")
    ax1.set_ylim(-CORTE_MIN, CORTE_MIN)
    fig.suptitle(
        f"GOL x Azul — Folga por Base HUB de Origem (corte fixo ±{CORTE_MIN:.0f}min, eixo Y compartilhado)",
        fontweight="bold",
    )
    fig.tight_layout()
    fig.savefig(FIG_DIR / "v08_folga_por_hub.png", dpi=150)
    plt.close(fig)


def v09_vies_match_mensal(df_g: pd.DataFrame, df_a: pd.DataFrame) -> None:
    """Nao truncado (fl_match_vra nao depende de folga/atraso) -- usa a
    base completa carregada por load_data(), mesma janela nas duas."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), sharey=True)
    for ax, df, cor, nome in ((ax1, df_g, GOL_ORANGE, "GOL"), (ax2, df_a, AZUL_BLUE, "Azul")):
        pct_geral = 100 * (df["fl_match_vra"] == 0).mean()
        mensal = (
            df.set_index("dt_partida_real")["fl_match_vra"]
            .resample("MS").apply(lambda s: 100 * (s == 0).mean())
        )
        ax.plot(mensal.index, mensal.values, color=cor, linewidth=2, marker="o", markersize=3)
        ax.axhline(pct_geral, color=NEUTRAL_GRAY, linestyle="--", linewidth=1.2)
        ax.set_title(f"{nome} (média geral = {pct_geral:.2f}%)")
        ax.set_xlabel("Mês")
    ax1.set_ylabel("% de etapas sem match VRA")
    fig.suptitle("GOL x Azul — Viés do Match VRA por Mês (eixo Y compartilhado)", fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "v09_vies_match_mensal.png", dpi=150)
    plt.close(fig)


def v10_atraso_recuperado_em_voo(df_g: pd.DataFrame, df_a: pd.DataFrame) -> None:
    diff_g = _preparar_diff(df_g)
    diff_a = _preparar_diff(df_a)
    xlim = (-CORTE_MIN, CORTE_MIN)

    fig, axes = plt.subplots(2, 2, figsize=(13, 7), sharex="col",
                              gridspec_kw={"height_ratios": [3, 1], "hspace": 0.08, "wspace": 0.15})
    axes[0, 1].sharey(axes[0, 0])
    for col, (diff, cor, nome) in enumerate(((diff_g, GOL_ORANGE, "GOL"), (diff_a, AZUL_BLUE, "Azul"))):
        ax_hist, ax_box = axes[0, col], axes[1, col]
        valores_min = (diff * 60).round()
        sns.histplot(valores_min, binwidth=1, binrange=(xlim[0] - 0.5, xlim[1] + 0.5), color=cor, stat="density",
                     ax=ax_hist, edgecolor="white", linewidth=0.3, alpha=0.85)
        sns.kdeplot(valores_min, color=NEUTRAL_GRAY, linewidth=2, ax=ax_hist, clip=xlim)
        ax_hist.axvline(0, color="#333333", linestyle=":", linewidth=1.0)
        ax_hist.axvline(valores_min.mean(), color="#2a78d6", linestyle="--", linewidth=1.2)
        ax_hist.set_title(
            f"{nome} (média={valores_min.mean():.1f}min, mediana={valores_min.median():.1f}min, "
            f"n={fmt_milhar(len(valores_min))})",
            fontsize=9.5,
        )
        ax_hist.set_xlim(xlim)
        ax_hist.set_ylabel("Densidade" if col == 0 else "")

        sns.boxplot(x=valores_min, color=cor, ax=ax_box, fliersize=2, linewidth=1)
        ax_box.set_xlim(xlim)
        ax_box.set_xlabel("Δ atraso em voo (min)")
        ax_box.set_yticks([])

    fig.suptitle(
        f"GOL x Azul — Δ Atraso em Voo: Atraso Chegada − Atraso Partida (corte fixo ±{CORTE_MIN:.0f}min)",
        fontweight="bold",
    )
    fig.savefig(FIG_DIR / "v10_atraso_recuperado_em_voo.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def v11_lag_plot_folga(diario_g: pd.Series, diario_a: pd.Series) -> None:
    series = {"GOL": (diario_g, GOL_ORANGE), "Azul": (diario_a, AZUL_BLUE)}
    limites = []
    for diario, _ in series.values():
        limites += [diario.min(), diario.max()]
    lims = (min(limites), max(limites))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5.5), sharex=True, sharey=True)
    for ax, nome in ((ax1, "GOL"), (ax2, "Azul")):
        diario, cor = series[nome]
        anterior = diario.iloc[:-1].to_numpy()
        atual = diario.iloc[1:].to_numpy()
        r = float(np.corrcoef(anterior, atual)[0, 1])
        ax.scatter(anterior, atual, color=cor, s=14, alpha=0.5, edgecolor="none")
        ax.plot(lims, lims, color=NEUTRAL_GRAY, linestyle="--", linewidth=1.2)
        ax.set_title(f"{nome} (r = {r:.3f})")
        ax.set_xlabel("Folga média em t-1 (min)")
    ax1.set_xlim(lims)
    ax1.set_ylim(lims)
    ax1.set_ylabel("Folga média em t (min)")
    fig.suptitle("GOL x Azul — Lag Plot (lag 1 dia): Folga Média Diária (eixos compartilhados)", fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "v11_lag_plot_folga.png", dpi=150)
    plt.close(fig)


def main() -> None:
    df_g = dg.load_data()
    df_a = da.load_data()
    print(f"GOL: {fmt_milhar(len(df_g))} etapas | Azul: {fmt_milhar(len(df_a))} etapas")

    folga_g = truncar_cerca(df_g, "folga_horas")
    folga_a = truncar_cerca(df_a, "folga_horas")
    atraso_p_g = truncar_cerca(df_g, "atraso_partida_horas")
    atraso_p_a = truncar_cerca(df_a, "atraso_partida_horas")
    atraso_c_g = truncar_cerca(df_g, "atraso_chegada_horas")
    atraso_c_a = truncar_cerca(df_a, "atraso_chegada_horas")
    print(f"corte fixo ±{CORTE_MIN:.0f}min | folga: GOL {fmt_milhar(len(folga_g))}, Azul {fmt_milhar(len(folga_a))} | "
          f"atraso partida: GOL {fmt_milhar(len(atraso_p_g))}, Azul {fmt_milhar(len(atraso_p_a))} | "
          f"atraso chegada: GOL {fmt_milhar(len(atraso_c_g))}, Azul {fmt_milhar(len(atraso_c_a))}")

    diario_folga_g, diario_folga_a = v01_folga_run_sequence_diaria(folga_g, folga_a)
    v02_folga_distribuicao_forma(folga_g, folga_a)
    v03_atraso_partida_distribuicao_forma(atraso_p_g, atraso_p_a)
    v04_atraso_chegada_distribuicao_forma(atraso_c_g, atraso_c_a)
    v05_folga_violin_por_modelo(folga_g, folga_a)
    v06_atraso_partida_violin_por_modelo(atraso_p_g, atraso_p_a)
    v07_atraso_chegada_violin_por_modelo(atraso_c_g, atraso_c_a)
    v08_folga_por_hub(folga_g, folga_a)
    v09_vies_match_mensal(df_g, df_a)
    v10_atraso_recuperado_em_voo(df_g, df_a)
    v11_lag_plot_folga(diario_folga_g, diario_folga_a)

    print(f"Figuras salvas em {FIG_DIR}")


if __name__ == "__main__":
    main()
