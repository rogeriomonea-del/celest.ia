from google.cloud import tasks_v2
from core.config import settings
from core.logging import logger
from services.scrapers import fetch_prices
from sqlalchemy.orm import Session
from db.base import SessionLocal
from db.models import FlightPrice
import json, asyncio

def enqueue_search_task(origin: str, destination: str, date: str, *, program: str | None = None, cabin: str | None = None, queue: str = "celestia-queue"):
    client = tasks_v2.CloudTasksClient()
    parent = client.queue_path(settings.gcp_project_id, settings.gcp_location, queue)
    if not settings.service_url:
        raise RuntimeError("SERVICE_URL não definido.")

    payload = {"origin": origin, "destination": destination, "date": date, "program": program, "cabin": cabin}
    task = {
        "http_request": {
            "http_method": tasks_v2.HttpMethod.POST,
            "url": f"{settings.service_url.rstrip('/')}/tasks/handler/search",
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(payload).encode("utf-8"),
        }
    }
    res = client.create_task(request={"parent": parent, "task": task})
    logger.info(f"Enqueued: {res.name}")
    return res.name

async def run_search(origin: str, destination: str, date: str):
    results = await fetch_prices(origin, destination, date)
    db: Session = SessionLocal()
    try:
        for r in results:
            fp = FlightPrice(route=r.get("route") or f"{origin}-{destination}",
                             date=date,
                             price=float(r["price"]),
                             currency=r.get("currency") or "BRL",
                             source=r.get("source") or "unknown",
                             cabin=r.get("cabin"),
                             program=r.get("program"),
                             fare_type=r.get("fare_type"),
                             meta=json.dumps(r, ensure_ascii=False))
            db.add(fp)
        db.commit()
    finally:
        db.close()
    return results
