-- Gerado a partir do cabecalho real dos arquivos VRA (data/anac/vra/*.csv,
-- linha 2 = cabecalho; linha 1 e metadado "Atualizado em: ..."), verificado
-- estavel entre 2010-01 e 2026-07 (SPEC-006, SPEC-009).
-- Camada RAW: todas as colunas como TEXT, fieis ao arquivo de origem.
-- Nomes seguem a convencao de prefixo do projeto (SPEC-006 Sec.5), nao os
-- nomes de coluna originais em portugues do CSV.

CREATE TABLE IF NOT EXISTS vra_raw (
    "sg_empresa_icao" TEXT,
    "nr_voo" TEXT,
    "cd_autorizacao_di" TEXT,
    "cd_tipo_linha" TEXT,
    "sg_icao_origem" TEXT,
    "sg_icao_destino" TEXT,
    "dt_hr_partida_prevista" TEXT,
    "dt_hr_partida_real" TEXT,
    "dt_hr_chegada_prevista" TEXT,
    "dt_hr_chegada_real" TEXT,
    "ds_situacao_voo" TEXT,
    "cd_justificativa" TEXT,
    nr_ano_mes_arquivo TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_vra_raw_empresa ON vra_raw (sg_empresa_icao);
CREATE INDEX IF NOT EXISTS idx_vra_raw_arquivo ON vra_raw (nr_ano_mes_arquivo);
