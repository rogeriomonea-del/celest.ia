import asyncio
import json
from services.pipeline import run_search
from db.base import Base, engine, SessionLocal
from sqlalchemy.orm import Session

def setup_module():
    Base.metadata.create_all(bind=engine)

def teardown_module():
    Base.metadata.drop_all(bind=engine)

def test_run_search_persists():
    res = asyncio.run(run_search("GRU","MCO","2025-09-01"))
    assert isinstance(res, list)
    db: Session = SessionLocal()
    try:
        rows = db.execute("SELECT COUNT(*) FROM flight_prices").scalar()
        assert rows >= 0
    finally:
        db.close()
