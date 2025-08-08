from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.sql import func
from db.base import Base

class Run(Base):
    __tablename__ = "runs"
    id = Column(Integer, primary_key=True)
    source = Column(String(50), index=True)      # latam, azul, ...
    mode = Column(String(16), index=True)        # http | selenium
    route = Column(String(31), index=True)       # GRU-MCO
    ok = Column(Boolean, default=False, index=True)
    latency_ms = Column(Integer, default=0)
    fail_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
