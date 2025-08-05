"""Main orchestrator for Celes.ia AI system."""
from __future__ import annotations

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, date
from loguru import logger

from ..ai.llm_client import LLMClient
from ..scrapers.base import BaseScraper
from ..database.repositories import FlightRepository, UserRepository
from ..utils.logging import setup_logging


class CelestiaOrchestrator:
    """Main AI orchestrator for flight search and analysis."""
    
    def __init__(self):
        """Initialize the orchestrator with required components."""
        setup_logging()
        self.llm_client = LLMClient()
        self.flight_repo = FlightRepository()
        self.user_repo = UserRepository()
        self.scrapers: Dict[str, BaseScraper] = {}
        
    def register_scraper(self, name: str, scraper: BaseScraper) -> None:
        """Register a new scraper with the orchestrator."""
        self.scrapers[name] = scraper
        logger.info(f"Registered scraper: {name}")
    
    async def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: date,
        return_date: Optional[date] = None,
        passengers: int = 1
    ) -> List[Dict[str, Any]]:
        """Orchestrate flight search across multiple sources."""
        logger.info(f"Starting flight search: {origin} -> {destination} on {departure_date}")
        
        # Collect flight data from all scrapers
        all_flights = []
        tasks = []
        
        for scraper_name, scraper in self.scrapers.items():
            task = self._scrape_with_error_handling(
                scraper, scraper_name, origin, destination, departure_date
            )
            tasks.append(task)
        
        # Execute all scraping tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for scraper_name, result in zip(self.scrapers.keys(), results):
            if isinstance(result, Exception):
                logger.error(f"Scraper {scraper_name} failed: {result}")
            elif result:
                all_flights.extend(result)
        
        # Analyze and rank flights using AI
        if all_flights:
            analyzed_flights = await self._analyze_flights(all_flights)
            
            # Store results in database
            await self._store_flight_data(analyzed_flights, origin, destination, departure_date)
            
            return analyzed_flights
        
        logger.warning("No flights found from any scraper")
        return []
    
    async def _scrape_with_error_handling(
        self,
        scraper: BaseScraper,
        scraper_name: str,
        origin: str,
        destination: str,
        departure_date: date
    ) -> List[Dict[str, Any]]:
        """Execute scraping with error handling and retries."""
        try:
            return await scraper.search_flights(origin, destination, departure_date)
        except Exception as e:
            logger.error(f"Error in {scraper_name}: {e}")
            return []
    
    async def _analyze_flights(self, flights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Use AI to analyze and enhance flight data."""
        logger.info(f"Analyzing {len(flights)} flights with AI")
        
        # Prepare data for AI analysis
        flight_summary = self._prepare_flight_summary(flights)
        
        # Get AI insights
        analysis_prompt = f"""
        Analyze the following flight data and provide insights:
        
        {flight_summary}
        
        Please provide:
        1. Best value flights (price vs convenience)
        2. Fastest routes
        3. Most convenient schedules
        4. Price trends and recommendations
        5. Risk assessment for each option
        
        Return your analysis in JSON format.
        """
        
        try:
            ai_analysis = await self.llm_client.analyze(analysis_prompt)
            
            # Enhance flight data with AI insights
            for flight in flights:
                flight['ai_score'] = self._calculate_ai_score(flight, ai_analysis)
                flight['recommendations'] = self._extract_recommendations(flight, ai_analysis)
            
            # Sort by AI score
            flights.sort(key=lambda x: x.get('ai_score', 0), reverse=True)
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            # Fallback to simple price sorting
            flights.sort(key=lambda x: x.get('price', float('inf')))
        
        return flights
    
    def _prepare_flight_summary(self, flights: List[Dict[str, Any]]) -> str:
        """Prepare a summary of flights for AI analysis."""
        summary_lines = []
        for i, flight in enumerate(flights[:10]):  # Limit to top 10 for analysis
            summary_lines.append(
                f"Flight {i+1}: {flight.get('airline', 'Unknown')} - "
                f"${flight.get('price', 'N/A')} - "
                f"{flight.get('departure_time', 'N/A')} to {flight.get('arrival_time', 'N/A')} - "
                f"Duration: {flight.get('duration', 'N/A')}"
            )
        return "\n".join(summary_lines)
    
    def _calculate_ai_score(self, flight: Dict[str, Any], ai_analysis: str) -> float:
        """Calculate AI-based score for a flight."""
        # Simple scoring based on price and basic factors
        # In a real implementation, this would use the AI analysis
        base_score = 50.0
        
        # Price factor (lower price = higher score)
        price = flight.get('price', 1000)
        if isinstance(price, (int, float)) and price > 0:
            price_score = max(0, 50 - (price / 20))
            base_score += price_score
        
        # Duration factor (shorter = better)
        duration = flight.get('duration_minutes', 600)
        if isinstance(duration, (int, float)) and duration > 0:
            duration_score = max(0, 30 - (duration / 20))
            base_score += duration_score
        
        return min(100.0, base_score)
    
    def _extract_recommendations(self, flight: Dict[str, Any], ai_analysis: str) -> List[str]:
        """Extract recommendations for a specific flight."""
        # Placeholder implementation
        recommendations = []
        
        price = flight.get('price', 0)
        if isinstance(price, (int, float)) and price < 500:
            recommendations.append("Great value for money!")
        
        duration = flight.get('duration_minutes', 0)
        if isinstance(duration, (int, float)) and duration < 360:
            recommendations.append("Quick flight option")
        
        return recommendations
    
    async def _store_flight_data(
        self,
        flights: List[Dict[str, Any]],
        origin: str,
        destination: str,
        departure_date: date
    ) -> None:
        """Store flight data in the database."""
        try:
            for flight in flights:
                await self.flight_repo.create_flight({
                    **flight,
                    'origin': origin,
                    'destination': destination,
                    'departure_date': departure_date,
                    'search_timestamp': datetime.utcnow()
                })
            logger.info(f"Stored {len(flights)} flights in database")
        except Exception as e:
            logger.error(f"Failed to store flight data: {e}")
    
    async def get_price_trends(
        self,
        origin: str,
        destination: str,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """Get price trends and predictions for a route."""
        historical_data = await self.flight_repo.get_price_history(
            origin, destination, days_back
        )
        
        if not historical_data:
            return {"error": "No historical data available"}
        
        # Use AI to analyze trends
        trend_prompt = f"""
        Analyze the following price trend data for flights from {origin} to {destination}:
        
        {historical_data}
        
        Provide:
        1. Current trend (increasing/decreasing/stable)
        2. Best time to book
        3. Price prediction for next 2 weeks
        4. Seasonal patterns if any
        
        Return analysis in JSON format.
        """
        
        try:
            trend_analysis = await self.llm_client.analyze(trend_prompt)
            return {
                "historical_data": historical_data,
                "ai_analysis": trend_analysis,
                "route": f"{origin} -> {destination}"
            }
        except Exception as e:
            logger.error(f"Trend analysis failed: {e}")
            return {
                "historical_data": historical_data,
                "error": "AI analysis unavailable"
            }
