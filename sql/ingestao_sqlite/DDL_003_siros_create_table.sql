-- Gerado a partir do cabecalho real dos arquivos SIROS (data/anac/siros/*.csv,
-- linha 2 = cabecalho; linha 1 e metadado "Atualizado em: ..."), verificado
-- estavel entre 2019-11-11 e 2024-01-15 (SPEC-007, SPEC-010).
-- Camada RAW: todas as colunas como TEXT, fieis ao arquivo de origem, uma
-- linha do CSV = uma linha na tabela (sem expandir autorizacao em voo-por-
-- data, DEC-008 Sec.2.d). Nomes seguem SPEC-007 Sec.5, nao os originais em
-- portugues do CSV.

CREATE TABLE IF NOT EXISTS siros_raw (
    "cd_empresa" TEXT,
    "nm_empresa" TEXT,
    "nr_voo" TEXT,
    "sg_equipamento_icao" TEXT,
    "fl_opera_segunda" TEXT,
    "fl_opera_terca" TEXT,
    "fl_opera_quarta" TEXT,
    "fl_opera_quinta" TEXT,
    "fl_opera_sexta" TEXT,
    "fl_opera_sabado" TEXT,
    "fl_opera_domingo" TEXT,
    "nr_assentos_ofertados" TEXT,
    "nr_siros" TEXT,
    "ds_situacao_siros" TEXT,
    "dt_registro" TEXT,
    "dt_inicio_operacao" TEXT,
    "dt_fim_operacao" TEXT,
    "ds_natureza_operacao" TEXT,
    "nr_etapa" TEXT,
    "cd_origem" TEXT,
    "nm_aerodromo_origem" TEXT,
    "cd_destino" TEXT,
    "nm_aerodromo_destino" TEXT,
    "hr_partida" TEXT,
    "hr_chegada" TEXT,
    "ds_tipo_servico" TEXT,
    "ds_objeto_transporte" TEXT,
    "ds_codeshare" TEXT,
    dt_arquivo TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_siros_raw_empresa ON siros_raw (cd_empresa);
CREATE INDEX IF NOT EXISTS idx_siros_raw_arquivo ON siros_raw (dt_arquivo);
CREATE INDEX IF NOT EXISTS idx_siros_raw_nr_siros ON siros_raw (nr_siros);
