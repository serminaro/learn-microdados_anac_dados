#!/usr/bin/env python3
"""Carrega arquivos de SIROS (data/anac/siros/registros_*.csv) no SQLite
(db/anac_siros.sqlite), compondo incrementalmente a mesma tabela siros_raw
a partir de dois formatos de origem que a ANAC publicou ao longo do tempo
(CSV ate ~2024-09, JSON dai em diante -- ver achado abaixo). Idempotente
por arquivo: pula qualquer dia (dt_arquivo) ja carregado, nao importa o
formato de origem. Uma linha do arquivo = uma linha na tabela, sem
expandir autorizacao em voo-por-data (DEC-008 Sec.2.d, fora de escopo).

Achado 1 (2026-08-31, teste diario de um mes): cada arquivo diario e um
snapshot completo das autorizacoes ativas, nao um incremento -- a mesma
autorizacao (nr_siros) se repete em todo dia em que esta vigente (media de
2,7x/mes no teste). Carga diaria de todo o historico projetava ~37 GB /
~3h. Decisao do autor: amostragem semanal (1 arquivo por semana, sempre de
segunda-feira) como politica padrao de "raw" para este dataset -- reduz
~7x o volume sem inventar dado, so reduz a frequencia de snapshot mantida
(SPEC-010 v2). Uso --diario para forcar fidelidade diaria completa.

Achado 2 (2026-08-31, carga completa): a ANAC muda o formato de CSV para
JSON a partir de meados de 2024, com transicao irregular (2024-06-17 ja e
JSON, 2024-06-24 volta a ser CSV) ate se fixar em JSON a partir de
2024-09-16. Mesmos 28 campos, chaves em ingles sem acento em vez do
cabecalho em portugues do CSV -- mapeados para as mesmas colunas de
siros_raw (SIROS_JSON_KEYS abaixo), sem mudanca de schema.

Uso:
    SRC_003_siros_load_sqlite.py                    # tudo, semanal (segundas)
    SRC_003_siros_load_sqlite.py --de 2022-08-01 --ate 2022-08-31
    SRC_003_siros_load_sqlite.py --diario            # fidelidade diaria completa
"""
import argparse
import csv
import json
import sqlite3
import time
from datetime import date
from pathlib import Path

# Raiz do repositorio, resolvida a partir deste arquivo: o pipeline roda
# de qualquer diretorio e em qualquer sistema operacional (ver DEC-011).
REPO_ROOT = Path(__file__).resolve().parents[2]

SRC_DIR = REPO_ROOT / "data" / "anac" / "siros"
DB_PATH = REPO_ROOT / "db" / "anac_siros.sqlite"
DDL_PATH = REPO_ROOT / "sql" / "ingestao_sqlite" / "DDL_003_siros_create_table.sql"
BATCH = 5000

# Ordem = ordem das 28 colunas de dado em siros_raw (DDL_003), da esquerda
# para a direita. Mapeia a chave do JSON (formato novo) para essa posicao.
SIROS_JSON_KEYS = [
    "Cod_Empresa", "Empresa", "N_Voo", "Equip",
    "Seg", "Ter", "Qua", "Qui", "Sex", "Sab", "Dom",
    "Quant_Assentos", "N_SIROS", "Situacao_SIROS", "Data_Registro",
    "Inicio_Operacao", "Fim_Operacao", "Natureza_Operacao", "N_Etapa",
    "Cod_Origem", "Arpt_Origem", "Cod_Destino", "Arpt_Destino",
    "Horario_Partida", "Horario_Chegada",
    "Tipo_Servico", "Objeto_Transporte", "Codeshare",
]


def day_files(de=None, ate=None, diario=False):
    out = []
    for f in sorted(SRC_DIR.glob("registros_*.csv")):
        dt_arquivo = f.stem.replace("registros_", "")
        if de and dt_arquivo < de:
            continue
        if ate and dt_arquivo > ate:
            continue
        if not diario:
            y, m, d = (int(x) for x in dt_arquivo.split("-"))
            if date(y, m, d).weekday() != 0:  # 0 = segunda-feira
                continue
        out.append((dt_arquivo, f))
    return out


def parse_csv(f, n_data_cols):
    """f ja posicionado apos a linha de metadado. Retorna lista de linhas
    (sem dt_arquivo) ou levanta ValueError com o motivo."""
    reader = csv.reader(f, delimiter=";", quotechar='"')
    try:
        header = next(reader)
    except StopIteration:
        raise ValueError("sem linha de cabecalho apos o metadado")
    if len(header) != n_data_cols:
        raise ValueError(f"cabecalho com {len(header)} colunas, esperado {n_data_cols}")
    rows = [row for row in reader if len(row) == n_data_cols]
    return rows


def parse_json(path):
    """Le o arquivo inteiro (formato novo da ANAC) e devolve lista de
    linhas na mesma ordem de SIROS_JSON_KEYS."""
    with open(path, encoding="utf-8-sig") as f:
        registros = json.load(f)
    return [[r.get(k, "") for k in SIROS_JSON_KEYS] for r in registros]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--de", help="data inicial AAAA-MM-DD (inclusive)")
    ap.add_argument("--ate", help="data final AAAA-MM-DD (inclusive)")
    ap.add_argument("--diario", action="store_true", help="carrega todo dia, nao so segundas")
    args = ap.parse_args()

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(DDL_PATH.read_text(encoding="utf-8"))
    conn.commit()

    cur = conn.cursor()
    cur.execute("PRAGMA table_info(siros_raw)")
    cols = [r[1] for r in cur.fetchall()]
    n_data_cols = len(cols) - 1  # todas menos dt_arquivo
    placeholders = ",".join(["?"] * len(cols))
    insert_sql = f"INSERT INTO siros_raw ({','.join(cols)}) VALUES ({placeholders})"

    t0 = time.time()
    total_lidas = 0
    total_pulados = 0
    total_csv = 0
    total_json = 0
    falhas = []  # (dt_arquivo, motivo)
    arquivos = day_files(args.de, args.ate, args.diario)

    for dt_arquivo, path in arquivos:
        cur.execute("SELECT COUNT(*) FROM siros_raw WHERE dt_arquivo = ?", (dt_arquivo,))
        if cur.fetchone()[0] > 0:
            total_pulados += 1
            continue

        if path.stat().st_size == 0:
            falhas.append((dt_arquivo, "arquivo vazio (0 bytes)"))
            continue

        try:
            with open(path, encoding="utf-8-sig", newline="") as f:
                primeira_linha = f.readline()
                corpo = primeira_linha.lstrip()
                if corpo.startswith("[") or corpo.startswith("{"):
                    rows = parse_json(path)
                    fonte = "json"
                elif primeira_linha.startswith("Atualizado em"):
                    rows = parse_csv(f, n_data_cols)
                    fonte = "csv"
                else:
                    raise ValueError("formato inesperado (nem CSV antigo, nem JSON)")
        except (ValueError, json.JSONDecodeError) as e:
            falhas.append((dt_arquivo, str(e)))
            continue

        batch = []
        for row in rows:
            batch.append(list(row) + [dt_arquivo])
            if len(batch) >= BATCH:
                cur.executemany(insert_sql, batch)
                batch = []
        if batch:
            cur.executemany(insert_sql, batch)

        conn.commit()
        total_lidas += len(rows)
        if fonte == "csv":
            total_csv += 1
        else:
            total_json += 1

    cur.execute("SELECT COUNT(*) FROM siros_raw")
    total_no_banco = cur.fetchone()[0]

    dt = time.time() - t0
    print(f"Arquivos no range: {len(arquivos)}")
    print(f"Arquivos pulados (ja carregados): {total_pulados}")
    print(f"Arquivos carregados via CSV: {total_csv}")
    print(f"Arquivos carregados via JSON: {total_json}")
    print(f"Arquivos com falha: {len(falhas)}")
    for dt_arquivo, motivo in falhas:
        print(f"  {dt_arquivo}: {motivo}")
    print(f"Total de linhas lidas nesta execucao: {total_lidas:,}")
    print(f"Total de linhas no banco apos carga:  {total_no_banco:,}")
    print(f"Tempo total: {dt:.1f}s")
    print(f"Banco em: {DB_PATH}")

    conn.close()


if __name__ == "__main__":
    main()
