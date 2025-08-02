# Celes.ia v2 Alpha

Protótipo avançado de uma Inteligência Artificial orquestradora com aprendizado iterativo, automação de scraping, painel interativo e integração com múltiplas fontes de dados.

## Funcionalidades

- Geração automática de testes com base em dados reais
- Correção automática de scripts e testes (self-healing)
- Aprimoramento de estratégias com base em testes bem-sucedidos (self-improvement)
- Scraping em tempo real de passagens aéreas (ex: LATAM, Copa Airlines, etc.)
- Integração com bot no Telegram para análise e execução de comandos por trecho
- Dashboard interativo para visualização de dados e controle
- Deploy automatizado (Railway, VPS ou similar)
- Exportação de resultados em planilhas e formatos estruturados

## Estrutura do Projeto

```
celesia_v2_alpha_final/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── deploy.yml
├── ai_engine/
│   ├── config.env.py
│   ├── gemini_caller.py
│   ├── openai_caller.py
│   └── orchestrator.py
├── ai_engine.zip
├── github.env.md
├── github_project_template.json
├── setup_github_project.py
├── tests/
│   └── (testes unitários com pytest)
├── research_planner.py
├── README.md
├── CHANGELOG.md
└── STATUS.md
```

## Requisitos

- Python 3.10+  
- Bibliotecas: `pytest`, `requests`, `openai`, `selenium`, entre outras (ver `requirements.txt`)  

## Execução dos Testes

Instale o `pytest`:

```bash
pip install pytest
```

Rode os testes:

```bash
pytest
```

## Deploy

O sistema está preparado para deploy via:

- Railway (CI/CD automatizado com workflows prontos)
- VPS própria (configuração flexível com `.env`)
- GitHub Actions (`.github/workflows/deploy.yml`)

## Observações

- O projeto utiliza tokens de acesso às APIs (OpenAI, Gemini, etc.), que devem ser definidos no arquivo `config.env.py`.
- O scraping pode depender de credenciais ou autenticação adicional, dependendo da fonte.
