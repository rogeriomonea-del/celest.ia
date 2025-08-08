# Auto-discovery Pack (Selenium CDP + HTTP handoff + Notifier)

## O que há de novo
- **CDP network capture**: os scrapers LATAM/Azul/Smiles agora capturam **endpoints XHR/fetch** usados pelas páginas e tentam acessá-los via **HTTP pós-login** (cookies do Selenium).
- **Anti-captcha hooks**: base para 2Captcha/Capsolver via envs (`ANTICAPTCHA_PROVIDER`, `ANTICAPTCHA_KEY`).
- **Telegram notifier**: função `notify_telegram()` para enviar um resumo dos melhores resultados após cada run.
- **Pytest markers**: `@pytest.mark.selenium` e `@pytest.mark.integration` + skip automático se Chromium não estiver presente.

## Como usar
1. Defina as credenciais nas envs: `LATAM_USER/PASS`, `AZUL_USER/PASS`, `SMILES_USER/PASS` (Secret Manager no Cloud Run).
2. Execute as rotas via seu task handler (Cloud Tasks) ou chame o orquestrador diretamente.
3. Opcional: configure `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID` para receber resumos.

## Observação
- Os seletores de login são **iniciais** e podem precisar de pequenos ajustes na primeira execução. A vantagem do CDP é **reduzir a necessidade de hardcode de endpoints**.
