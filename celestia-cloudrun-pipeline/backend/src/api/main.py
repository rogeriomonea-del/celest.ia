from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from core.config import settings
from core.logging import logger
from db.base import SessionLocal, engine, Base
from db.models import FlightPrice
from api.schemas import SearchRequest
from services.scrapers import fetch_prices
from services.llm import summarize_prices
from tasks.cloudtasks import enqueue_task
import hmac
import hashlib
import os
import json
import asyncio

app = FastAPI(title="Celest.ia Backend", version="v2-alpha")

# Create tables if not exists (prefer Alembic for migration, kept here for first run)
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

# ------------ Telegram webhook ---------------
@app.post("/bot/webhook")
async def telegram_webhook(request: Request, db: Session = Depends(get_db)):
    secret = settings.telegram_webhook_secret
    if secret:
        header = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if header != secret:
            raise HTTPException(status_code=401, detail="Invalid webhook secret")

    payload = await request.json()
    logger.info(f"Incoming Telegram update: {payload}")

    message = payload.get("message", {}) or payload.get("edited_message", {})
    text = message.get("text") if isinstance(message, dict) else None
    if text and text.strip().lower().startswith("/search"):
        # formato: /search GRU MCO 2025-09-01
        parts = text.split()
        if len(parts) >= 4:
            _, o, d, date = parts[:4]
            task_name = enqueue_task("/tasks/handler/search", {"origin": o, "destination": d, "date": date})
            return JSONResponse({"ok": True, "task": task_name})
        return JSONResponse({"ok": False, "msg": "Uso: /search ORIG DEST YYYY-MM-DD"})

    if text and text.strip().lower().startswith("/ping"):
        p = FlightPrice(route="GRU-MCO", date="2025-09-01", price=1999.0, source="telegram")
        db.add(p); db.commit()
        return JSONResponse({"ok": True, "msg": "pong", "id": p.id})

    return JSONResponse({"ok": True})

# ------------ API de busca (enqueue) ---------------
@app.post("/search/enqueue")
def search_enqueue(req: SearchRequest):
    task_name = enqueue_task("/tasks/handler/search", {"origin": req.origin, "destination": req.destination, "date": req.departure_date})
    return {"queued": True, "task": task_name}

# ------------ Cloud Tasks Handler ------------------
@app.post("/tasks/handler/search")
async def task_handler(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()
    origin = payload["origin"]
    destination = payload["destination"]
    date = payload["date"]

    results = await fetch_prices(origin, destination, date)
    # Persistir
    for r in results:
        p = FlightPrice(route=r["route"], date=r["date"], price=r["price"], source=r["source"], meta=None)
        db.add(p)
    db.commit()

    summary = await summarize_prices(results)
    return {"ok": True, "summary": summary, "count": len(results)}
