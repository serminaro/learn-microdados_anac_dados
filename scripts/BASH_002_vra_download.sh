#!/usr/bin/env bash
# Baixa os csv da VRA (Voo Regular Ativo) para 2010-01 ate o mes corrente.
# Cadencia mensal. Nao hardcoda nome de pasta de mes em portugues (varia --
# ex.: 2024 tem "03 - Marco" em SIROS mas "03 - Marco" com cedilha em VRA,
# confirmado por teste direto em 2026-08-26): le a listagem HTML da pasta do
# ano e extrai o href real de cada mes.
set -euo pipefail

UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
BASE="https://sistemas.anac.gov.br/dadosabertos/Voos%20e%20opera%C3%A7%C3%B5es%20a%C3%A9reas/Voo%20Regular%20Ativo%20(VRA)"
# Raiz do repositorio, derivada da localizacao deste script: roda de
# qualquer diretorio, sem caminho de maquina cravado (ver DEC-011).
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="$REPO_ROOT/data/anac/vra"

ANO_FIM=$(date +%Y)
MES_FIM=$((10#$(date +%m)))

mkdir -p "$DEST"
LOG="$DEST/_download_log.csv"
echo "ano,mes,url,arquivo,http_status,bytes" > "$LOG"

total_ok=0

for ano in $(seq 2010 "$ANO_FIM"); do
  listing=$(curl -s -A "$UA" "${BASE}/${ano}/") || listing=""
  mapfile -t meses_hrefs < <(echo "$listing" | grep -oE 'href="[0-9]{2}%20-%20[^"]+/"' | sed -e 's/^href="//' -e 's/"$//' | sort -u)

  if [ "${#meses_hrefs[@]}" -eq 0 ]; then
    echo "AVISO: nenhuma pasta de mes encontrada para $ano (pulando ano)"
    continue
  fi

  for href in "${meses_hrefs[@]}"; do
    mes_padded="${href:0:2}"
    mes_num=$((10#$mes_padded))
    if [ "$ano" = "$ANO_FIM" ] && [ "$mes_num" -gt "$MES_FIM" ]; then
      continue
    fi

    fname="VRA_${ano}${mes_num}.csv"
    url="${BASE}/${ano}/${href}${fname}"
    out="${DEST}/${fname}"

    if [ -f "$out" ] && [ -s "$out" ]; then
      echo "SKIP (ja existe): $fname"
      continue
    fi

    status=$(curl -s -A "$UA" -L "$url" -o "$out" -w "%{http_code}")
    bytes=$(stat -c%s "$out" 2>/dev/null || echo 0)
    echo "$ano,$mes_padded,$url,$fname,$status,$bytes" >> "$LOG"

    if [ "$status" != "200" ] || [ "$bytes" -lt 200 ]; then
      echo "FALHOU: $fname (status=$status bytes=$bytes)"
      rm -f "$out"
    else
      echo "OK: $fname ($bytes bytes)"
      total_ok=$((total_ok + 1))
    fi
  done
done

echo ""
echo "=== Resumo ==="
echo "Arquivos baixados nesta execucao: $total_ok"
echo "Total em disco: $(ls "$DEST"/*.csv 2>/dev/null | wc -l)"
