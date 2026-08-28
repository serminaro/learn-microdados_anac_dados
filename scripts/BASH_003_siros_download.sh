#!/usr/bin/env bash
# Baixa os csv do SIROS (Registro de servicos aereos) para 2019-11 ate o mes
# corrente. Cadencia DIARIA (nao mensal como Basica/VRA) -- volume ~30x maior
# por ano coberto (docs/plano_expansao_multidataset.md). A fonte nao publica
# lote anterior a 2019-11; nao forcar periodo anterior a isso.
#
# AVISO DE VOLUME: da ordem de 2.500+ arquivos (2019-11 ate hoje). Rode em
# background e acompanhe _download_log.csv -- nao foi disparado automaticamente
# na mesma rodada que criou este script (decisao do autor, 2026-08-26).
#
# NOTA (2026-08-27, achado empirico, teste HTTP direto): o portal usa DOIS
# formatos de pasta de mes para o SIROS, sem aviso -- "NN - MesNome/" a partir
# de 2024, so "MesNome/" (sem numero, sem zero a esquerda) em 2019-2023. VRA
# nao tem essa inconsistencia (sempre "NN - MesNome/"). Por isso o numero do
# mes e derivado do NOME (com fallback de acento via iconv), nao só lido do
# prefixo numerico, que pode nao existir.
set -euo pipefail

declare -A MES_NUM=(
  [janeiro]=01 [fevereiro]=02 [marco]=03 [abril]=04 [maio]=05 [junho]=06
  [julho]=07 [agosto]=08 [setembro]=09 [outubro]=10 [novembro]=11 [dezembro]=12
)

url_decode() {
  local data="${1//+/ }"
  printf '%b' "${data//%/\\x}"
}

mes_num_do_href() {
  # recebe o href decodificado (ex.: "01 - Janeiro/" ou "Janeiro/"), devolve NN
  local nome="${1%/}"
  nome="${nome#*-}"                 # remove prefixo "NN -" se existir; no-op se nao houver "-"
  nome="${nome// /}"
  nome="$(printf '%s' "$nome" | iconv -f utf8 -t ascii//TRANSLIT 2>/dev/null | tr '[:upper:]' '[:lower:]')"
  echo -n "${MES_NUM[$nome]:-}"
}

UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
BASE="https://sistemas.anac.gov.br/dadosabertos/Voos%20e%20opera%C3%A7%C3%B5es%20a%C3%A9reas/Registro%20de%20servi%C3%A7os%20a%C3%A9reos"
DEST="/home/bruno/Projetos/learn-microdados_anac_dados/data/anac/siros"

ANO_INICIO=2019
MES_INICIO_NO_ANO_INICIO=11

ANO_FIM=$(date +%Y)
MES_FIM=$((10#$(date +%m)))

mkdir -p "$DEST"
LOG="$DEST/_download_log.csv"
echo "ano,mes,dia,url,arquivo,http_status,bytes" > "$LOG"

total_ok=0

for ano in $(seq "$ANO_INICIO" "$ANO_FIM"); do
  listing=$(curl -s -A "$UA" "${BASE}/${ano}/") || listing=""
  mapfile -t meses_hrefs < <(echo "$listing" | grep -oE 'href="[^"]+/"' | sed -e 's/^href="//' -e 's/"$//' | grep -v '^\.\./$' | sort -u)

  if [ "${#meses_hrefs[@]}" -eq 0 ]; then
    echo "AVISO: nenhuma pasta de mes encontrada para $ano (pulando ano)"
    continue
  fi

  for href in "${meses_hrefs[@]}"; do
    mes_padded=$(mes_num_do_href "$(url_decode "$href")")
    if [ -z "$mes_padded" ]; then
      echo "AVISO: nao consegui mapear mes a partir de '$href' em $ano (pulando pasta)"
      continue
    fi
    mes_num=$((10#$mes_padded))

    if [ "$ano" = "$ANO_INICIO" ] && [ "$mes_num" -lt "$MES_INICIO_NO_ANO_INICIO" ]; then
      continue
    fi
    if [ "$ano" = "$ANO_FIM" ] && [ "$mes_num" -gt "$MES_FIM" ]; then
      continue
    fi

    dias_no_mes=$(date -d "${ano}-${mes_padded}-01 +1 month -1 day" +%d)

    for dia in $(seq -w 1 "$dias_no_mes"); do
      fname="registros_${ano}-${mes_padded}-${dia}.csv"
      url="${BASE}/${ano}/${href}${fname}"
      out="${DEST}/${fname}"

      if [ -f "$out" ] && [ -s "$out" ]; then
        continue
      fi

      status=$(curl -s -A "$UA" -L "$url" -o "$out" -w "%{http_code}")
      bytes=$(stat -c%s "$out" 2>/dev/null || echo 0)
      echo "$ano,$mes_padded,$dia,$url,$fname,$status,$bytes" >> "$LOG"

      if [ "$status" != "200" ] || [ "$bytes" -lt 100 ]; then
        rm -f "$out"
      else
        total_ok=$((total_ok + 1))
      fi
    done
    echo "Mes ${ano}-${mes_padded} processado (acumulado ok: $total_ok)"
  done
done

echo ""
echo "=== Resumo ==="
echo "Arquivos baixados nesta execucao: $total_ok"
echo "Total em disco: $(ls "$DEST"/*.csv 2>/dev/null | wc -l)"
