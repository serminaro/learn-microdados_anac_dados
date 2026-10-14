#!/usr/bin/env python3
"""Envia um e-mail por pasta de figuras de analise/, com todas as PNGs anexadas.

Por que um script e nao a ferramenta de e-mail do assistente: aquela via exige
o anexo em base64 dentro da propria chamada, o que faria os 44,6 MB codificados
(33,4 MB brutos) atravessarem o contexto do modelo. Aqui os arquivos sao lidos
direto do disco.

Credencial: NAO fica no arquivo. O script le a variavel de ambiente
GMAIL_APP_PASSWORD ou, se ela nao existir, pergunta no terminal (getpass, sem
eco). Precisa ser uma "Senha de app" do Google, nao a senha da conta:
https://myaccount.google.com/apppasswords (exige verificacao em duas etapas).

Enderecos: NAO ficam no arquivo, mesma logica da credencial. Este repositorio
e publico; endereco cravado aqui entra no historico do git de forma permanente
e indexavel. Remetente e destinatario vem de --de/--para ou, na ausencia
deles, das variaveis de ambiente EMAIL_REMETENTE e EMAIL_DESTINATARIO. Sem
nenhum dos dois o script para com erro, sem default cravado (ver DEC-011).

Uso:
    export EMAIL_REMETENTE=voce@gmail.com
    export EMAIL_DESTINATARIO=destino@empresa.com

    python scripts/enviar_figuras_por_email.py --dry-run     # so' lista, nao envia
    python scripts/enviar_figuras_por_email.py               # envia as 9
    python scripts/enviar_figuras_por_email.py --pasta a3_figuras_gol
    python scripts/enviar_figuras_por_email.py --de a@b.com --para c@d.com
"""

import argparse
import getpass
import mimetypes
import os
import smtplib
import ssl
import sys
from email.message import EmailMessage
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ANALISE = REPO / "analise"

SMTP_HOST, SMTP_PORT = "smtp.gmail.com", 465
LIMITE_GMAIL = 25 * 1024 * 1024   # 25 MB por mensagem, anexos somados

# (caminho relativo a analise/, rotulo da linha de analise, descricao)
PASTAS = [
    ("a3_tempo_de_solo/a3_figuras_gol",     "A3 · Tempo de Solo",  "GOL"),
    ("a3_tempo_de_solo/a3_figuras_azul",    "A3 · Tempo de Solo",  "Azul"),
    ("a3_tempo_de_solo/a3_figuras_versus",  "A3 · Tempo de Solo",  "GOL x Azul"),
    ("a4_etapa_media/a4_figuras_gol",       "A4 · Etapa Média",    "GOL"),
    ("a4_etapa_media/a4_figuras_azul",      "A4 · Etapa Média",    "Azul"),
    ("a4_etapa_media/a4_figuras_versus",    "A4 · Etapa Média",    "GOL x Azul"),
    ("a5_block_time/a5_figuras_gol",        "A5 · Block Time",     "GOL"),
    ("a5_block_time/a5_figuras_azul",       "A5 · Block Time",     "Azul"),
    ("a5_block_time/a5_figuras_versus",     "A5 · Block Time",     "GOL x Azul"),
]

CORPO = """\
Figuras da linha de análise {linha}, recorte {recorte}.

{n} figuras anexadas, {mb:.1f} MB no total.

Códigos de aeroporto em IATA (GRU, CGH, BSB), traduzidos do ICAO da
fonte ANAC contra a dimensão de aeródromos. Onde não há IATA utilizável,
o rótulo permanece em ICAO.

Filtro: serviço PASSAGEIRO. Fonte: microdados da Básica e do VRA (ANAC).

Arquivos:
{lista}
"""


def montar(pasta_rel, linha, recorte, remetente, destinatario):
    pasta = ANALISE / pasta_rel
    figuras = sorted(pasta.glob("*.png"))
    if not figuras:
        return None, f"{pasta_rel}: nenhuma PNG, pulada"

    total = sum(f.stat().st_size for f in figuras)

    msg = EmailMessage()
    msg["From"] = remetente
    msg["To"] = destinatario
    msg["Subject"] = f"[Análise ANAC] {linha} — {recorte} ({len(figuras)} figuras)"
    msg.set_content(CORPO.format(
        linha=linha, recorte=recorte, n=len(figuras),
        mb=total / 1048576,
        lista="\n".join(f"  - {f.name}" for f in figuras),
    ))

    for f in figuras:
        tipo, _ = mimetypes.guess_type(f.name)
        maintype, subtype = (tipo or "application/octet-stream").split("/", 1)
        msg.add_attachment(f.read_bytes(), maintype=maintype,
                           subtype=subtype, filename=f.name)

    tamanho = len(bytes(msg))
    if tamanho > LIMITE_GMAIL:
        return None, (f"{pasta_rel}: {tamanho/1048576:.1f} MB codificado, "
                      f"acima do limite de 25 MB do Gmail -- NAO enviada")
    return msg, f"{pasta_rel}: {len(figuras)} figuras, {tamanho/1048576:.1f} MB codificado"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="monta as mensagens e mostra o resumo, sem conectar nem enviar")
    ap.add_argument("--pasta", help="envia so' a pasta cujo nome termine com este valor")
    ap.add_argument("--de", help="remetente; se omitido, usa a variavel EMAIL_REMETENTE")
    ap.add_argument("--para", help="destinatario; se omitido, usa a variavel EMAIL_DESTINATARIO")
    args = ap.parse_args()

    # Precedencia: argumento > variavel de ambiente > erro. Sem default cravado,
    # de proposito: o repositorio e publico (ver docstring).
    remetente = args.de or os.environ.get("EMAIL_REMETENTE")
    destinatario = args.para or os.environ.get("EMAIL_DESTINATARIO")
    faltando = [rotulo for valor, rotulo in
                ((remetente, "remetente (--de ou EMAIL_REMETENTE)"),
                 (destinatario, "destinatario (--para ou EMAIL_DESTINATARIO)"))
                if not valor]
    if faltando:
        sys.exit("Falta definir: " + "; ".join(faltando))

    alvos = [p for p in PASTAS if not args.pasta or p[0].endswith(args.pasta)]
    if not alvos:
        sys.exit(f"Nenhuma pasta casa com --pasta {args.pasta!r}")

    mensagens, problemas = [], []
    for pasta_rel, linha, recorte in alvos:
        msg, nota = montar(pasta_rel, linha, recorte, remetente, destinatario)
        print(("  OK   " if msg else "  ERRO ") + nota)
        (mensagens if msg else problemas).append((pasta_rel, msg))

    print(f"\n{len(mensagens)} mensagem(ns) prontas, {len(problemas)} com problema.")
    if args.dry_run:
        print("--dry-run: nada foi enviado.")
        return
    if problemas:
        sys.exit("Abortado: resolva os problemas acima ou rode com --pasta.")

    senha = os.environ.get("GMAIL_APP_PASSWORD") or getpass.getpass(
        f"Senha de app do Google para {remetente}: ")

    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ctx) as smtp:
        smtp.login(remetente, senha)
        for pasta_rel, msg in mensagens:
            smtp.send_message(msg)
            print(f"  enviado: {pasta_rel} -> {destinatario}")

    print(f"\n{len(mensagens)} e-mail(s) enviado(s) de {remetente} para {destinatario}.")


if __name__ == "__main__":
    main()
