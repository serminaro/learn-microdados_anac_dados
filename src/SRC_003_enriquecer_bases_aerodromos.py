#!/usr/bin/env python3
"""Enriquece data/Bases_dos_microdados_2015_2026.txt (aerodromos que aparecem
como origem/destino nos microdados ANAC desde 2015) com latitude, longitude,
fuso horario IANA, offset UTC padrao (sem horario de verao), e dois flags:
se o local observa horario de verao atualmente, e se ja observou alguma vez
(varredura historica 1970-presente).

Fontes, nenhum dado inventado:
- Coordenadas: OurAirports (dado aberto, https://ourairports.com/data/),
  ~86 mil aerodromos mundiais, baixado em tempo de execucao.
- Fuso/DST: tzdata (IANA), via timezonefinder (lat/lon -> fuso) e zoneinfo
  (Python stdlib) para os offsets e a varredura de DST.

Alguns codigos ICAO da base ANAC correspondem a aeroportos fechados ou
renomeados, sem entrada estruturada (ident/icao_code/gps_code) no
OurAirports -- so aparecem no campo de texto livre "keywords". Esses casos
sao resolvidos por overrides manuais (MANUAL_OVERRIDES abaixo), cada um com
a fonte da coordenada documentada, nunca por adivinhacao a partir do nome.
Requer rede (baixa o OurAirports a cada execucao).
"""
import csv
import datetime as dt
from pathlib import Path
from urllib.request import urlretrieve

from timezonefinder import TimezoneFinder
from zoneinfo import ZoneInfo

# Raiz do repositorio, resolvida a partir deste arquivo: o pipeline roda
# de qualquer diretorio e em qualquer sistema operacional (ver DEC-011).
REPO_ROOT = Path(__file__).resolve().parents[1]

BASES_TXT = REPO_ROOT / "data" / "Bases_dos_microdados_2015_2026.txt"
AIRPORTS_URL = "https://davidmegginson.github.io/ourairports-data/airports.csv"
AIRPORTS_CSV = REPO_ROOT / "data" / "_airports_ourairports_cache.csv"
OUT_CSV = REPO_ROOT / "data" / "aerodromos_enriquecido.csv"
OUT_UNMATCHED = REPO_ROOT / "data" / "aerodromos_sem_match.csv"

# Valores que a fonte ANAC grava no campo BASE_IATA mas que nao sao codigo:
# "..." e "N/I" sao as duas formas de "nao informado" observadas em
# Bases_dos_microdados_2015_2026.txt (36 e 4 linhas, 2026-09-04). Aqui a
# lista so evita match falso por IATA -- hoje nenhuma das duas existe como
# iata_code no OurAirports, entao o efeito e' nulo, mas a premissa e'
# fragil e a lista fica explicita. Quem transforma
# a sentinela em NULL e' SRC_004 (limpar/SENTINELAS): este script preserva
# a fonte como ela e'.
SENTINELAS_IATA = {"", "...", "N/I"}

# codigo ANAC (BASE_ICAO): (lat, lon, nome, fonte da coordenada)
MANUAL_OVERRIDES = {
    "SBQV": (-14.862567, -40.863186, "Pedro Otacilio Figueiredo Airport (Vitoria da Conquista, BA, fechado)", "OurAirports id 5963, keyword-match"),
    "FAJS": (-26.140081, 28.246801, "O.R. Tambo International Airport (Johannesburgo) -- FAJS renomeado p/ FAOR em 1994", "OurAirports id 31055, keyword-match"),
    "SEQU": (-0.136782, -78.490598, "Area do antigo Aeroporto Mariscal Sucre (Quito, fechado 2013)", "OurAirports id 6073 (heliport proximo), keyword-match -- CONFIANCA MENOR, coordenada aproximada"),
    "SBFE": (-12.200694, -38.906164, "Joao Durval Carneiro Airport (Feira de Santana, BA) -- ident atual SDIY", "OurAirports id 329, keyword-match"),
    "SBJC": (-1.415051, -48.459805, "Belem/Brigadeiro Protasio de Oliveira Airport (fechado)", "OurAirports id 5921, keyword-match"),
    "EGCN": (53.475287, -1.004267, "Doncaster Sheffield Airport (fechado 2022)", "OurAirports id 2401, keyword-match"),
    "SBRG": (-32.083065, -52.167184, "Rio Grande Regional / Gustavo Cramer Airport -- ident atual SJRG", "OurAirports id 44713, keyword-match"),
    "VDSR": (13.410676, 103.812074, "Siem Reap International Airport, Camboja (fechado)", "OurAirports id 26476, keyword-match"),
}


def carregar_ourairports():
    if not AIRPORTS_CSV.exists():
        print(f"Baixando {AIRPORTS_URL} ...")
        urlretrieve(AIRPORTS_URL, AIRPORTS_CSV)
    by_icao, by_iata = {}, {}
    with open(AIRPORTS_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            codes = {
                (row.get(field) or "").strip().upper()
                for field in ("ident", "icao_code", "gps_code")
            } - {""}
            iata = (row.get("iata_code") or "").strip().upper()
            try:
                lat, lon = float(row["latitude_deg"]), float(row["longitude_deg"])
            except (ValueError, KeyError):
                continue
            rec = {"lat": lat, "lon": lon, "name": row.get("name"),
                   "municipality": row.get("municipality"),
                   "iso_country": row.get("iso_country"), "type": row.get("type")}
            for c in codes:
                by_icao.setdefault(c, rec)
            if iata:
                by_iata.setdefault(iata, rec)
    return by_icao, by_iata


def match(row, by_icao, by_iata):
    icao = (row.get("BASE_ICAO") or "").strip().upper()
    iata = (row.get("BASE_IATA") or "").strip().upper()
    if icao in by_icao:
        return by_icao[icao], "ICAO"
    if iata in by_iata and iata not in SENTINELAS_IATA:
        return by_iata[iata], "IATA"
    if icao in MANUAL_OVERRIDES:
        lat, lon, nome, fonte = MANUAL_OVERRIDES[icao]
        return {"lat": lat, "lon": lon, "name": nome, "municipality": None,
                "iso_country": None, "type": fonte}, "MANUAL_KEYWORD"
    return None, None


def calcular_tz_info(tzname, hoje):
    zi = ZoneInfo(tzname)
    year = hoje.year
    offsets_no_dst, offsets_all = [], []
    dst_este_ano = False
    d = dt.date(year, 1, 1)
    while d.year == year:
        momento = dt.datetime(d.year, d.month, d.day, 12, tzinfo=zi)
        off, dst = momento.utcoffset(), momento.dst()
        offsets_all.append(off)
        if dst == dt.timedelta(0):
            offsets_no_dst.append(off)
        else:
            dst_este_ano = True
        d += dt.timedelta(days=1)
    padrao = max(set(offsets_no_dst or offsets_all), key=(offsets_no_dst or offsets_all).count)

    ja_teve_dst = False
    d = dt.date(1970, 1, 1)
    while d <= hoje:
        momento = dt.datetime(d.year, d.month, d.day, 12, tzinfo=zi)
        if momento.dst() and momento.dst() != dt.timedelta(0):
            ja_teve_dst = True
            break
        d += dt.timedelta(days=1)

    return padrao.total_seconds() / 3600, dst_este_ano, ja_teve_dst


def main():
    by_icao, by_iata = carregar_ourairports()
    print(f"OurAirports: {len(by_icao)} ICAO, {len(by_iata)} IATA")

    with open(BASES_TXT, encoding="utf-8") as f:
        bases = list(csv.DictReader(f))
    print(f"Bases lidas: {len(bases)}")

    tf = TimezoneFinder()
    for row in bases:
        rec, method = match(row, by_icao, by_iata)
        row["_match"] = method or "SEM_MATCH"
        if rec is None:
            continue
        row["LATITUDE"] = rec["lat"]
        row["LONGITUDE"] = rec["lon"]
        row["NOME_OURAIRPORTS"] = rec["name"]
        row["MUNICIPIO_OURAIRPORTS"] = rec["municipality"]
        row["PAIS_ISO"] = rec["iso_country"]
        row["TIPO_OURAIRPORTS"] = rec["type"]
        row["TZ_IANA"] = tf.timezone_at(lat=rec["lat"], lng=rec["lon"])

    n_ok = sum(1 for r in bases if r["_match"] != "SEM_MATCH")
    print(f"Match: {n_ok} / sem match: {len(bases) - n_ok}")

    hoje = dt.date.today()
    tz_cache = {}
    for tzname in sorted({r.get("TZ_IANA") for r in bases if r.get("TZ_IANA")}):
        tz_cache[tzname] = calcular_tz_info(tzname, hoje)
    print(f"Timezones IANA distintos: {len(tz_cache)}")

    for row in bases:
        tzname = row.get("TZ_IANA")
        if tzname in tz_cache:
            padrao, dst_atual, ja_teve = tz_cache[tzname]
            row["UTC_OFFSET_PADRAO_H"] = padrao
            row["HORARIO_VERAO_ATUAL"] = dst_atual
            row["JA_TEVE_HORARIO_VERAO"] = ja_teve

    fieldnames = ["BASE_IATA", "BASE_ICAO", "QT_OCORRENCIAS", "_match",
                  "LATITUDE", "LONGITUDE", "TZ_IANA", "UTC_OFFSET_PADRAO_H",
                  "HORARIO_VERAO_ATUAL", "JA_TEVE_HORARIO_VERAO",
                  "NOME_OURAIRPORTS", "MUNICIPIO_OURAIRPORTS", "PAIS_ISO",
                  "TIPO_OURAIRPORTS"]
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in bases:
            w.writerow({k: row.get(k, "") for k in fieldnames})

    with open(OUT_UNMATCHED, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["BASE_IATA", "BASE_ICAO", "QT_OCORRENCIAS"])
        w.writeheader()
        for row in bases:
            if row["_match"] == "SEM_MATCH":
                w.writerow({k: row.get(k, "") for k in ["BASE_IATA", "BASE_ICAO", "QT_OCORRENCIAS"]})

    print(f"Gravado: {OUT_CSV}")
    print(f"Sem match: {OUT_UNMATCHED}")


if __name__ == "__main__":
    main()
