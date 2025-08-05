"""Pydantic schemas for API requests and responses."""
from __future__ import annotations

from typing import Optional, List, Dict, Any
from datetime import date, datetime
from pydantic import BaseModel, Field, validator


class FlightSearchRequest(BaseModel):
    """Flight search request schema."""
    origin: str = Field(..., description="Origin airport code", min_length=3, max_length=3)
    destination: str = Field(..., description="Destination airport code", min_length=3, max_length=3)
    departure_date: date = Field(..., description="Departure date")
    return_date: Optional[date] = Field(None, description="Return date for round trip")
    passengers: int = Field(1, description="Number of passengers", ge=1, le=9)
    
    @validator('origin', 'destination')
    def validate_airport_codes(cls, v):
        """Validate airport codes are uppercase."""
        return v.upper()
    
    @validator('departure_date')
    def validate_departure_date(cls, v):
        """Validate departure date is not in the past."""
        if v < date.today():
            raise ValueError('Departure date cannot be in the past')
        return v
    
    @validator('return_date')
    def validate_return_date(cls, v, values):
        """Validate return date is after departure date."""
        if v and 'departure_date' in values and v <= values['departure_date']:
            raise ValueError('Return date must be after departure date')
        return v


class FlightInfo(BaseModel):
    """Flight information schema."""
    airline: str
    flight_number: str
    origin: str
    destination: str
    departure_time: Optional[datetime]
    arrival_time: Optional[datetime]
    price: float
    currency: str = "USD"
    duration_minutes: Optional[int]
    stops: int = 0
    aircraft_type: Optional[str]
    booking_url: Optional[str]
    source: str
    ai_score: Optional[float] = None
    recommendations: List[str] = []


class FlightSearchResponse(BaseModel):
    """Flight search response schema."""
    flights: List[FlightInfo]
    search_params: FlightSearchRequest
    total_results: int
    search_timestamp: datetime
    execution_time_ms: int


class PriceTrendRequest(BaseModel):
    """Price trend analysis request schema."""
    origin: str = Field(..., min_length=3, max_length=3)
    destination: str = Field(..., min_length=3, max_length=3)
    days_back: int = Field(30, description="Number of days to look back", ge=1, le=365)
    
    @validator('origin', 'destination')
    def validate_airport_codes(cls, v):
        """Validate airport codes are uppercase."""
        return v.upper()


class PriceTrendResponse(BaseModel):
    """Price trend analysis response schema."""
    route: str
    basic_statistics: Dict[str, float]
    trend_analysis: Dict[str, Any]
    ai_insights: Dict[str, Any]
    recommendation: Dict[str, Any]
    analysis_timestamp: datetime


class MilesBalanceRequest(BaseModel):
    """Miles balance check request schema."""
    program: str = Field(..., description="Loyalty program name")
    username: str = Field(..., description="Program username")
    password: str = Field(..., description="Program password")


class MilesBalanceResponse(BaseModel):
    """Miles balance response schema."""
    program: str
    available_miles: Optional[str]
    expiring_miles: Optional[int]
    tier_status: Optional[str]
    last_updated: Optional[datetime]
    error: Optional[str]


class AnalysisRequest(BaseModel):
    """General analysis request schema."""
    data: Dict[str, Any] = Field(..., description="Data to analyze")
    analysis_type: str = Field(..., description="Type of analysis to perform")
    options: Dict[str, Any] = Field(default_factory=dict, description="Analysis options")


class AnalysisResponse(BaseModel):
    """General analysis response schema."""
    analysis_type: str
    results: Dict[str, Any]
    confidence: Optional[float]
    timestamp: datetime


class TelegramWebhookUpdate(BaseModel):
    """Telegram webhook update schema."""
    update_id: int
    message: Optional[Dict[str, Any]] = None
    callback_query: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Error response schema."""
    error: str
    detail: str
    timestamp: datetime
    request_id: Optional[str] = None


class SuccessResponse(BaseModel):
    """Success response schema."""
    success: bool = True
    message: str
    timestamp: datetime
    data: Optional[Dict[str, Any]] = None
