from core.logging import logger
import asyncio

async def http_then_http_alt(http_call_a, http_call_b, *, budget_errors=2):
    errors = 0
    try:
        res = await http_call_a()
        if res:
            return res
    except Exception as e:
        logger.warning(f"[fallback] HTTP primary failed: {e}")
        errors += 1
        if errors >= budget_errors:
            return []
    try:
        res2 = await http_call_b()
        if res2:
            return res2
    except Exception as e:
        logger.warning(f"[fallback] HTTP alternate failed: {e}")
        errors += 1
    return []
