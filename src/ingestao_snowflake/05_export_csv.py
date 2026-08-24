#!/home/bruno/miniconda3/envs/pesquisa-azul/bin/python
"""Exporta a tabela basica_raw inteira para um CSV unico, UTF-8, pronto para
COPY INTO em um stage do Snowflake (ou qualquer outro banco)."""
import csv
import sqlite3
from pathlib import Path

DB_PATH = Path("/home/bruno/Projetos/learn-microdados_anac_dados/db/anac_basica.sqlite")
CSV_OUT = Path("/home/bruno/Projetos/learn-microdados_anac_dados/data/anac/basica_consolidado_2024_2026.csv")

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(basica_raw)")
    cols = [r[1] for r in cur.fetchall()]

    cur.execute(f"SELECT {','.join(cols)} FROM basica_raw ORDER BY nr_ano_mes_arquivo, id_basica")

    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with open(CSV_OUT, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(cols)
        while True:
            rows = cur.fetchmany(10000)
            if not rows:
                break
            writer.writerows(rows)
            n += len(rows)

    conn.close()
    size_mb = CSV_OUT.stat().st_size / 1024 / 1024
    print(f"Exportadas {n:,} linhas para {CSV_OUT} ({size_mb:.0f} MB)")

if __name__ == "__main__":
    main()
