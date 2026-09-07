---
documento: DEC-007
titulo: Arquitetura de camadas para as Perguntas de Análise (Deep Dive GOL/Azul) — genérica, dois caminhos
versao: v4
status: aprovado
data: 2026-08-31
autor: Bruno Alexandre Serminaro
referencia: SPEC-002
escopo: projeto
---

# DEC-007 · Arquitetura para as Perguntas de Análise: Trusted_Essencial + Curated Deep Dive (GOL, Azul), genérica e dual-path

> DEC de conteúdo: fixa a arquitetura de camadas e o método para responder,
> dentro deste projeto, seis perguntas de análise sobre a operação de GOL
> e Azul, de forma **agnóstica de engine** — a decisão de arquitetura é
> única, válida para os dois caminhos de produção do projeto
> (`SPEC-002 §3.1`: Snowflake e SQLite+Python); a implementação concreta
> em cada caminho é descrita, não decidida, na `SPEC-004`.

---

## 1. Contexto

A v1 desta DEC (2026-08-30) fixou a arquitetura só para o caminho
Snowflake, com nomenclatura de objeto em maiúsculas
(`TRUSTED_ESSENCIAL`, `CURATED_DEEP_DIVE_GOL`). O autor pediu, nesta
sessão (2026-08-31), reformular em três pontos: (i) as perguntas de
análise devem ser especificadas de forma genérica, sem pensar em engine;
(ii) a implementação por caminho (SQLite, Snowflake) vem depois, descrita
separadamente; (iii) uma das perguntas deve ser detalhada por completo,
como exemplo de tradução genérico → implementação.

Uma iteração mais avançada da análise, do mesmo ambiente de trabalho,
dado 100% público, trouxe resultado real para três perguntas (destinos,
frota, tempo de solo hub/off-hub), cobrindo GOL **e** Azul lado a lado,
na janela 2021-01-01 até "o momento atual" (a mesma janela que esta DEC
já fixava), e **redefiniu** o conteúdo de duas perguntas frente à
formulação original:

- "Utilização de frota" (horas voadas/dia por tipo) vira **"Distribuição
  da frota"** (composição percentual por modelo + idade de serviço por
  matrícula) — o docx não mede horas/dia em nenhum ponto, mede % de frota
  e histograma de idade em serviço.
- A v1 desta DEC (2026-08-31, primeira revisão) leu a ausência de "etapa
  média" na lista do autor como substituição por "tempo médio no ar". O
  autor corrigiu: **não é substituição, é fusão** — as duas metades
  (distância e duração) ficam sob um único nome, **"Etapa média"**, com a
  duração do voo (tempo no ar) como métrica principal, a distância (km,
  só a versão simples, `NR_ASK` continua fora de escopo) como métrica
  complementar, e a velocidade média inferida (distância/duração) como
  terceira métrica derivada.

## 2. Decisão

Fixar, para este projeto, **de forma agnóstica de engine** — válida
igualmente para o caminho Snowflake e o caminho SQLite+Python
(`SPEC-002 §3.1`):

**(a) Método.** Manter a metodologia de perguntas já estabelecida para
este bloco de análise — destravar o conceito, mapear colunas candidatas,
declarar premissas/incertezas antes de calcular, reportar alternativas
quando há mais de uma definição válida.

**(b) As cinco perguntas de análise deste projeto passam a ser:**

1. Números de destinos, rotas e mercados (destinos já respondida; rota e
   mercado como extensão em andamento, pedida pelo autor — verificar
   assimetria de fluxo entre os dois sentidos de um mercado, definido por
   par de aeroportos, medido por frequência de etapas — capacidade/ASK
   deliberadamente adiada)
2. Distribuição da frota
3. Comportamento do tempo de solo (distribuição do intervalo entre
   pouso e próxima decolagem da mesma aeronave, por modelo)
4. Caracterização das bases (hub / off-hub) (classificação de aeroporto
   por volume de chegadas, regra de Pareto — pergunta de estrutura de
   rede, separada da 3 por pedido do autor, 2026-08-31; a implementação
   das duas é compartilhada, `SPEC-004 §6`)
5. Etapa média (duração do voo como métrica principal; distância e
   velocidade média inferida como métricas complementares)
6. Block time (sobra e estratégia)

**(c) Camada `trusted_essencial`**: view/tabela de nome genérico (sem
prefixo de engine), derivada da camada silver do dataset (`basica_silver`
no caminho SQLite, `sql/tratamento/DDL_003_basica_view_silver_sqlite.sql`
— substitui `basica_typed`, retirada em 2026-08-31 por cobrir só ~27 das
112 colunas com métrica derivada misturada, ver `SPEC-008 v3`), restrita
às 29 colunas essenciais marcadas em `SPEC-005` (Dicionário de Colunas —
Básica).

**(d) Duas camadas fixas `curated_deep_dive_gol` e
`curated_deep_dive_azul`**, sobre `trusted_essencial`, filtro
`sg_empresa_icao` (`'GLO'`/`'AZU'`) e janela
`dt_partida_real >= '2021-01-01'`, sem limite superior fixo.

**(e) Escopo dual-path por decisão explícita** (correção da v1 desta DEC,
que só cobria Snowflake): a arquitetura de camadas e o método de cada
pergunta são definidos **uma única vez**, de forma genérica; a
implementação concreta (sintaxe SQL, funções disponíveis em cada motor)
é descrita por caminho na `SPEC-004`, sem duplicar a decisão de
arquitetura — mesma lógica que a camada silver já segue (uma decisão de
camada, um script por caminho).

**(f) "Block time" permanece bloqueada** até o VRA existir neste projeto;
o autor está avaliando ativamente essa base agora (mudança frente à v1:
de "bloqueada, sem prazo" para "bloqueada, investigação em andamento").

**(g) Padrão de junção cross-dataset, registrado agora, implementado só
quando o VRA existir.** Quando desbloqueada, a pergunta 6 nasce como
objeto **dedicado**, **único** (não mais um objeto por empresa — correção
v4, decisão inalterada, `R-TAX-11`: `curated_deep`/`fato_rotacao_
aeronave_gol_azul`, construídos depois desta DEC, já fixam o padrão de um
objeto só com coluna `sg_empresa_icao` filtrando GOL/Azul, e a pergunta 6
segue o mesmo padrão para consistência — `fato_block_time_gol_azul`, não
`curated_block_time_gol`/`curated_block_time_azul` como a v3 registrava)
— não como extensão de `curated_deep_dive_*`. As bases `basica.sqlite` e
`vra.sqlite` continuam fisicamente separadas (`DEC-004` intacta); só o
**resultado** da junção passa a viver num objeto só, materializado **uma
vez** por carga, não recalculado a cada consulta:

- **SQLite**: `ATTACH DATABASE 'vra.sqlite' AS vra;` dentro do script que
  constrói a curated, `CREATE TABLE fato_block_time_gol_azul AS SELECT
  ...` (join Básica × VRA), `DETACH DATABASE vra;` — o `ATTACH` fica
  confinado ao script de construção, não à consulta analítica.
- **Snowflake**: referência cross-schema nativa
  (`ANAC.VRA.<objeto> JOIN ANAC.BASICA.<objeto>`), sem custo de sintaxe
  extra — assimetria real frente ao SQLite, aceita como consequência
  (§5.2).
- **Chave de junção**: hipótese de trabalho original (v1-v3) — empresa
  (ICAO) + número de voo + data de partida + aeroporto de origem.
  **Refinada (v4, achado real, não mais hipótese pura)**: adicionar
  **hora** de partida à chave (empresa+voo+data+hora+origem) — medido
  fora deste documento (sessão de trabalho, amostra GOL/Azul 2025): sem
  hora, 6.392 grupos de chave duplicada (mesmo nº de voo pode operar duas
  vezes no mesmo dia calendário); com hora, cai para 13 grupos residuais,
  correspondência ~97%. Chave completa ainda não medida contra o par
  atual `fato_rotacao_aeronave_gol_azul`×`vra_curated_deep` — fica para
  a implementação real desta pergunta.

## 3. Origem ou rastro

- Metodologia de análise já validada em trabalho anterior — destravar
  conceito, mapear colunas, declarar premissas, reportar alternativas
  (§2.a) — e achados reais já obtidos para destinos, frota e tempo de
  solo hub/off-hub (GOL e Azul, janela 2021-01-01 até o presente): origem
  da redefinição de duas perguntas (§1) e do método detalhado da
  pergunta 3 (IQR para outlier, regra de Pareto para hub/off-hub, ambos
  formalizados na `SPEC-004 §6`).
- `SPEC-005` (Dicionário de Colunas — Básica): lista de colunas essenciais,
  base literal da `trusted_essencial`.
- Pedido do autor nesta sessão (2026-08-31): perguntas genéricas
  (sem pensar em engine), implementação descrita depois por caminho, uma
  pergunta detalhada como exemplo.
- `SPEC-002 §3.1` e §3.2: dois caminhos de produção igualmente investidos
  — usado para descartar a v1 desta DEC, que cobria só Snowflake (§4.1).
- `SPEC-005`: `DT_PARTIDA_REAL` como coluna de ancoragem da janela
  temporal, categoria `BLOCK_TIME`.
- `DEC-004 §5.2/§6`: nomeia o custo de `ATTACH DATABASE` para cruzar
  datasets no SQLite e já prevê critério de reavaliação se isso virar
  operação frequente — a materialização única (§2.g), não repetida por
  consulta, é desenhada precisamente para não acionar esse gatilho.
- Debate desta sessão (2026-08-31) sobre engenharia de dado com três
  bancos separados (Básica, VRA, SIROS): descartou mesclar bancos
  fisicamente (reabriria `DEC-004` alternativa 4.1) e descartou deixar o
  padrão de junção indefinido até o VRA existir (mesmo risco de decisão
  às pressas que a alternativa 4.4 desta DEC já evita para "block time"
  com proxy).

## 4. Alternativas consideradas

### 4.1 Manter a arquitetura restrita ao caminho Snowflake (estado da v1 desta DEC)

Manter a decisão como estava, sem estender a decisão de camada ao
caminho SQLite+Python.

**Por que descartada.** Contradiz `SPEC-002` (dois caminhos igualmente
investidos, §1/§3.1) sem necessidade técnica real — a arquitetura de
camada (`trusted_essencial`, `curated_*`) é a mesma nos dois caminhos, só
muda a sintaxe SQL de cada view/tabela, exatamente como a camada silver já
faz hoje.

### 4.2 Responder as perguntas direto sobre a camada silver (112 colunas), sem `trusted_essencial`

Cada `curated` filtraria e selecionaria as 29 colunas por conta própria.

**Por que descartada.** Replica a mesma lógica de seleção de coluna em
cada `curated` (hoje duas; qualquer deep dive futuro repetiria).
`trusted_essencial` existe uma vez, reusada pelas duas curated atuais e
por qualquer análise futura.

### 4.3 Uma única `curated_deep_dive` parametrizada por empresa

View genérica, com filtro dinâmico de `sg_empresa_icao`, em vez de dois
objetos fixos.

**Por que descartada.** O autor trata GOL e Azul como dois objetos de
análise distintos; view fixa por concorrente é mais direta de auditar e
de consumir num BI, ao custo aceito de duplicar a definição de filtro.

### 4.4 Responder "block time" com proxy, sem esperar o VRA

Já cogitada em iteração anterior desta análise.

**Por que descartada.** O autor pediu explicitamente que só essa pergunta
dependa do VRA — manter o bloqueio evita achado inflado (proxy reportada
como se respondesse a pergunta original).

### 4.5 Arquitetura genérica, dual-path, cinco perguntas redefinidas (decisão atual)

**Adotada.** Corrige o escopo Snowflake-only da v1, mantém a camada
intermediária e as curated fixas (razões de 4.2/4.3 continuam válidas),
mantém "block time" bloqueada (razão de 4.4 continua válida), e absorve a
redefinição de perguntas trazida pela iteração mais avançada da análise
(§1).

### 4.6 Mesclar `basica.sqlite` e `vra.sqlite` num banco único, para simplificar a junção

Abandonar o isolamento por dataset especificamente para viabilizar
"block time".

**Por que descartada.** Reabriria a `DEC-004` (alternativa 4.1 lá, já
descartada pelo risco de um dataset problemático — volume, corrupção —
afetar os outros). O risco fica pior pensando em SIROS, que compartilharia
o mesmo arquivo se a lógica se generalizasse, e é o dataset com maior
incerteza de volume ainda não medida (`REP-001 §5.2`).

### 4.7 Deixar o padrão de junção indefinido até o VRA existir de fato

Não registrar nada agora; decidir chave de junção e mecanismo só quando o
VRA for ingerido.

**Por que descartada.** Mesmo risco que a alternativa 4.4 já nomeia para
"block time" com proxy: decisão tomada às pressas, sob pressão do momento
em que o VRA finalmente existir, em vez de registrada com calma agora,
mesmo sabendo que a chave de junção é hipótese até então.

### 4.8 Padrão de junção registrado agora, objeto dedicado por caminho, materialização única (decisão atual, §2.g)

**Adotada.** Fecha a lacuna de honestidade sobre "block time" (a v1 desta
DEC tratava como "fora desta DEC" sem registrar nem o formato do
problema) sem forçar implementação prematura — o padrão fica escrito, a
execução continua bloqueada até o VRA existir.

## 5. Consequências

### 5.1 Positivas

- Alinha esta DEC com `SPEC-002` (dois caminhos igualmente investidos),
  corrigindo o desvio da v1.
- `trusted_essencial` e o método de cada pergunta ficam definidos uma vez
  só, reduzindo risco de os dois caminhos divergirem em conceito (só
  divergem em implementação, o esperado).
- Absorve achados já validados em iteração anterior da análise (IQR para
  outlier de tempo de solo, Pareto para hub/off-hub) como método de
  referência, não repete trabalho de definição já feito.
- Fecha a lacuna de honestidade sobre "block time" (§2.g): o padrão de
  junção cross-dataset fica registrado, sem forçar implementação
  prematura nem reabrir o isolamento por dataset da `DEC-004`.

### 5.2 Negativas

- **Mais esforço de implementação**: cada camada nova
  (`trusted_essencial`, `curated_deep_dive_gol`, `curated_deep_dive_azul`)
  agora precisa de dois scripts (SQLite e Snowflake) em vez de um,
  frente à v1 desta DEC.
- **Risco de divergência numérica entre caminhos**: onde um motor tem
  função nativa que o outro não tem (ex. percentil/mediana, ausente no
  SQLite), a técnica de implementação diverge (SQL puro vs. SQL+Python) —
  gerenciado na `SPEC-004 §6`, não eliminado.
- **Pergunta 5 (etapa média) carrega três métricas em vez de uma**
  (duração, distância, velocidade inferida) — mais rica, mas exige decisão
  de agregação para a velocidade (razão das somas vs. média das razões por
  etapa, `SPEC-004 §5.5`) que as outras perguntas não têm.
- **Perguntas 3 e 4 nasceram de uma única implementação partilhada** — o
  passo de classificação hub/off-hub (pergunta 4) é insumo do cruzamento
  final da pergunta 3 (`SPEC-004 §6.3`, passo 7); separar em duas
  perguntas formais ganha critério de sucesso próprio para cada uma, ao
  custo de uma dependência de implementação que o nome "duas perguntas"
  não deixa óbvia por si só.
- **Pergunta 1 (destinos, rota, mercado) fica com uma parte respondida e
  outra em andamento** — a mesma pergunta mistura status diferentes
  (`SPEC-004 §5.1`), o que exige atenção redobrada em qualquer REP futura
  para não reportar a parte pronta como se a extensão também estivesse.
- **A chave de junção Básica × VRA (§2.g) é hipótese, não achado** —
  empresa + voo + data + origem é a leitura mais provável dada a estrutura
  pública conhecida do VRA, mas só se confirma inspecionando o dicionário
  real do dataset, ainda não baixado neste projeto.
- **Assimetria de custo entre caminhos fica maior nesta pergunta do que
  nas demais**: SQLite paga `ATTACH`/materialização, Snowflake não paga
  nada de sintaxe extra (cross-schema nativo) — mais desigual que a
  assimetria de percentil já registrada para as perguntas 3/4
  (`SPEC-004` R-ANL-06).

### 5.3 O que esta decisão não resolve

- Não decide a numeração exata dos scripts por caminho — convenção
  `TIPO_NNN` já fixada no `DEC-001 §6.6`.
- Não resolve quando "block time" deixa de estar bloqueada — depende do
  pipeline VRA; o padrão de junção (§2.g) fica pronto para quando isso
  acontecer, mas a implementação em si continua fora desta DEC.
- Não confirma a chave de junção Básica × VRA — hipótese até o dicionário
  real do VRA ser inspecionado.
- Não formaliza as respostas às perguntas em si — conteúdo de REP futura.
- Não estende o método de referência do docx (Fourier, sazonalidade de
  destinos) como requisito — fica registrado como extensão opcional na
  `SPEC-004 §5.1`.

## 6. Critérios de reavaliação

Esta decisão deve ser revisitada se:

- VRA ganhar ingestão completa neste projeto — desbloqueia "block time" e
  aciona a implementação do padrão de junção (§2.g); nesse momento,
  confirmar a chave de junção contra o dicionário real do VRA.
- Um terceiro concorrente entrar na análise — reabre a alternativa 4.3
  (parametrizar em vez de duplicar).
- Mais de uma pergunta cross-dataset aparecer (ex.: quando SIROS entrar) —
  revisitar junto com o critério da `DEC-004 §6` (`ATTACH` virar
  frequente); sinal para considerar um padrão de junção único, não um
  objeto dedicado por pergunta.
- O autor decidir retomar a análise de assimetria de rota/mercado por
  capacidade (ASK, assentos ofertados) — hoje deliberadamente adiada
  (`SPEC-004 §5.1`).
- A implementação revelar que a arquitetura genérica não se sustenta
  igualmente nos dois caminhos (ex. uma camada só faz sentido num deles) —
  sinal para tratar aquele caso como exceção documentada, não para
  reverter a decisão inteira.

## 7. Histórico

| Data | Evento |
|---|---|
| 2026-08-30 | DEC-007 v1 produzida em status `proposto`, escopo Snowflake-only. Fixa a arquitetura de camadas e o método para responder as cinco perguntas de análise originais do `rascunho/SPEC-010`, com "block time" bloqueada até o VRA. Quatro alternativas avaliadas. |
| 2026-08-31 | Revisão a pedido do autor: perguntas reformuladas de forma genérica (agnóstica de engine), escopo estendido para os dois caminhos de produção (`SPEC-002 §3.1`), duas perguntas redefinidas a partir de `rascunho/Deep_Dive_Gol_ANAC_1a_.docx` ("distribuição da frota", "tempo médio no ar"). Quinta alternativa avaliada (4.1, descarta o escopo Snowflake-only da v1). |
| 2026-08-31 | Correção do autor: "tempo médio no ar" não substitui "etapa média", as duas se fundem sob o nome "Etapa média" — duração do voo como métrica principal, distância como complementar, velocidade média inferida (distância/duração) como terceira métrica. §1 e §2.b atualizados. |
| 2026-08-31 | Segunda correção do autor: pergunta "tempo de solo (hub/off-hub)" separada em duas — "comportamento do tempo de solo" e "caracterização das bases hub/off-hub" — implementação compartilhada, critério de sucesso próprio para cada uma (`SPEC-004 §6`). Pergunta "destinos" ganhou extensão em andamento de rota e mercado, pedida pelo autor para investigar assimetria de fluxo por sentido dentro de um mercado; conceitos de rota (par ordenado, aeroporto) e mercado (par não ordenado) definidos em `SPEC-004 §5.1`. Seis perguntas agora. |
| 2026-08-31 | Duas decisões do autor fecham pontos em aberto da extensão de rota/mercado: mercado definido por **par de aeroportos**; assimetria medida por **frequência de etapas**, capacidade (ASK/assentos ofertados) deliberadamente adiada. §2.b, §6 atualizados. |
| 2026-08-31 | Debate sobre engenharia de dado com três bancos separados (Básica, VRA, SIROS): registrado o padrão de junção cross-dataset para "block time" (§2.g) — objeto dedicado (`curated_block_time_gol`/`azul`), materialização única por caminho (`ATTACH`+`CREATE TABLE` no SQLite; cross-schema nativo no Snowflake), chave de junção hipotética (empresa+voo+data+origem). Descartadas duas alternativas: mesclar bancos (reabriria DEC-004) e deixar o padrão indefinido até o VRA existir. Isolamento por dataset da DEC-004 preservado. |
| 2026-09-01 | **v4 — correção pós-aprovação, decisão inalterada (`R-TAX-11`).** VRA já ingerido e desbloqueado (`SPEC-012`), `curated_deep`/`fato_rotacao_aeronave_gol_azul` já implementados desde então fixaram o padrão de objeto único (não um por empresa) — pergunta 6 alinhada ao mesmo padrão, pedido do autor: `fato_block_time_gol_azul` substitui `curated_block_time_gol`/`curated_block_time_azul` da v3. Chave de junção refinada de hipótese pura para achado real (adicionar hora à chave elimina quase toda duplicidade, medido em amostra 2025 GOL/Azul nesta sessão) — ainda não medida contra o par atual de tabelas, fica para a implementação. §2.g atualizado. |
| 2026-08-31 | **Aprovada.** Revisão estrutural sem divergência: sete seções obrigatórias presentes, oito alternativas avaliadas com veredito, consequências negativas não vazias (inclui as assimetrias de custo entre caminhos), `referencia:` cita SPEC-002 e as duas origens informais (SPEC-010, docx). Autor revisou o resumo (quadro "Aprovações ANAC") e aprovou explicitamente. Chave de junção Básica×VRA e implementação da pergunta 6 seguem como premissa/bloqueio registrados, não pendências que impedem esta aprovação. |
| 2026-08-31 | **v2 — correção pós-aprovação, decisão inalterada.** A pedido do autor, `rascunho/SPEC-010-ANAC-Perguntas_Analise-Deep_Dive-Gol.md` e `rascunho/Deep_Dive_Gol_ANAC_1a_.docx` foram excluídos do repositório; toda citação a eles no corpo desta DEC foi removida ou reescrita em prosa (o conteúdo que sustentavam — metodologia, achados de IQR/Pareto — já estava descrito por completo no texto, não dependia da citação). Citações a `rascunho/colunas.txt` substituídas por `SPEC-005` (Dicionário de Colunas — Básica), peça que o formaliza. `referencia:` do frontmatter atualizado para `SPEC-002` apenas. Nenhuma decisão de arquitetura muda; edição puramente de rastro/citação. |
| 2026-08-31 | **v3 — correção pós-aprovação, decisão inalterada.** `basica_typed` foi retirada (cobria só ~27 das 112 colunas, com métrica derivada misturada — achado registrado em `SPEC-008 v3`); `trusted_essencial` passa a derivar de `basica_silver` (view nova, 112 colunas, organizada e comentada a partir de `SPEC-005`). §2.c, §2.e, §4.1, §4.2 atualizados — a decisão em si (`trusted_essencial` deriva da camada silver/typed do dataset) não muda, só o nome e o alcance do objeto concreto que a implementa. Pendência ainda aberta: se este tipo de mudança deveria ir por `supersede` em vez de versão (achado do `gov-check`, não resolvido pelo autor até esta edição). |
| 2026-09-07 | **Precisão do registro de exclusão, decisão inalterada.** A entrada de 2026-08-31 acima diz que `Deep_Dive_Gol_ANAC_1a_.docx` e `SPEC-010-ANAC-Perguntas_Analise-Deep_Dive-Gol.md` foram "excluídos do repositório". Verificado em 2026-09-07: a afirmação vale para a árvore de trabalho e para o `HEAD`, e não para o histórico publicado. Os dois foram adicionados no commit `607cb8a` e removidos em `a74fff3`, ambos de 2026-08-31, e `607cb8a` é alcançável a partir de `origin/main`. Como o repositório é público, os dois blobs (`9f32b1de` e `a80d8e41`) seguem acessíveis a quem tiver o hash do commit. O autor optou por manter o histórico como está, apoiado na classificação já registrada no próprio rascunho (dado 100% público/regulatório, sem informação confidencial). Registrado aqui para que "excluído" não seja lido como "inacessível". |

---

*Fim do documento.*
