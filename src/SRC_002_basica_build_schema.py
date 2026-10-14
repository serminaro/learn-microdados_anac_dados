#!/usr/bin/env python3
"""Gera o DDL (sql/ingestao_sqlite/DDL_001_basica_create_table.sql) a partir do cabecalho validado.
Tabela 'raw': todas as colunas como TEXT, fieis ao arquivo original (padrao raw->typed).
Chave: id_basica (verificado sem duplicatas na validacao). Coluna extra: nr_ano_mes_arquivo (proveniencia).
DDL escrito em SQL ANSI-compativel (tipos padrao), para servir de base tambem a um CREATE TABLE no Snowflake.
"""
import json
from pathlib import Path

# Raiz do repositorio, resolvida a partir deste arquivo: o pipeline roda
# de qualquer diretorio e em qualquer sistema operacional (ver DEC-011).
REPO_ROOT = Path(__file__).resolve().parents[1]

REPORT = REPO_ROOT / "data" / "anac" / "basica" / "_validation_report.json"
SQL_OUT = REPO_ROOT / "sql" / "ingestao_sqlite" / "DDL_001_basica_create_table.sql"

with open(REPORT, encoding="utf-8") as f:
    report = json.load(f)

header = report["cabecalho_referencia"]

cols_sql = []
for col in header:
    if col == "id_basica":
        cols_sql.append(f'    "{col}" TEXT NOT NULL')
    else:
        cols_sql.append(f'    "{col}" TEXT')

ddl = "-- Gerado por src/SRC_002_basica_build_schema.py a partir do cabecalho real dos 30 arquivos da basica (2024-01 a 2026-06)\n"
ddl += "-- Camada RAW: todas as colunas como TEXT, fieis ao arquivo de origem (Latin-1 -> UTF-8 na carga).\n"
ddl += "-- Tipagem/limpeza fica para uma camada seguinte (view ou tabela derivada), nao aqui.\n"
ddl += "-- DDL em SQL ANSI-compativel: mesma estrutura serve de base para CREATE TABLE no Snowflake.\n\n"
ddl += "CREATE TABLE IF NOT EXISTS basica_raw (\n"
ddl += ",\n".join(cols_sql)
ddl += ",\n    nr_ano_mes_arquivo TEXT NOT NULL,\n"
ddl += '    PRIMARY KEY ("id_basica")\n'
ddl += ");\n\n"
ddl += "CREATE INDEX IF NOT EXISTS idx_basica_raw_empresa ON basica_raw (id_empresa);\n"
ddl += "CREATE INDEX IF NOT EXISTS idx_basica_raw_ano_mes_ref ON basica_raw (nr_ano_referencia, nr_mes_referencia);\n"
ddl += "CREATE INDEX IF NOT EXISTS idx_basica_raw_arquivo ON basica_raw (nr_ano_mes_arquivo);\n"

SQL_OUT.write_text(ddl, encoding="utf-8")
print(f"DDL escrito em {SQL_OUT}")
print(f"{len(header)} colunas + nr_ano_mes_arquivo")
