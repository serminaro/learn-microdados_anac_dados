"""Exporta para Excel os dados da rota MAO<->RBR -- GOL (recorte da a6).

Cinco abas: Leia-me (premissas), Mensal 2026, Mensal 2021-2026, Anual, e o
detalhe voo a voo de 2026 para auditoria.

As definicoes de metrica, virada de data e descarte vem por import de
analise_pontualidade_gol -- a planilha nao redefine nada, senao um dia ela
e a figura discordariam sem ninguem notar.

TRES CUIDADOS DE DENOMINADOR, explicados tambem na aba Leia-me:

1. `realizados` = voos que ocorreram, com ou sem horario previsto.
   `programados` = realizados COM previsto + cancelados. O voo extra nao
   entra em programados: ele nunca foi programado.
2. As quatro metricas tem por denominador a `base_calculo`, que e'
   realizados com previsto menos os descartes de atraso absurdo. Nao e' o
   total de realizados.
3. Voo extra so' e' localizavel pela data REAL (falta justamente o campo
   previsto). Filtro por data prevista mede zero extra em qualquer rota,
   por construcao.

Roda com: conda run -n gov-sermi-perf python analise/a6_pontualidade/exportar_rota_mao_rbr.py
"""

import sqlite3
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analise_pontualidade_gol import (  # noqa: E402
    DB_VRA, EMPRESA, LIMITE_ABSURDO_MIN, contagens, corrigir_virada, metricas,
)
from rota_mao_rbr_gol import ROTAS, icao_de  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
SAIDA = REPO_ROOT / "analise" / "a6_pontualidade" / "a6_dados_rota_mao_rbr.xlsx"
SAIDA_CSV_DIR = REPO_ROOT / "analise" / "a6_pontualidade"

JANELA_TOTAL = ("2021-01-01", "2026-07-31")
ANO_FOCO = "2026"

COLUNAS_AGG = [
    "rota", "periodo", "programados", "realizados", "cancelados",
    "pct_cancelamento", "extras", "pct_extra", "base_calculo", "descartados",
    "D0_n", "D0_pct", "D14_n", "D14_pct", "A0_n", "A0_pct", "A14_n", "A14_pct",
    "atraso_partida_mediano_min", "atraso_chegada_mediano_min",
]


def carregar_realizados(origem_iata: str, destino_iata: str) -> pd.DataFrame:
    """Todos os realizados da rota, COM e SEM previsto, pela data real."""
    con = sqlite3.connect(DB_VRA)
    q = """
        SELECT nr_voo, sg_icao_origem, sg_icao_destino,
               dt_hr_partida_prevista, dt_hr_partida_real,
               dt_hr_chegada_prevista, dt_hr_chegada_real
        FROM vra_curated_deep
        WHERE sg_empresa_icao = ? AND sg_icao_origem = ? AND sg_icao_destino = ?
          AND dt_hr_partida_real BETWEEN ? AND ?
    """
    df = pd.read_sql_query(
        q, con,
        params=(EMPRESA, icao_de(origem_iata), icao_de(destino_iata),
                JANELA_TOTAL[0], JANELA_TOTAL[1] + " 23:59:59"),
    )
    con.close()

    df["rota"] = f"{origem_iata} → {destino_iata}"
    for c in ("dt_hr_partida_prevista", "dt_hr_partida_real",
              "dt_hr_chegada_prevista", "dt_hr_chegada_real"):
        df[c] = pd.to_datetime(df[c].replace("", pd.NA), errors="coerce")

    df["extra"] = df["dt_hr_partida_prevista"].isna() | df["dt_hr_chegada_prevista"].isna()
    df["atraso_part"] = corrigir_virada(
        (df["dt_hr_partida_real"] - df["dt_hr_partida_prevista"]).dt.total_seconds() / 60.0)
    df["atraso_cheg"] = corrigir_virada(
        (df["dt_hr_chegada_real"] - df["dt_hr_chegada_prevista"]).dt.total_seconds() / 60.0)
    df["descartado"] = (~df["extra"]) & (
        (df["atraso_part"].abs() > LIMITE_ABSURDO_MIN)
        | (df["atraso_cheg"].abs() > LIMITE_ABSURDO_MIN))
    df["mes"] = df["dt_hr_partida_real"].dt.to_period("M").astype(str)
    df["ano"] = df["dt_hr_partida_real"].dt.year.astype(str)
    return df


def carregar_cancelados(origem_iata: str, destino_iata: str) -> pd.DataFrame:
    """Cancelados da rota, pela data PREVISTA (nao ha data real)."""
    con = sqlite3.connect(DB_VRA)
    q = """
        SELECT nr_voo, dt_hr_partida_prevista
        FROM vra_silver
        WHERE sg_empresa_icao = ? AND sg_icao_origem = ? AND sg_icao_destino = ?
          AND ds_situacao_voo = 'CANCELADO'
          AND dt_hr_partida_prevista BETWEEN ? AND ?
    """
    d = pd.read_sql_query(
        q, con,
        params=(EMPRESA, icao_de(origem_iata), icao_de(destino_iata),
                JANELA_TOTAL[0], JANELA_TOTAL[1] + " 23:59:59"),
    )
    con.close()
    d["rota"] = f"{origem_iata} → {destino_iata}"
    d["dt_hr_partida_prevista"] = pd.to_datetime(d["dt_hr_partida_prevista"])
    d["mes"] = d["dt_hr_partida_prevista"].dt.to_period("M").astype(str)
    d["ano"] = d["dt_hr_partida_prevista"].dt.year.astype(str)
    return d


def agregar(real: pd.DataFrame, canc: pd.DataFrame, chave: str) -> pd.DataFrame:
    """Uma linha por rota x periodo, com todos os denominadores explicitos."""
    linhas = []
    periodos = sorted(set(real[chave]) | set(canc[chave]))
    for rota in real["rota"].unique():
        for per in periodos:
            r = real[(real["rota"] == rota) & (real[chave] == per)]
            c = canc[(canc["rota"] == rota) & (canc[chave] == per)]
            if r.empty and c.empty:
                continue
            base = r[(~r["extra"]) & (~r["descartado"])]
            n_extra, n_canc = int(r["extra"].sum()), len(c)
            n_prog = int((~r["extra"]).sum()) + n_canc
            m = metricas(base) if len(base) else {}
            cnt = contagens(base) if len(base) else {}
            linhas.append({
                "rota": rota,
                "periodo": per,
                "programados": n_prog,
                "realizados": len(r),
                "cancelados": n_canc,
                "pct_cancelamento": (100.0 * n_canc / n_prog) if n_prog else None,
                "extras": n_extra,
                "pct_extra": (100.0 * n_extra / len(r)) if len(r) else None,
                "base_calculo": len(base),
                "descartados": int(r["descartado"].sum()),
                **{f"{k}_n": cnt.get(k) for k in ("D0", "D14", "A0", "A14")},
                **{f"{k}_pct": m.get(k) for k in ("D0", "D14", "A0", "A14")},
                "atraso_partida_mediano_min": base["atraso_part"].median() if len(base) else None,
                "atraso_chegada_mediano_min": base["atraso_cheg"].median() if len(base) else None,
            })
    return pd.DataFrame(linhas)[COLUNAS_AGG]


def aba_leia_me() -> pd.DataFrame:
    itens = [
        ("Objeto", "Pontualidade e regularidade da GOL nas rotas MAO ↔ RBR"),
        ("Empresa", "GOL (sg_empresa_icao = GLO). Nenhuma outra empresa operou a rota em 2026."),
        ("Rotas", "MAO → RBR e RBR → MAO (IATA). ICAO correspondente: SBEG e SBRB."),
        ("Período", "2021-01-01 a 2026-07-31 (último mês de VRA publicado pela ANAC)."),
        ("Fonte", "vra_curated_deep e vra_silver, em db/anac_vra.sqlite. VRA da ANAC."),
        ("Gerado por", "analise/a6_pontualidade/exportar_rota_mao_rbr.py"),
        ("", ""),
        ("DEFINIÇÃO DAS MÉTRICAS", ""),
        ("D0", "Partidas com atraso <= 0 min (saiu no horário previsto ou antes)."),
        ("D14", "Partidas com atraso <= 14 min (equivale ao padrão 'menos de 15')."),
        ("A0", "Chegadas com atraso <= 0 min."),
        ("A14", "Chegadas com atraso <= 14 min."),
        ("atraso", "real menos previsto, em minutos. Adiantado conta como no horário."),
        ("", ""),
        ("DENOMINADORES (o ponto mais fácil de errar)", ""),
        ("realizados", "Voos que ocorreram, COM ou SEM horário previsto."),
        ("extras", "Voos realizados SEM horário previsto. Não foram programados."),
        ("programados", "Realizados COM previsto + cancelados. NÃO inclui os extras."),
        ("base_calculo", "Denominador das quatro métricas: realizados com previsto, "
                         "menos os descartes por atraso absurdo. NÃO é o total de realizados."),
        ("pct_cancelamento", "cancelados / programados."),
        ("pct_extra", "extras / realizados."),
        ("", ""),
        ("TRATAMENTO DE DADO", ""),
        ("Virada de data", "Atraso abaixo de -720 min ganha +1440, e acima de +720 ganha -1440, "
                           "quando a correção traz o valor para dentro de ±720. Partida 23:50 "
                           "registrada como 00:10 do mesmo dia é erro de data, não antecipação."),
        ("Descarte", "O que continuar fora de ±720 min após a correção sai do cálculo e é "
                     "contado na coluna 'descartados'."),
        ("Como achar extra", "Voo extra só é localizável pela data REAL: falta justamente o campo "
                             "previsto. Filtro por data prevista mede zero extra em qualquer "
                             "rota, por construção."),
        ("Mês de referência", "Realizados e extras pelo mês da partida real; cancelados pelo mês da "
                              "partida prevista, que é o único horário que possuem. Verificado: "
                              "nesta rota nenhum voo tem mês previsto diferente do mês real, "
                              "então as duas convenções coincidem aqui."),
        ("Fuso", "Os quatro carimbos do VRA estão numa referência única, verificado por três vias, "
                 "então 'real menos previsto' dispensa conversão de fuso."),
        ("", ""),
        ("UNIDADE", ""),
        ("Nesta planilha", "Colunas *_pct e pct_* em PORCENTAGEM, base 100: 84,62 significa 84,62%."),
        ("Nos CSV por rota", "Os arquivos a6_rota_MAO_RBR_2026.csv e a6_rota_RBR_MAO_2026.csv trazem "
                             "as quatro métricas em PROPORÇÃO, base 1: 0,8462 significa 84,62%. "
                             "Diferença deliberada (o CSV alimenta gráfico e modelagem, que esperam "
                             "base 1); registrada aqui para quem comparar os dois arquivos."),
        ("Ponto percentual", "Diferença entre duas porcentagens. De 84% para 92% são 8 pontos "
                             "percentuais, não 8%."),
        ("", ""),
        ("LIMITES DE LEITURA", ""),
        ("Tamanho da amostra", "A rota tem 12 a 27 voos por mês por sentido. UM voo vale de 3,7 a "
                               "8,3 pontos percentuais. Variação mensal de 10 pontos pode ser um "
                               "único voo atrasado: nenhum movimento mês a mês aqui é robusto."),
        ("O que resiste", "A diferença entre sentidos: RBR → MAO é melhor que MAO → RBR nos sete "
                          "meses de 2026 e nas quatro métricas, sobre 231 voos."),
        ("Métrica no teto", "Em RBR → MAO, D14 e A14 saturam em 100% na maioria dos meses. "
                            "Métrica saturada não discrimina mais nada."),
        ("Cancelamento e pontualidade", "Cancelar voo que ia atrasar melhora as quatro métricas. "
                                        "Por isso o cancelamento está na mesma tabela, e não em "
                                        "outro documento."),
        ("Hipótese, não achado", "2026 tem zero cancelamento e zero extra nas duas rotas, depois de "
                                 "anos com ambos. Sugere malha estabilizada, mas dois anos de série "
                                 "não separam mudança real de coincidência."),
    ]
    return pd.DataFrame(itens, columns=["Campo", "Descrição"])


def escrever(livro: dict[str, pd.DataFrame]) -> None:
    with pd.ExcelWriter(SAIDA, engine="xlsxwriter") as xl:
        wb = xl.book
        f_cab = wb.add_format({"bold": True, "bg_color": "#B34700", "font_color": "white",
                               "border": 1, "text_wrap": True, "valign": "vcenter"})
        f_pct = wb.add_format({"num_format": "0.0"})
        f_min = wb.add_format({"num_format": "0.0"})
        f_txt = wb.add_format({"text_wrap": True, "valign": "top"})
        f_neg = wb.add_format({"bold": True})

        for aba, df in livro.items():
            df.to_excel(xl, sheet_name=aba, index=False, startrow=1, header=False)
            ws = xl.sheets[aba]
            for i, col in enumerate(df.columns):
                ws.write(0, i, col, f_cab)

            if aba == "Leia-me":
                ws.set_column(0, 0, 30, f_neg)
                ws.set_column(1, 1, 105, f_txt)
                ws.freeze_panes(1, 0)
                continue

            larguras = {"rota": 13, "periodo": 10}
            for i, col in enumerate(df.columns):
                fmt = None
                if col.endswith("_pct") or col.startswith("pct_"):
                    fmt = f_pct
                elif col.endswith("_min"):
                    fmt = f_min
                ws.set_column(i, i, larguras.get(col, 13), fmt)
            ws.freeze_panes(1, 2)
            ws.autofilter(0, 0, len(df), len(df.columns) - 1)


def exportar_csv_por_rota(mensal_2026: pd.DataFrame) -> list[Path]:
    """Um CSV por rota: mes de 2026, quantidade de voos e as quatro metricas.

    `voos` e' a base de calculo (realizados com previsto, menos descarte),
    que e' o DENOMINADOR das quatro taxas -- assim o arquivo fecha em si
    mesmo: voos * A0/100 da o numero de chegadas no horario. Em 2026 esse
    numero coincide com o total de realizados, porque a rota nao teve extra
    nem descarte; nos anos anteriores nao coincidiria.

    UNIDADE DAS QUATRO METRICAS: proporcao em base 1, nao porcentagem em
    base 100 (decisao do autor, 2026-09-11). 0.8462 significa 84,62%. E' a
    forma que biblioteca de grafico e de modelagem espera receber, e no
    Excel basta aplicar o formato de porcentagem. Quatro casas decimais aqui
    equivalem as duas casas da porcentagem.

    ATENCAO: o resto do projeto (planilha, figuras, cercas) usa base 100.
    Este CSV e' a excecao, deliberada; a aba Leia-me da planilha registra a
    diferenca para quem comparar os dois artefatos.

    Separador e decimal seguem os CSV que ja existem no projeto: virgula
    como separador, ponto decimal (ver analise/a4_etapa_media/pareto_bases_*.csv).
    """
    caminhos = []
    for origem, destino in ROTAS:
        rota = f"{origem} → {destino}"
        d = mensal_2026[mensal_2026["rota"] == rota]
        saida = pd.DataFrame({
            "mes": d["periodo"],
            "voos": d["base_calculo"].astype(int),
            "A0": (d["A0_pct"] / 100.0).round(4),
            "A14": (d["A14_pct"] / 100.0).round(4),
            "D0": (d["D0_pct"] / 100.0).round(4),
            "D14": (d["D14_pct"] / 100.0).round(4),
        })
        caminho = SAIDA_CSV_DIR / f"a6_rota_{origem}_{destino}_{ANO_FOCO}.csv"
        saida.to_csv(caminho, index=False)
        caminhos.append(caminho)
        print(f"[csv_{origem}_{destino}] {len(saida)} meses, "
              f"{int(saida['voos'].sum())} voos -> {caminho.name}")
    return caminhos


def main() -> None:
    reais, cancs = [], []
    for origem, destino in ROTAS:
        reais.append(carregar_realizados(origem, destino))
        cancs.append(carregar_cancelados(origem, destino))
    real = pd.concat(reais, ignore_index=True)
    canc = pd.concat(cancs, ignore_index=True)

    mensal = agregar(real, canc, "mes")
    anual = agregar(real, canc, "ano")
    mensal_2026 = mensal[mensal["periodo"].str.startswith(ANO_FOCO)].reset_index(drop=True)

    detalhe = (
        real[real["ano"] == ANO_FOCO]
        [["rota", "nr_voo", "sg_icao_origem", "sg_icao_destino",
          "dt_hr_partida_prevista", "dt_hr_partida_real", "atraso_part",
          "dt_hr_chegada_prevista", "dt_hr_chegada_real", "atraso_cheg",
          "extra", "descartado"]]
        .sort_values(["rota", "dt_hr_partida_real"])
        .reset_index(drop=True)
    )

    escrever({
        "Leia-me": aba_leia_me(),
        f"Mensal {ANO_FOCO}": mensal_2026,
        "Mensal 2021-2026": mensal,
        "Anual 2021-2026": anual,
        f"Voos {ANO_FOCO} (detalhe)": detalhe,
    })

    print(f"[xls_01] abas: Leia-me, Mensal {ANO_FOCO} ({len(mensal_2026)} linhas), "
          f"Mensal 2021-2026 ({len(mensal)}), Anual ({len(anual)}), "
          f"Voos {ANO_FOCO} ({len(detalhe)})")
    print(f"[xls_02] confere 2026: realizados={int(mensal_2026['realizados'].sum())}  "
          f"extras={int(mensal_2026['extras'].sum())}  "
          f"cancelados={int(mensal_2026['cancelados'].sum())}  "
          f"base_calculo={int(mensal_2026['base_calculo'].sum())}")
    exportar_csv_por_rota(mensal_2026)
    print(f"\nPlanilha: {SAIDA}")


if __name__ == "__main__":
    main()
