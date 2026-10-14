<#
Baixa os csv da VRA (Voo Regular Ativo) para 2010-01 ate o mes corrente.
Cadencia mensal.

Equivalente PowerShell de BASH_002_vra_download.sh (DEC-011): mesma fonte,
mesmo criterio de nome, mesmo log, mesma idempotencia. Os dois scripts sao
pareados pelo numero -- se um mudar de regra, o outro muda junto, ou divergem
em silencio.

Nao hardcoda nome de pasta de mes em portugues (varia -- ex.: 2024 tem
"03 - Marco" em SIROS mas "03 - Marco" com cedilha em VRA, confirmado por
teste direto em 2026-08-26): le a listagem HTML da pasta do ano e extrai o
href real de cada mes.

Roda com: powershell -ExecutionPolicy Bypass -File scripts\PS1_002_vra_download.ps1
#>
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
$BASE = "https://sistemas.anac.gov.br/dadosabertos/Voos%20e%20opera%C3%A7%C3%B5es%20a%C3%A9reas/Voo%20Regular%20Ativo%20(VRA)"

# Raiz do repositorio, derivada da localizacao deste script: roda de
# qualquer diretorio, sem caminho de maquina cravado (ver DEC-011).
$REPO_ROOT = Split-Path -Parent $PSScriptRoot
$DEST = Join-Path $REPO_ROOT "data\anac\vra"

$ANO_FIM = [int](Get-Date -Format "yyyy")
$MES_FIM = [int](Get-Date -Format "MM")

New-Item -ItemType Directory -Force -Path $DEST | Out-Null
$LOG = Join-Path $DEST "_download_log.csv"
"ano,mes,url,arquivo,http_status,bytes" | Set-Content -Path $LOG -Encoding UTF8

$total_ok = 0

foreach ($ano in 2010..$ANO_FIM) {
    $listing = ""
    try {
        $listing = (Invoke-WebRequest -Uri "$BASE/$ano/" -UserAgent $UA `
                                      -UseBasicParsing -ErrorAction Stop).Content
    } catch { $listing = "" }

    # href="NN%20-%20<nome do mes>/"  -- mesmo padrao do script bash
    $meses_hrefs = [regex]::Matches($listing, 'href="([0-9]{2}%20-%20[^"]+/)"') |
                   ForEach-Object { $_.Groups[1].Value } |
                   Sort-Object -Unique

    if ($meses_hrefs.Count -eq 0) {
        Write-Host "AVISO: nenhuma pasta de mes encontrada para $ano (pulando ano)"
        continue
    }

    foreach ($href in $meses_hrefs) {
        $mes_padded = $href.Substring(0, 2)
        $mes_num = [int]$mes_padded
        if ($ano -eq $ANO_FIM -and $mes_num -gt $MES_FIM) { continue }

        # o nome do arquivo usa o mes SEM zero a esquerda (VRA_20241.csv)
        $fname = "VRA_$ano$mes_num.csv"
        $url = "$BASE/$ano/$href$fname"
        $out = Join-Path $DEST $fname

        if ((Test-Path $out) -and ((Get-Item $out).Length -gt 0)) {
            Write-Host "SKIP (ja existe): $fname"
            continue
        }

        $status = 0
        try {
            $r = Invoke-WebRequest -Uri $url -OutFile $out -UserAgent $UA `
                                   -UseBasicParsing -PassThru -ErrorAction Stop
            $status = [int]$r.StatusCode
        } catch {
            if ($_.Exception.Response) { $status = [int]$_.Exception.Response.StatusCode }
        }
        $bytes = if (Test-Path $out) { (Get-Item $out).Length } else { 0 }
        "$ano,$mes_padded,$url,$fname,$status,$bytes" | Add-Content -Path $LOG -Encoding UTF8

        if ($status -ne 200 -or $bytes -lt 200) {
            Write-Host "FALHOU: $fname (status=$status bytes=$bytes)"
            Remove-Item $out -Force -ErrorAction SilentlyContinue
        } else {
            Write-Host "OK: $fname ($bytes bytes)"
            $total_ok++
        }
    }
}

Write-Host ""
Write-Host "=== Resumo ==="
Write-Host "Arquivos baixados nesta execucao: $total_ok"
$total = (Get-ChildItem -Path $DEST -Filter *.csv -ErrorAction SilentlyContinue).Count
Write-Host "Total em disco: $total"
