"""GOL x Azul lado a lado -- mesmo grafico, dois paineis, mesma escala
sempre que a comparacao pedir isso.

Nao reimplementa a query: importa analise_etapa_media_gol/azul.py e
distribuicao_etapa_media_gol/azul.py como modulos e reusa load_data()/
selecionar_hub()/calcular_corte_outlier() de cada um -- fonte unica de
verdade por empresa, este script so desenha o par lado a lado.

"Mesmo olhar do problema" (pedido do autor, 2026-09-02) foi traduzido,
grafico a grafico, como uma destas tres formas concretas de ajuste:
  (a) mesmo eixo Y ou X compartilhado entre os dois paineis (sharex/sharey
      do matplotlib) -- quando a pergunta e' "quem e' maior".
  (b) mesma escala de cor entre os dois hexbins/heatmaps (vmin/vmax fixos)
      -- quando a pergunta e' "onde a densidade e' mais forte".
  (c) normalizar para densidade (nao contagem bruta) quando o volume
      total de etapas das duas empresas e' muito diferente (Azul tem
      ~1,54M, GOL ~1,16M) -- senao GOL pareceria sempre "menor" so por
      ter menos etapas, nao por ter formato diferente.

Selecionei 12 graficos (de mais de 25 gerados nos dois scripts fonte) na
primeira rodada, um por "angulo" de analise ja usado nesta linha de
trabalho -- v01 a v12. Auditoria posterior (pedido do autor, 2026-09-02)
encontrou 9 tipos que faltavam (alguns avisados na hora, outros nao --
omissao real, corrigida aqui). Esses 9 entram com prefixo "novo_" nos
arquivos, para nao misturar com a numeracao v01-v12 ja em uso:
  novo_01: dispersao etapa media x tempo de solo por matricula (dist_03)
  novo_02: dispersao etapa media x distancia por modelo (dist_04)
  novo_03: hexbin por hub individual, top 5 por empresa (dist_10 --
           escopo reduzido de 10 para 5 por empresa, decisao explicita)
  novo_04: grade hexbin top 6, GOL empilhado sobre Azul (dist_11/dist_12
           -- um layout so, nao os dois, decisao explicita)
  novo_05: decomposicao real x contrafactual, mix de frota (dist_16)
  novo_06: duracao media mensal por modelo, valor absoluto (nao e' o
           mesmo que v10, que e' % de participacao)
  novo_07: duracao media mensal por base HUB (com legenda em caixa,
           licao ja aprendida em a3_tempo_de_solo -- nao rotulo direto
           na ponta da linha)
  novo_08: top bases HUB por numero de chegadas
  novo_09: violin unico com media/mediana/Q1/Q3 (dist_08)

Roda com: conda run -n gov-sermi-perf python analise/a4_etapa_media/versus_gol_azul.py
"""

from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import analise_etapa_media_gol as ag
import analise_etapa_media_azul as aa
import distribuicao_etapa_media_gol as dg
import distribuicao_etapa_media_azul as da

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from iata_bases import aplicar_iata  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
FIG_DIR = REPO_ROOT / "analise" / "a4_etapa_media" / "a4_figuras_versus"
FIG_DIR.mkdir(parents=True, exist_ok=True)

GOL_ORANGE = "#FF6900"
AZUL_BLUE = "#0039A6"
NEUTRAL_GRAY = "#4d4d4d"

sns.set_theme(style="whitegrid")
plt.rcParams.update({
    "figure.facecolor": "#ffffff",
    "axes.facecolor": "#ffffff",
    "axes.titleweight": "bold",
    "font.size": 10,
})


def fmt_milhar(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def v01_duracao_media_mensal(df_g, df_a) -> None:
    mensal_g = df_g.set_index("dt_partida_real")["nr_horas_voadas"].resample("MS").mean()
    mensal_a = df_a.set_index("dt_partida_real")["nr_horas_voadas"].resample("MS").mean()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5), sharey=True)
    for ax, mensal, cor, nome in ((ax1, mensal_g, GOL_ORANGE, "GOL"), (ax2, mensal_a, AZUL_BLUE, "Azul")):
        ax.plot(mensal.index, mensal.values, color=cor, linewidth=2, marker="o", markersize=3)
        ax.axhline(mensal.mean(), color=NEUTRAL_GRAY, linestyle="--", linewidth=1.2)
        ax.set_title(f"{nome} (média geral = {mensal.mean():.2f}h)")
        ax.set_xlabel("Mês")
    ax1.set_ylabel("Etapa média (h)")
    fig.suptitle("GOL x Azul — Duração Média de Etapa por Mês (2021-2026, eixo Y compartilhado)", fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "v01_duracao_media_mensal.png", dpi=150)
    plt.close(fig)


def v02_duracao_por_frota_natureza(df_full_g, df_full_a) -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), sharey=True)
    for ax, df, cor_dom, cor_int, nome in (
        (ax1, df_full_g, GOL_ORANGE, "#B34700", "GOL"),
        (ax2, df_full_a, AZUL_BLUE, "#00204D", "Azul"),
    ):
        agg = (
            df.groupby(["sg_equipamento_icao", "ds_natureza_tipo_linha"])["nr_horas_voadas"]
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
    ax1.set_ylabel("Etapa média (h)")
    fig.suptitle("GOL x Azul — Duração Média por Modelo e Natureza (eixo Y compartilhado)", fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "v02_duracao_por_frota_natureza.png", dpi=150)
    plt.close(fig)


def v03_top_bases_origem(df_g, df_a) -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6.5), sharex=True)
    aggs = {}
    for nome, df, selecionar_hub in (("GOL", df_g, dg.selecionar_hub), ("Azul", df_a, da.selecionar_hub)):
        agg_full = df.groupby("sg_iata_origem")["nr_horas_voadas"].agg(n_etapas="count", duracao_media="mean")
        hub = selecionar_hub(agg_full["n_etapas"])
        aggs[nome] = agg_full.loc[hub.index].sort_values("n_etapas")

    vmin = min(agg["duracao_media"].min() for agg in aggs.values())
    vmax = max(agg["duracao_media"].max() for agg in aggs.values())
    norm = plt.Normalize(vmin, vmax)
    cmap = plt.get_cmap("YlOrBr")

    for ax, nome in ((ax1, "GOL"), (ax2, "Azul")):
        agg = aggs[nome]
        cores = cmap(norm(agg["duracao_media"]))
        barras = ax.barh(agg.index, agg["n_etapas"], color=cores, edgecolor="#333333", linewidth=0.5)
        ax.bar_label(barras, fmt="%.0f", fontweight="bold", fontsize=8, padding=3)
        ax.margins(x=0.12)
        ax.set_title(nome)
        ax.set_xlabel("Nº de etapas")

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=[ax1, ax2], shrink=0.85)
    cbar.set_label("Duração média (h) — escala compartilhada")
    fig.suptitle("GOL x Azul — Bases HUB de Origem (80% acumulado, eixo X e cor compartilhados)", fontweight="bold")
    fig.savefig(FIG_DIR / "v03_top_bases_origem.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def v04_distribuicao_forma(df_g, df_a) -> None:
    """Densidade (nao contagem bruta) -- Azul tem ~1,54M etapas, GOL
    ~1,16M; comparar contagem faria GOL parecer sempre 'menor' so por
    volume, nao por formato."""
    p99_g, p99_a = df_g["nr_horas_voadas"].quantile(0.995), df_a["nr_horas_voadas"].quantile(0.995)
    xlim = (0, max(p99_g, p99_a))

    fig, axes = plt.subplots(2, 2, figsize=(13, 7), sharex="col",
                              gridspec_kw={"height_ratios": [3, 1], "hspace": 0.08, "wspace": 0.15})
    # sharey so na linha do histograma (densidade e' comparavel entre as
    # duas empresas); a linha do boxplot e' 1 categoria so, sharey ali
    # faz o seaborn colapsar os dois eixos (warning "identical ylims").
    axes[0, 1].sharey(axes[0, 0])
    for col, (df, cor, nome) in enumerate(((df_g, GOL_ORANGE, "GOL"), (df_a, AZUL_BLUE, "Azul"))):
        ax_hist, ax_box = axes[0, col], axes[1, col]
        horas = df["nr_horas_voadas"]
        sns.histplot(horas, bins=80, color=cor, stat="density", ax=ax_hist,
                     edgecolor="white", linewidth=0.3, alpha=0.85)
        sns.kdeplot(horas, color=NEUTRAL_GRAY, linewidth=2, ax=ax_hist)
        ax_hist.set_title(f"{nome} (n={fmt_milhar(len(horas))})")
        ax_hist.set_xlim(xlim)
        ax_hist.set_ylabel("Densidade" if col == 0 else "")

        sns.boxplot(x=horas, color=cor, ax=ax_box, fliersize=2, linewidth=1)
        ax_box.set_xlim(xlim)
        ax_box.set_xlabel("Horas voadas (etapa)")
        ax_box.set_yticks([])

    fig.suptitle("GOL x Azul — Forma da Distribuição de Etapa Média (densidade, eixo X compartilhado)",
                 fontweight="bold")
    fig.savefig(FIG_DIR / "v04_distribuicao_forma.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def v05_violin_por_modelo(df_g, df_a) -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    for ax, df, calcular_corte, nome in (
        (ax1, df_g, dg.calcular_corte_outlier, "GOL"), (ax2, df_a, da.calcular_corte_outlier, "Azul"),
    ):
        inferior, superior = calcular_corte(df["nr_horas_voadas"])
        inferior = max(inferior, 0.0)
        sub = df[df["sg_equipamento_icao"].isin(
            df["sg_equipamento_icao"].value_counts()[lambda s: s >= 1000].index
        )]
        sub = sub[sub["nr_horas_voadas"].between(inferior, superior)]
        ordem = sub.groupby("sg_equipamento_icao")["nr_horas_voadas"].median().sort_values(ascending=False).index.tolist()
        sns.violinplot(data=sub, x="sg_equipamento_icao", y="nr_horas_voadas", order=ordem,
                        hue="sg_equipamento_icao", hue_order=ordem,
                        palette=dg.PALETA_CATEGORICA[:len(ordem)], legend=False, cut=0, ax=ax)
        ax.set_title(f"{nome} (com corte de outlier, n={fmt_milhar(len(sub))})")
        ax.set_xlabel("Modelo")
        ax.tick_params(axis="x", rotation=30)
    ax1.set_ylabel("Etapa média (h)")
    ax2.set_ylabel("")
    ax1.set_ylim(0, max(ax1.get_ylim()[1], ax2.get_ylim()[1]))
    ax2.set_ylim(ax1.get_ylim())
    fig.suptitle("GOL x Azul — Distribuição de Etapa Média por Modelo (eixo Y compartilhado)", fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "v05_violin_por_modelo.png", dpi=150)
    plt.close(fig)


def _boxplot_por_categoria(ax, df, coluna, selecionar_hub, cor_ignorada, max_n=6):
    hub = selecionar_hub(df[coluna].value_counts())
    cats = hub.index.tolist()[:max_n]
    sub = df[df[coluna].isin(cats)]
    ordem = sub.groupby(coluna)["nr_horas_voadas"].median().sort_values(ascending=False).index.tolist()
    sns.boxplot(data=sub, x=coluna, y="nr_horas_voadas", order=ordem,
                hue=coluna, hue_order=ordem, palette=dg.PALETA_CATEGORICA[:len(ordem)],
                legend=False, fliersize=2, linewidth=1, ax=ax)
    return ordem


def v06_distribuicao_por_hub(df_g, df_a) -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
    _boxplot_por_categoria(ax1, df_g, "sg_iata_origem", dg.selecionar_hub, GOL_ORANGE)
    _boxplot_por_categoria(ax2, df_a, "sg_iata_origem", da.selecionar_hub, AZUL_BLUE)
    ax1.set_title("GOL")
    ax2.set_title("Azul")
    for ax in (ax1, ax2):
        ax.set_xlabel("Base de origem (top 6 HUB, 80% acumulado)")
    ax1.set_ylabel("Etapa média (h)")
    ax2.set_ylabel("")
    fig.suptitle("GOL x Azul — Distribuição de Etapa Média por Base HUB (eixo Y compartilhado)", fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "v06_distribuicao_por_hub.png", dpi=150)
    plt.close(fig)


def v07_distribuicao_por_destino(df_g, df_a) -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
    _boxplot_por_categoria(ax1, df_g, "sg_iata_destino", dg.selecionar_hub, GOL_ORANGE)
    _boxplot_por_categoria(ax2, df_a, "sg_iata_destino", da.selecionar_hub, AZUL_BLUE)
    ax1.set_title("GOL")
    ax2.set_title("Azul")
    for ax in (ax1, ax2):
        ax.set_xlabel("Destino (top 6 HUB, 80% acumulado)")
    ax1.set_ylabel("Etapa média (h)")
    ax2.set_ylabel("")
    fig.suptitle("GOL x Azul — Distribuição de Etapa Média por Destino (eixo Y compartilhado)", fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "v07_distribuicao_por_destino.png", dpi=150)
    plt.close(fig)


def v08_hexbin_horario_partida(df_g, df_a) -> None:
    xmax = max(df_g["nr_horas_voadas"].max(), df_a["nr_horas_voadas"].max())
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6.5), sharex=True, sharey=True)
    hbs = []
    for ax, df, nome in ((ax1, df_g, "GOL"), (ax2, df_a, "Azul")):
        hb = ax.hexbin(df["nr_horas_voadas"], df["hora_partida_decimal"],
                        gridsize=45, cmap="YlOrBr", mincnt=1, extent=(0, xmax, 0, 24))
        hbs.append(hb)
        ax.set_title(f"{nome} (n={fmt_milhar(len(df))})")
        ax.set_xlabel("Horas voadas (etapa)")
    ax1.set_yticks(range(0, 25, 3))
    ax1.set_yticklabels([f"{h:02d}:00" for h in range(0, 25, 3)])
    ax1.set_ylabel("Horário de partida")

    vmax_global = max(hb.get_array().max() for hb in hbs)
    for hb in hbs:
        hb.set_clim(0, vmax_global)
    cbar = fig.colorbar(hbs[0], ax=[ax1, ax2], shrink=0.85)
    cbar.set_label("Nº de etapas por célula (escala compartilhada)")
    fig.suptitle("GOL x Azul — Etapa Média x Horário de Partida (eixos e cor compartilhados)", fontweight="bold")
    fig.savefig(FIG_DIR / "v08_hexbin_horario_partida.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def v09_run_sequence(df_g, df_a) -> None:
    diario_g = df_g.set_index("dt_partida_real")["nr_horas_voadas"].resample("D").mean().dropna()
    diario_a = df_a.set_index("dt_partida_real")["nr_horas_voadas"].resample("D").mean().dropna()

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7.5), sharex=True, sharey=True)
    for ax, diario, cor, nome in ((ax1, diario_g, GOL_ORANGE, "GOL"), (ax2, diario_a, AZUL_BLUE, "Azul")):
        ax.plot(diario.index, diario.values, color=cor, linewidth=0.8, alpha=0.85)
        ax.axhline(diario.mean(), color=NEUTRAL_GRAY, linestyle="--", linewidth=1.2)
        ax.set_title(f"{nome} (média geral = {diario.mean():.2f}h)")
        ax.set_ylabel("Etapa média do dia (h)")
    ax2.set_xlabel("Data (ordem cronológica)")
    fig.suptitle("GOL x Azul — Run Sequence Plot: Etapa Média Diária (eixo Y compartilhado)", fontweight="bold")
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
            sub.set_index("dt_partida_real").groupby("sg_equipamento_icao")["nr_horas_voadas"]
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
    cols = {"nr_horas_voadas": "Etapa média (h)", "km_distancia": "Distância (km)",
            "tempo_solo_horas": "Tempo de solo (h)"}
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5))
    for ax, df, nome in ((ax1, df_g, "GOL"), (ax2, df_a, "Azul")):
        corr = df[list(cols)].rename(columns=cols).corr(method="pearson")
        sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", vmin=-1, vmax=1,
                    square=True, cbar_kws={"label": "Correlação de Pearson"}, ax=ax)
        ax.set_title(nome)
    fig.suptitle("GOL x Azul — Correlação entre Etapa Média, Distância e Tempo de Solo", fontweight="bold")
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
        ax.set_xlabel("Etapa média em t-1 (h)")
    ax1.set_xlim(lims)
    ax1.set_ylim(lims)
    ax1.set_ylabel("Etapa média em t (h)")
    fig.suptitle("GOL x Azul — Lag Plot (lag 1 dia), eixos compartilhados", fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "v12_lag_plot.png", dpi=150)
    plt.close(fig)


def novo_01_dispersao_etapa_media_tempo_solo(df_g, df_a) -> None:
    """Espelho de dist_03 (nao entrou nos 12 primeiros). 1 ponto = 1
    matricula, media de etapa e de tempo de solo no periodo."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6), sharex=True, sharey=True)
    for ax, df, nome in ((ax1, df_g, "GOL"), (ax2, df_a, "Azul")):
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
        por_matricula = por_matricula[por_matricula["n_etapas"] >= 30]
        modelos = por_matricula["modelo"].value_counts().index.tolist()[:len(dg.PALETA_CATEGORICA)]
        cores = {m: c for m, c in zip(modelos, dg.PALETA_CATEGORICA)}
        por_matricula = por_matricula[por_matricula["modelo"].isin(modelos)]
        for modelo in modelos:
            sub = por_matricula[por_matricula["modelo"] == modelo]
            ax.scatter(sub["etapa_media"], sub["tempo_solo_medio"], color=cores[modelo],
                       label=modelo, s=42, alpha=0.8, edgecolor="white", linewidth=0.5)
        ax.set_title(nome)
        ax.set_xlabel("Etapa média (h)")
        ax.legend(title="Modelo", frameon=True, edgecolor="#333333", fontsize=8)
    ax1.set_ylabel("Tempo de solo médio (h)")
    ax2.set_ylabel("")
    fig.suptitle("GOL x Azul — Tempo de Solo x Etapa Média, por Aeronave (eixos compartilhados)", fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "novo_01_dispersao_etapa_media_tempo_solo.png", dpi=150)
    plt.close(fig)


def novo_02_dispersao_etapa_media_distancia(df_g, df_a, min_etapas: int = 1000,
                                             amostra: int = 30_000, seed: int = 42) -> None:
    """Espelho de dist_04. Amostra fixa so' para legibilidade."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6), sharex=True, sharey=True)
    for ax, df, nome in ((ax1, df_g, "GOL"), (ax2, df_a, "Azul")):
        contagem = df["sg_equipamento_icao"].value_counts()
        modelos = contagem[contagem >= min_etapas].index.tolist()
        sub = df[df["sg_equipamento_icao"].isin(modelos)].dropna(subset=["km_distancia"])
        if len(sub) > amostra:
            sub = sub.sample(amostra, random_state=seed)
        sns.scatterplot(data=sub, x="km_distancia", y="nr_horas_voadas",
                         hue="sg_equipamento_icao", palette=dg.PALETA_CATEGORICA[:len(modelos)],
                         s=14, alpha=0.5, edgecolor="none", ax=ax)
        ax.set_title(f"{nome} (amostra de {fmt_milhar(len(sub))})")
        ax.set_xlabel("Distância (km)")
        ax.legend(title="Modelo", frameon=True, edgecolor="#333333", fontsize=8)
    ax1.set_ylabel("Etapa média (h)")
    ax2.set_ylabel("")
    fig.suptitle("GOL x Azul — Etapa Média x Distância, por Modelo (eixos compartilhados)", fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "novo_02_dispersao_etapa_media_distancia.png", dpi=150)
    plt.close(fig)


def novo_03_hexbin_hub_top5(df_g, df_a, top_n: int = 5) -> None:
    """Espelho de dist_10, escopo reduzido: dist_10 gera 10 paineis
    individuais grandes por empresa (20 no total, inviavel lado a lado).
    Aqui, top 5 por empresa, grade 2 linhas (GOL/Azul) x 5 colunas,
    escala de cor compartilhada entre os 10 paineis -- decisao de escopo
    explicita, nao os 10 originais por empresa."""
    fig, axes = plt.subplots(2, top_n, figsize=(4.2 * top_n, 8), sharex=True, sharey=True)
    hbs = []
    for row, (df, nome) in enumerate(((df_g, "GOL"), (df_a, "Azul"))):
        top_bases = df["sg_iata_origem"].value_counts().head(top_n).index.tolist()
        for col, base in enumerate(top_bases):
            ax = axes[row, col]
            sub = df[df["sg_iata_origem"] == base]
            hb = ax.hexbin(sub["nr_horas_voadas"], sub["hora_partida_decimal"],
                            gridsize=28, cmap="YlOrBr", mincnt=1)
            hbs.append(hb)
            ax.set_title(base, fontsize=10, fontweight="bold")
            if col == 0:
                ax.set_ylabel(nome, fontsize=11, fontweight="bold")
    axes[0, 0].set_yticks(range(0, 25, 6))
    axes[0, 0].set_yticklabels([f"{h:02d}:00" for h in range(0, 25, 6)])
    vmax_global = max(hb.get_array().max() for hb in hbs)
    for hb in hbs:
        hb.set_clim(0, vmax_global)
    fig.supxlabel("Horas voadas (etapa)")
    cbar = fig.colorbar(hbs[0], ax=axes, shrink=0.7)
    cbar.set_label("Nº de etapas por célula (escala compartilhada)")
    fig.suptitle(f"GOL x Azul — Etapa Média x Horário de Partida, Top {top_n} Bases por Empresa",
                 fontweight="bold")
    fig.savefig(FIG_DIR / "novo_03_hexbin_hub_top5.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def novo_04_hexbin_grid_top6(df_g, df_a, top_n: int = 6) -> None:
    """Espelho de dist_11/dist_12 -- la' sao dois layouts (2x3 e 3x2) do
    MESMO conteudo por empresa. Aqui, um layout so (2x3), empilhado:
    bloco de cima = GOL, bloco de baixo = Azul, escala de cor
    compartilhada entre os 12 paineis -- decisao explicita, nao os dois
    layouts x duas empresas (o que daria 4 figuras)."""
    fig, axes = plt.subplots(4, 3, figsize=(14, 14), sharex=True, sharey=True)
    hbs = []
    for bloco, (df, nome) in enumerate(((df_g, "GOL"), (df_a, "Azul"))):
        top_bases = df["sg_iata_origem"].value_counts().head(top_n).index.tolist()
        for i, base in enumerate(top_bases):
            row = bloco * 2 + i // 3
            col = i % 3
            ax = axes[row, col]
            sub = df[df["sg_iata_origem"] == base]
            hb = ax.hexbin(sub["nr_horas_voadas"], sub["hora_partida_decimal"],
                            gridsize=26, cmap="YlOrBr", mincnt=1)
            hbs.append(hb)
            ax.set_title(f"{nome} — {base}", fontsize=9, fontweight="bold")
    axes[0, 0].set_yticks(range(0, 25, 6))
    axes[0, 0].set_yticklabels([f"{h:02d}:00" for h in range(0, 25, 6)])
    vmax_global = max(hb.get_array().max() for hb in hbs)
    for hb in hbs:
        hb.set_clim(0, vmax_global)
    fig.supxlabel("Horas voadas (etapa)")
    fig.supylabel("Horário de partida")
    cbar = fig.colorbar(hbs[0], ax=axes, shrink=0.6)
    cbar.set_label("Nº de etapas por célula (escala compartilhada)")
    fig.suptitle(f"GOL x Azul — Etapa Média x Horário, Top {top_n} Bases (GOL em cima, Azul embaixo)",
                 fontweight="bold")
    fig.savefig(FIG_DIR / "novo_04_hexbin_grid_top6.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def novo_05_decomposicao_mix_vs_intramodelo(df_g, df_a, min_etapas: int = 1000,
                                             ano_base: str = "2021") -> None:
    """Espelho de dist_16. Eixo Y NAO compartilhado entre os paineis de
    proposito -- a pergunta aqui nao e' "quem tem etapa maior" (isso ja'
    esta' no v01), e' "o quanto cada real diverge do proprio
    contrafactual" -- forcar a mesma escala absoluta comprimiria a
    divergencia da Azul, que opera numa faixa de valor menor que a GOL."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))
    for ax, df, cor, nome in ((ax1, df_g, GOL_ORANGE, "GOL"), (ax2, df_a, AZUL_BLUE, "Azul")):
        contagem = df["sg_equipamento_icao"].value_counts()
        modelos = contagem[contagem >= min_etapas].index.tolist()
        sub = df[df["sg_equipamento_icao"].isin(modelos)]
        mensal_contagem = (
            sub.set_index("dt_partida_real").groupby("sg_equipamento_icao")["nr_horas_voadas"]
            .resample("MS").count().unstack(0).fillna(0)
        )
        duracao_mensal = (
            sub.set_index("dt_partida_real").groupby("sg_equipamento_icao")["nr_horas_voadas"]
            .resample("MS").mean().unstack(0)
        )
        share_mensal = mensal_contagem.div(mensal_contagem.sum(axis=1), axis=0)
        share_base = share_mensal.loc[ano_base].mean()
        real = (share_mensal[modelos] * duracao_mensal[modelos]).sum(axis=1)
        contrafactual = (duracao_mensal[modelos] * share_base[modelos]).sum(axis=1)
        ax.plot(real.index, real.values, color=cor, linewidth=2, marker="o", markersize=3, label="Real")
        ax.plot(contrafactual.index, contrafactual.values, color=NEUTRAL_GRAY, linewidth=2, linestyle="--",
                label=f"Contrafactual ({ano_base})")
        ax.set_title(nome)
        ax.set_xlabel("Mês")
        ax.legend(frameon=True, edgecolor="#333333")
    ax1.set_ylabel("Etapa média (h)")
    ax2.set_ylabel("Etapa média (h)")
    fig.suptitle("GOL x Azul — Real x Contrafactual com Mix de Frota Travado (eixo Y independente por painel)",
                 fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "novo_05_decomposicao_mix_vs_intramodelo.png", dpi=150)
    plt.close(fig)


def novo_06_duracao_mensal_por_frota(df_g, df_a, min_etapas: int = 1000) -> None:
    """Espelho de duracao_media_mensal_por_frota (script 'analise_').
    Diferente do v10 (mix_frota_temporal, % de participacao): aqui e'
    valor absoluto de duracao por modelo, mes a mes."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5), sharey=True)
    for ax, df, nome in ((ax1, df_g, "GOL"), (ax2, df_a, "Azul")):
        modelos = df["sg_equipamento_icao"].value_counts()
        modelos = modelos[modelos >= min_etapas].index.tolist()
        cores = {m: c for m, c in zip(modelos, dg.PALETA_CATEGORICA)}
        for modelo in modelos:
            sub = df[df["sg_equipamento_icao"] == modelo]
            mensal = sub.set_index("dt_partida_real")["nr_horas_voadas"].resample("MS").mean()
            ax.plot(mensal.index, mensal.values, linewidth=2, marker="o", markersize=3,
                    label=modelo, color=cores[modelo])
        ax.set_title(nome)
        ax.set_xlabel("Mês")
        ax.legend(title="Modelo", frameon=True, edgecolor="#333333", fontsize=8)
    ax1.set_ylabel("Etapa média (h, mensal)")
    fig.suptitle("GOL x Azul — Duração Média Mensal por Modelo, Valor Absoluto (eixo Y compartilhado)",
                 fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "novo_06_duracao_mensal_por_frota.png", dpi=150)
    plt.close(fig)


def novo_07_duracao_mensal_por_base(df_g, df_a, max_bases: int = 6) -> None:
    """Espelho de duracao_media_mensal_por_base -- com legenda em caixa
    desde o inicio (licao ja aprendida em a3_tempo_de_solo: rotulo direto
    na ponta da linha fica ilegivel quando as bases convergem no fim da
    serie)."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5.5), sharey=True)
    for ax, df, selecionar_hub, nome in (
        (ax1, df_g, dg.selecionar_hub, "GOL"), (ax2, df_a, da.selecionar_hub, "Azul"),
    ):
        hub = selecionar_hub(df["sg_iata_origem"].value_counts())
        bases = hub.index.tolist()[:max_bases]
        cores = {b: c for b, c in zip(bases, dg.PALETA_CATEGORICA)}
        for base in bases:
            sub = df[df["sg_iata_origem"] == base]
            mensal = sub.set_index("dt_partida_real")["nr_horas_voadas"].resample("MS").mean()
            ax.plot(mensal.index, mensal.values, linewidth=2, marker="o", markersize=3,
                    label=base, color=cores[base])
        ax.set_title(nome)
        ax.set_xlabel("Mês")
        ax.legend(title="Base", loc="upper right", frameon=True, edgecolor="#333333", fontsize=8)
    ax1.set_ylabel("Etapa média (h, mensal)")
    fig.suptitle("GOL x Azul — Duração Média Mensal por Base HUB (eixo Y compartilhado)", fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "novo_07_duracao_mensal_por_base.png", dpi=150)
    plt.close(fig)


def novo_08_top_bases_chegadas(df_g, df_a) -> None:
    """Espelho de top_bases_chegadas -- so' contagem, sem codificar
    duracao por cor (isso ja e' o v03, que e' a versao de origem)."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), sharex=True)
    for ax, df, selecionar_hub, cor, nome in (
        (ax1, df_g, dg.selecionar_hub, GOL_ORANGE, "GOL"),
        (ax2, df_a, da.selecionar_hub, AZUL_BLUE, "Azul"),
    ):
        contagem_full = df["sg_iata_destino"].value_counts()
        contagem = selecionar_hub(contagem_full).sort_values()
        barras = ax.barh(contagem.index, contagem.values, color=cor, edgecolor="#333333", linewidth=0.5)
        ax.bar_label(barras, fmt="%.0f", fontweight="bold", fontsize=8, padding=3)
        ax.margins(x=0.12)
        ax.set_title(nome)
        ax.set_xlabel("Nº de chegadas")
    fig.suptitle("GOL x Azul — Bases HUB com Mais Chegadas (80% acumulado, eixo X compartilhado)",
                 fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "novo_08_top_bases_chegadas.png", dpi=150)
    plt.close(fig)


def novo_09_violin_sem_outlier_referencias(df_g, df_a) -> None:
    """Espelho de dist_08. Cada empresa usa a SUA propria cerca de Tukey
    para truncar (GOL e Azul diferem um pouco); eixo Y compartilhado usa
    o maior dos dois limiares."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 7))
    superiores = {}
    for ax, df, calcular_corte, cor, nome in (
        (ax1, df_g, dg.calcular_corte_outlier, GOL_ORANGE, "GOL"),
        (ax2, df_a, da.calcular_corte_outlier, AZUL_BLUE, "Azul"),
    ):
        inferior, superior = calcular_corte(df["nr_horas_voadas"])
        inferior = max(inferior, 0.0)
        sub = df.loc[df["nr_horas_voadas"].between(inferior, superior), "nr_horas_voadas"]
        superiores[nome] = superior
        media, mediana = sub.mean(), sub.median()
        q1, q3 = sub.quantile([0.25, 0.75])
        sns.violinplot(y=sub, color=cor, cut=0, inner="quartile", ax=ax)
        referencias = [
            (media, "Média", "#2a78d6", "-"), (mediana, "Mediana (Q2)", NEUTRAL_GRAY, "--"),
            (q1, "Q1", "#4a3aa7", ":"), (q3, "Q3", "#008300", ":"),
        ]
        for valor, rotulo, cor_ref, estilo in referencias:
            ax.axhline(valor, color=cor_ref, linestyle=estilo, linewidth=1.6, zorder=5)
            ax.text(0.62, valor, f"{rotulo} = {valor:.2f}h", transform=ax.get_yaxis_transform(),
                    color=cor_ref, fontweight="bold", fontsize=8, va="center", zorder=6,
                    bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.85, "pad": 1.5})
        ax.set_title(f"{nome} (truncado ≤{superior:.2f}h, n={fmt_milhar(len(sub))})")
        ax.set_xticks([])
        ax.set_xlim(-0.5, 1.3)
    ylim_max = max(superiores.values())
    ax1.set_ylim(0, ylim_max)
    ax2.set_ylim(0, ylim_max)
    ax1.set_ylabel("Etapa média (h)")
    ax2.set_ylabel("")
    fig.suptitle("GOL x Azul — Distribuição Sem Outlier, com Referências (eixo Y compartilhado)",
                 fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "novo_09_violin_sem_outlier_referencias.png", dpi=150)
    plt.close(fig)


def main() -> None:
    df_g = dg.load_data()
    df_a = da.load_data()
    print(f"GOL: {fmt_milhar(len(df_g))} etapas | Azul: {fmt_milhar(len(df_a))} etapas")

    df_full_g = ag.load_data(*ag.WINDOW_FULL)
    df_full_a = aa.load_data(*aa.WINDOW_FULL)

    v01_duracao_media_mensal(df_g, df_a)
    v02_duracao_por_frota_natureza(df_full_g, df_full_a)
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

    novo_01_dispersao_etapa_media_tempo_solo(df_g, df_a)
    novo_02_dispersao_etapa_media_distancia(df_g, df_a)
    novo_03_hexbin_hub_top5(df_g, df_a)
    novo_04_hexbin_grid_top6(df_g, df_a)
    novo_05_decomposicao_mix_vs_intramodelo(df_g, df_a)
    novo_06_duracao_mensal_por_frota(df_g, df_a)
    novo_07_duracao_mensal_por_base(df_g, df_a)
    novo_08_top_bases_chegadas(df_g, df_a)
    novo_09_violin_sem_outlier_referencias(df_g, df_a)

    print(f"Figuras salvas em {FIG_DIR}")


if __name__ == "__main__":
    main()
