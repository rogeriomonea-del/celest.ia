from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from core.config import settings
from core.logging import logger
from db.base import SessionLocal, engine, Base
from db.models import FlightPrice
import hmac
import hashlib
import os

app = FastAPI(title="Celest.ia Backend", version="v2-alpha")

# Create tables if not exists (for simplicity; prefer Alembic in prod)
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health(db: Session = Depends(get_db)):
    # simple query to ensure DB is reachable
    try:
        db.execute("SELECT 1")
    except Exception as e:
        logger.error(f"DB health error: {e}")
        raise HTTPException(status_code=500, detail="DB not healthy")
    return {"status": "ok", "env": settings.env}

@app.post("/bot/webhook")
async def telegram_webhook(request: Request, db: Session = Depends(get_db)):
    # optional secret verification
    secret = settings.telegram_webhook_secret
    if secret:
        header = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if header != secret:
            raise HTTPException(status_code=401, detail="Invalid webhook secret")

    payload = await request.json()
    logger.info(f"Incoming Telegram update: {payload}")

    # Minimal behavior: respond to /ping by inserting a sample record
    message = payload.get("message", {}) or payload.get("edited_message", {})
    text = message.get("text") if isinstance(message, dict) else None
    if text and text.strip().lower().startswith("/ping"):
        p = FlightPrice(route="GRU-MCO", date="2025-09-01", price=1999.0, source="telegram")
        db.add(p)
        db.commit()
        return JSONResponse({"ok": True, "msg": "pong", "id": p.id})

    return JSONResponse({"ok": True})
