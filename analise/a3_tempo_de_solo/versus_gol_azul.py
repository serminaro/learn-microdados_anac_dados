"""GOL x Azul lado a lado -- tempo de solo, mesmo grafico, dois paineis,
mesma escala sempre que a comparacao pedir isso.

Espelho de analise/a4_etapa_media/versus_gol_azul.py: nao reimplementa a
query, importa analise_tempo_solo_gol/azul.py e
distribuicao_tempo_solo_gol/azul.py como modulos e reusa load_data()/
selecionar_hub()/calcular_corte_outlier() de cada um.

"Mesmo olhar do problema" traduzido, grafico a grafico, do mesmo jeito
que no espelho de a4:
  (a) mesmo eixo Y ou X compartilhado -- quando a pergunta e' "quem e' maior".
  (b) mesma escala de cor entre os dois hexbins/heatmaps -- quando a
      pergunta e' "onde a densidade e' mais forte".
  (c) densidade (nao contagem bruta) quando o volume total de etapas das
      duas empresas e' muito diferente -- senao GOL pareceria sempre
      "menor" so por volume (o numero exato de linhas pos-truncamento
      varia com CORTE_HORAS, ver print() em main() para o valor atual).

Corte de truncagem: CORTE_HORAS = 3h fixo para as duas empresas, aplicado
UMA VEZ em main() logo apos carregar os dados -- pedido do autor,
2026-09-02, apos ver que 72h deixava o v05 (violin por modelo) achatado
e ilegivel. Diferente da rodada anterior (72h so' em v04/v05/v08), agora
TODOS os 12 graficos usam a mesma base ja truncada, inclusive os que
antes usavam a populacao inteira (v01, v03, v09, v10, v11) -- isso muda
o que esses graficos representam: passam a excluir pernoite e fim de
semana da conta inteira, nao so' da visualizacao. Registrado aqui para
nao ficar implicito.

Roda com: conda run -n gov-sermi-perf python analise/a3_tempo_de_solo/versus_gol_azul.py
"""

from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import analise_tempo_solo_gol as ag
import analise_tempo_solo_azul as aa
import distribuicao_tempo_solo_gol as dg
import distribuicao_tempo_solo_azul as da

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from iata_bases import aplicar_iata  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
FIG_DIR = REPO_ROOT / "analise" / "a3_tempo_de_solo" / "a3_figuras_versus"
FIG_DIR.mkdir(parents=True, exist_ok=True)

GOL_ORANGE = "#FF6900"
AZUL_BLUE = "#0039A6"
NEUTRAL_GRAY = "#4d4d4d"

# Corte unico para as duas empresas E para todos os 12 graficos (pedido
# do autor, 2026-09-02) -- aplicado uma vez em main(), nao por grafico.
CORTE_HORAS = 3.0

sns.set_theme(style="whitegrid")
plt.rcParams.update({
    "figure.facecolor": "#ffffff",
    "axes.facecolor": "#ffffff",
    "axes.titleweight": "bold",
    "font.size": 10,
})


def fmt_milhar(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def v01_tempo_solo_medio_mensal(df_g, df_a) -> None:
    mensal_g = df_g.set_index("dt_partida_real")["tempo_solo_horas"].resample("MS").mean()
    mensal_a = df_a.set_index("dt_partida_real")["tempo_solo_horas"].resample("MS").mean()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5), sharey=True)
    for ax, mensal, cor, nome in ((ax1, mensal_g, GOL_ORANGE, "GOL"), (ax2, mensal_a, AZUL_BLUE, "Azul")):
        ax.plot(mensal.index, mensal.values, color=cor, linewidth=2, marker="o", markersize=3)
        ax.axhline(mensal.mean(), color=NEUTRAL_GRAY, linestyle="--", linewidth=1.2)
        ax.set_title(f"{nome} (média geral = {mensal.mean():.2f}h)")
        ax.set_xlabel("Mês")
    ax1.set_ylabel("Tempo de solo (h, média)")
    fig.suptitle("GOL x Azul — Tempo de Solo Médio por Mês (2021-2026, eixo Y compartilhado)", fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "v01_tempo_solo_medio_mensal.png", dpi=150)
    plt.close(fig)


def v02_tempo_solo_por_frota_natureza(df_full_g, df_full_a) -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), sharey=True)
    for ax, df, cor_dom, cor_int, nome in (
        (ax1, df_full_g, GOL_ORANGE, "#B34700", "GOL"),
        (ax2, df_full_a, AZUL_BLUE, "#00204D", "Azul"),
    ):
        agg = (
            df.groupby(["sg_equipamento_icao", "ds_natureza_tipo_linha"])["tempo_solo_horas"]
            .agg(["mean", "count"]).reset_index()
        )
        agg = agg[agg["count"] >= 30]
        ordem = agg.groupby("sg_equipamento_icao")["mean"].mean().sort_values(ascending=False).index
        pivot = agg.pivot(index="sg_equipamento_icao", columns="ds_natureza_tipo_linha", values="mean").reindex(ordem)

        x = range(len(pivot))
        largura = 0.38
        cores = {"DOMÉSTICA": cor_dom, "INTERNACIONAL": cor_int}
        for i, coluna in enumerate(pivot.columns):
            deslocamento = (i - (len(pivot.columns) - 1) / 2) * largura
            barras = ax.bar([xi + deslocamento for xi in x], pivot[coluna], width=largura,
                             label=coluna.title(), color=cores.get(coluna, cor_dom))
            ax.bar_label(barras, fmt="%.2f", fontweight="bold", fontsize=8, padding=2)
        ax.set_xticks(list(x))
        ax.set_xticklabels(pivot.index, rotation=0)
        ax.set_title(nome)
        ax.set_xlabel("Modelo")
        ax.legend(frameon=True, edgecolor="#333333")
    ax1.set_ylabel("Tempo de solo (h, média)")
    fig.suptitle("GOL x Azul — Tempo de Solo Médio por Modelo e Natureza (eixo Y compartilhado)", fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "v02_tempo_solo_por_frota_natureza.png", dpi=150)
    plt.close(fig)


def v03_top_bases_origem(df_g, df_a) -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6.5), sharex=True)
    aggs = {}
    for nome, df, selecionar_hub in (("GOL", df_g, dg.selecionar_hub), ("Azul", df_a, da.selecionar_hub)):
        agg_full = df.groupby("sg_iata_origem")["tempo_solo_horas"].agg(n_etapas="count", solo_medio="mean")
        hub = selecionar_hub(agg_full["n_etapas"])
        aggs[nome] = agg_full.loc[hub.index].sort_values("n_etapas")

    vmin = min(agg["solo_medio"].min() for agg in aggs.values())
    vmax = max(agg["solo_medio"].max() for agg in aggs.values())
    norm = plt.Normalize(vmin, vmax)
    cmap = plt.get_cmap("YlOrBr")

    for ax, nome in ((ax1, "GOL"), (ax2, "Azul")):
        agg = aggs[nome]
        cores = cmap(norm(agg["solo_medio"]))
        barras = ax.barh(agg.index, agg["n_etapas"], color=cores, edgecolor="#333333", linewidth=0.5)
        ax.bar_label(barras, fmt="%.0f", fontweight="bold", fontsize=8, padding=3)
        ax.margins(x=0.12)
        ax.set_title(nome)
        ax.set_xlabel("Nº de etapas")

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=[ax1, ax2], shrink=0.85)
    cbar.set_label("Tempo de solo médio (h) — escala compartilhada")
    fig.suptitle("GOL x Azul — Bases HUB de Origem (80% acumulado, eixo X e cor compartilhados)", fontweight="bold")
    fig.savefig(FIG_DIR / "v03_top_bases_origem.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def v04_distribuicao_forma(df_g, df_a) -> None:
    """Densidade (nao contagem bruta) -- Azul tem mais etapas que GOL
    mesmo depois do truncamento; comparar contagem faria GOL parecer
    sempre 'menor' so por volume, nao por formato. df ja chega truncado
    em <= CORTE_HORAS (main())."""
    xlim = (0, CORTE_HORAS)

    fig, axes = plt.subplots(2, 2, figsize=(13, 7), sharex="col",
                              gridspec_kw={"height_ratios": [3, 1], "hspace": 0.08, "wspace": 0.15})
    axes[0, 1].sharey(axes[0, 0])
    for col, (df, cor, nome) in enumerate(((df_g, GOL_ORANGE, "GOL"), (df_a, AZUL_BLUE, "Azul"))):
        ax_hist, ax_box = axes[0, col], axes[1, col]
        solo = df["tempo_solo_horas"]
        sns.histplot(solo, bins=80, binrange=xlim, color=cor, stat="density", ax=ax_hist,
                     edgecolor="white", linewidth=0.3, alpha=0.85)
        sns.kdeplot(solo, color=NEUTRAL_GRAY, linewidth=2, ax=ax_hist, clip=xlim)
        ax_hist.set_title(f"{nome} (n={fmt_milhar(len(solo))})")
        ax_hist.set_xlim(xlim)
        ax_hist.set_ylabel("Densidade" if col == 0 else "")

        sns.boxplot(x=solo, color=cor, ax=ax_box, fliersize=2, linewidth=1)
        ax_box.set_xlim(xlim)
        ax_box.set_xlabel("Tempo de solo (h)")
        ax_box.set_yticks([])

    fig.suptitle(f"GOL x Azul — Forma da Distribuição de Tempo de Solo (densidade, truncado em ≤{CORTE_HORAS:.0f}h)",
                 fontweight="bold")
    fig.savefig(FIG_DIR / "v04_distribuicao_forma.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def v05_violin_por_modelo(df_g, df_a) -> None:
    """df ja chega truncado em <= CORTE_HORAS (main()) -- sem filtro
    interno de tempo_solo_horas."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6.5))
    for ax, df, nome in ((ax1, df_g, "GOL"), (ax2, df_a, "Azul")):
        sub = df[df["sg_equipamento_icao"].isin(
            df["sg_equipamento_icao"].value_counts()[lambda s: s >= 1000].index
        )]
        ordem = sub.groupby("sg_equipamento_icao")["tempo_solo_horas"].median().sort_values(ascending=False).index.tolist()
        sns.violinplot(data=sub, x="sg_equipamento_icao", y="tempo_solo_horas", order=ordem,
                        hue="sg_equipamento_icao", hue_order=ordem,
                        palette=dg.PALETA_CATEGORICA[:len(ordem)], legend=False, cut=0, ax=ax)
        ax.set_title(f"{nome} (n={fmt_milhar(len(sub))})")
        ax.set_xlabel("Modelo")
        ax.tick_params(axis="x", rotation=30)
    ax1.set_ylabel("Tempo de solo (h)")
    ax2.set_ylabel("")
    ax1.set_ylim(0, CORTE_HORAS)
    ax2.set_ylim(0, CORTE_HORAS)
    fig.suptitle(f"GOL x Azul — Distribuição de Tempo de Solo por Modelo (truncado em ≤{CORTE_HORAS:.0f}h, eixo Y compartilhado)",
                 fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "v05_violin_por_modelo.png", dpi=150)
    plt.close(fig)


def _boxplot_por_categoria(ax, df, coluna, selecionar_hub, max_n=6):
    hub = selecionar_hub(df[coluna].value_counts())
    cats = hub.index.tolist()[:max_n]
    sub = df[df[coluna].isin(cats)]
    ordem = sub.groupby(coluna)["tempo_solo_horas"].median().sort_values(ascending=False).index.tolist()
    sns.boxplot(data=sub, x=coluna, y="tempo_solo_horas", order=ordem,
                hue=coluna, hue_order=ordem, palette=dg.PALETA_CATEGORICA[:len(ordem)],
                legend=False, fliersize=2, linewidth=1, ax=ax)
    return ordem


def v06_distribuicao_por_hub(df_g, df_a) -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
    _boxplot_por_categoria(ax1, df_g, "sg_iata_origem", dg.selecionar_hub)
    _boxplot_por_categoria(ax2, df_a, "sg_iata_origem", da.selecionar_hub)
    ax1.set_title("GOL")
    ax2.set_title("Azul")
    for ax in (ax1, ax2):
        ax.set_xlabel("Base de origem (top 6 HUB, 80% acumulado)")
    ax1.set_ylabel("Tempo de solo (h)")
    ax2.set_ylabel("")
    fig.suptitle("GOL x Azul — Distribuição de Tempo de Solo por Base HUB (eixo Y compartilhado)", fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "v06_distribuicao_por_hub.png", dpi=150)
    plt.close(fig)


def v07_distribuicao_por_destino(df_g, df_a) -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
    _boxplot_por_categoria(ax1, df_g, "sg_iata_destino", dg.selecionar_hub)
    _boxplot_por_categoria(ax2, df_a, "sg_iata_destino", da.selecionar_hub)
    ax1.set_title("GOL")
    ax2.set_title("Azul")
    for ax in (ax1, ax2):
        ax.set_xlabel("Destino (top 6 HUB, 80% acumulado)")
    ax1.set_ylabel("Tempo de solo (h)")
    ax2.set_ylabel("")
    fig.suptitle("GOL x Azul — Distribuição de Tempo de Solo por Destino (eixo Y compartilhado)", fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "v07_distribuicao_por_destino.png", dpi=150)
    plt.close(fig)


def v08_hexbin_horario_partida(df_g, df_a) -> None:
    """df ja chega truncado em <= CORTE_HORAS (main())."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6.5), sharex=True, sharey=True)
    hbs = []
    for ax, df, nome in ((ax1, df_g, "GOL"), (ax2, df_a, "Azul")):
        hb = ax.hexbin(df["tempo_solo_horas"], df["hora_partida_decimal"],
                        gridsize=45, cmap="YlOrBr", mincnt=1, extent=(0, CORTE_HORAS, 0, 24))
        hbs.append(hb)
        ax.set_title(f"{nome} (n={fmt_milhar(len(df))})")
        ax.set_xlabel("Tempo de solo (h)")
    ax1.set_yticks(range(0, 25, 3))
    ax1.set_yticklabels([f"{h:02d}:00" for h in range(0, 25, 3)])
    ax1.set_ylabel("Horário de partida")

    vmax_global = max(hb.get_array().max() for hb in hbs)
    for hb in hbs:
        hb.set_clim(0, vmax_global)
    cbar = fig.colorbar(hbs[0], ax=[ax1, ax2], shrink=0.85)
    cbar.set_label("Nº de etapas por célula (escala compartilhada)")
    fig.suptitle(f"GOL x Azul — Tempo de Solo x Horário de Partida (truncado em ≤{CORTE_HORAS:.0f}h, eixos e cor compartilhados)",
                 fontweight="bold")
    fig.savefig(FIG_DIR / "v08_hexbin_horario_partida.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def v09_run_sequence(df_g, df_a) -> None:
    diario_g = df_g.set_index("dt_partida_real")["tempo_solo_horas"].resample("D").mean().dropna()
    diario_a = df_a.set_index("dt_partida_real")["tempo_solo_horas"].resample("D").mean().dropna()

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7.5), sharex=True, sharey=True)
    for ax, diario, cor, nome in ((ax1, diario_g, GOL_ORANGE, "GOL"), (ax2, diario_a, AZUL_BLUE, "Azul")):
        ax.plot(diario.index, diario.values, color=cor, linewidth=0.8, alpha=0.85)
        ax.axhline(diario.mean(), color=NEUTRAL_GRAY, linestyle="--", linewidth=1.2)
        ax.set_title(f"{nome} (média geral = {diario.mean():.2f}h)")
        ax.set_ylabel("Tempo de solo médio do dia (h)")
    ax2.set_xlabel("Data (ordem cronológica)")
    fig.suptitle("GOL x Azul — Run Sequence Plot: Tempo de Solo Médio Diário (eixo Y compartilhado)", fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "v09_run_sequence.png", dpi=150)
    plt.close(fig)
    return diario_g, diario_a


def v10_mix_frota_temporal(df_g, df_a, min_etapas: int = 1000) -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5.5), sharey=True)
    for ax, df, nome in ((ax1, df_g, "GOL"), (ax2, df_a, "Azul")):
        contagem = df["sg_equipamento_icao"].value_counts()
        modelos = contagem[contagem >= min_etapas].index.tolist()
        sub = df[df["sg_equipamento_icao"].isin(modelos)]
        mensal_contagem = (
            sub.set_index("dt_partida_real").groupby("sg_equipamento_icao")["tempo_solo_horas"]
            .resample("MS").count().unstack(0).fillna(0)
        )
        ordem = mensal_contagem.sum().sort_values(ascending=False).index.tolist()
        share = mensal_contagem[ordem].div(mensal_contagem[ordem].sum(axis=1), axis=0) * 100
        ax.stackplot(share.index, [share[m] for m in ordem], labels=ordem,
                     colors=dg.PALETA_CATEGORICA[:len(ordem)], alpha=0.9)
        ax.set_ylim(0, 100)
        ax.set_title(nome)
        ax.set_xlabel("Mês")
        ax.legend(title="Modelo", loc="upper left", frameon=True, edgecolor="#333333", fontsize=8)
    ax1.set_ylabel("% de etapas do mês")
    fig.suptitle("GOL x Azul — Composição da Frota por Mês (eixo Y compartilhado, 0-100%)", fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "v10_mix_frota_temporal.png", dpi=150)
    plt.close(fig)


def v11_correlacao(df_g, df_a) -> None:
    """Escala de cor ja e' compartilhada por construcao (-1 a 1 fixo em
    qualquer matriz de Pearson) -- nao precisa de ajuste extra."""
    cols = {"tempo_solo_horas": "Tempo de solo (h)", "nr_horas_voadas": "Etapa média (h)",
            "km_distancia": "Distância (km)"}
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5))
    for ax, df, nome in ((ax1, df_g, "GOL"), (ax2, df_a, "Azul")):
        corr = df[list(cols)].rename(columns=cols).corr(method="pearson")
        sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", vmin=-1, vmax=1,
                    square=True, cbar_kws={"label": "Correlação de Pearson"}, ax=ax)
        ax.set_title(nome)
    fig.suptitle("GOL x Azul — Correlação entre Tempo de Solo, Etapa Média e Distância", fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "v11_correlacao.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def v12_lag_plot(diario_g, diario_a) -> None:
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
        ax.set_xlabel("Tempo de solo médio em t-1 (h)")
    ax1.set_xlim(lims)
    ax1.set_ylim(lims)
    ax1.set_ylabel("Tempo de solo médio em t (h)")
    fig.suptitle("GOL x Azul — Lag Plot (lag 1 dia), eixos compartilhados", fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "v12_lag_plot.png", dpi=150)
    plt.close(fig)


def main() -> None:
    df_g = dg.load_data()
    df_a = da.load_data()
    n_g_antes, n_a_antes = len(df_g), len(df_a)

    df_full_g = ag.load_data(*ag.WINDOW_FULL)
    df_full_a = aa.load_data(*aa.WINDOW_FULL)

    # Truncagem unica, aqui, antes de qualquer grafico -- pedido do
    # autor, 2026-09-02: CORTE_HORAS (3h) vale para os 12 graficos,
    # nao so' os que antes tinham corte individual (v04/v05/v08).
    df_g = df_g[df_g["tempo_solo_horas"] <= CORTE_HORAS].reset_index(drop=True)
    df_a = df_a[df_a["tempo_solo_horas"] <= CORTE_HORAS].reset_index(drop=True)
    df_full_g = df_full_g[df_full_g["tempo_solo_horas"] <= CORTE_HORAS].reset_index(drop=True)
    df_full_a = df_full_a[df_full_a["tempo_solo_horas"] <= CORTE_HORAS].reset_index(drop=True)

    print(f"GOL: {fmt_milhar(len(df_g))} de {fmt_milhar(n_g_antes)} etapas (truncado ≤{CORTE_HORAS:.0f}h) | "
          f"Azul: {fmt_milhar(len(df_a))} de {fmt_milhar(n_a_antes)} etapas")

    v01_tempo_solo_medio_mensal(df_g, df_a)
    v02_tempo_solo_por_frota_natureza(df_full_g, df_full_a)
    v03_top_bases_origem(df_g, df_a)
    v04_distribuicao_forma(df_g, df_a)
    v05_violin_por_modelo(df_g, df_a)
    v06_distribuicao_por_hub(df_g, df_a)
    v07_distribuicao_por_destino(df_g, df_a)
    v08_hexbin_horario_partida(df_g, df_a)
    diario_g, diario_a = v09_run_sequence(df_g, df_a)
    v10_mix_frota_temporal(df_g, df_a)
    v11_correlacao(df_g, df_a)
    v12_lag_plot(diario_g, diario_a)

    print(f"Figuras salvas em {FIG_DIR}")


if __name__ == "__main__":
    main()
