from core.logging import logger

# Placeholder simples de gateway LLM (pode conectar OpenAI/Gemini)
async def summarize_prices(prices: list[dict]) -> str:
    logger.info(f"Summarizing {len(prices)} prices via LLM placeholder")
    if not prices:
        return "Sem resultados."
    best = min(prices, key=lambda p: p['price'])
    return f"Melhor preço: {best['price']} para {best['route']} em {best['date']} (fonte: {best['source']})."
