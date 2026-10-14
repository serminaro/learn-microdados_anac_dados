"""Pontualidade na rota MAO<->RBR -- GOL, 2026 (recorte da a6).

Corte pedido pelo autor (2026-09-11): A0/D0, depois A14/D14, depois as
quatro juntas, para MAO->RBR e RBR->MAO, so 2026, com o numero de voos
realizados e cancelados de cada mes no rotulo.

CUIDADO COM O N. A rota tem 12 a 27 voos por mes por sentido em 2026, nao
milhares. Um voo mexe a taxa entre 3,7 e 8,3 pontos percentuais, entao a
serie mensal aqui e' grossa por natureza: variacao de 10 pontos entre dois
meses pode ser um unico voo atrasado. Por isso o n vai no eixo, em todos os
graficos, e nao no rodape -- quem ler a figura tem que ver o denominador na
mesma passada em que ve a taxa.

CANCELAMENTO EM 2026 E' ZERO nos sete meses, nos dois sentidos. O rotulo
`c=0` nao e' erro de calculo: a rota teve 37 cancelamentos em 2021 e 54 em
2022, caiu para 5 em 2023, 2 em 2024, e zero em 2025 e 2026.

Premissas de metrica, virada de data e fuso: as mesmas da linha, herdadas
por import de analise_pontualidade_gol (fonte unica, sem copia).

Roda com: conda run -n gov-sermi-perf python analise/a6_pontualidade/rota_mao_rbr_gol.py
"""

import sqlite3
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analise_pontualidade_gol import (  # noqa: E402
    COR_METRICA, DB_VRA, EMPRESA, ROTULO,
    contagens, load_data, metricas, preparar,
)
from iata_bases import carregar_de_para  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
FIG_DIR = REPO_ROOT / "analise" / "a6_pontualidade" / "a6_figuras_rota_mao_rbr"
FIG_DIR.mkdir(parents=True, exist_ok=True)

JANELA = ("2026-01-01", "2026-07-31")
SUFFIX = "2026"

# Rotas em IATA, que e' a convencao de rotulo do projeto (README, "Convencao
# de rotulo"; iata_bases.py). O ICAO nao some: ele continua na coluna de
# rastro do dataframe e e' derivado daqui pelo de-para da dimensao, nunca
# cravado a mao -- Manaus e Rio Branco entram como MAO e RBR, e SBEG/SBRB
# aparecem so' onde a fonte exige (o filtro contra vra_silver).
ROTAS = [
    ("MAO", "RBR"),
    ("RBR", "MAO"),
]

MESES_PT = {1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
            7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"}

# Deslocamento vertical fixo do rotulo de cada metrica, em pontos: quatro
# slots (-22, -8, +8, +22) em torno do ponto. A atribuicao nao e' arbitraria
# -- os pares que mais coincidem nesta rota ficam nos slots mais distantes:
# D14 e A14 saturam juntos em 100%, e D0 e A0 andam colados. Cada par fica a
# 30 pontos de distancia; os pares que raramente empatam dividem os 14 do
# meio. Fixo por metrica (nao por posicao na figura) para o rotulo da mesma
# metrica cair sempre no mesmo lugar relativo, em todas as figuras.
OFFSET_ROTULO = {"D0": -22, "A0": 8, "D14": -8, "A14": 22}


def icao_de(iata: str) -> str:
    """IATA -> ICAO pelo de-para da dimensao, para falar com a fonte.

    A vra_silver so' tem ICAO, entao o filtro de cancelado precisa traduzir
    de volta. A inversao e' checada: IATA que nao existe, ou que aponta para
    mais de um ICAO, para o script em vez de escolher um em silencio (a
    dimensao tem IATA repetido, ver iata_bases.py).
    """
    icaos = [k for k, v in carregar_de_para().items() if v == iata]
    if not icaos:
        raise ValueError(f"IATA {iata!r} nao esta no de-para da dimensao")
    if len(icaos) > 1:
        raise ValueError(f"IATA {iata!r} aponta para mais de um ICAO: {icaos}")
    return icaos[0]


def cancelados_por_mes(origem: str, destino: str) -> pd.Series:
    """Cancelados do mes, por rota (entrada em IATA, consulta em ICAO)."""
    con = sqlite3.connect(DB_VRA)
    q = """
        SELECT substr(dt_hr_partida_prevista, 1, 7) AS mes, COUNT(*) AS n
        FROM vra_silver
        WHERE sg_empresa_icao = ? AND sg_icao_origem = ? AND sg_icao_destino = ?
          AND ds_situacao_voo = 'CANCELADO'
          AND dt_hr_partida_prevista BETWEEN ? AND ?
        GROUP BY 1
    """
    d = pd.read_sql_query(
        q, con,
        params=(EMPRESA, icao_de(origem), icao_de(destino),
                JANELA[0], JANELA[1] + " 23:59:59"),
    )
    con.close()
    if d.empty:
        return pd.Series(dtype="int64")
    d["mes"] = pd.to_datetime(d["mes"] + "-01")
    return d.set_index("mes")["n"]


def serie_da_rota(df: pd.DataFrame, origem: str, destino: str) -> pd.DataFrame:
    """Taxas mensais da rota, com realizados e cancelados ao lado.

    Filtra pelas colunas IATA que aplicar_iata criou, nao pelo ICAO bruto.
    """
    sub = df[(df["sg_iata_origem"] == origem) & (df["sg_iata_destino"] == destino)]
    mensal = (
        sub.assign(mes=sub["dt_hr_partida_real"].dt.to_period("M").dt.to_timestamp())
        .groupby("mes")
        .apply(
            lambda g: pd.Series({
                **metricas(g),
                # Contagem por metrica, sufixo _n: e' o que vai no rotulo do
                # ponto. A taxa fica no eixo (comparavel entre meses de n
                # diferente), a contagem fica no ponto (o dado bruto atras dela).
                **{f"{k}_n": v for k, v in contagens(g).items()},
                "realizados": len(g),
            }),
            include_groups=False,
        )
    )
    canc = cancelados_por_mes(origem, destino).reindex(mensal.index).fillna(0)
    mensal["cancelados"] = canc.astype(int)
    return mensal


def rotulos_x(mensal: pd.DataFrame) -> list[str]:
    """Mes + denominador no proprio tick: taxa e n lidos na mesma passada."""
    return [
        f"{MESES_PT[d.month]}\nn={int(r.realizados)}  c={int(r.cancelados)}"
        for d, r in zip(mensal.index, mensal.itertuples())
    ]


def _painel(ax, mensal: pd.DataFrame, chaves: tuple[str, ...], titulo: str) -> None:
    x = range(len(mensal))
    for k in chaves:
        ax.plot(x, mensal[k], linewidth=2, marker="o", markersize=5,
                color=COR_METRICA[k], label=k)
        for xi, v, c in zip(x, mensal[k], mensal[f"{k}_n"]):
            # Halo branco: com duas series a 4 pontos percentuais de
            # distancia, o deslocamento fixo nao basta e o rotulo cai sobre
            # o marcador vizinho. O fundo garante leitura sem precisar de
            # deteccao de colisao.
            ax.annotate(f"{v:.0f}", xy=(xi, v), xytext=(0, OFFSET_ROTULO[k]),
                        textcoords="offset points", ha="center", va="center",
                        fontsize=7.5, fontweight="bold", color=COR_METRICA[k],
                        bbox=dict(boxstyle="round,pad=0.18", fc="white",
                                  ec="none", alpha=0.8))
    ax.set_ylim(0, 118)
    ax.set_xticks(list(x))
    ax.set_xticklabels(rotulos_x(mensal), fontsize=8)
    ax.set_title(titulo)


def _nota_n(mensal_por_rota: list[pd.DataFrame]) -> str:
    todos = pd.concat([m["realizados"] for m in mensal_por_rota])
    pior, melhor = int(todos.min()), int(todos.max())
    return (f"n de {pior} a {melhor} voos/mês: 1 voo vale de "
            f"{100 / melhor:.1f} a {100 / pior:.1f} pontos percentuais")


def fig_par_de_metricas(series: dict[str, pd.DataFrame], chaves: tuple[str, ...],
                        nome: str) -> None:
    """Um par de metricas (A0/D0 ou A14/D14), uma rota por painel."""
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.4), sharey=True)
    for ax, (rot, mensal) in zip(axes, series.items()):
        _painel(ax, mensal, chaves, rot)
    axes[0].set_ylabel("% dos voos realizados")
    axes[0].legend(loc="lower left", frameon=True)
    fig.suptitle(
        f"{ROTULO} — {' e '.join(chaves)} por Mês, "
        f"{ROTAS[0][0]} ↔ {ROTAS[0][1]} ({SUFFIX})\n"
        f"{_nota_n(list(series.values()))}",
        fontweight="bold",
    )
    fig.tight_layout()
    fig.savefig(FIG_DIR / f"{nome}_{SUFFIX}.png", dpi=150)
    plt.close(fig)


def fig_todas_metricas(rot: str, mensal: pd.DataFrame, slug: str) -> None:
    """As quatro metricas juntas, uma figura por rota."""
    fig, ax = plt.subplots(figsize=(11, 5.6))
    _painel(ax, mensal, ("D0", "D14", "A0", "A14"), "")
    ax.set_ylabel("% dos voos realizados")
    ax.legend(loc="lower left", ncols=4, frameon=True)
    nota = (f"n de {int(mensal['realizados'].min())} a "
            f"{int(mensal['realizados'].max())} voos/mês; "
            f"cancelados no período: {int(mensal['cancelados'].sum())}")
    fig.suptitle(
        f"{ROTULO} — A0 / A14 / D0 / D14 por Mês, {rot} ({SUFFIX})\n{nota}",
        fontweight="bold",
    )
    fig.tight_layout()
    fig.savefig(FIG_DIR / f"todas_metricas_{slug}_{SUFFIX}.png", dpi=150)
    plt.close(fig)


def main() -> None:
    df = preparar(load_data(*JANELA), f"rota_mao_rbr_{SUFFIX}")

    series: dict[str, pd.DataFrame] = {}
    for origem, destino in ROTAS:
        rot = f"{origem} → {destino}"
        mensal = serie_da_rota(df, origem, destino)
        series[rot] = mensal
        print(f"\n[rota_{origem}_{destino}] {rot} (ICAO: "
              f"{icao_de(origem)}->{icao_de(destino)}) — {SUFFIX}")
        print(mensal.assign(mes=[f"{d:%Y-%m}" for d in mensal.index])
              .set_index("mes")[["realizados", "cancelados",
                                 "D0", "D0_n", "D14", "D14_n",
                                 "A0", "A0_n", "A14", "A14_n"]]
              .round(1).to_string())

    fig_par_de_metricas(series, ("A0", "D0"), "a0_d0")
    fig_par_de_metricas(series, ("A14", "D14"), "a14_d14")
    for origem, destino in ROTAS:
        rot = f"{origem} → {destino}"
        fig_todas_metricas(rot, series[rot], f"{origem}_{destino}")

    print(f"\nFiguras salvas em {FIG_DIR}")


if __name__ == "__main__":
    main()
