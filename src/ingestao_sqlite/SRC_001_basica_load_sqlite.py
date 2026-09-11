#!/usr/bin/env python3
"""Carrega em SQLite (db/anac_basica.sqlite) todo mes de Basica ja baixado em
data/anac/basica/*.zip, a partir de 2010-01. Idempotente: id_basica e chave
primaria, INSERT OR IGNORE nao duplica em reexecucao. Lida com a mudanca de
schema real da ANAC (nr_chave existe so a partir de 2020-01; meses anteriores
carregam nr_chave = NULL).
"""
import csv
import sqlite3
import time
import zipfile
from pathlib import Path

# Raiz do repositorio, resolvida a partir deste arquivo: o pipeline roda
# de qualquer diretorio e em qualquer sistema operacional (ver DEC-011).
REPO_ROOT = Path(__file__).resolve().parents[2]

DEST = REPO_ROOT / "data" / "anac" / "basica"
DB_PATH = REPO_ROOT / "db" / "anac_basica.sqlite"
DDL_PATH = REPO_ROOT / "sql" / "ingestao_sqlite" / "DDL_001_basica_create_table.sql"
BATCH = 5000

def month_files():
    # Corte por mes fixo (ate 2026-08-31: "if ano == 2026 and mes > 6") ficava
    # obsoleto a cada novo mes baixado -- 2026-07 baixado em disco nunca
    # chegava a ser tentado. Trocado por checagem de existencia do zip: cobre
    # qualquer mes ja baixado, sem precisar de edicao manual a cada carga.
    out = []
    for ano in range(2010, 2030):
        for mes in range(1, 13):
            fname = "basica202606.zip" if (ano == 2026 and mes == 6) else f"basica{ano}-{mes:02d}.zip"
            zip_path = DEST / fname
            if not zip_path.exists():
                continue
            txt_name = fname.replace(".zip", ".txt") if fname != "basica202606.zip" else "basica2026-06.txt"
            out.append((ano, mes, zip_path, DEST / txt_name))
    return out

def main():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(DDL_PATH.read_text(encoding="utf-8"))
    conn.commit()

    cur = conn.cursor()
    cur.execute("PRAGMA table_info(basica_raw)")
    cols = [r[1] for r in cur.fetchall()]  # inclui nr_ano_mes_arquivo no final
    n_data_cols = len(cols) - 1  # todas menos nr_ano_mes_arquivo (111: ... ate nr_chave)
    # Achado (2026-08-31, extensao 2010-2023): a ANAC acrescentou a coluna
    # nr_chave (ultima antes de nr_ano_mes_arquivo) a partir de 2020-01.
    # Arquivos 2010-01 a 2019-12 tem 110 colunas (sem nr_chave); carregados
    # com nr_chave = NULL, nao e erro de dado, e ausencia real na fonte.
    n_data_cols_sem_chave = n_data_cols - 1
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
            if header == cols[:n_data_cols]:
                tem_nr_chave = True
            elif header == cols[:n_data_cols_sem_chave]:
                tem_nr_chave = False
            else:
                raise AssertionError(f"cabecalho inesperado em {txt_path.name} ({len(header)} colunas)")

            batch = []
            n_mes = 0
            for row in reader:
                if tem_nr_chave:
                    assert len(row) == n_data_cols, f"linha com {len(row)} campos, esperado {n_data_cols} em {txt_path.name}"
                    batch.append(row + [ano_mes_arquivo])
                else:
                    assert len(row) == n_data_cols_sem_chave, f"linha com {len(row)} campos, esperado {n_data_cols_sem_chave} em {txt_path.name}"
                    batch.append(row + [None, ano_mes_arquivo])
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
    print(f"Total de linhas lidas dos arquivos: {total_lidas:,}")
    print(f"Total de linhas no banco apos carga:   {total_no_banco:,}")
    print(f"Tempo total: {dt:.1f}s")
    print(f"Banco em: {DB_PATH}")

    conn.close()

if __name__ == "__main__":
    main()
