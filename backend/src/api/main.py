from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from core.config import settings
from core.logging import logger
from db.base import SessionLocal, engine, Base
from db.models import FlightPrice
from api.schemas import SearchRequest
from services.pipeline import enqueue_search_task
from services.orchestrator import summarize_and_rules
import hmac

app = FastAPI(title="Celest.ia Backend", version="v2-alpha")

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
    except Exception as e:
        logger.error(f"DB health error: {e}")
        raise HTTPException(status_code=500, detail="DB not healthy")
    return {"status": "ok", "env": settings.env}

@app.post("/bot/webhook")
async def telegram_webhook(request: Request):
    secret = settings.telegram_webhook_secret
    if secret and request.headers.get("X-Telegram-Bot-Api-Secret-Token") != secret:
        raise HTTPException(status_code=401, detail="Invalid webhook secret")

    payload = await request.json()
    message = payload.get("message", {}) or payload.get("edited_message", {})
    text = message.get("text") if isinstance(message, dict) else None

    if not text:
        return {"ok": True}

    parts = text.split()
    cmd = parts[0].lower()

    if cmd == "/search" and len(parts) >= 4:
        _, o, d, date = parts[:4]
        enqueue_search_task(o, d, date)
        return {"ok": True, "queued": True}

    if cmd == "/best":
        # simple summarizer over recent data
        out = await summarize_and_rules(limit=20)
        return {"ok": True, "summary": out}

    return {"ok": True}

@app.post("/search/enqueue")
def search_enqueue(req: SearchRequest):
    enqueue_search_task(req.origin, req.destination, req.departure_date, program=req.program, cabin=req.cabin)
    return {"queued": True}
