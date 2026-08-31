#!/home/bruno/miniconda3/envs/pesquisa-azul/bin/python
"""Carrega os meses de VRA (data/anac/vra/*.csv) no SQLite (db/anac_vra.sqlite).
Idempotente por arquivo: pula qualquer mes (nr_ano_mes_arquivo) ja carregado,
nao por linha (VRA nao publica id de linha nativo, SPEC-009 Sec.5).
"""
import csv
import re
import sqlite3
import time
from pathlib import Path

SRC_DIR = Path("/home/bruno/Projetos/learn-microdados_anac_dados/data/anac/vra")
DB_PATH = Path("/home/bruno/Projetos/learn-microdados_anac_dados/db/anac_vra.sqlite")
DDL_PATH = Path("/home/bruno/Projetos/learn-microdados_anac_dados/sql/ingestao_sqlite/DDL_002_vra_create_table.sql")
BATCH = 5000

FNAME_RE = re.compile(r"^VRA_(\d{4})(\d{1,2})\.csv$", re.IGNORECASE)


def month_files():
    out = []
    for f in sorted(SRC_DIR.glob("VRA_*.csv")):
        m = FNAME_RE.match(f.name)
        if not m:
            continue  # ex.: _download_log.csv
        ano, mes = int(m.group(1)), int(m.group(2))
        out.append((f"{ano}-{mes:02d}", f))
    return out


def main():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(DDL_PATH.read_text(encoding="utf-8"))
    conn.commit()

    cur = conn.cursor()
    cur.execute("PRAGMA table_info(vra_raw)")
    cols = [r[1] for r in cur.fetchall()]
    n_data_cols = len(cols) - 1  # todas menos nr_ano_mes_arquivo
    placeholders = ",".join(["?"] * len(cols))
    insert_sql = f"INSERT INTO vra_raw ({','.join(cols)}) VALUES ({placeholders})"

    t0 = time.time()
    total_lidas = 0
    total_pulados = 0

    for ano_mes, path in month_files():
        cur.execute("SELECT COUNT(*) FROM vra_raw WHERE nr_ano_mes_arquivo = ?", (ano_mes,))
        if cur.fetchone()[0] > 0:
            total_pulados += 1
            continue

        with open(path, encoding="utf-8-sig", newline="") as f:
            next(f)  # linha 1: metadado "Atualizado em: ..."
            reader = csv.reader(f, delimiter=";", quotechar='"')
            header = next(reader)
            assert len(header) == n_data_cols, (
                f"cabecalho com {len(header)} colunas em {path.name}, esperado {n_data_cols}"
            )

            batch = []
            n_mes = 0
            for row in reader:
                if len(row) != n_data_cols:
                    continue  # linha em branco ao fim do arquivo, ignorada
                batch.append(row + [ano_mes])
                n_mes += 1
                if len(batch) >= BATCH:
                    cur.executemany(insert_sql, batch)
                    batch = []
            if batch:
                cur.executemany(insert_sql, batch)

        conn.commit()
        total_lidas += n_mes
        print(f"{ano_mes}: {n_mes:,} linhas carregadas ({path.name})")

    cur.execute("SELECT COUNT(*) FROM vra_raw")
    total_no_banco = cur.fetchone()[0]

    dt = time.time() - t0
    print()
    print(f"Meses pulados (ja carregados): {total_pulados}")
    print(f"Total de linhas lidas nesta execucao: {total_lidas:,}")
    print(f"Total de linhas no banco apos carga:  {total_no_banco:,}")
    print(f"Tempo total: {dt:.1f}s")
    print(f"Banco em: {DB_PATH}")

    conn.close()


if __name__ == "__main__":
    main()
