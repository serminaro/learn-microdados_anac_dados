================================================================================
CONTEXTO DO PROJETO
Pasta: rascunho/contexto/
================================================================================

Esta pasta guarda a matéria-prima de construção do projeto:

  contexto/
    ├── README.txt        (este arquivo)
    ├── blueprints/       (JSON que descreve como construir cada peça fundacional)
    │     ├── DEC_001.json
    │     ├── SPEC_001.json
    │     ├── REP_001.json
    │     ├── SPEC_002.json
    │     └── SPEC_003.json
    ├── pesquisa/         (documentos de pesquisa do projeto)
    └── relatorios/       (relatórios e análises pertinentes)

O que cada parte é:

  - blueprints/  são o núcleo prescritivo. Cada JSON descreve, para uma peça da
    fundação, suas seções, subtópicos, mínimos e critérios auditáveis (campo
    "checar"). A IA de apoio lê o blueprint da peça antes de escrevê-la e produz
    o documento conforme a estrutura declarada. Os blueprints derivam da
    SPEC-META-001 (taxonomia) e da DEC-META-002 §2.1 (conteúdo das peças).

  - pesquisa/ e relatorios/  recebem o material bruto específico do projeto
    (estudos, dados, relatórios, links). É o que a IA lê na etapa de sensemaking
    e destila para a seção "Fatos duráveis" da MEMORIA.txt.

Formato: os blueprints são JSON (estruturados, legíveis por máquina). O restante
do material do projeto entra no formato em que existir.
================================================================================
