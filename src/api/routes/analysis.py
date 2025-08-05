"""Analysis API routes."""
from __future__ import annotations

from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from loguru import logger

from ...core.database import get_db
from ...ai.price_analyzer import PriceAnalyzer
from ...ai.llm_client import LLMClient
from ..models.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    PriceTrendRequest,
    PriceTrendResponse
)

router = APIRouter()

# Global analyzer instances
price_analyzer = PriceAnalyzer()
llm_client = LLMClient()


@router.post("/price-trends", response_model=PriceTrendResponse)
async def analyze_price_trends(
    request: PriceTrendRequest,
    db: Session = Depends(get_db)
):
    """Analyze price trends for a route."""
    logger.info(f"Price trend analysis: {request.origin} -> {request.destination}")
    
    try:
        # In a real implementation, we would fetch historical data from the database
        # For now, we'll use mock data
        mock_historical_data = [
            {"price": 450.0, "timestamp": datetime(2024, 1, 1)},
            {"price": 420.0, "timestamp": datetime(2024, 1, 5)},
            {"price": 480.0, "timestamp": datetime(2024, 1, 10)},
            {"price": 410.0, "timestamp": datetime(2024, 1, 15)},
            {"price": 440.0, "timestamp": datetime(2024, 1, 20)},
            {"price": 390.0, "timestamp": datetime(2024, 1, 25)},
        ]
        
        route = f"{request.origin} -> {request.destination}"
        analysis = await price_analyzer.analyze_price_trends(
            historical_prices=mock_historical_data,
            route=route
        )
        
        return PriceTrendResponse(
            route=route,
            basic_statistics=analysis.get("basic_statistics", {}),
            trend_analysis=analysis.get("trend_analysis", {}),
            ai_insights=analysis.get("ai_insights", {}),
            recommendation=analysis.get("recommendation", {}),
            analysis_timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Price trend analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/compare-sources")
async def compare_booking_sources(
    flight_data: dict,
    db: Session = Depends(get_db)
):
    """Compare prices across different booking sources."""
    logger.info("Comparing booking sources")
    
    try:
        comparison = await price_analyzer.compare_prices_across_sources(flight_data)
        
        return {
            "comparison": comparison,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Source comparison failed: {e}")
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


@router.post("/flights/analyze")
async def analyze_flights(
    flights_data: list,
    db: Session = Depends(get_db)
):
    """Analyze flight options using AI."""
    logger.info(f"Analyzing {len(flights_data)} flights")
    
    try:
        analysis = await llm_client.analyze_flights(flights_data)
        
        return {
            "analysis": analysis,
            "flight_count": len(flights_data),
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Flight analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/general", response_model=AnalysisResponse)
async def general_analysis(
    request: AnalysisRequest,
    db: Session = Depends(get_db)
):
    """Perform general AI analysis on provided data."""
    logger.info(f"General analysis request: {request.analysis_type}")
    
    try:
        # Prepare analysis prompt based on type and data
        if request.analysis_type == "route_optimization":
            prompt = f"Analyze the following route data and provide optimization recommendations: {request.data}"
        elif request.analysis_type == "travel_pattern":
            prompt = f"Analyze travel patterns in the following data: {request.data}"
        elif request.analysis_type == "price_prediction":
            prompt = f"Predict future prices based on this data: {request.data}"
        else:
            prompt = f"Analyze the following data for {request.analysis_type}: {request.data}"
        
        ai_response = await llm_client.analyze(prompt)
        
        try:
            import json
            results = json.loads(ai_response)
        except json.JSONDecodeError:
            results = {"raw_analysis": ai_response}
        
        return AnalysisResponse(
            analysis_type=request.analysis_type,
            results=results,
            confidence=0.8,  # Mock confidence score
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"General analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/market-insights")
async def get_market_insights(
    region: str = "global",
    timeframe: str = "30d",
    db: Session = Depends(get_db)
):
    """Get AI-powered market insights."""
    logger.info(f"Market insights request: {region}, {timeframe}")
    
    try:
        # Mock market data - in production, this would come from real analytics
        mock_market_data = {
            "average_prices": {"domestic": 300, "international": 800},
            "booking_trends": {"advance_booking_days": 45, "peak_season": "December"},
            "popular_destinations": ["PTY", "JFK", "LAX", "LHR"],
            "price_volatility": {"low": ["domestic"], "high": ["international"]}
        }
        
        insights_prompt = f"""
        Analyze the following market data for {region} region over {timeframe}:
        {mock_market_data}
        
        Provide insights on:
        1. Current market trends
        2. Best booking strategies
        3. Price predictions
        4. Seasonal recommendations
        
        Format as actionable insights for travelers.
        """
        
        ai_insights = await llm_client.analyze(insights_prompt)
        
        return {
            "region": region,
            "timeframe": timeframe,
            "market_data": mock_market_data,
            "ai_insights": ai_insights,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Market insights failed: {e}")
        raise HTTPException(status_code=500, detail=f"Insights generation failed: {str(e)}")
