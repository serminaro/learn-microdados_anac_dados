"""Carrega data/aerodromos_enriquecido.csv em db/anac_basica.sqlite.

Fonte original: rascunho/dim_airport_location_time_zone.csv (283 de 863
aeródromos). Completada em 2026-08-31 a pedido do autor com o arquivo
cheio (data/aerodromos_enriquecido.csv), que é a fonte primária real
(SRC_001_enriquecer_bases_aerodromos.py) -- o recorte de 283 vira
histórico, não é mais lido por este script.

Tratamentos, na ordem:
1. Descarta as 5 linhas `_match == SEM_MATCH` (sem coordenada, sem uso
   possível como dimensão de localização).
2. Deduplica por BASE_ICAO: o arquivo de origem tem granularidade
   (ICAO, IATA observado nos microdados), não uma linha por aeroporto --
   fica a linha de maior QT_OCORRENCIAS. Único caso onde isso resolve uma
   divergência real (não só ruído de IATA): SBQV, que teve o código
   reatribuído entre dois aeroportos físicos diferentes ao longo do
   tempo -- fica o aeroporto historicamente dominante na janela
   observada, mesmo resultado que a resolução manual original já tinha
   escolhido.
3. Descarta HOR_VERAO_ATUAL/HORARIO_VERAO_ATUAL e JA_TEVE_HORARIO_VERAO
   (pedido do autor).
4. BASE_IATA vazio ou "..." (placeholder) vira NULL, não o literal.
5. MUNICIPIO_OURAIRPORTS/PAIS_ISO vazios (os 8 aeródromos MANUAL_KEYWORD:
   fechados ou com ICAO reatribuído) viram NULL, não string vazia.
"""

import csv
import sqlite3
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
CSV_PATH = RAIZ / "data" / "aerodromos_enriquecido.csv"
DB_PATH = RAIZ / "db" / "anac_basica.sqlite"
DDL_PATH = RAIZ / "sql" / "ingestao_sqlite" / "DDL_005_dim_airport_create_table.sql"


def limpar(v):
    v = (v or "").strip()
    return None if v in ("", "...") else v


def carregar():
    with open(CSV_PATH, encoding="utf-8") as f:
        linhas = list(csv.DictReader(f))

    linhas = [r for r in linhas if r["_match"] != "SEM_MATCH"]

    canonicas = {}
    for r in linhas:
        icao = r["BASE_ICAO"]
        atual = canonicas.get(icao)
        if atual is None or int(r["QT_OCORRENCIAS"] or 0) > int(atual["QT_OCORRENCIAS"] or 0):
            canonicas[icao] = r

    conn = sqlite3.connect(DB_PATH)
    conn.executescript(DDL_PATH.read_text())

    for r in canonicas.values():
        conn.execute(
            """
            INSERT INTO dim_airport_location_time_zone (
                base_icao, base_iata, latitude, longitude, tz_iana,
                utc_offset, nome_ourairports, municipio_ourairports,
                pais_iso, tipo_ourairports
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                r["BASE_ICAO"],
                limpar(r["BASE_IATA"]),
                float(r["LATITUDE"]),
                float(r["LONGITUDE"]),
                r["TZ_IANA"],
                float(r["UTC_OFFSET_PADRAO_H"]),
                r["NOME_OURAIRPORTS"],
                limpar(r["MUNICIPIO_OURAIRPORTS"]),
                limpar(r["PAIS_ISO"]),
                r["TIPO_OURAIRPORTS"],
            ),
        )
    conn.commit()
    total = conn.execute("SELECT COUNT(*) FROM dim_airport_location_time_zone").fetchone()[0]
    print(f"dim_airport_location_time_zone: {total} linhas carregadas ({len(linhas)} linhas na fonte, {len(canonicas)} ICAO únicos)")
    conn.close()


if __name__ == "__main__":
    carregar()
