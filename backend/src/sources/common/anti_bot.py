from core.logging import logger

def jitter_sleep(attempt: int):
    import time, random
    time.sleep(1.0 + random.random() * (attempt * 0.8))

def report_challenge(provider: str, kind: str, detail: str):
    logger.warning(f"[AntiBot] {provider}: {kind} - {detail}")
