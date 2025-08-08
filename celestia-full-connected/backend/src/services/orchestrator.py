from core.logging import logger
from sqlalchemy.orm import Session
from db.base import SessionLocal
from db.models import FlightPrice

# Simple rule-based summarizer; hook to LLM later
async def summarize_and_rules(limit: int = 20) -> str:
    db: Session = SessionLocal()
    try:
        rows = db.query(FlightPrice).order_by(FlightPrice.id.desc()).limit(limit).all()
        if not rows:
            return "Sem dados recentes."
        best = min(rows, key=lambda r: r.price)
        return f"Melhor atual: {best.price} {best.currency} {best.route} em {best.date} via {best.source}."
    finally:
        db.close()

# Self-healing hints (record failures, try alternate selectors/flows)
def record_failure(context: str, details: str):
    logger.warning(f"[Self-Healing] {context}: {details}")

def record_success(context: str):
    logger.info(f"[Self-Healing] success: {context}")
