#!/home/bruno/miniconda3/envs/pesquisa-azul/bin/python
"""Carrega os 30 meses de basica (data/anac/basica/*.txt) no SQLite (db/anac_basica.sqlite).
Idempotente: id_basica e chave primaria, INSERT OR IGNORE nao duplica em reexecucao.
"""
import csv
import sqlite3
import time
import zipfile
from pathlib import Path

DEST = Path("/home/bruno/Projetos/learn-microdados_anac_dados/data/anac/basica")
DB_PATH = Path("/home/bruno/Projetos/learn-microdados_anac_dados/db/anac_basica.sqlite")
DDL_PATH = Path("/home/bruno/Projetos/learn-microdados_anac_dados/sql/ingestao_sqlite/create_table_basica.sql")
BATCH = 5000

def month_files():
    out = []
    for ano in (2024, 2025, 2026):
        for mes in range(1, 13):
            if ano == 2026 and mes > 6:
                continue
            fname = "basica202606.zip" if (ano == 2026 and mes == 6) else f"basica{ano}-{mes:02d}.zip"
            txt_name = fname.replace(".zip", ".txt") if fname != "basica202606.zip" else "basica2026-06.txt"
            out.append((ano, mes, DEST / fname, DEST / txt_name))
    return out

def main():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(DDL_PATH.read_text(encoding="utf-8"))
    conn.commit()

    cur = conn.cursor()
    cur.execute("PRAGMA table_info(basica_raw)")
    cols = [r[1] for r in cur.fetchall()]  # inclui nr_ano_mes_arquivo no final
    n_data_cols = len(cols) - 1  # todas menos nr_ano_mes_arquivo
    placeholders = ",".join(["?"] * len(cols))
    insert_sql = f"INSERT OR IGNORE INTO basica_raw ({','.join(cols)}) VALUES ({placeholders})"

    t0 = time.time()
    total_inseridas = 0
    total_lidas = 0

    for ano, mes, zip_path, txt_path in month_files():
        if not txt_path.exists():
            with zipfile.ZipFile(zip_path) as z:
                txts = [n for n in z.namelist() if n.lower().endswith(".txt")]
                z.extract(txts[0], path=zip_path.parent)

        ano_mes_arquivo = f"{ano}-{mes:02d}"
        with open(txt_path, encoding="latin-1", newline="") as f:
            reader = csv.reader(f, delimiter=";", quotechar='"')
            header = next(reader)
            assert header == cols[:n_data_cols], f"cabecalho inesperado em {txt_path.name}"

            batch = []
            n_mes = 0
            for row in reader:
                assert len(row) == n_data_cols, f"linha com {len(row)} campos, esperado {n_data_cols} em {txt_path.name}"
                batch.append(row + [ano_mes_arquivo])
                n_mes += 1
                if len(batch) >= BATCH:
                    cur.executemany(insert_sql, batch)
                    total_inseridas += cur.rowcount if cur.rowcount > 0 else 0
                    batch = []
            if batch:
                cur.executemany(insert_sql, batch)

        conn.commit()
        total_lidas += n_mes
        print(f"{ano_mes_arquivo}: {n_mes:,} linhas lidas do arquivo")

    cur.execute("SELECT COUNT(*) FROM basica_raw")
    total_no_banco = cur.fetchone()[0]

    dt = time.time() - t0
    print()
    print(f"Total de linhas lidas dos 30 arquivos: {total_lidas:,}")
    print(f"Total de linhas no banco apos carga:   {total_no_banco:,}")
    print(f"Tempo total: {dt:.1f}s")
    print(f"Banco em: {DB_PATH}")

    conn.close()

if __name__ == "__main__":
    main()
