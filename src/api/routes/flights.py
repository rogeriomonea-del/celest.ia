"""Flight search API routes."""
from __future__ import annotations

import time
from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from loguru import logger

from ...core.database import get_db
from ...core.orchestrator import CelestiaOrchestrator
from ...scrapers.airlines.copa import CopaScraper
from ...scrapers.airlines.skyscanner import SkyscannerScraper
from ...scrapers.loyalty.connect_miles import ConnectMilesScraper
from ..models.schemas import (
    FlightSearchRequest,
    FlightSearchResponse,
    MilesBalanceRequest,
    MilesBalanceResponse,
    ErrorResponse
)

router = APIRouter()

# Global orchestrator instance
orchestrator = CelestiaOrchestrator()

# Register scrapers
orchestrator.register_scraper("copa", CopaScraper())
orchestrator.register_scraper("skyscanner", SkyscannerScraper())


@router.post("/search", response_model=FlightSearchResponse)
async def search_flights(
    request: FlightSearchRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Search for flights across multiple sources."""
    start_time = time.time()
    
    logger.info(f"Flight search request: {request.origin} -> {request.destination}")
    
    try:
        # Perform flight search
        flights = await orchestrator.search_flights(
            origin=request.origin,
            destination=request.destination,
            departure_date=request.departure_date,
            return_date=request.return_date,
            passengers=request.passengers
        )
        
        execution_time = int((time.time() - start_time) * 1000)
        
        return FlightSearchResponse(
            flights=flights,
            search_params=request,
            total_results=len(flights),
            search_timestamp=datetime.utcnow(),
            execution_time_ms=execution_time
        )
        
    except Exception as e:
        logger.error(f"Flight search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Flight search failed: {str(e)}")


@router.get("/routes/{origin}/{destination}/trends")
async def get_price_trends(
    origin: str,
    destination: str,
    days_back: int = 30,
    db: Session = Depends(get_db)
):
    """Get price trends for a specific route."""
    logger.info(f"Price trends request: {origin} -> {destination} ({days_back} days)")
    
    try:
        trends = await orchestrator.get_price_trends(
            origin=origin.upper(),
            destination=destination.upper(),
            days_back=days_back
        )
        
        return trends
        
    except Exception as e:
        logger.error(f"Price trends failed: {e}")
        raise HTTPException(status_code=500, detail=f"Price trends analysis failed: {str(e)}")


@router.post("/miles/balance", response_model=MilesBalanceResponse)
async def check_miles_balance(
    request: MilesBalanceRequest,
    db: Session = Depends(get_db)
):
    """Check miles balance for a loyalty program."""
    logger.info(f"Miles balance check: {request.program} for user {request.username}")
    
    if request.program.lower() != "connectmiles":
        raise HTTPException(
            status_code=400,
            detail="Only ConnectMiles program is currently supported"
        )
    
    try:
        async with ConnectMilesScraper() as scraper:
            balance_info = await scraper.get_miles_balance(
                username=request.username,
                password=request.password
            )
        
        if "error" in balance_info:
            return MilesBalanceResponse(
                program=request.program,
                error=balance_info["error"],
                last_updated=datetime.utcnow()
            )
        
        return MilesBalanceResponse(
            program=request.program,
            available_miles=balance_info.get("available_miles"),
            expiring_miles=balance_info.get("expiring_miles"),
            tier_status=balance_info.get("tier_status"),
            last_updated=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Miles balance check failed: {e}")
        return MilesBalanceResponse(
            program=request.program,
            error=str(e),
            last_updated=datetime.utcnow()
        )


@router.get("/airports/search")
async def search_airports(query: str):
    """Search for airports by name or code."""
    # This would typically query a database of airports
    # For now, return a mock response
    mock_airports = [
        {"code": "GRU", "name": "São Paulo/Guarulhos International Airport", "city": "São Paulo", "country": "Brazil"},
        {"code": "GIG", "name": "Rio de Janeiro/Galeão International Airport", "city": "Rio de Janeiro", "country": "Brazil"},
        {"code": "BSB", "name": "Brasília International Airport", "city": "Brasília", "country": "Brazil"},
        {"code": "PTY", "name": "Tocumen International Airport", "city": "Panama City", "country": "Panama"},
        {"code": "JFK", "name": "John F. Kennedy International Airport", "city": "New York", "country": "USA"},
        {"code": "LAX", "name": "Los Angeles International Airport", "city": "Los Angeles", "country": "USA"},
    ]
    
    # Filter airports based on query
    filtered_airports = [
        airport for airport in mock_airports
        if query.lower() in airport["code"].lower() 
        or query.lower() in airport["name"].lower()
        or query.lower() in airport["city"].lower()
    ]
    
    return {"airports": filtered_airports[:10]}  # Limit to 10 results


@router.get("/popular-routes")
async def get_popular_routes():
    """Get popular flight routes."""
    # Mock popular routes - in production, this would come from analytics
    popular_routes = [
        {"origin": "GRU", "destination": "PTY", "origin_city": "São Paulo", "destination_city": "Panama City"},
        {"origin": "GIG", "destination": "JFK", "origin_city": "Rio de Janeiro", "destination_city": "New York"},
        {"origin": "BSB", "destination": "LAX", "origin_city": "Brasília", "destination_city": "Los Angeles"},
        {"origin": "GRU", "destination": "LHR", "origin_city": "São Paulo", "destination_city": "London"},
        {"origin": "GIG", "destination": "CDG", "origin_city": "Rio de Janeiro", "destination_city": "Paris"},
    ]
    
    return {"routes": popular_routes}
