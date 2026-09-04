"""Pareto de bases GOL por chegadas (HUB = acumula ate 80%) -- SPEC-013.

Atualiza rascunho/pareto_bases_gol.csv (2026-08-31, stale -- construido
antes da correcao do SPEC-008 v4 e antes de basica_curated_deep existir,
achado registrado em SPEC-013 historico) com o dado atual, mesmas
colunas, para consistencia de formato.

Regra de HUB: acumulado ANTES desta base < 80% (mesma regra implicita no
CSV original -- confirmado batendo contra ele: SBNF/NVT, cumulativo
79,36% antes dele, fica HUB; SBVT/VIX, cumulativo 80,85% apos, fica
OFF-HUB).

A coluna BASE passou a carregar o codigo IATA (rotulo usado nas figuras);
o ICAO original fica preservado em BASE_ICAO, ao lado. E' a unica
diferenca de formato em relacao ao CSV de 2026-08-31.

Roda com: conda run -n pesquisa-azul python analise/a4_etapa_media/gerar_pareto_bases_gol.py
"""

import sqlite3
from pathlib import Path

import pandas as pd

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from iata_bases import aplicar_iata  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = REPO_ROOT / "db" / "anac_basica.sqlite"
OUT_PATH = REPO_ROOT / "analise" / "a4_etapa_media" / "pareto_bases_gol_atualizado.csv"


def gerar() -> pd.DataFrame:
    con = sqlite3.connect(DB_PATH)
    query = """
        SELECT sg_icao_destino AS BASE_ICAO,
               COUNT(*) AS N_CHEGADAS,
               COUNT(DISTINCT ds_matricula) AS N_MATRICULAS
        FROM basica_curated_deep
        WHERE sg_empresa_icao = 'GLO' AND ds_servico_tipo_linha = 'PASSAGEIRO'
        GROUP BY sg_icao_destino
        ORDER BY N_CHEGADAS DESC
    """
    df = pd.read_sql_query(query, con)
    con.close()

    df = aplicar_iata(df, DB_PATH, colunas=(("BASE_ICAO", "BASE"),))

    total = df["N_CHEGADAS"].sum()
    df["PCT"] = (100 * df["N_CHEGADAS"] / total).round(2)
    df["PCT_ACUM"] = df["PCT"].cumsum().round(2)
    df.insert(0, "RANK", range(1, len(df) + 1))
    df = df[["RANK", "BASE", "BASE_ICAO", "N_CHEGADAS", "N_MATRICULAS", "PCT", "PCT_ACUM"]]
    df["TIPO"] = [
        "HUB" if (df["PCT_ACUM"][i] - df["PCT"][i]) < 80 else "OFF-HUB"
        for i in range(len(df))
    ]
    return df


if __name__ == "__main__":
    df = gerar()
    df.to_csv(OUT_PATH, index=False)
    n_hub = (df["TIPO"] == "HUB").sum()
    print(f"{len(df)} bases, {n_hub} classificadas HUB, total {df['N_CHEGADAS'].sum():,} chegadas".replace(",", "."))
    print(f"Salvo em {OUT_PATH}")
