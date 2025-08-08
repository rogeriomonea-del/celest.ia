from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from db.base import Base

class FlightPrice(Base):
    __tablename__ = "flight_prices"
    id = Column(Integer, primary_key=True, index=True)
    route = Column(String(31), index=True)  # e.g., GRU-MCO
    date = Column(String(10), index=True)   # YYYY-MM-DD
    price = Column(Float, nullable=False)
    source = Column(String(50), index=True)
    meta = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
