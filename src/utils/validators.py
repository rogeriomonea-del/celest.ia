"""Data validation utilities."""
from __future__ import annotations

import re
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from email_validator import validate_email, EmailNotValidError


def validate_airport_code(code: str) -> bool:
    """Validate IATA airport code format."""
    if not code or len(code) != 3:
        return False
    return code.isalpha() and code.isupper()


def validate_date_format(date_str: str, format: str = "%Y-%m-%d") -> Optional[date]:
    """Validate and parse date string."""
    try:
        return datetime.strptime(date_str, format).date()
    except ValueError:
        return None


def validate_email_format(email: str) -> bool:
    """Validate email format."""
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False


def validate_phone_number(phone: str) -> bool:
    """Validate phone number format."""
    # Simple regex for international phone numbers
    pattern = r'^\+?1?[0-9]{10,15}$'
    return bool(re.match(pattern, phone.replace(' ', '').replace('-', '')))


def validate_currency_code(currency: str) -> bool:
    """Validate ISO currency code."""
    if not currency or len(currency) != 3:
        return False
    
    # Common currency codes
    valid_currencies = {
        'USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY',
        'BRL', 'MXN', 'ARS', 'COP', 'PEN', 'CLP', 'UYU'
    }
    
    return currency.upper() in valid_currencies


def validate_passenger_count(count: int) -> bool:
    """Validate passenger count."""
    return isinstance(count, int) and 1 <= count <= 9


def validate_flight_search_params(params: Dict[str, Any]) -> List[str]:
    """Validate flight search parameters and return list of errors."""
    errors = []
    
    # Required fields
    required_fields = ['origin', 'destination', 'departure_date']
    for field in required_fields:
        if field not in params or not params[field]:
            errors.append(f"Missing required field: {field}")
    
    # Airport codes
    if 'origin' in params and not validate_airport_code(params['origin']):
        errors.append("Invalid origin airport code")
    
    if 'destination' in params and not validate_airport_code(params['destination']):
        errors.append("Invalid destination airport code")
    
    # Same origin and destination
    if (params.get('origin') and params.get('destination') and 
        params['origin'].upper() == params['destination'].upper()):
        errors.append("Origin and destination cannot be the same")
    
    # Departure date
    if 'departure_date' in params:
        if isinstance(params['departure_date'], str):
            parsed_date = validate_date_format(params['departure_date'])
            if not parsed_date:
                errors.append("Invalid departure date format (use YYYY-MM-DD)")
            elif parsed_date < date.today():
                errors.append("Departure date cannot be in the past")
        elif isinstance(params['departure_date'], date):
            if params['departure_date'] < date.today():
                errors.append("Departure date cannot be in the past")
    
    # Return date
    if 'return_date' in params and params['return_date']:
        if isinstance(params['return_date'], str):
            parsed_return = validate_date_format(params['return_date'])
            if not parsed_return:
                errors.append("Invalid return date format (use YYYY-MM-DD)")
            elif 'departure_date' in params:
                parsed_departure = validate_date_format(params['departure_date'])
                if parsed_departure and parsed_return <= parsed_departure:
                    errors.append("Return date must be after departure date")
        elif isinstance(params['return_date'], date):
            if 'departure_date' in params and isinstance(params['departure_date'], date):
                if params['return_date'] <= params['departure_date']:
                    errors.append("Return date must be after departure date")
    
    # Passenger count
    if 'passengers' in params and not validate_passenger_count(params['passengers']):
        errors.append("Invalid passenger count (must be 1-9)")
    
    return errors


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Sanitize user input."""
    if not text:
        return ""
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', str(text))
    
    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized.strip()


def validate_price_range(min_price: Optional[float], max_price: Optional[float]) -> List[str]:
    """Validate price range parameters."""
    errors = []
    
    if min_price is not None:
        if not isinstance(min_price, (int, float)) or min_price < 0:
            errors.append("Minimum price must be a positive number")
    
    if max_price is not None:
        if not isinstance(max_price, (int, float)) or max_price < 0:
            errors.append("Maximum price must be a positive number")
    
    if (min_price is not None and max_price is not None and 
        min_price >= max_price):
        errors.append("Minimum price must be less than maximum price")
    
    return errors


def validate_telegram_data(data: Dict[str, Any]) -> List[str]:
    """Validate Telegram webhook data."""
    errors = []
    
    # Check required fields
    if 'update_id' not in data:
        errors.append("Missing update_id")
    
    if 'message' not in data and 'callback_query' not in data:
        errors.append("Missing message or callback_query")
    
    # Validate message structure
    if 'message' in data:
        message = data['message']
        if 'from' not in message:
            errors.append("Missing sender information")
        if 'chat' not in message:
            errors.append("Missing chat information")
    
    return errors


def normalize_airport_code(code: str) -> str:
    """Normalize airport code to standard format."""
    if not code:
        return ""
    
    normalized = code.strip().upper()
    
    # Remove common prefixes/suffixes
    if normalized.startswith('IATA:'):
        normalized = normalized[5:]
    
    return normalized if validate_airport_code(normalized) else ""


def format_price(price: float, currency: str = "USD") -> str:
    """Format price for display."""
    if currency.upper() == "USD":
        return f"${price:.2f}"
    elif currency.upper() == "EUR":
        return f"€{price:.2f}"
    elif currency.upper() == "GBP":
        return f"£{price:.2f}"
    elif currency.upper() == "BRL":
        return f"R${price:.2f}"
    else:
        return f"{currency} {price:.2f}"


def parse_duration(duration_str: str) -> Optional[int]:
    """Parse duration string to minutes."""
    if not duration_str:
        return None
    
    # Try various formats
    patterns = [
        r'(\d+)h\s*(\d+)m',  # 2h 30m
        r'(\d+):(\d+)',      # 2:30
        r'(\d+)h',           # 2h
        r'(\d+)m',           # 30m
        r'(\d+)\s*min',      # 150 min
    ]
    
    for pattern in patterns:
        match = re.search(pattern, duration_str.lower())
        if match:
            if len(match.groups()) == 2:
                hours, minutes = match.groups()
                return int(hours) * 60 + int(minutes)
            else:
                value = int(match.group(1))
                if 'h' in pattern:
                    return value * 60
                else:
                    return value
    
    return None
