"""Flight price analyzer using AI."""
from __future__ import annotations

import statistics
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

from .llm_client import LLMClient

logger = logging.getLogger(__name__)


class PriceAnalyzer:
    """AI-powered flight price analyzer."""
    
    def __init__(self):
        """Initialize price analyzer."""
        self.llm_client = LLMClient()
    
    async def analyze_price_trends(
        self,
        historical_prices: List[Dict[str, Any]],
        route: str
    ) -> Dict[str, Any]:
        """Analyze price trends for a route."""
        logger.info(f"Analyzing price trends for route: {route}")
        
        if not historical_prices:
            return {"error": "No historical price data available"}
        
        try:
            # Calculate basic statistics - filter valid prices
            prices = []
            for p in historical_prices:
                price = p.get('price')
                # More robust price validation
                if price is not None:
                    try:
                        price_float = float(price)
                        if price_float > 0:  # Only positive prices
                            prices.append(price_float)
                    except (ValueError, TypeError):
                        continue  # Skip invalid prices
            
            if not prices:
                return {"error": "No valid price data found"}
            
            basic_stats = self._calculate_basic_stats(prices)
            
            # Detect trends
            trend_analysis = self._detect_trend(historical_prices)
            
            # Use AI for deeper analysis
            ai_insights = await self._get_ai_price_insights(historical_prices, route, basic_stats)
            
            return {
                "route": route,
                "basic_statistics": basic_stats,
                "trend_analysis": trend_analysis,
                "ai_insights": ai_insights,
                "recommendation": self._generate_booking_recommendation(basic_stats, trend_analysis),
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "data_quality": {
                    "total_records": len(historical_prices),
                    "valid_prices": len(prices),
                    "data_completeness": len(prices) / len(historical_prices) if historical_prices else 0
                }
            }
        except Exception as e:
            logger.error(f"Error in price trend analysis: {e}")
            return {
                "error": f"Analysis failed: {str(e)}",
                "route": route,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
    
    def _calculate_basic_stats(self, prices: List[float]) -> Dict[str, float]:
        """Calculate basic price statistics."""
        if not prices:
            return {}
        
        # Filter out invalid prices
        valid_prices = [p for p in prices if p and p > 0]
        if not valid_prices:
            return {}
        
        try:
            min_price = min(valid_prices)
            max_price = max(valid_prices)
            avg_price = statistics.mean(valid_prices)
            median_price = statistics.median(valid_prices)
            
            # Handle standard deviation safely
            if len(valid_prices) > 1:
                try:
                    std_dev = statistics.stdev(valid_prices)
                    coeff_var = std_dev / avg_price if avg_price > 0 else 0
                except statistics.StatisticsError:
                    std_dev = 0
                    coeff_var = 0
            else:
                std_dev = 0
                coeff_var = 0
            
            return {
                "min_price": min_price,
                "max_price": max_price,
                "avg_price": avg_price,
                "median_price": median_price,
                "std_deviation": std_dev,
                "price_range": max_price - min_price,
                "coefficient_of_variation": coeff_var,
                "sample_size": len(valid_prices)
            }
        except Exception as e:
            logger.error(f"Error calculating basic stats: {e}")
            return {"error": "Statistics calculation failed"}
    
    def _detect_trend(self, historical_prices: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect price trends in historical data."""
        if len(historical_prices) < 2:
            return {"trend": "insufficient_data"}
        
        # Sort by date - handle both string and datetime objects
        def get_timestamp(item):
            timestamp = item.get('timestamp')
            if timestamp is None:
                return datetime.min
            if isinstance(timestamp, str):
                try:
                    # Try to parse common date formats
                    for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S']:
                        try:
                            return datetime.strptime(timestamp, fmt)
                        except ValueError:
                            continue
                    # If parsing fails, return a default
                    return datetime.min
                except Exception:
                    return datetime.min
            elif isinstance(timestamp, datetime):
                return timestamp
            else:
                return datetime.min
        
        sorted_prices = sorted(historical_prices, key=get_timestamp)
        
        # Filter prices more robustly
        prices = []
        for p in sorted_prices:
            price = p.get('price')
            if price is not None:
                try:
                    price_float = float(price)
                    if price_float > 0:
                        prices.append(price_float)
                except (ValueError, TypeError):
                    continue
        
        if len(prices) < 2:
            return {"trend": "insufficient_data"}
        
        # Simple linear trend detection
        recent_count = min(7, len(prices))
        recent_avg = statistics.mean(prices[-recent_count:])  # Last data points
        older_avg = statistics.mean(prices[:recent_count])    # First data points
        
        trend_direction = "stable"
        trend_strength = 0
        
        if recent_avg > older_avg * 1.1:  # 10% increase
            trend_direction = "increasing"
            trend_strength = (recent_avg - older_avg) / older_avg
        elif recent_avg < older_avg * 0.9:  # 10% decrease
            trend_direction = "decreasing"
            trend_strength = (older_avg - recent_avg) / older_avg
        
        return {
            "trend": trend_direction,
            "strength": trend_strength,
            "recent_average": recent_avg,
            "historical_average": older_avg,
            "data_points": len(prices)
        }
    
    async def _get_ai_price_insights(
        self,
        historical_prices: List[Dict[str, Any]],
        route: str,
        basic_stats: Dict[str, float]
    ) -> Dict[str, Any]:
        """Get AI insights on price patterns."""
        try:
            # Prepare data summary for AI
            price_summary = self._prepare_price_summary(historical_prices, basic_stats)
            
            analysis_prompt = f"""
            Analyze the following flight price data for route {route}:

            {price_summary}

            Please provide insights on:
            1. Seasonal patterns (if any)
            2. Day-of-week patterns
            3. Optimal booking window
            4. Price volatility assessment
            5. Future price predictions (next 2-4 weeks)
            6. Risk assessment for waiting vs booking now

            Format your response as JSON with clear, actionable insights.
            """
            
            ai_response = await self.llm_client.analyze(analysis_prompt)
            
            # Try to parse JSON response
            if ai_response:
                try:
                    import json
                    parsed_response = json.loads(ai_response)
                    return parsed_response
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse AI response as JSON: {e}")
                    # Return structured fallback
                    return {
                        "raw_insights": ai_response,
                        "parsing_error": "Response was not valid JSON",
                        "fallback_analysis": self._generate_fallback_insights(basic_stats)
                    }
            else:
                return {"error": "Empty AI response"}
                
        except Exception as e:
            logger.error(f"AI price analysis failed: {e}")
            return {
                "error": "AI analysis unavailable",
                "fallback_analysis": self._generate_fallback_insights(basic_stats)
            }
    
    def _generate_fallback_insights(self, basic_stats: Dict[str, float]) -> Dict[str, Any]:
        """Generate basic insights when AI analysis fails."""
        try:
            volatility = basic_stats.get('coefficient_of_variation', 0)
            avg_price = basic_stats.get('avg_price', 0)
            
            insights = {
                "price_assessment": "stable" if volatility < 0.15 else "volatile" if volatility > 0.3 else "moderate",
                "booking_urgency": "low" if volatility < 0.15 else "high",
                "price_level": "reasonable" if avg_price > 0 else "unknown",
                "data_quality": "sufficient" if basic_stats.get('sample_size', 0) > 10 else "limited"
            }
            
            return insights
        except Exception:
            return {"assessment": "analysis_unavailable"}
    
    def _prepare_price_summary(
        self,
        historical_prices: List[Dict[str, Any]],
        basic_stats: Dict[str, float]
    ) -> str:
        """Prepare price summary for AI analysis."""
        try:
            summary_lines = [
                f"Price Statistics:",
                f"- Average: ${basic_stats.get('avg_price', 0):.2f}",
                f"- Range: ${basic_stats.get('min_price', 0):.2f} - ${basic_stats.get('max_price', 0):.2f}",
                f"- Volatility (CV): {basic_stats.get('coefficient_of_variation', 0):.3f}",
                f"- Data points: {len(historical_prices)}",
                "",
                "Recent price samples:"
            ]
            
            # Add recent price samples with safe timestamp handling
            def get_sort_key(item):
                timestamp = item.get('timestamp')
                if isinstance(timestamp, datetime):
                    return timestamp
                elif isinstance(timestamp, str):
                    try:
                        # Try parsing common formats
                        for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S']:
                            try:
                                return datetime.strptime(timestamp, fmt)
                            except ValueError:
                                continue
                        return datetime.min
                    except Exception:
                        return datetime.min
                else:
                    return datetime.min
            
            recent_prices = sorted(
                historical_prices,
                key=get_sort_key,
                reverse=True
            )[:10]
            
            for price_data in recent_prices:
                timestamp = price_data.get('timestamp', 'Unknown')
                price = price_data.get('price', 0)
                
                # Format timestamp for display
                if isinstance(timestamp, datetime):
                    timestamp_str = timestamp.strftime('%Y-%m-%d')
                else:
                    timestamp_str = str(timestamp)
                
                summary_lines.append(f"- {timestamp_str}: ${price}")
            
            return "\n".join(summary_lines)
        except Exception as e:
            logger.error(f"Error preparing price summary: {e}")
            return f"Price summary generation failed: {str(e)}"
    
    def _generate_booking_recommendation(
        self,
        basic_stats: Dict[str, float],
        trend_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate booking recommendation based on analysis."""
        current_trend = trend_analysis.get('trend', 'stable')
        volatility = basic_stats.get('coefficient_of_variation', 0)
        
        if current_trend == "decreasing":
            recommendation = "wait"
            reason = "Prices are trending downward. Consider waiting a few days."
            confidence = "medium"
        elif current_trend == "increasing":
            recommendation = "book_soon"
            reason = "Prices are trending upward. Book soon to avoid higher prices."
            confidence = "medium"
        elif volatility > 0.3:  # High volatility
            recommendation = "monitor_closely"
            reason = "High price volatility detected. Monitor daily and book when you see a dip."
            confidence = "low"
        else:
            recommendation = "flexible"
            reason = "Stable pricing. Book when convenient within your travel dates."
            confidence = "high"
        
        return {
            "action": recommendation,
            "reason": reason,
            "confidence": confidence,
            "volatility_level": "high" if volatility > 0.3 else "medium" if volatility > 0.15 else "low"
        }
    
    async def compare_prices_across_sources(
        self,
        flight_results: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Compare prices across different booking sources."""
        logger.info("Comparing prices across booking sources")
        
        try:
            source_analysis = {}
            all_flights = []
            
            # Analyze each source
            for source, flights in flight_results.items():
                if not flights or not isinstance(flights, list):
                    continue
                
                # Filter valid flights with prices
                valid_flights = []
                prices = []
                
                for flight in flights:
                    if isinstance(flight, dict):
                        price = flight.get('price')
                        if price is not None:
                            try:
                                price_float = float(price)
                                if price_float > 0:
                                    prices.append(price_float)
                                    valid_flights.append(flight)
                            except (ValueError, TypeError):
                                continue  # Skip invalid prices
                
                if prices:
                    source_analysis[source] = {
                        "flight_count": len(valid_flights),
                        "avg_price": statistics.mean(prices),
                        "min_price": min(prices),
                        "max_price": max(prices),
                        "price_range": max(prices) - min(prices),
                        "data_quality": len(valid_flights) / len(flights) if flights else 0
                    }
                    all_flights.extend(valid_flights)
            
            # Find best deals
            if all_flights:
                try:
                    best_deal = min(all_flights, key=lambda x: x.get('price', float('inf')))
                except (ValueError, TypeError):
                    best_deal = None
                
                # Use AI to analyze source reliability and recommendations
                ai_analysis = await self._analyze_source_reliability(source_analysis)
                
                return {
                    "source_comparison": source_analysis,
                    "best_deal": best_deal,
                    "total_flights_found": len(all_flights),
                    "ai_analysis": ai_analysis,
                    "comparison_timestamp": datetime.utcnow().isoformat()
                }
            
            return {
                "error": "No valid flight data found across sources",
                "source_count": len(flight_results),
                "comparison_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in price comparison: {e}")
            return {
                "error": f"Price comparison failed: {str(e)}",
                "comparison_timestamp": datetime.utcnow().isoformat()
            }
    
    async def _analyze_source_reliability(
        self,
        source_analysis: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze booking source reliability using AI."""
        try:
            if not source_analysis:
                return {"error": "No source data to analyze"}
            
            analysis_prompt = f"""
            Analyze the following flight booking source comparison:

            {source_analysis}

            Provide insights on:
            1. Which source typically offers the best prices
            2. Price consistency across sources
            3. Reliability recommendations
            4. Potential booking strategies

            Return as JSON with actionable recommendations.
            """
            
            ai_response = await self.llm_client.analyze(analysis_prompt)
            
            # Parse AI response with fallback
            if ai_response:
                try:
                    import json
                    parsed_response = json.loads(ai_response)
                    return parsed_response
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse source analysis as JSON: {e}")
                    return {
                        "raw_analysis": ai_response,
                        "parsing_error": "Response was not valid JSON",
                        "fallback_recommendation": self._generate_source_fallback(source_analysis)
                    }
            else:
                return {
                    "error": "Empty AI response",
                    "fallback_recommendation": self._generate_source_fallback(source_analysis)
                }
                
        except Exception as e:
            logger.error(f"Source reliability analysis failed: {e}")
            return {
                "error": "Analysis unavailable",
                "fallback_recommendation": self._generate_source_fallback(source_analysis)
            }
    
    def _generate_source_fallback(self, source_analysis: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Generate fallback recommendations for source comparison."""
        try:
            if not source_analysis:
                return {"recommendation": "No data available for comparison"}
            
            # Find source with lowest average price
            best_source = min(
                source_analysis.items(),
                key=lambda x: x[1].get('avg_price', float('inf'))
            )
            
            # Calculate price spreads
            all_avg_prices = [data.get('avg_price', 0) for data in source_analysis.values()]
            price_spread = max(all_avg_prices) - min(all_avg_prices) if all_avg_prices else 0
            
            return {
                "best_price_source": best_source[0],
                "best_avg_price": best_source[1].get('avg_price'),
                "price_spread": price_spread,
                "recommendation": f"Consider {best_source[0]} for best average prices",
                "sources_analyzed": len(source_analysis)
            }
        except Exception:
            return {"recommendation": "Unable to generate source comparison"}
