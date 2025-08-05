"""Base scraper class with common functionality."""
from __future__ import annotations

import asyncio
import random
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import date, datetime
from dataclasses import dataclass
import httpx

try:
    from ..core.config import settings
except ImportError:
    # Fallback configuration
    class MockScrapingSettings:
        request_timeout = 30
        delay = 2
        max_retries = 3
    
    class MockSettings:
        def __init__(self):
            self.scraping = MockScrapingSettings()
    
    settings = MockSettings()

# Use standard logging
logger = logging.getLogger(__name__)


@dataclass
class FlightInfo:
    """Structured flight information."""
    airline: str
    flight_number: str
    origin: str
    destination: str
    departure_time: datetime
    arrival_time: datetime
    price: float
    currency: str = "USD"
    duration_minutes: Optional[int] = None
    stops: int = 0
    aircraft_type: Optional[str] = None
    booking_url: Optional[str] = None
    source: str = "unknown"


class BaseScraper(ABC):
    """Base class for all flight scrapers."""
    
    def __init__(self, name: str):
        """Initialize base scraper."""
        self.name = name
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }
        self.session: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = httpx.AsyncClient(
            headers=self.headers,
            timeout=settings.scraping.request_timeout,
            follow_redirects=True
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.aclose()
    
    async def _make_request(
        self,
        method: str,
        url: str,
        max_retries: int = 3,
        **kwargs
    ) -> httpx.Response:
        """Make HTTP request with retry logic."""
        if not self.session:
            raise RuntimeError("Scraper not initialized. Use async context manager.")
        
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                logger.debug(f"Making {method} request to {url} (attempt {attempt + 1})")
                
                response = await self.session.request(method, url, **kwargs)
                response.raise_for_status()
                
                # Random delay to avoid rate limiting
                await asyncio.sleep(random.uniform(1, 3))
                
                return response
                
            except Exception as e:
                last_exception = e
                wait_time = 2 ** attempt  # Exponential backoff
                logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
        
        logger.error(f"All {max_retries} attempts failed for {url}")
        raise last_exception or Exception("Request failed after all retries")
    
    @abstractmethod
    async def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: date,
        return_date: Optional[date] = None,
        passengers: int = 1
    ) -> List[Dict[str, Any]]:
        """Search for flights. Must be implemented by subclasses."""
        pass
    
    def _parse_price(self, price_text: str) -> Optional[float]:
        """Parse price from text, handling various formats."""
        if not price_text:
            return None
        
        # Remove currency symbols and extra characters
        import re
        price_clean = re.sub(r'[^\d.,]', '', price_text)
        
        if not price_clean:
            return None
        
        try:
            # Handle different decimal separators
            if ',' in price_clean and '.' in price_clean:
                # Assume comma is thousands separator
                price_clean = price_clean.replace(',', '')
            elif ',' in price_clean:
                # Assume comma is decimal separator (European format)
                price_clean = price_clean.replace(',', '.')
            
            return float(price_clean)
        except ValueError:
            logger.warning(f"Could not parse price: {price_text}")
            return None
    
    def _parse_duration(self, duration_text: str) -> Optional[int]:
        """Parse flight duration to minutes."""
        if not duration_text:
            return None
        
        import re
        
        # Try to match patterns like "2h 30m", "2:30", "150 min"
        hours_match = re.search(r'(\d+)h', duration_text.lower())
        minutes_match = re.search(r'(\d+)m', duration_text.lower())
        
        hours = int(hours_match.group(1)) if hours_match else 0
        minutes = int(minutes_match.group(1)) if minutes_match else 0
        
        if hours == 0 and minutes == 0:
            # Try colon format like "2:30"
            colon_match = re.search(r'(\d+):(\d+)', duration_text)
            if colon_match:
                hours = int(colon_match.group(1))
                minutes = int(colon_match.group(2))
        
        return hours * 60 + minutes if (hours > 0 or minutes > 0) else None
    
    def _parse_datetime(
        self,
        date_str: str,
        time_str: str,
        base_date: Optional[date] = None
    ) -> Optional[datetime]:
        """Parse date and time strings into datetime object."""
        try:
            if base_date:
                # Combine base date with time
                time_str = time_str.strip()
                
                # Try to parse time in format HH:MM
                import re
                time_match = re.search(r'(\d{1,2}):(\d{2})', time_str)
                if time_match:
                    hours = int(time_match.group(1))
                    minutes = int(time_match.group(2))
                    
                    if 0 <= hours <= 23 and 0 <= minutes <= 59:
                        return datetime.combine(base_date, datetime.min.time().replace(hour=hours, minute=minutes))
                
                # If time parsing fails, return default datetime
                return datetime.combine(base_date, datetime.min.time())
            else:
                # Try basic datetime parsing
                datetime_str = f"{date_str} {time_str}"
                return datetime.fromisoformat(datetime_str.replace(' ', 'T'))
                
        except Exception as e:
            logger.warning(f"Could not parse datetime '{date_str} {time_str}': {e}")
            return None
    
    def flight_info_to_dict(self, flight_info: FlightInfo) -> Dict[str, Any]:
        """Convert FlightInfo dataclass to dictionary."""
        return {
            "airline": flight_info.airline,
            "flight_number": flight_info.flight_number,
            "origin": flight_info.origin,
            "destination": flight_info.destination,
            "departure_time": flight_info.departure_time.isoformat() if flight_info.departure_time else None,
            "arrival_time": flight_info.arrival_time.isoformat() if flight_info.arrival_time else None,
            "price": flight_info.price,
            "currency": flight_info.currency,
            "duration_minutes": flight_info.duration_minutes,
            "stops": flight_info.stops,
            "aircraft_type": flight_info.aircraft_type,
            "booking_url": flight_info.booking_url,
            "source": flight_info.source,
        }
