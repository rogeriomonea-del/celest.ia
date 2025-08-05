"""Telegram bot commands implementation."""
from __future__ import annotations

import re
from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta
from loguru import logger

from ..core.orchestrator import CelestiaOrchestrator


class BotCommands:
    """Bot command handlers."""
    
    def __init__(self, orchestrator: CelestiaOrchestrator):
        """Initialize bot commands."""
        self.orchestrator = orchestrator
    
    async def start_command(self, user_id: int) -> str:
        """Handle /start command."""
        logger.info(f"Start command from user {user_id}")
        
        welcome_text = """
🛩️ *Welcome to Celes.ia!*

I'm your AI travel assistant. I can help you:

✈️ *Search flights* across multiple airlines
📊 *Analyze price trends* for better booking decisions
💳 *Check miles balance* for loyalty programs
🤖 *Get AI recommendations* for optimal travel planning

*Quick commands:*
• `/search GRU PTY 2024-03-15` - Search flights
• `/trends GRU JFK` - Check price trends
• `/miles connectmiles` - Check miles balance
• `/help` - See all commands

Just tell me where you want to go and when, and I'll find the best options for you! 🌎
        """
        
        return welcome_text
    
    async def help_command(self) -> str:
        """Handle /help command."""
        help_text = """
🤖 *Celes.ia Bot Commands*

*Flight Search:*
• `/search <origin> <destination> <date>` - Search flights
• Example: `/search GRU PTY 2024-03-15`

*Price Analysis:*
• `/trends <origin> <destination>` - Get price trends
• Example: `/trends GRU JFK`

*Miles & Loyalty:*
• `/miles <program>` - Check miles balance
• Example: `/miles connectmiles`

*Settings:*
• `/settings` - Manage your preferences

*Natural Language:*
You can also just type what you want:
• "Find flights from São Paulo to Panama tomorrow"
• "What are the cheapest flights to New York?"
• "Check my ConnectMiles balance"

Need help? Just ask! 😊
        """
        
        return help_text
    
    async def search_command(self, args: List[str]) -> str:
        """Handle /search command."""
        logger.info(f"Search command with args: {args}")
        
        if len(args) < 3:
            return """
❌ *Invalid search format*

Please use: `/search <origin> <destination> <date>`

*Examples:*
• `/search GRU PTY 2024-03-15`
• `/search JFK LAX 2024-04-20`

*Airport codes:*
• GRU - São Paulo (Guarulhos)
• GIG - Rio de Janeiro
• PTY - Panama City
• JFK - New York (JFK)
• LAX - Los Angeles
            """
        
        origin = args[0].upper()
        destination = args[1].upper()
        date_str = args[2]
        
        try:
            # Parse date
            departure_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            
            if departure_date < date.today():
                return "❌ Departure date cannot be in the past!"
            
            # Search flights
            flights = await self.orchestrator.search_flights(
                origin=origin,
                destination=destination,
                departure_date=departure_date
            )
            
            if not flights:
                return f"😕 No flights found for {origin} → {destination} on {date_str}"
            
            # Format results
            response = f"✈️ *Flights {origin} → {destination}* on {date_str}\n\n"
            
            for i, flight in enumerate(flights[:5]):  # Show top 5
                price = flight.get('price', 'N/A')
                currency = flight.get('currency', 'USD')
                airline = flight.get('airline', 'Unknown')
                departure = flight.get('departure_time', 'N/A')
                
                if isinstance(departure, str):
                    try:
                        departure = datetime.fromisoformat(departure).strftime('%H:%M')
                    except:
                        departure = departure[:5] if len(departure) > 5 else departure
                
                response += f"*{i+1}.* {airline}\n"
                response += f"💰 {currency} {price} | 🕐 {departure}\n"
                
                recommendations = flight.get('recommendations', [])
                if recommendations:
                    response += f"💡 {recommendations[0]}\n"
                
                response += "\n"
            
            response += f"Found {len(flights)} total flights. Use the web dashboard for detailed analysis!"
            
            return response
            
        except ValueError:
            return "❌ Invalid date format. Please use YYYY-MM-DD (e.g., 2024-03-15)"
        except Exception as e:
            logger.error(f"Search command error: {e}")
            return f"❌ Search failed: {str(e)}"
    
    async def trends_command(self, args: List[str]) -> str:
        """Handle /trends command."""
        logger.info(f"Trends command with args: {args}")
        
        if len(args) < 2:
            return """
❌ *Invalid trends format*

Please use: `/trends <origin> <destination>`

*Examples:*
• `/trends GRU PTY`
• `/trends JFK LAX`
            """
        
        origin = args[0].upper()
        destination = args[1].upper()
        
        try:
            trends = await self.orchestrator.get_price_trends(
                origin=origin,
                destination=destination,
                days_back=30
            )
            
            if "error" in trends:
                return f"❌ {trends['error']}"
            
            # Format trends response
            route = f"{origin} → {destination}"
            response = f"📊 *Price Trends for {route}*\n\n"
            
            historical_data = trends.get('historical_data', [])
            if historical_data:
                avg_price = sum(p.get('price', 0) for p in historical_data) / len(historical_data)
                min_price = min(p.get('price', float('inf')) for p in historical_data)
                max_price = max(p.get('price', 0) for p in historical_data)
                
                response += f"💰 *Average Price:* ${avg_price:.2f}\n"
                response += f"🔽 *Lowest:* ${min_price:.2f}\n"
                response += f"🔼 *Highest:* ${max_price:.2f}\n\n"
            
            ai_analysis = trends.get('ai_analysis', {})
            if isinstance(ai_analysis, dict) and 'analysis' in ai_analysis:
                response += f"🤖 *AI Analysis:*\n{ai_analysis['analysis']}\n\n"
            
            response += "📈 Use the web dashboard for detailed charts and predictions!"
            
            return response
            
        except Exception as e:
            logger.error(f"Trends command error: {e}")
            return f"❌ Trends analysis failed: {str(e)}"
    
    async def miles_command(self, args: List[str]) -> str:
        """Handle /miles command."""
        logger.info(f"Miles command with args: {args}")
        
        if not args:
            return """
💳 *Miles Balance Check*

Please specify the loyalty program:
• `/miles connectmiles` - ConnectMiles balance

*Note:* You'll need to provide your login credentials securely.
For security, consider using the web dashboard for sensitive operations.
            """
        
        program = args[0].lower()
        
        if program != "connectmiles":
            return f"❌ Program '{program}' not supported yet. Currently available: connectmiles"
        
        return """
💳 *ConnectMiles Balance Check*

For security reasons, miles balance checking requires your login credentials.

Please use the secure web dashboard at your Celes.ia portal to:
• Check your miles balance safely
• View expiring miles
• See tier status
• Get personalized recommendations

🔒 Your credentials are never stored and are only used for real-time balance checking.
        """
    
    async def settings_command(self, user_id: int) -> str:
        """Handle /settings command."""
        logger.info(f"Settings command from user {user_id}")
        
        # In a real implementation, this would load user preferences from database
        settings_text = """
⚙️ *Your Celes.ia Settings*

*Current Preferences:*
• 🌍 Preferred currency: USD
• 📧 Price alerts: Enabled
• 🕐 Timezone: UTC
• 📱 Notifications: Enabled

*Available Settings:*
• Currency preferences
• Price alert thresholds
• Notification preferences
• Default airports
• Travel preferences

Use the web dashboard for detailed settings management.
        """
        
        return settings_text
    
    async def natural_language_search(self, text: str) -> str:
        """Handle natural language flight search."""
        logger.info(f"Natural language search: {text}")
        
        # Simple pattern matching for common phrases
        text_lower = text.lower()
        
        # Check if it's a flight search request
        flight_keywords = ['flight', 'fly', 'travel', 'trip', 'book']
        if any(keyword in text_lower for keyword in flight_keywords):
            
            # Try to extract airport codes or city names
            airport_pattern = r'\b[A-Z]{3}\b'
            airports = re.findall(airport_pattern, text.upper())
            
            if len(airports) >= 2:
                origin = airports[0]
                destination = airports[1]
                
                # Try to extract date
                date_pattern = r'\d{4}-\d{2}-\d{2}'
                dates = re.findall(date_pattern, text)
                
                if dates:
                    return await self.search_command([origin, destination, dates[0]])
                else:
                    # Suggest date format
                    return f"""
I understand you want to search flights from {origin} to {destination}!

Please specify a date in YYYY-MM-DD format, like:
`/search {origin} {destination} 2024-03-15`

Or try: "Find flights from {origin} to {destination} on 2024-03-15"
                    """
            
            # If no clear airports found, provide guidance
            return """
I can help you search for flights! Please provide:
• Origin airport (e.g., GRU, JFK)
• Destination airport (e.g., PTY, LAX)  
• Date (YYYY-MM-DD format)

*Example:* `/search GRU PTY 2024-03-15`
            """
        
        # Check if it's a miles balance request
        miles_keywords = ['miles', 'balance', 'connectmiles', 'loyalty']
        if any(keyword in text_lower for keyword in miles_keywords):
            return await self.miles_command(['connectmiles'])
        
        # Check if it's a trends request
        trends_keywords = ['trend', 'price', 'analysis', 'history']
        if any(keyword in text_lower for keyword in trends_keywords):
            return """
I can analyze price trends for any route!

*Example:* `/trends GRU PTY`

This will show you:
• Historical price data
• AI-powered predictions
• Best booking recommendations
            """
        
        # General help response
        return """
I'm here to help with your travel needs! I can:

✈️ Search flights: Tell me origin, destination, and date
📊 Analyze prices: Ask about trends for any route
💳 Check miles: Ask about your loyalty program balance

Type `/help` to see all commands, or just tell me what you need!
        """
    
    async def handle_callback(self, callback_data: str) -> str:
        """Handle callback query from inline keyboards."""
        logger.info(f"Handling callback: {callback_data}")
        
        if callback_data.startswith("book_"):
            flight_id = callback_data.replace("book_", "")
            return f"To book flight {flight_id}, please visit the airline's website or use the Celes.ia web dashboard for direct booking links."
        
        elif callback_data.startswith("details_"):
            flight_id = callback_data.replace("details_", "")
            return f"For detailed information about flight {flight_id}, please check the web dashboard."
        
        else:
            return "Unknown action. Please try again or use the menu commands."
