<#
Baixa os csv do SIROS (Registro de servicos aereos) para 2019-11 ate o mes
corrente. Cadencia DIARIA (nao mensal como Basica/VRA) -- volume ~30x maior
por ano coberto. A fonte nao publica lote anterior a 2019-11; nao forcar
periodo anterior a isso.

Equivalente PowerShell de BASH_003_siros_download.sh (DEC-011): mesma fonte,
mesmo criterio de nome, mesmo log, mesma idempotencia. Os dois scripts sao
pareados pelo numero -- se um mudar de regra, o outro muda junto, ou divergem
em silencio.

AVISO DE VOLUME: da ordem de 2.500+ arquivos (2019-11 ate hoje), ~32 GB.
Acompanhe _download_log.csv.

NOTA (2026-08-27, achado empirico, teste HTTP direto): o portal usa DOIS
formatos de pasta de mes para o SIROS, sem aviso -- "NN - MesNome/" a partir
de 2024, so "MesNome/" (sem numero, sem zero a esquerda) em 2019-2023. VRA
nao tem essa inconsistencia (sempre "NN - MesNome/"). Por isso o numero do
mes e derivado do NOME (com remocao de acento), nao so lido do prefixo
numerico, que pode nao existir. A remocao de acento aqui usa normalizacao
Unicode NFD, equivalente ao "iconv -t ascii//TRANSLIT" do script bash.

Roda com: powershell -ExecutionPolicy Bypass -File scripts\PS1_003_siros_download.ps1
#>
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$MES_NUM = @{
    "janeiro" = "01"; "fevereiro" = "02"; "marco"    = "03"; "abril"    = "04"
    "maio"    = "05"; "junho"     = "06"; "julho"    = "07"; "agosto"   = "08"
    "setembro"= "09"; "outubro"   = "10"; "novembro" = "11"; "dezembro" = "12"
}

function Remove-Acento {
    param([string]$Texto)
    $nfd = $Texto.Normalize([Text.NormalizationForm]::FormD)
    $sb = New-Object Text.StringBuilder
    foreach ($c in $nfd.ToCharArray()) {
        if ([Globalization.CharUnicodeInfo]::GetUnicodeCategory($c) -ne
            [Globalization.UnicodeCategory]::NonSpacingMark) {
            [void]$sb.Append($c)
        }
    }
    return $sb.ToString()
}

function Get-MesNumDoHref {
    # recebe o href decodificado (ex.: "01 - Janeiro/" ou "Janeiro/"), devolve NN
    param([string]$Href)
    $nome = $Href.TrimEnd("/")
    if ($nome.Contains("-")) { $nome = $nome.Substring($nome.IndexOf("-") + 1) }
    $nome = (Remove-Acento $nome).Replace(" ", "").ToLower()
    if ($MES_NUM.ContainsKey($nome)) { return $MES_NUM[$nome] }
    return ""
}

$UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
$BASE = "https://sistemas.anac.gov.br/dadosabertos/Voos%20e%20opera%C3%A7%C3%B5es%20a%C3%A9reas/Registro%20de%20servi%C3%A7os%20a%C3%A9reos"

# Raiz do repositorio, derivada da localizacao deste script: roda de
# qualquer diretorio, sem caminho de maquina cravado (ver DEC-011).
$REPO_ROOT = Split-Path -Parent $PSScriptRoot
$DEST = Join-Path $REPO_ROOT "data\anac\siros"

$ANO_INICIO = 2019
$MES_INICIO_NO_ANO_INICIO = 11

$ANO_FIM = [int](Get-Date -Format "yyyy")
$MES_FIM = [int](Get-Date -Format "MM")

New-Item -ItemType Directory -Force -Path $DEST | Out-Null
$LOG = Join-Path $DEST "_download_log.csv"
"ano,mes,dia,url,arquivo,http_status,bytes" | Set-Content -Path $LOG -Encoding UTF8

$total_ok = 0

foreach ($ano in $ANO_INICIO..$ANO_FIM) {
    $listing = ""
    try {
        $listing = (Invoke-WebRequest -Uri "$BASE/$ano/" -UserAgent $UA `
                                      -UseBasicParsing -ErrorAction Stop).Content
    } catch { $listing = "" }

    $meses_hrefs = [regex]::Matches($listing, 'href="([^"]+/)"') |
                   ForEach-Object { $_.Groups[1].Value } |
                   Where-Object { $_ -ne "../" } |
                   Sort-Object -Unique

    if ($meses_hrefs.Count -eq 0) {
        Write-Host "AVISO: nenhuma pasta de mes encontrada para $ano (pulando ano)"
        continue
    }

    foreach ($href in $meses_hrefs) {
        $mes_padded = Get-MesNumDoHref ([Uri]::UnescapeDataString($href))
        if ([string]::IsNullOrEmpty($mes_padded)) {
            Write-Host "AVISO: nao consegui mapear mes a partir de '$href' em $ano (pulando pasta)"
            continue
        }
        $mes_num = [int]$mes_padded

        if ($ano -eq $ANO_INICIO -and $mes_num -lt $MES_INICIO_NO_ANO_INICIO) { continue }
        if ($ano -eq $ANO_FIM -and $mes_num -gt $MES_FIM) { continue }

        $dias_no_mes = [DateTime]::DaysInMonth($ano, $mes_num)

        foreach ($dia in 1..$dias_no_mes) {
            $diaPad = "{0:D2}" -f $dia
            $fname = "registros_$ano-$mes_padded-$diaPad.csv"
            $url = "$BASE/$ano/$href$fname"
            $out = Join-Path $DEST $fname

            if ((Test-Path $out) -and ((Get-Item $out).Length -gt 0)) { continue }

            $status = 0
            try {
                $r = Invoke-WebRequest -Uri $url -OutFile $out -UserAgent $UA `
                                       -UseBasicParsing -PassThru -ErrorAction Stop
                $status = [int]$r.StatusCode
            } catch {
                if ($_.Exception.Response) { $status = [int]$_.Exception.Response.StatusCode }
            }
            $bytes = if (Test-Path $out) { (Get-Item $out).Length } else { 0 }
            "$ano,$mes_padded,$diaPad,$url,$fname,$status,$bytes" | Add-Content -Path $LOG -Encoding UTF8

            if ($status -ne 200 -or $bytes -lt 100) {
                Remove-Item $out -Force -ErrorAction SilentlyContinue
            } else {
                $total_ok++
            }
        }
        Write-Host "Mes $ano-$mes_padded processado (acumulado ok: $total_ok)"
    }
}

Write-Host ""
Write-Host "=== Resumo ==="
Write-Host "Arquivos baixados nesta execucao: $total_ok"
$total = (Get-ChildItem -Path $DEST -Filter *.csv -ErrorAction SilentlyContinue).Count
Write-Host "Total em disco: $total"
