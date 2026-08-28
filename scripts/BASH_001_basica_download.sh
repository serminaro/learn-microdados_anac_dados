#!/usr/bin/env bash
# Baixa os zips da tabela "basica" (microdados ANAC) para 2010-01 ate o mes
# corrente (DEC-002: corte historico em 2010, nao 2000).
# Trata a excecao de nome do arquivo mais recente (basica202606.zip, sem hifen)
# -- se a mesma excecao (sem hifen) se repetir em meses futuros, precisa virar
# deteccao real (tentar as duas formas), nao suposicao; ver nota em
# docs/plano_expansao_multidataset.md sobre validacao de schema ao longo do tempo.
set -euo pipefail

UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
BASE="https://www.gov.br/anac/pt-br/assuntos/regulados/empresas-aereas/Instrucoes-para-a-elaboracao-e-apresentacao-das-demonstracoes-contabeis/envio-de-informacoes/basica"
DEST="/home/bruno/Projetos/learn-microdados_anac_dados/data/anac/basica"

ANO_FIM=$(date +%Y)
MES_FIM=$(date +%m)

mkdir -p "$DEST"
LOG="$DEST/_download_log.csv"
echo "ano,mes,url,arquivo,http_status,bytes" > "$LOG"

for ano in $(seq 2010 "$ANO_FIM"); do
  for mes in 01 02 03 04 05 06 07 08 09 10 11 12; do
    if [ "$ano" = "$ANO_FIM" ] && [ "$mes" -gt "$((10#$MES_FIM))" ]; then
      continue
    fi
    # excecao conhecida: 2026-06 nao tem hifen no nome do arquivo
    if [ "$ano" = "2026" ] && [ "$mes" = "06" ]; then
      fname="basica202606.zip"
    else
      fname="basica${ano}-${mes}.zip"
    fi
    url="${BASE}/${ano}/${fname}"
    out="${DEST}/${fname}"

    if [ -f "$out" ] && [ -s "$out" ]; then
      echo "SKIP (ja existe): $fname"
      continue
    fi

    status=$(curl -s -A "$UA" -L "$url" -o "$out" -w "%{http_code}")
    bytes=$(stat -c%s "$out" 2>/dev/null || echo 0)
    echo "$ano,$mes,$url,$fname,$status,$bytes" >> "$LOG"

    if [ "$status" != "200" ] || [ "$bytes" -lt 1000 ]; then
      echo "FALHOU: $fname (status=$status bytes=$bytes)"
      rm -f "$out"
    else
      echo "OK: $fname ($bytes bytes)"
    fi
  done
done

echo ""
echo "=== Resumo ==="
echo "Arquivos baixados: $(ls "$DEST"/*.zip 2>/dev/null | wc -l)"
