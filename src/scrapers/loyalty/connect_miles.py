"""ConnectMiles loyalty program scraper."""
from __future__ import annotations

import re
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
from loguru import logger

from ..base import BaseScraper


class ConnectMilesScraper(BaseScraper):
    """ConnectMiles loyalty program scraper."""
    
    def __init__(self):
        """Initialize ConnectMiles scraper."""
        super().__init__("connect_miles")
        self.base_url = "https://www.connectmiles.com"
        self.login_url = f"{self.base_url}/login"
        self.account_url = f"{self.base_url}/account"
    
    async def get_miles_balance(
        self,
        username: str,
        password: str
    ) -> Dict[str, Any]:
        """Get miles balance for a user account."""
        logger.info(f"Getting ConnectMiles balance for user: {username}")
        
        try:
            # Get login page for CSRF token
            login_response = await self._make_request("GET", self.login_url)
            csrf_token = self._extract_csrf_token(login_response.text)
            
            # Login
            login_data = {
                "username": username,
                "password": password,
                "csrf_token": csrf_token
            }
            
            await self._make_request("POST", self.login_url, data=login_data)
            
            # Get account page
            account_response = await self._make_request("GET", self.account_url)
            balance_info = self._parse_balance(account_response.text)
            
            logger.info(f"Successfully retrieved balance: {balance_info.get('available_miles', 'N/A')} miles")
            return balance_info
            
        except Exception as e:
            logger.error(f"ConnectMiles scraper error: {e}")
            return {"error": str(e)}
    
    def _extract_csrf_token(self, html_content: str) -> str:
        """Extract CSRF token from login page."""
        soup = BeautifulSoup(html_content, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrf_token'})
        
        if csrf_input:
            return csrf_input.get('value', '')
        
        # Fallback: regex extraction
        token_match = re.search(r'name="csrf_token" value="([^"]+)"', html_content)
        return token_match.group(1) if token_match else ""
    
    def _parse_balance(self, html_content: str) -> Dict[str, Any]:
        """Parse miles balance from account page."""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Look for available miles
        available_miles = self._extract_available_miles(soup, html_content)
        
        # Look for additional balance information
        balance_info = {
            "available_miles": available_miles,
            "source": self.name,
            "last_updated": None
        }
        
        # Try to extract expiring miles
        expiring_element = soup.find(id="expiring-miles")
        if expiring_element:
            expiring_text = expiring_element.get_text().strip()
            balance_info["expiring_miles"] = self._parse_miles_number(expiring_text)
        
        # Try to extract tier status
        tier_element = soup.find(['span', 'div'], class_=re.compile(r'tier|status|level'))
        if tier_element:
            balance_info["tier_status"] = tier_element.get_text().strip()
        
        return balance_info
    
    def _extract_available_miles(self, soup: BeautifulSoup, html_content: str) -> Optional[str]:
        """Extract available miles from the page."""
        # Try to find by ID first
        miles_element = soup.find(id="available-miles")
        if miles_element:
            return miles_element.get_text().strip()
        
        # Try to find by class
        miles_element = soup.find(['span', 'div'], class_=re.compile(r'available-miles|miles-balance|balance'))
        if miles_element:
            return miles_element.get_text().strip()
        
        # Fallback: regex extraction (from original scrapers.py)
        balance_match = re.search(r'id="available-miles">([^<]+)<', html_content)
        if balance_match:
            return balance_match.group(1).strip()
        
        # Try other common patterns
        miles_patterns = [
            r'available.*?(\d{1,3}(?:,\d{3})*)',
            r'balance.*?(\d{1,3}(?:,\d{3})*)',
            r'miles.*?(\d{1,3}(?:,\d{3})*)'
        ]
        
        for pattern in miles_patterns:
            match = re.search(pattern, html_content, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _parse_miles_number(self, miles_text: str) -> Optional[int]:
        """Parse miles number from text."""
        if not miles_text:
            return None
        
        # Remove non-numeric characters except commas and periods
        clean_text = re.sub(r'[^\d,.]', '', miles_text)
        
        if not clean_text:
            return None
        
        try:
            # Remove commas (thousands separators)
            number_str = clean_text.replace(',', '')
            return int(float(number_str))
        except ValueError:
            logger.warning(f"Could not parse miles number: {miles_text}")
            return None
    
    async def search_flights(self, origin: str, destination: str, departure_date, return_date=None, passengers: int = 1):
        """Not applicable for loyalty scraper."""
        raise NotImplementedError("ConnectMiles scraper is for balance checking, not flight search")
