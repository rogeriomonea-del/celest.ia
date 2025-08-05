"""Copa Airlines scraper implementation."""
from __future__ import annotations

import re
from typing import List, Dict, Any, Optional
from datetime import date, datetime
from bs4 import BeautifulSoup
from loguru import logger

from ..base import BaseScraper, FlightInfo


class CopaScraper(BaseScraper):
    """Copa Airlines flight scraper."""
    
    def __init__(self):
        """Initialize Copa scraper."""
        super().__init__("copa_airlines")
        self.base_url = "https://www.copaair.com"
    
    async def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: date,
        return_date: Optional[date] = None,
        passengers: int = 1
    ) -> List[Dict[str, Any]]:
        """Search Copa Airlines flights."""
        logger.info(f"Searching Copa flights: {origin} -> {destination}")
        
        search_url = self._build_search_url(
            origin, destination, departure_date, return_date, passengers
        )
        
        try:
            response = await self._make_request("GET", search_url)
            flights = await self._parse_flights(response.text, departure_date)
            
            logger.info(f"Found {len(flights)} Copa flights")
            return [self.flight_info_to_dict(flight) for flight in flights]
            
        except Exception as e:
            logger.error(f"Copa scraper error: {e}")
            return []
    
    def _build_search_url(
        self,
        origin: str,
        destination: str,
        departure_date: date,
        return_date: Optional[date],
        passengers: int
    ) -> str:
        """Build search URL for Copa Airlines."""
        trip_type = "RT" if return_date else "OW"
        
        url = (
            f"{self.base_url}/en-us/flights/"
            f"{origin.upper()}-{destination.upper()}"
            f"?departure={departure_date.strftime('%Y-%m-%d')}"
        )
        
        if return_date:
            url += f"&return={return_date.strftime('%Y-%m-%d')}"
        
        url += f"&passengers={passengers}&tripType={trip_type}"
        
        return url
    
    async def _parse_flights(
        self,
        html_content: str,
        departure_date: date
    ) -> List[FlightInfo]:
        """Parse flight information from Copa Airlines HTML."""
        soup = BeautifulSoup(html_content, 'html.parser')
        flights = []
        
        # Look for flight containers (this is a simplified example)
        flight_containers = soup.find_all('div', class_=['flight-option', 'flight-card', 'cm-flight-card'])
        
        for container in flight_containers:
            try:
                flight_info = self._extract_flight_info(container, departure_date)
                if flight_info:
                    flights.append(flight_info)
            except Exception as e:
                logger.warning(f"Error parsing Copa flight: {e}")
                continue
        
        # Fallback: try regex-based extraction for price patterns
        if not flights:
            flights.extend(self._extract_with_regex(html_content, departure_date))
        
        return flights
    
    def _extract_flight_info(
        self,
        container,
        departure_date: date
    ) -> Optional[FlightInfo]:
        """Extract flight information from a container element."""
        try:
            # Extract price
            price_element = container.find(['span', 'div'], class_=re.compile(r'price|fare|amount'))
            if not price_element:
                price_element = container.find(string=re.compile(r'\$\d+|\d+\.\d+'))
            
            price_text = price_element.get_text() if hasattr(price_element, 'get_text') else str(price_element)
            price = self._parse_price(price_text)
            
            if not price:
                return None
            
            # Extract times
            time_elements = container.find_all(['span', 'div'], class_=re.compile(r'time|departure|arrival'))
            departure_time = None
            arrival_time = None
            
            if len(time_elements) >= 2:
                dep_time_text = time_elements[0].get_text().strip()
                arr_time_text = time_elements[1].get_text().strip()
                
                departure_time = self._parse_datetime("", dep_time_text, departure_date)
                arrival_time = self._parse_datetime("", arr_time_text, departure_date)
            
            # Extract flight number
            flight_num_element = container.find(['span', 'div'], class_=re.compile(r'flight-number|flight-code'))
            flight_number = flight_num_element.get_text().strip() if flight_num_element else "CM-XXX"
            
            # Extract duration
            duration_element = container.find(['span', 'div'], class_=re.compile(r'duration|time-duration'))
            duration_text = duration_element.get_text().strip() if duration_element else ""
            duration_minutes = self._parse_duration(duration_text)
            
            return FlightInfo(
                airline="Copa Airlines",
                flight_number=flight_number,
                origin=container.get('data-origin', 'UNK'),
                destination=container.get('data-destination', 'UNK'),
                departure_time=departure_time,
                arrival_time=arrival_time,
                price=price,
                currency="USD",
                duration_minutes=duration_minutes,
                stops=0,  # Assume direct flight unless specified
                source=self.name
            )
            
        except Exception as e:
            logger.warning(f"Error extracting Copa flight info: {e}")
            return None
    
    def _extract_with_regex(
        self,
        html_content: str,
        departure_date: date
    ) -> List[FlightInfo]:
        """Fallback regex-based extraction."""
        flights = []
        
        # Extract prices using regex (from original scrapers.py)
        price_matches = re.findall(r'class="price">([^<]+)<', html_content)
        
        for i, price_text in enumerate(price_matches):
            price = self._parse_price(price_text)
            if price:
                flights.append(FlightInfo(
                    airline="Copa Airlines",
                    flight_number=f"CM-{i+1:03d}",
                    origin="UNK",
                    destination="UNK",
                    departure_time=None,
                    arrival_time=None,
                    price=price,
                    currency="USD",
                    source=self.name
                ))
        
        return flights
