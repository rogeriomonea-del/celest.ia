"""LLM client for interfacing with various AI providers."""
from __future__ import annotations

import json
import logging
from typing import Dict, Any, Optional, List, Union
from abc import ABC, abstractmethod
from enum import Enum

try:
    from ..core.config import settings
except ImportError:
    # Fallback for when config is not available
    class MockLLMSettings:
        openai_api_key = None
        anthropic_api_key = None
        default_provider = "openai"
    
    class MockSettings:
        def __init__(self):
            self.llm = MockLLMSettings()
    
    settings = MockSettings()

# Use standard logging instead of loguru for better compatibility
logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Available LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class BaseLLMClient(ABC):
    """Base class for LLM clients."""
    
    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Send chat completion request."""
        pass
    
    @abstractmethod
    async def analyze(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.3
    ) -> str:
        """Analyze text and return insights."""
        pass


class OpenAIClient(BaseLLMClient):
    """OpenAI LLM client."""
    
    def __init__(self, api_key: str):
        """Initialize OpenAI client."""
        self.api_key = api_key
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize OpenAI client."""
        try:
            import openai
            self.client = openai.AsyncOpenAI(api_key=self.api_key)
            logger.info("OpenAI client initialized successfully")
        except ImportError:
            logger.error("OpenAI package not installed. Install with: pip install openai")
            self.client = None
            raise
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            self.client = None
            raise
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Send chat completion request to OpenAI."""
        if not self.client:
            raise RuntimeError("OpenAI client not initialized")
        
        try:
            response = await self.client.chat.completions.create(
                model=model or "gpt-4o",
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens or 2000
            )
            
            return response.choices[0].message.content or "No response generated"
            
        except Exception as e:
            logger.error(f"OpenAI chat error: {e}")
            raise
    
    async def analyze(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.3
    ) -> str:
        """Analyze text using OpenAI."""
        messages = [
            {
                "role": "system",
                "content": "You are an expert travel analyst. Provide detailed, accurate analysis."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        return await self.chat(messages, model, temperature)


class AnthropicClient(BaseLLMClient):
    """Anthropic (Claude) LLM client."""
    
    def __init__(self, api_key: str):
        """Initialize Anthropic client."""
        self.api_key = api_key
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Anthropic client."""
        try:
            import anthropic
            self.client = anthropic.AsyncAnthropic(api_key=self.api_key)
            logger.info("Anthropic client initialized successfully")
        except ImportError:
            logger.error("Anthropic package not installed. Install with: pip install anthropic")
            self.client = None
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
            self.client = None
            raise
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Send chat completion request to Anthropic."""
        if not self.client:
            raise RuntimeError("Anthropic client not initialized")
        
        try:
            # Convert messages format for Anthropic
            system_message = ""
            user_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    user_messages.append(msg)
            
            response = await self.client.messages.create(
                model=model or "claude-3-5-sonnet-20240620",
                system=system_message,
                messages=user_messages,
                temperature=temperature,
                max_tokens=max_tokens or 2000
            )
            
            return response.content[0].text if response.content else "No response generated"
            
        except Exception as e:
            logger.error(f"Anthropic chat error: {e}")
            raise
    
    async def analyze(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.3
    ) -> str:
        """Analyze text using Anthropic."""
        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        system_prompt = "You are an expert travel analyst. Provide detailed, accurate analysis."
        
        try:
            response = await self.client.messages.create(
                model=model or "claude-3-5-sonnet-20240620",
                system=system_prompt,
                messages=messages,
                temperature=temperature,
                max_tokens=2000
            )
            
            return response.content[0].text if response.content else "No response generated"
            
        except Exception as e:
            logger.error(f"Anthropic analysis error: {e}")
            raise


class LLMClient:
    """Main LLM client that can use different providers."""
    
    def __init__(self, provider: Optional[str] = None):
        """Initialize LLM client with specified provider."""
        # Try to get provider from settings with fallback
        default_provider = 'openai'  # Safe default
        
        try:
            if hasattr(settings, 'llm') and hasattr(settings.llm, 'default_provider'):
                default_provider = settings.llm.default_provider
            elif hasattr(settings, 'default_llm_provider'):
                default_provider = settings.default_llm_provider
        except (AttributeError, ImportError):
            # Use the safe default
            pass
            
        self.provider = provider or default_provider
        self.client: Optional[BaseLLMClient] = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the appropriate LLM client."""
        try:
            if self.provider == LLMProvider.OPENAI.value:
                # Try multiple ways to get the API key
                api_key = None
                if hasattr(settings, 'llm') and hasattr(settings.llm, 'openai_api_key'):
                    api_key = settings.llm.openai_api_key
                elif hasattr(settings, 'openai_api_key'):
                    api_key = settings.openai_api_key
                
                # Also try environment variable as fallback
                if not api_key:
                    import os
                    api_key = os.getenv('OPENAI_API_KEY')
                
                if not api_key:
                    raise ValueError("OpenAI API key not configured")
                self.client = OpenAIClient(api_key)
                
            elif self.provider == LLMProvider.ANTHROPIC.value:
                # Try multiple ways to get the API key
                api_key = None
                if hasattr(settings, 'llm') and hasattr(settings.llm, 'anthropic_api_key'):
                    api_key = settings.llm.anthropic_api_key
                elif hasattr(settings, 'anthropic_api_key'):
                    api_key = settings.anthropic_api_key
                
                # Also try environment variable as fallback
                if not api_key:
                    import os
                    api_key = os.getenv('ANTHROPIC_API_KEY')
                
                if not api_key:
                    raise ValueError("Anthropic API key not configured")
                self.client = AnthropicClient(api_key)
                
            else:
                raise ValueError(f"Unsupported LLM provider: {self.provider}")
                
            logger.info(f"LLM client initialized with provider: {self.provider}")
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            # Fallback to mock client for development
            logger.warning("Falling back to mock LLM client")
            self.client = MockLLMClient()
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Send chat completion request."""
        if not self.client:
            raise RuntimeError("LLM client not initialized")
        
        return await self.client.chat(messages, model, temperature, max_tokens)
    
    async def analyze(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.3
    ) -> str:
        """Analyze text and return insights."""
        if not self.client:
            raise RuntimeError("LLM client not initialized")
        
        return await self.client.analyze(prompt, model, temperature)
    
    async def analyze_flights(self, flights_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze flight data and provide recommendations."""
        if not flights_data:
            return {"error": "No flight data provided"}
        
        # Check if client is available
        if not self.client:
            logger.error("LLM client not available for flight analysis")
            return {"error": "LLM client not available"}
        
        # Prepare flight summary for analysis
        flight_summary = self._format_flights_for_analysis(flights_data)
        
        analysis_prompt = f"""
        Analyze the following flight options and provide recommendations:

        {flight_summary}

        Please provide your analysis in JSON format with the following structure:
        {{
            "best_value": {{"flight_index": 0, "reason": "explanation"}},
            "fastest": {{"flight_index": 1, "reason": "explanation"}},
            "recommendations": ["recommendation1", "recommendation2"],
            "price_analysis": "overall price analysis",
            "booking_advice": "when to book advice"
        }}
        """
        
        try:
            analysis_result = await self.analyze(analysis_prompt)
            
            # Try to parse as JSON
            try:
                return json.loads(analysis_result)
            except json.JSONDecodeError:
                # Return raw analysis if JSON parsing fails
                return {"raw_analysis": analysis_result}
                
        except Exception as e:
            logger.error(f"Flight analysis failed: {e}")
            return {"error": "Analysis failed", "details": str(e)}
    
    def _format_flights_for_analysis(self, flights: List[Dict[str, Any]]) -> str:
        """Format flight data for LLM analysis."""
        if not flights:
            return "No flights to analyze"
            
        formatted_flights = []
        
        for i, flight in enumerate(flights[:10]):  # Limit to top 10
            # Safely get values with defaults
            airline = flight.get('airline', 'Unknown')
            price = flight.get('price', 'N/A')
            currency = flight.get('currency', '$')
            departure_time = flight.get('departure_time', 'N/A')
            arrival_time = flight.get('arrival_time', 'N/A')
            duration_minutes = flight.get('duration_minutes', 'N/A')
            stops = flight.get('stops', 'Unknown')
            
            formatted_flights.append(
                f"Flight {i+1}:\n"
                f"  Airline: {airline}\n"
                f"  Price: {currency}{price}\n"
                f"  Departure: {departure_time}\n"
                f"  Arrival: {arrival_time}\n"
                f"  Duration: {duration_minutes} minutes\n"
                f"  Stops: {stops}\n"
            )
        
        return "\n".join(formatted_flights) if formatted_flights else "No valid flight data"


class MockLLMClient(BaseLLMClient):
    """Mock LLM client for development/testing."""
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Mock chat response."""
        logger.warning("Using mock LLM client - configure API keys for real AI analysis")
        return "This is a mock response. Please configure your LLM API keys for real analysis."
    
    async def analyze(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.3
    ) -> str:
        """Mock analysis response."""
        logger.warning("Using mock LLM client - configure API keys for real AI analysis")
        return json.dumps({
            "analysis": "Mock analysis result",
            "recommendations": ["Configure API keys", "Use real LLM provider"],
            "note": "This is a mock response"
        })
