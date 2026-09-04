"""De-para ICAO -> IATA das bases (origem/destino) usadas nas analises.

Motivacao: as figuras rotulavam as bases pelo codigo ICAO de 4 letras
(SBGR, SBSP), que e' o que a Basica/VRA carregam. A audiencia dessas
analises le IATA de 3 letras (GRU, CGH). Este modulo faz a traducao no
ponto de carga, sem tocar na fonte: o dataframe passa a ter as duas
colunas, sg_icao_* (rastro) e sg_iata_* (rotulo), e a plotagem usa a
segunda.

Fonte do de-para: dim_airport_location_time_zone (SRC_003/SRC_004,
origem OurAirports). Cobertura conferida em 2026-09-04 contra
fato_rotacao_aeronave_gol_azul: todo ICAO presente no fato tem linha na
dimensao, e so' 3 codigos nao tem IATA utilizavel.

Fallback: quando nao ha IATA, o rotulo continua sendo o ICAO. Sao dois
casos distintos e ambos caem na mesma regra:

  - base_iata NULL/vazio -- SBUY (676 etapas), LPAR (2), SBYS (1).
  - base_iata == 'N/I', que e' sentinela de "nao informado" gravado como
    se fosse codigo. Sao 3 aerodromos na dimensao (SBFE, SDIY, SNJD) e um
    deles, SDIY (Feira de Santana), aparece 317 vezes no fato. Sem esta
    regra os tres colapsariam num unico balde "N/I" e o grafico mostraria
    uma base inexistente com a soma dos tres.

Nao ha colisao IATA real nos dados: os unicos IATA repetidos na dimensao
sao IST (LTFM/LTBA), RAI (GVNP/GVPR) e o proprio N/I. Desses, so' GVNP e
LTBA aparecem no fato, uma etapa cada, e nunca o par completo -- ou seja,
nenhum par de ICAO distintos vira o mesmo IATA no recorte analisado.
"""

from pathlib import Path
import sqlite3

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
DB_PATH_PADRAO = REPO_ROOT / "db" / "anac_basica.sqlite"

# Valores que aparecem na coluna base_iata mas nao sao codigo IATA.
SENTINELAS_IATA = {"", "N/I", "NI", "N/A", "NA", "-", "--", "NULL", "NONE"}

# Pares (coluna ICAO de origem, coluna IATA a criar) procurados no dataframe.
COLUNAS_PADRAO = (
    ("sg_icao_origem", "sg_iata_origem"),
    ("sg_icao_destino", "sg_iata_destino"),
    ("sg_icao_destino_anterior", "sg_iata_destino_anterior"),
)


def carregar_de_para(db_path: Path | str = DB_PATH_PADRAO) -> dict[str, str]:
    """ICAO -> IATA, ja sem sentinela. ICAO ausente do dict = usar o proprio ICAO."""
    con = sqlite3.connect(db_path)
    dim = pd.read_sql_query(
        "SELECT base_icao, base_iata FROM dim_airport_location_time_zone", con
    )
    con.close()

    iata = dim["base_iata"].fillna("").astype(str).str.strip().str.upper()
    valido = ~iata.isin(SENTINELAS_IATA)
    return dict(zip(dim.loc[valido, "base_icao"], iata[valido]))


def aplicar_iata(
    df: pd.DataFrame,
    db_path: Path | str = DB_PATH_PADRAO,
    colunas: tuple[tuple[str, str], ...] = COLUNAS_PADRAO,
    verboso: bool = True,
) -> pd.DataFrame:
    """Cria a coluna IATA ao lado de cada coluna ICAO presente no df.

    Preserva a coluna ICAO (rastro de auditoria) e insere a coluna IATA
    imediatamente a direita dela. Colunas de `colunas` que nao existirem
    no df sao ignoradas em silencio -- cada script traz um subconjunto.
    """
    de_para = carregar_de_para(db_path)

    for col_icao, col_iata in colunas:
        if col_icao not in df.columns:
            continue

        icao = df[col_icao].astype("string")
        rotulo = icao.map(de_para).fillna(icao)

        if col_iata in df.columns:
            df[col_iata] = rotulo
        else:
            df.insert(df.columns.get_loc(col_icao) + 1, col_iata, rotulo)

        if verboso:
            sem_iata = icao[~icao.isin(de_para.keys())].dropna()
            n_sem = len(sem_iata)
            if n_sem:
                amostra = ", ".join(sorted(sem_iata.unique())[:5])
                pct = 100 * n_sem / len(df)
                print(f"[iata] {col_icao}: {n_sem} linhas ({pct:.3f}%) sem IATA, "
                      f"rotuladas com o proprio ICAO -- {amostra}")
            else:
                print(f"[iata] {col_icao}: 100% mapeado para IATA")

    return df
