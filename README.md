# Celest.ia v2 Alpha

Protótipo avançado de uma Inteligência Artificial orquestradora com scraping real de passagens, dashboard interativo, auto-correção de código (self-healing), auto-melhoria (self-improvement) e integração com bots e APIs externas.

---

## Visão Geral

O sistema integra:

- Scrapers reais para plataformas como Skyscanner, ConnectMiles, Copa Airlines
- Painel web interativo com visualização de preços, históricos e alertas
- Módulo de pesquisa inteligente que testa e melhora seu próprio desempenho
- Integração com IA (Codex, Gemini Pro, GPT-4 Turbo)
- Automação de alertas via Telegram Bot
- Deploy contínuo com Vercel

---

## Estrutura do Projeto

```bash
Celest.ia-v2-Alpha/
├── celestia_dashboard/         # Frontend interativo com Vite + React
│   ├── index.html
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   ├── MilhasChart.jsx
│   ├── vite.config.js
│   └── package.json
│
├── scrapers.py                 # Scrapers reais de companhias e buscadores
├── research_planner.py         # Núcleo de autoaprendizado e testes
├── tests/
│   └── test_scrapers.py        # Testes automatizados
│
├── README.md
├── STATUS.md                   # Progresso, versões e metas
├── requirements.txt            # Bibliotecas Python necessárias
└── .github/workflows/
    └── deploy.yml              # CI/CD automatizado com Vercel
```

---

## Funcionalidades

- Scraping funcional para milhas/promoções em tempo real
- Painel com histórico de preços e gráficos
- Testes automatizados e self-healing
- Self-improvement com feedback de desempenho
- Deploy automático via GitHub Actions + Vercel
- Bot do Telegram integrado (fase beta)
- Integração com ML e Codex (ativo)

---

## Como Rodar Localmente

### Pré-requisitos
```bash
Python 3.10+
Node.js 18+
```

### Backend
```bash
pip install -r requirements.txt
python scrapers.py
```

### Dashboard
```bash
cd celestia_dashboard
npm install
npm run dev
```

Acesse em: http://localhost:5173

---

## IA Orquestradora (modo Alpha)

- O research_planner.py coordena estratégias de busca
- Avalia desempenho dos scrapers
- Ajusta ou reinicia automaticamente scrapers com erro
- Em breve: integração com Codex Pro para reescrita autônoma de código

---

## Status do Projeto

Veja o progresso em STATUS.md

---

## Deploy

O sistema é implantado via Vercel, com deploys separados para:

- celestia_dashboard
- celest.ia backend

Deploy automático via CI/CD configurado em .github/workflows/deploy.yml

---

## Bot do Telegram

Em desenvolvimento:
- Alerta de promoções
- Consulta por comando (/award, /buscar, etc.)
- Conectado à IA para resposta contextual com histórico

---

## Planejamento e Tarefas

O projeto está organizado em GitHub Projects:

Link: https://github.com/rogeriomonea-del/Celest.ia-v2-Alpha/projects

---

## Licença

MIT – Livre para uso e modificação.

---

## Desenvolvido por

Rogerio Monea  
Com suporte de IA Orquestradora (Codex + Gemini + GPT-4 Turbo)
