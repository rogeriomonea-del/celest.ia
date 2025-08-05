#!/usr/bin/env python3
"""
Test script for LLM Client functionality
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ai.llm_client import LLMClient, LLMProvider

async def test_llm_client():
    """Test LLM client functionality."""
    print("🧪 Testing LLM Client...")
    
    # Test 1: Initialize without API keys (should use mock)
    print("\n1️⃣ Testing initialization without API keys:")
    client = LLMClient()
    print(f"   Provider: {client.provider}")
    print(f"   Client type: {type(client.client).__name__}")
    
    # Test 2: Test mock analysis
    print("\n2️⃣ Testing mock analysis:")
    try:
        result = await client.analyze("Test flight analysis")
        print(f"   Result: {result[:100]}...")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Test flight analysis with empty data
    print("\n3️⃣ Testing flight analysis with empty data:")
    try:
        result = await client.analyze_flights([])
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: Test flight analysis with sample data
    print("\n4️⃣ Testing flight analysis with sample data:")
    sample_flights = [
        {
            "airline": "Copa Airlines",
            "price": 450.99,
            "currency": "USD",
            "departure_time": "2025-08-10 08:00",
            "arrival_time": "2025-08-10 15:30",
            "duration_minutes": 450,
            "stops": 0
        },
        {
            "airline": "LATAM",
            "price": 520.50,
            "currency": "USD",
            "departure_time": "2025-08-10 10:30",
            "arrival_time": "2025-08-10 18:45",
            "duration_minutes": 495,
            "stops": 1
        }
    ]
    
    try:
        result = await client.analyze_flights(sample_flights)
        print(f"   Result keys: {list(result.keys())}")
        if 'raw_analysis' in result:
            print(f"   Analysis: {result['raw_analysis'][:100]}...")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n✅ LLM Client tests completed!")

def test_with_api_key():
    """Test with actual API key if available."""
    print("\n🔑 Testing with API key (if available):")
    
    # Check for OpenAI API key
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        print(f"   Found OpenAI API key: {openai_key[:10]}...")
        client = LLMClient(provider="openai")
        print(f"   Client type: {type(client.client).__name__}")
    else:
        print("   No OpenAI API key found in environment")
    
    # Check for Anthropic API key
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    if anthropic_key:
        print(f"   Found Anthropic API key: {anthropic_key[:10]}...")
        client = LLMClient(provider="anthropic")
        print(f"   Client type: {type(client.client).__name__}")
    else:
        print("   No Anthropic API key found in environment")

def main():
    """Main test function."""
    print("🚀 LLM Client Test Suite")
    print("=" * 50)
    
    # Test configuration loading
    print("\n📋 Testing configuration:")
    try:
        from src.core.config import settings
        print(f"   Settings loaded: ✅")
        print(f"   LLM default provider: {getattr(settings.llm, 'default_provider', 'Not set')}")
        print(f"   OpenAI key configured: {'✅' if getattr(settings.llm, 'openai_api_key', None) else '❌'}")
        print(f"   Anthropic key configured: {'✅' if getattr(settings.llm, 'anthropic_api_key', None) else '❌'}")
    except Exception as e:
        print(f"   Configuration error: {e}")
    
    # Test with environment variables
    test_with_api_key()
    
    # Run async tests
    asyncio.run(test_llm_client())
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    main()
