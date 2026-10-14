#!/usr/bin/env python3
"""Extrai os zips da basica e valida consistencia entre os 30 meses.
Nao carrega no banco ainda -- so extrai e produz um relatorio (data/anac/basica/_validation_report.json).
"""
import csv
import json
import zipfile
from pathlib import Path
from collections import defaultdict

# Raiz do repositorio, resolvida a partir deste arquivo: o pipeline roda
# de qualquer diretorio e em qualquer sistema operacional (ver DEC-011).
REPO_ROOT = Path(__file__).resolve().parents[1]

DEST = REPO_ROOT / "data" / "anac" / "basica"

def month_files():
    out = []
    for ano in (2024, 2025, 2026):
        for mes in range(1, 13):
            if ano == 2026 and mes > 6:
                continue
            if ano == 2026 and mes == 6:
                fname = "basica202606.zip"
            else:
                fname = f"basica{ano}-{mes:02d}.zip"
            out.append((ano, mes, DEST / fname))
    return out

def extract_zip(zip_path: Path):
    if not zip_path.exists():
        return None, f"zip nao encontrado: {zip_path.name}"
    with zipfile.ZipFile(zip_path) as z:
        names = z.namelist()
        txts = [n for n in names if n.lower().endswith(".txt")]
        if len(txts) != 1:
            return None, f"zip {zip_path.name} tem {len(txts)} arquivos .txt (esperado 1): {names}"
        txt_name = txts[0]
        out_path = zip_path.parent / txt_name
        if not out_path.exists():
            z.extract(txt_name, path=zip_path.parent)
        return out_path, None

def read_rows(txt_path: Path):
    with open(txt_path, encoding="latin-1", newline="") as f:
        reader = csv.reader(f, delimiter=";", quotechar='"')
        header = next(reader)
        rows = list(reader)
    return header, rows

def main():
    files = month_files()
    report = {"meses": {}, "erros_globais": []}
    canonical_header = None
    seen_ids_global = {}  # id_basica -> primeiro arquivo onde apareceu
    dup_across_files = []

    for ano, mes, zip_path in files:
        key = f"{ano}-{mes:02d}"
        entry = {"arquivo_zip": zip_path.name, "ok": True, "erros": [], "avisos": []}

        txt_path, err = extract_zip(zip_path)
        if err:
            entry["ok"] = False
            entry["erros"].append(err)
            report["meses"][key] = entry
            continue

        try:
            header, rows = read_rows(txt_path)
        except UnicodeDecodeError as e:
            entry["ok"] = False
            entry["erros"].append(f"falha de encoding (latin-1): {e}")
            report["meses"][key] = entry
            continue

        entry["n_linhas"] = len(rows)
        entry["n_colunas"] = len(header)

        if canonical_header is None:
            canonical_header = header
            entry["avisos"].append("definido como referencia de cabecalho")
        elif header != canonical_header:
            entry["ok"] = False
            if len(header) != len(canonical_header):
                entry["erros"].append(
                    f"numero de colunas diferente: {len(header)} vs referencia {len(canonical_header)}"
                )
            diffs = [
                (i, a, b) for i, (a, b) in enumerate(zip(header, canonical_header)) if a != b
            ]
            entry["erros"].append(f"cabecalho diverge da referencia em {len(diffs)} posicoes: {diffs[:5]}")

        if entry["n_linhas"] == 0:
            entry["ok"] = False
            entry["erros"].append("arquivo sem linhas de dados")
            report["meses"][key] = entry
            continue

        idx = {name: i for i, name in enumerate(header)}
        need = ["id_basica", "nr_ano_referencia", "nr_mes_referencia"]
        if not all(n in idx for n in need):
            entry["ok"] = False
            entry["erros"].append(f"colunas essenciais ausentes: {[n for n in need if n not in idx]}")
            report["meses"][key] = entry
            continue

        i_id = idx["id_basica"]
        i_ano_ref = idx["nr_ano_referencia"]
        i_mes_ref = idx["nr_mes_referencia"]

        ids_no_arquivo = set()
        dup_no_arquivo = 0
        ano_ref_mismatch = 0
        mes_ref_mismatch = 0

        for r in rows:
            rid = r[i_id]
            if rid in ids_no_arquivo:
                dup_no_arquivo += 1
            else:
                ids_no_arquivo.add(rid)
            if rid in seen_ids_global:
                dup_across_files.append((rid, seen_ids_global[rid], key))
            else:
                seen_ids_global[rid] = key

            if r[i_ano_ref] != str(ano):
                ano_ref_mismatch += 1
            if r[i_mes_ref] != str(mes):
                mes_ref_mismatch += 1

        if dup_no_arquivo:
            entry["ok"] = False
            entry["erros"].append(f"{dup_no_arquivo} id_basica duplicados dentro do proprio arquivo")

        if ano_ref_mismatch:
            pct = 100 * ano_ref_mismatch / len(rows)
            entry["avisos"].append(f"{ano_ref_mismatch} linhas ({pct:.2f}%) com nr_ano_referencia != {ano}")
        if mes_ref_mismatch:
            pct = 100 * mes_ref_mismatch / len(rows)
            entry["avisos"].append(f"{mes_ref_mismatch} linhas ({pct:.2f}%) com nr_mes_referencia != {mes}")

        report["meses"][key] = entry

    if dup_across_files:
        report["erros_globais"].append(
            {
                "tipo": "id_basica duplicado entre arquivos diferentes",
                "n_ocorrencias": len(dup_across_files),
                "exemplos": dup_across_files[:10],
            }
        )

    report["cabecalho_referencia"] = canonical_header
    report["total_meses_ok"] = sum(1 for m in report["meses"].values() if m.get("ok"))
    report["total_meses_esperados"] = len(files)
    report["total_linhas"] = sum(m.get("n_linhas", 0) for m in report["meses"].values())

    out_path = DEST / "_validation_report.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"Meses OK: {report['total_meses_ok']} / {report['total_meses_esperados']}")
    print(f"Total de linhas (soma dos meses lidos): {report['total_linhas']:,}")
    print(f"Duplicados de id_basica entre arquivos diferentes: {len(dup_across_files)}")
    print(f"Relatorio completo em: {out_path}")

    for key, entry in report["meses"].items():
        if not entry.get("ok", False):
            print(f"  [FALHA] {key}: {entry.get('erros')}")
        elif entry.get("avisos"):
            avisos_relevantes = [a for a in entry["avisos"] if "referencia" in a]
            if avisos_relevantes:
                print(f"  [AVISO] {key}: {avisos_relevantes}")

if __name__ == "__main__":
    main()
