"""Skyscanner scraper implementation."""
from __future__ import annotations

import re
import logging
from typing import List, Dict, Any, Optional
from datetime import date, datetime
from bs4 import BeautifulSoup

from ..base import BaseScraper, FlightInfo

# Use standard logging instead of loguru for better compatibility
logger = logging.getLogger(__name__)


class SkyscannerScraper(BaseScraper):
    """Skyscanner flight scraper."""
    
    def __init__(self):
        """Initialize Skyscanner scraper."""
        super().__init__("skyscanner")
        self.base_url = "https://www.skyscanner.com.br"
    
    async def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: date,
        return_date: Optional[date] = None,
        passengers: int = 1
    ) -> List[Dict[str, Any]]:
        """Search Skyscanner flights."""
        logger.info(f"Searching Skyscanner flights: {origin} -> {destination}")
        
        search_url = self._build_search_url(
            origin, destination, departure_date, return_date, passengers
        )
        
        try:
            response = await self._make_request("GET", search_url)
            flights = await self._parse_flights(response.text, departure_date)
            
            logger.info(f"Found {len(flights)} Skyscanner flights")
            return [self.flight_info_to_dict(flight) for flight in flights]
            
        except Exception as e:
            logger.error(f"Skyscanner scraper error: {e}")
            return []
    
    def _build_search_url(
        self,
        origin: str,
        destination: str,
        departure_date: date,
        return_date: Optional[date],
        passengers: int
    ) -> str:
        """Build search URL for Skyscanner."""
        url = (
            f"{self.base_url}/transport/flights/"
            f"{origin.upper()}/{destination.upper()}/"
            f"{departure_date.strftime('%y%m%d')}/"
        )
        
        if return_date:
            url += f"{return_date.strftime('%y%m%d')}/"
        
        url += f"?adults={passengers}"
        
        return url
    
    async def _parse_flights(
        self,
        html_content: str,
        departure_date: date
    ) -> List[FlightInfo]:
        """Parse flight information from Skyscanner HTML."""
        soup = BeautifulSoup(html_content, 'html.parser')
        flights = []
        
        # Look for flight containers
        flight_containers = soup.find_all('div', class_=[
            'FlightResultItem',
            'flight-result',
            'BpkTicket',
            'fqs-flight-card'
        ])
        
        for container in flight_containers:
            try:
                flight_info = self._extract_flight_info(container, departure_date)
                if flight_info:
                    flights.append(flight_info)
            except Exception as e:
                logger.warning(f"Error parsing Skyscanner flight: {e}")
                continue
        
        # Fallback: regex-based extraction
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
            price_element = container.find(['span', 'div'], class_=re.compile(r'price|fare|cost'))
            if not price_element:
                price_element = container.find(string=re.compile(r'R\$\d+|\$\d+|€\d+'))
            
            price_text = price_element.get_text() if hasattr(price_element, 'get_text') else str(price_element)
            price = self._parse_price(price_text)
            
            if not price:
                return None
            
            # Extract airline
            airline_element = container.find(['img', 'span', 'div'], attrs={'alt': True})
            airline = "Unknown"
            if airline_element:
                airline = airline_element.get('alt', 'Unknown')
            
            # Extract times
            time_elements = container.find_all(['span', 'div'], class_=re.compile(r'time|departure|arrival'))
            departure_time = None
            arrival_time = None
            
            if len(time_elements) >= 2:
                dep_time_text = time_elements[0].get_text().strip()
                arr_time_text = time_elements[1].get_text().strip()
                
                departure_time = self._parse_time_with_date(dep_time_text, departure_date)
                arrival_time = self._parse_time_with_date(arr_time_text, departure_date)
            
            # Extract duration
            duration_element = container.find(['span', 'div'], class_=re.compile(r'duration'))
            duration_text = duration_element.get_text().strip() if duration_element else ""
            duration_minutes = self._parse_duration(duration_text)
            
            # Extract stops
            stops_element = container.find(['span', 'div'], string=re.compile(r'Direct|Non-stop|\d+ stop'))
            stops = 0
            if stops_element:
                stops_text = stops_element.get_text().lower()
                if 'direct' in stops_text or 'non-stop' in stops_text:
                    stops = 0
                else:
                    stops_match = re.search(r'(\d+)', stops_text)
                    stops = int(stops_match.group(1)) if stops_match else 1
            
            # Get origin/destination from container or use defaults
            origin = container.get('data-origin', 'UNK')
            destination = container.get('data-destination', 'UNK')
            
            # Create default datetime if parsing failed
            if departure_time is None:
                departure_time = datetime.combine(departure_date, datetime.min.time())
            if arrival_time is None:
                arrival_time = datetime.combine(departure_date, datetime.min.time())
            
            return FlightInfo(
                airline=airline,
                flight_number="SKY-001",  # Skyscanner doesn't always show flight numbers
                origin=origin,
                destination=destination,
                departure_time=departure_time,
                arrival_time=arrival_time,
                price=price,
                currency="BRL",  # Assuming Brazilian Real for .com.br
                duration_minutes=duration_minutes,
                stops=stops,
                source=self.name
            )
            
        except Exception as e:
            logger.warning(f"Error extracting Skyscanner flight info: {e}")
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
                # Create default datetime
                default_time = datetime.combine(departure_date, datetime.min.time())
                
                flights.append(FlightInfo(
                    airline="Various",
                    flight_number=f"SKY-{i+1:03d}",
                    origin="UNK",
                    destination="UNK",
                    departure_time=default_time,
                    arrival_time=default_time,
                    price=price,
                    currency="BRL",
                    source=self.name
                ))
        
        return flights
    
    def _parse_time_with_date(self, time_text: str, date_obj: date) -> Optional[datetime]:
        """Parse time string and combine with date."""
        try:
            # Clean the time text
            time_text = re.sub(r'[^\d:]', '', time_text)
            
            # Try to parse time in format HH:MM
            time_match = re.search(r'(\d{1,2}):(\d{2})', time_text)
            if time_match:
                hours = int(time_match.group(1))
                minutes = int(time_match.group(2))
                
                # Validate time
                if 0 <= hours <= 23 and 0 <= minutes <= 59:
                    return datetime.combine(date_obj, datetime.min.time().replace(hour=hours, minute=minutes))
            
            return None
        except (ValueError, AttributeError) as e:
            logger.debug(f"Could not parse time '{time_text}': {e}")
            return None
