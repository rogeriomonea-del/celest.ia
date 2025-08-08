# LATAM/Azul/Smiles — Selenium login + HTTP pós-login (estrutura) + Runner 3 rotas

## O que foi feito
- Adicionados scrapers para **LATAM**, **Azul**, **Smiles** com **Selenium login** e tentativa de **API/HTML pós-login**.
- Adicionado `tools/run_all.py` para executar **GRU→MCO**, **CGH→SDU**, **GRU→LIS** com um comando.
- Teste `test_orchestrator_three_routes.py` garantindo execução do orquestrador nas 3 rotas.

## Notas
- **Endpoints API/seletores estão como placeholders** — devem ser preenchidos com os URLs/endpoints reais observados no DevTools.
- Fluxo estrutural e integração com o **orquestrador dinâmico + telemetria** está pronto.
- Após inserir seletores/URLs reais, rodar `pytest` e `tools/run_all.py` para smoke/end-to-end.

## Próximos passos
- Preencher endpoints reais: LATAM/Azul/Smiles (API e/ou HTML selectors).
- Gravar fixtures HTML (sanitizadas) para testes de regressão de parsing.
- Ativar notificação Telegram ao final de cada run.
