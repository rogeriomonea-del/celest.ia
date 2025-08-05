#!/usr/bin/env python3
"""
Test script for Skyscanner scraper functionality
"""

import asyncio
import sys
import os
from datetime import date, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.scrapers.airlines.skyscanner import SkyscannerScraper

async def test_skyscanner_scraper():
    """Test Skyscanner scraper functionality."""
    print("🧪 Testing Skyscanner Scraper...")
    
    # Test 1: Initialize scraper
    print("\n1️⃣ Testing scraper initialization:")
    scraper = SkyscannerScraper()
    print(f"   Scraper name: {scraper.name}")
    print(f"   Base URL: {scraper.base_url}")
    
    # Test 2: URL building
    print("\n2️⃣ Testing URL building:")
    departure_date = date.today() + timedelta(days=30)
    return_date = departure_date + timedelta(days=7)
    
    url = scraper._build_search_url(
        origin="GRU",
        destination="MIA", 
        departure_date=departure_date,
        return_date=return_date,
        passengers=2
    )
    print(f"   Search URL: {url}")
    
    # Test 3: Price parsing
    print("\n3️⃣ Testing price parsing:")
    test_prices = [
        "R$ 1.234,56",
        "$567.89",
        "€ 890,12",
        "1234",
        "invalid price"
    ]
    
    for price_text in test_prices:
        parsed = scraper._parse_price(price_text)
        print(f"   '{price_text}' -> {parsed}")
    
    # Test 4: Duration parsing
    print("\n4️⃣ Testing duration parsing:")
    test_durations = [
        "2h 30m",
        "1h 45m",
        "5:30",
        "180 min",
        "invalid duration"
    ]
    
    for duration_text in test_durations:
        parsed = scraper._parse_duration(duration_text)
        print(f"   '{duration_text}' -> {parsed} minutes")
    
    # Test 5: Time parsing
    print("\n5️⃣ Testing time parsing:")
    test_times = [
        "14:30",
        "09:15",
        "23:45",
        "invalid time"
    ]
    
    test_date = date.today()
    for time_text in test_times:
        parsed = scraper._parse_time_with_date(time_text, test_date)
        print(f"   '{time_text}' on {test_date} -> {parsed}")
    
    # Test 6: Context manager (mock test)
    print("\n6️⃣ Testing async context manager:")
    try:
        async with scraper:
            print("   ✅ Context manager entered successfully")
            # Don't actually make requests in test
            print("   ✅ Context manager working")
    except Exception as e:
        print(f"   ❌ Context manager error: {e}")
    
    print("\n✅ Skyscanner scraper tests completed!")

def test_html_parsing():
    """Test HTML parsing with sample data."""
    print("\n🌐 Testing HTML parsing:")
    
    # Sample HTML content for testing
    sample_html = """
    <div class="flight-result">
        <span class="price">R$ 850,99</span>
        <img alt="LATAM Airlines" src="latam.png">
        <span class="departure-time">14:30</span>
        <span class="arrival-time">18:45</span>
        <span class="duration">4h 15m</span>
        <span class="stops">1 stop</span>
    </div>
    <div class="fqs-flight-card">
        <div class="price">$1,200.50</div>
        <span class="airline">Copa Airlines</span>
        <span class="time">08:15</span>
        <span class="time">12:30</span>
        <span class="duration">4:15</span>
        <span>Direct</span>
    </div>
    """
    
    scraper = SkyscannerScraper()
    test_date = date.today()
    
    try:
        # This would normally parse actual HTML
        # For testing, we'll just verify the method exists
        flights = scraper._extract_with_regex(sample_html, test_date)
        print(f"   Regex extraction found {len(flights)} flights")
        
        for i, flight in enumerate(flights):
            print(f"   Flight {i+1}: {flight.airline} - {flight.currency}{flight.price}")
            
    except Exception as e:
        print(f"   HTML parsing test error: {e}")

def main():
    """Main test function."""
    print("🚀 Skyscanner Scraper Test Suite")
    print("=" * 50)
    
    # Run async tests
    asyncio.run(test_skyscanner_scraper())
    
    # Run HTML parsing tests
    test_html_parsing()
    
    print("\n🎉 All Skyscanner tests completed!")

if __name__ == "__main__":
    main()
