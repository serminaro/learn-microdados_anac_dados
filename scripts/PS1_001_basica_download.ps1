<#
Baixa os zips da tabela "basica" (microdados ANAC) para 2010-01 ate o mes
corrente (DEC-002: corte historico em 2010, nao 2000).

Equivalente PowerShell de BASH_001_basica_download.sh (DEC-011): mesma fonte,
mesmo criterio de nome, mesmo log, mesma idempotencia. Os dois scripts sao
pareados pelo numero -- se um mudar de regra, o outro muda junto, ou divergem
em silencio.

Trata a excecao de nome do arquivo mais recente (basica202606.zip, sem hifen)
-- se a mesma excecao (sem hifen) se repetir em meses futuros, precisa virar
deteccao real (tentar as duas formas), nao suposicao.

Roda com: powershell -ExecutionPolicy Bypass -File scripts\PS1_001_basica_download.ps1
#>
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"  # sem a barra de progresso, ~10x mais rapido

$UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
$BASE = "https://www.gov.br/anac/pt-br/assuntos/regulados/empresas-aereas/Instrucoes-para-a-elaboracao-e-apresentacao-das-demonstracoes-contabeis/envio-de-informacoes/basica"

# Raiz do repositorio, derivada da localizacao deste script: roda de
# qualquer diretorio, sem caminho de maquina cravado (ver DEC-011).
$REPO_ROOT = Split-Path -Parent $PSScriptRoot
$DEST = Join-Path $REPO_ROOT "data\anac\basica"

$ANO_FIM = [int](Get-Date -Format "yyyy")
$MES_FIM = [int](Get-Date -Format "MM")

New-Item -ItemType Directory -Force -Path $DEST | Out-Null
$LOG = Join-Path $DEST "_download_log.csv"
"ano,mes,url,arquivo,http_status,bytes" | Set-Content -Path $LOG -Encoding UTF8

foreach ($ano in 2010..$ANO_FIM) {
    foreach ($mes in 1..12) {
        if ($ano -eq $ANO_FIM -and $mes -gt $MES_FIM) { continue }
        $mesPad = "{0:D2}" -f $mes

        # excecao conhecida: 2026-06 nao tem hifen no nome do arquivo
        if ($ano -eq 2026 -and $mes -eq 6) {
            $fname = "basica202606.zip"
        } else {
            $fname = "basica$ano-$mesPad.zip"
        }
        $url = "$BASE/$ano/$fname"
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
        "$ano,$mesPad,$url,$fname,$status,$bytes" | Add-Content -Path $LOG -Encoding UTF8

        if ($status -ne 200 -or $bytes -lt 1000) {
            Write-Host "FALHOU: $fname (status=$status bytes=$bytes)"
            Remove-Item $out -Force -ErrorAction SilentlyContinue
        } else {
            Write-Host "OK: $fname ($bytes bytes)"
        }
    }
}

Write-Host ""
Write-Host "=== Resumo ==="
$total = (Get-ChildItem -Path $DEST -Filter *.zip -ErrorAction SilentlyContinue).Count
Write-Host "Arquivos baixados: $total"
