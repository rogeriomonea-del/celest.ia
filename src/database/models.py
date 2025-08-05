"""Database models for Celes.ia."""
from __future__ import annotations

from typing import Optional, List
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Boolean, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

from ..core.database import Base


class User(Base):
    """User model."""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_user_id = Column(String, unique=True, nullable=True, index=True)
    username = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=True, index=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    preferred_currency = Column(String, default="USD")
    timezone = Column(String, default="UTC")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    searches = relationship("FlightSearch", back_populates="user")
    preferences = relationship("UserPreference", back_populates="user")


class FlightSearch(Base):
    """Flight search history model."""
    __tablename__ = "flight_searches"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    origin = Column(String(3), nullable=False, index=True)
    destination = Column(String(3), nullable=False, index=True)
    departure_date = Column(Date, nullable=False)
    return_date = Column(Date, nullable=True)
    passengers = Column(Integer, default=1)
    search_timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    results_count = Column(Integer, default=0)
    execution_time_ms = Column(Integer, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="searches")
    flights = relationship("Flight", back_populates="search")
    
    # Indexes
    __table_args__ = (
        Index('idx_route_date', 'origin', 'destination', 'departure_date'),
        Index('idx_search_timestamp', 'search_timestamp'),
    )


class Flight(Base):
    """Individual flight result model."""
    __tablename__ = "flights"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    search_id = Column(UUID(as_uuid=True), ForeignKey("flight_searches.id"), nullable=False)
    
    # Flight details
    airline = Column(String, nullable=False)
    flight_number = Column(String, nullable=True)
    origin = Column(String(3), nullable=False)
    destination = Column(String(3), nullable=False)
    departure_time = Column(DateTime, nullable=True)
    arrival_time = Column(DateTime, nullable=True)
    
    # Pricing
    price = Column(Float, nullable=False, index=True)
    currency = Column(String(3), default="USD")
    
    # Additional details
    duration_minutes = Column(Integer, nullable=True)
    stops = Column(Integer, default=0)
    aircraft_type = Column(String, nullable=True)
    booking_url = Column(Text, nullable=True)
    source = Column(String, nullable=False)  # Scraper source
    
    # AI analysis
    ai_score = Column(Float, nullable=True)
    recommendations = Column(JSONB, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    search = relationship("FlightSearch", back_populates="flights")
    
    # Indexes
    __table_args__ = (
        Index('idx_flight_route', 'origin', 'destination'),
        Index('idx_flight_price', 'price'),
        Index('idx_flight_date', 'departure_time'),
    )


class PriceHistory(Base):
    """Historical price data for trend analysis."""
    __tablename__ = "price_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Route information
    origin = Column(String(3), nullable=False, index=True)
    destination = Column(String(3), nullable=False, index=True)
    
    # Price data
    min_price = Column(Float, nullable=False)
    avg_price = Column(Float, nullable=False)
    max_price = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    
    # Metadata
    date = Column(Date, nullable=False, index=True)
    sample_size = Column(Integer, default=1)  # Number of flights sampled
    data_source = Column(String, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_price_route_date', 'origin', 'destination', 'date'),
        Index('idx_price_date', 'date'),
    )


class UserPreference(Base):
    """User preferences and settings."""
    __tablename__ = "user_preferences"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Preference data
    key = Column(String, nullable=False)  # e.g., 'preferred_airlines', 'max_stops'
    value = Column(Text, nullable=True)   # JSON string for complex values
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="preferences")
    
    # Constraints
    __table_args__ = (
        Index('idx_user_preferences', 'user_id', 'key'),
    )


class LoyaltyAccount(Base):
    """User loyalty program accounts."""
    __tablename__ = "loyalty_accounts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Program details
    program_name = Column(String, nullable=False)  # e.g., 'connectmiles'
    account_number = Column(String, nullable=True)
    username = Column(String, nullable=True)
    
    # Balance information (latest)
    available_miles = Column(Integer, nullable=True)
    expiring_miles = Column(Integer, nullable=True)
    expiry_date = Column(Date, nullable=True)
    tier_status = Column(String, nullable=True)
    
    # Metadata
    last_checked = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    balance_history = relationship("MilesBalanceHistory", back_populates="account")


class MilesBalanceHistory(Base):
    """Historical miles balance data."""
    __tablename__ = "miles_balance_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("loyalty_accounts.id"), nullable=False)
    
    # Balance snapshot
    available_miles = Column(Integer, nullable=True)
    expiring_miles = Column(Integer, nullable=True)
    tier_status = Column(String, nullable=True)
    
    # Metadata
    checked_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    account = relationship("LoyaltyAccount", back_populates="balance_history")


class AlertRule(Base):
    """Price alert rules."""
    __tablename__ = "alert_rules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Alert criteria
    origin = Column(String(3), nullable=False)
    destination = Column(String(3), nullable=False)
    max_price = Column(Float, nullable=True)
    preferred_dates = Column(JSONB, nullable=True)  # Flexible date ranges
    
    # Alert settings
    is_active = Column(Boolean, default=True)
    notification_method = Column(String, default="telegram")  # telegram, email
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_triggered = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User")


class AnalysisCache(Base):
    """Cache for AI analysis results."""
    __tablename__ = "analysis_cache"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Cache key
    cache_key = Column(String, nullable=False, unique=True, index=True)
    analysis_type = Column(String, nullable=False)
    
    # Cached data
    results = Column(JSONB, nullable=False)
    confidence = Column(Float, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True, index=True)
    hit_count = Column(Integer, default=0)
