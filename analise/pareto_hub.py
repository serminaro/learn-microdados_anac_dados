"""Regra unica de classificacao HUB / OFF-HUB das bases (SPEC-013 Sec.6.5).

Por que este modulo existe: a mesma regra estava reimplementada em 11
scripts de analise/, cada um com sua copia e um comentario dizendo "mesma
regra de <outro script>". Onze copias de uma regra de negocio e' onze
oportunidades de divergir em silencio -- basta alguem ajustar o limiar num
arquivo. Aqui ela existe uma vez.

REGRA. Ordena as bases por contagem decrescente e classifica como HUB
enquanto o percentual acumulado ANTES da base for menor que 80%. A base que
cruza a linha entra; a seguinte fica de fora. Nao e' corte fixo top-N, e o
numero de bases varia com a distribuicao.

ESCOPO DELIBERADO: a regra e' aplicada sobre o recorte de quem chama, nao
sobre um universo fixo. Cada figura calcula HUB dentro da propria janela e
do proprio filtro. Consequencia medida em 2026-09-05, e mantida de
proposito: o conjunto de HUB muda com a janela.

    GOL   2021-2026: 16 bases | 2026 isolado: 17 (NAT entra)
    Azul  2021-2026: 22 bases | 2025-2026: 21 (FLN sai) | 2026: 20 (NAT sai)

Essa mobilidade e' achado registrado na SPEC-013 v5, nao ruido. A
alternativa (congelar o conjunto pela view pareto_bases_gol_azul) foi
avaliada e descartada pelo autor em 2026-09-05: tornaria as figuras
comparaveis entre janelas, mas apagaria o achado.

RELACAO COM A VIEW. A view pareto_bases_gol_azul
(sql/curated_deep/DDL_006_pareto_bases_gol_azul_create_view_sqlite.sql)
aplica esta mesma regra no SQL, sobre um recorte fixo: as duas empresas,
os dois sentidos, janela movel de cinco anos fechados. Ela e' a referencia
canonica consultavel e substituiu o CSV estatico que ficava em rascunho/.
As duas implementacoes sao pareadas pelo limiar de 80% e pelo criterio
"acumulado ANTES da base" -- se uma mudar de regra, a outra muda junto, ou
divergem em silencio.
"""

import pandas as pd

LIMIAR_ACUMULADO_PCT = 80.0


def selecionar_hub(contagens: pd.Series) -> pd.Series:
    """Recebe contagens por base e devolve so' as HUB, em ordem decrescente.

    O indice de `contagens` sao as bases (rotulo IATA, ou ICAO no fallback
    de analise/iata_bases.py); os valores sao a contagem de etapas. Devolve
    uma Series do mesmo tipo, filtrada, preservando os valores originais.
    """
    ordenado = contagens.sort_values(ascending=False)
    pct = 100 * ordenado / ordenado.sum()
    pct_acum_antes = pct.cumsum() - pct
    return ordenado[pct_acum_antes < LIMIAR_ACUMULADO_PCT]
