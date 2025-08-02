# celest.ia Research Planner

Protótipo de uma IA planejadora de pesquisa com capacidades de auto-correção
(self-healing) e auto-melhoria (self-improvement). O projeto é composto pelo
módulo principal `research_planner.py` e pelos testes unitários em `tests/`.

## Funcionalidades
- Gera novos testes a partir de dados existentes.
- Analisa resultados para identificar sucessos e falhas.
- Corrige automaticamente testes falhos.
- Ajusta sua estratégia com base nos testes bem-sucedidos.

## Estrutura do Projeto

```text
.
├── README.md
├── research_planner.py
└── tests
    └── test_research_planner.py
```

## Execução dos testes

Requisitos: [pytest](https://pytest.org/).

```bash
pip install pytest
pytest
```
