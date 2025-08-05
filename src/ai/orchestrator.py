"""
IA Orquestradora para Celest.ia v2
Sistema central que coordena ML, Self-Healing e Self-Improvement
"""

import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from .ml_engine import MLOrchestrator, MLPricePredictor, PricePrediction, MarketInsight
from .self_healing import SelfHealingOrchestrator, HealthStatus, HealthMetric
from .self_improvement import SelfImprovementOrchestrator, MetricType, ImprovementCategory
from .llm_client import LLMClient
from .price_analyzer import PriceAnalyzer

try:
    from ..core.config import settings
except ImportError:
    # Mock settings when config module is not available
    class MockSettings:
        def __init__(self):
            self.database = type('obj', (object,), {'host': 'localhost', 'port': 5432})()
            self.api = type('obj', (object,), {'host': '0.0.0.0', 'port': 8000})()
            self.llm = type('obj', (object,), {'default_provider': 'openai'})()
    
    settings = MockSettings()

logger = logging.getLogger(__name__)

class SystemMode(Enum):
    """System operational modes."""
    NORMAL = "normal"
    LEARNING = "learning"
    RECOVERY = "recovery"
    OPTIMIZATION = "optimization"
    MAINTENANCE = "maintenance"

class Priority(Enum):
    """Task priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5

@dataclass
class SystemTask:
    """Task for the orchestrator."""
    task_id: str
    task_type: str
    priority: Priority
    payload: Dict[str, Any]
    scheduled_time: datetime
    retry_count: int = 0
    max_retries: int = 3
    completed: bool = False
    result: Optional[Any] = None
    error: Optional[str] = None

@dataclass
class SystemStatus:
    """Overall system status."""
    mode: SystemMode
    health: HealthStatus
    active_tasks: int
    ml_models_trained: int
    improvements_applied: int
    last_analysis: Optional[datetime]
    uptime: timedelta
    performance_score: float

class CelestiaAIOrchestrator:
    """
    Central AI Orchestrator for Celest.ia v2
    
    Coordinates all AI systems:
    - Machine Learning Engine (price prediction, market analysis)
    - Self-Healing System (health monitoring, auto-recovery)
    - Self-Improvement System (performance optimization, adaptive learning)
    - LLM Integration (intelligent analysis, decision making)
    """
    
    def __init__(self):
        """Initialize the AI Orchestrator."""
        self.start_time = datetime.now()
        self.mode = SystemMode.NORMAL
        self.task_queue = asyncio.Queue()
        self.completed_tasks = []
        self.active_tasks = {}
        
        # Initialize AI systems
        self.ml_orchestrator = MLOrchestrator()
        self.self_healing = SelfHealingOrchestrator()
        self.self_improvement = SelfImprovementOrchestrator()
        self.llm_client = LLMClient()
        self.price_analyzer = PriceAnalyzer()
        
        # System metrics
        self.metrics = {
            'predictions_made': 0,
            'errors_recovered': 0,
            'improvements_applied': 0,
            'analyses_performed': 0,
            'uptime_seconds': 0
        }
        
        # Configuration
        self.config = {
            'analysis_interval': 300,  # 5 minutes
            'health_check_interval': 60,  # 1 minute
            'improvement_interval': 1800,  # 30 minutes
            'max_concurrent_tasks': 10,
            'emergency_mode_threshold': 0.5  # Health score threshold
        }
        
        # Background tasks
        self.orchestrator_task = None
        self.monitor_task = None
        self.scheduler_task = None
        
        logger.info("Celest.ia AI Orchestrator initialized")
    
    async def start(self):
        """Start the AI Orchestrator and all subsystems."""
        logger.info("🚀 Starting Celest.ia AI Orchestrator")
        
        try:
            # Start subsystems
            await self.ml_orchestrator.start()
            await self.self_healing.start()
            await self.self_improvement.start()
            
            # Start orchestrator tasks
            self.orchestrator_task = asyncio.create_task(self._orchestrator_loop())
            self.monitor_task = asyncio.create_task(self._monitor_loop())
            self.scheduler_task = asyncio.create_task(self._scheduler_loop())
            
            # Schedule initial tasks
            await self._schedule_initial_tasks()
            
            logger.info("✅ Celest.ia AI Orchestrator started successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to start AI Orchestrator: {e}")
            await self.stop()
            raise
    
    async def stop(self):
        """Stop the AI Orchestrator and all subsystems."""
        logger.info("🛑 Stopping Celest.ia AI Orchestrator")
        
        # Cancel orchestrator tasks
        for task in [self.orchestrator_task, self.monitor_task, self.scheduler_task]:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        # Stop subsystems
        await self.ml_orchestrator.stop()
        await self.self_healing.stop()
        await self.self_improvement.stop()
        
        logger.info("✅ Celest.ia AI Orchestrator stopped")
    
    async def predict_flight_price(
        self,
        origin: str,
        destination: str,
        departure_date: datetime,
        return_date: Optional[datetime] = None,
        passengers: int = 1
    ) -> Dict[str, Any]:
        """
        Predict flight price using ML engine and enhance with AI analysis.
        
        Returns comprehensive price prediction with market insights.
        """
        try:
            logger.info(f"🔮 Predicting price for {origin}->{destination}")
            
            # Get ML prediction
            prediction = await self.ml_orchestrator.price_predictor.predict_price(
                origin, destination, departure_date, return_date, passengers
            )
            
            # Get market insights
            market_insight = await self.ml_orchestrator.price_predictor.analyze_market_trends(
                f"{origin}-{destination}"
            )
            
            # Get AI-enhanced analysis
            ai_analysis = await self._get_ai_enhanced_analysis(
                prediction, market_insight, origin, destination
            )
            
            # Check for price anomalies
            anomaly_check = await self.ml_orchestrator.price_predictor.detect_price_anomalies(
                f"{origin}-{destination}", prediction.predicted_price
            )
            
            # Update metrics
            self.metrics['predictions_made'] += 1
            
            # Record performance metric
            self.self_improvement.record_performance_metric(
                MetricType.ACCURACY, prediction.confidence, "price_prediction"
            )
            
            result = {
                "prediction": {
                    "price": prediction.predicted_price,
                    "confidence": prediction.confidence,
                    "trend": prediction.price_trend,
                    "booking_window": prediction.best_booking_window,
                    "savings_potential": prediction.savings_potential,
                    "model_version": prediction.model_version
                },
                "market_insights": {
                    "seasonal_pattern": market_insight.seasonal_pattern,
                    "peak_months": market_insight.peak_months,
                    "low_season_months": market_insight.low_season_months,
                    "average_price": market_insight.average_price,
                    "volatility": market_insight.price_volatility,
                    "recommendations": market_insight.booking_recommendations
                },
                "ai_analysis": ai_analysis,
                "anomaly_detection": anomaly_check,
                "generated_at": datetime.now().isoformat(),
                "route": f"{origin}-{destination}",
                "passengers": passengers
            }
            
            logger.info(f"✅ Price prediction completed for {origin}->{destination}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error predicting flight price: {e}")
            
            # Record error for self-improvement
            self.self_improvement.record_performance_metric(
                MetricType.ERROR_RATE, 1.0, "price_prediction"
            )
            
            return {
                "error": str(e),
                "fallback_prediction": {
                    "price": 800.0,  # Default fallback
                    "confidence": 0.3,
                    "trend": "unknown",
                    "booking_window": 30,
                    "savings_potential": 0.0,
                    "model_version": "fallback"
                },
                "generated_at": datetime.now().isoformat()
            }
    
    async def analyze_flight_data(self, flights_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze flight data using AI and provide insights."""
        try:
            logger.info(f"🔍 Analyzing {len(flights_data)} flights")
            
            # Use price analyzer for detailed analysis
            analysis = await self.price_analyzer.analyze_price_trends(
                flights_data, "multi-route"
            )
            
            # Get LLM insights
            llm_analysis = await self.llm_client.analyze_flights(flights_data)
            
            # Update metrics
            self.metrics['analyses_performed'] += 1
            
            # Record performance
            self.self_improvement.record_performance_metric(
                MetricType.THROUGHPUT, len(flights_data), "flight_analysis"
            )
            
            return {
                "statistical_analysis": analysis,
                "ai_insights": llm_analysis,
                "flights_analyzed": len(flights_data),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error analyzing flight data: {e}")
            return {"error": str(e), "generated_at": datetime.now().isoformat()}
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        try:
            # Get health status
            health_report = await self.self_healing.get_system_health_report()
            
            # Get improvement status
            improvement_report = await self.self_improvement.get_improvement_report()
            
            # Calculate uptime
            uptime = datetime.now() - self.start_time
            self.metrics['uptime_seconds'] = int(uptime.total_seconds())
            
            # Calculate performance score
            performance_score = await self._calculate_performance_score()
            
            # Get active tasks
            active_task_count = len(self.active_tasks)
            
            return {
                "system_status": {
                    "mode": self.mode.value,
                    "uptime_seconds": self.metrics['uptime_seconds'],
                    "uptime_human": str(uptime),
                    "performance_score": performance_score,
                    "active_tasks": active_task_count
                },
                "health_status": health_report,
                "improvement_status": improvement_report,
                "metrics": self.metrics,
                "subsystems": {
                    "ml_engine": "running",
                    "self_healing": "running",
                    "self_improvement": "running",
                    "llm_client": "running",
                    "price_analyzer": "running"
                },
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting system status: {e}")
            return {
                "error": str(e),
                "generated_at": datetime.now().isoformat()
            }
    
    async def emergency_mode(self, reason: str):
        """Activate emergency mode for critical system issues."""
        logger.warning(f"🚨 Activating emergency mode: {reason}")
        
        self.mode = SystemMode.RECOVERY
        
        # Pause non-critical operations
        await self._pause_non_critical_tasks()
        
        # Focus on recovery
        await self._schedule_emergency_recovery()
        
        # Notify administrators (if configured)
        await self._send_emergency_notification(reason)
    
    async def optimize_system(self):
        """Trigger system optimization."""
        logger.info("⚡ Starting system optimization")
        
        # Schedule optimization task
        optimization_task = SystemTask(
            task_id=f"optimize_{datetime.now().timestamp()}",
            task_type="system_optimization",
            priority=Priority.HIGH,
            payload={"action": "full_optimization"},
            scheduled_time=datetime.now()
        )
        
        await self.task_queue.put(optimization_task)
    
    # Private methods
    
    async def _orchestrator_loop(self):
        """Main orchestrator loop."""
        while True:
            try:
                # Process tasks from queue
                try:
                    task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                    await self._execute_task(task)
                except asyncio.TimeoutError:
                    continue  # No tasks in queue
                
                # Check system health and adapt
                await self._check_and_adapt_system()
                
                await asyncio.sleep(0.1)  # Small delay to prevent high CPU usage
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Error in orchestrator loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _monitor_loop(self):
        """System monitoring loop."""
        while True:
            try:
                # Update metrics
                await self._update_system_metrics()
                
                # Check for emergency conditions
                await self._check_emergency_conditions()
                
                # Cleanup completed tasks
                await self._cleanup_completed_tasks()
                
                await asyncio.sleep(self.config['health_check_interval'])
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Error in monitor loop: {e}")
                await asyncio.sleep(10)
    
    async def _scheduler_loop(self):
        """Task scheduler loop."""
        while True:
            try:
                # Schedule periodic tasks
                await self._schedule_periodic_tasks()
                
                await asyncio.sleep(60)  # Check every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Error in scheduler loop: {e}")
                await asyncio.sleep(60)
    
    async def _execute_task(self, task: SystemTask):
        """Execute a system task."""
        task_start = time.time()
        self.active_tasks[task.task_id] = task
        
        try:
            logger.info(f"🔄 Executing task: {task.task_type} (ID: {task.task_id})")
            
            # Execute based on task type
            if task.task_type == "ml_training":
                task.result = await self._handle_ml_training(task.payload)
            elif task.task_type == "health_check":
                task.result = await self._handle_health_check(task.payload)
            elif task.task_type == "system_improvement":
                task.result = await self._handle_system_improvement(task.payload)
            elif task.task_type == "system_optimization":
                task.result = await self._handle_system_optimization(task.payload)
            elif task.task_type == "data_analysis":
                task.result = await self._handle_data_analysis(task.payload)
            else:
                logger.warning(f"⚠️ Unknown task type: {task.task_type}")
                task.error = f"Unknown task type: {task.task_type}"
            
            task.completed = True
            execution_time = time.time() - task_start
            
            # Record performance
            self.self_improvement.record_performance_metric(
                MetricType.RESPONSE_TIME, execution_time, f"task_{task.task_type}"
            )
            
            logger.info(f"✅ Task completed: {task.task_type} ({execution_time:.2f}s)")
            
        except Exception as e:
            task.error = str(e)
            task.retry_count += 1
            
            logger.error(f"❌ Task failed: {task.task_type} - {e}")
            
            # Retry if within limits
            if task.retry_count < task.max_retries:
                logger.info(f"🔄 Retrying task: {task.task_type} (attempt {task.retry_count + 1})")
                task.scheduled_time = datetime.now() + timedelta(seconds=30 * task.retry_count)
                await self.task_queue.put(task)
        
        finally:
            if task.task_id in self.active_tasks:
                del self.active_tasks[task.task_id]
            self.completed_tasks.append(task)
    
    async def _get_ai_enhanced_analysis(
        self, 
        prediction: PricePrediction, 
        market_insight: MarketInsight,
        origin: str,
        destination: str
    ) -> Dict[str, Any]:
        """Get AI-enhanced analysis using LLM."""
        try:
            analysis_prompt = f"""
            Analyze this flight price prediction and market data:
            
            Route: {origin} to {destination}
            Predicted Price: ${prediction.predicted_price:.2f}
            Confidence: {prediction.confidence:.2%}
            Price Trend: {prediction.price_trend}
            Best Booking Window: {prediction.best_booking_window} days
            
            Market Insights:
            - Average Price: ${market_insight.average_price:.2f}
            - Price Volatility: {market_insight.price_volatility:.2%}
            - Peak Months: {', '.join(market_insight.peak_months)}
            - Low Season: {', '.join(market_insight.low_season_months)}
            
            Provide strategic booking recommendations and market analysis.
            """
            
            ai_response = await self.llm_client.analyze(analysis_prompt)
            
            return {
                "strategic_analysis": ai_response,
                "confidence_level": "high" if prediction.confidence > 0.8 else "medium" if prediction.confidence > 0.6 else "low",
                "booking_urgency": "high" if prediction.price_trend == "rising" else "medium" if prediction.price_trend == "stable" else "low",
                "market_opportunity": "excellent" if prediction.savings_potential > 100 else "good" if prediction.savings_potential > 50 else "fair"
            }
            
        except Exception as e:
            logger.error(f"❌ Error in AI analysis: {e}")
            return {
                "strategic_analysis": "AI analysis temporarily unavailable",
                "confidence_level": "medium",
                "booking_urgency": "medium",
                "market_opportunity": "unknown"
            }
    
    async def _schedule_initial_tasks(self):
        """Schedule initial system tasks."""
        initial_tasks = [
            SystemTask(
                task_id="initial_health_check",
                task_type="health_check",
                priority=Priority.HIGH,
                payload={"comprehensive": True},
                scheduled_time=datetime.now()
            ),
            SystemTask(
                task_id="initial_ml_training",
                task_type="ml_training",
                priority=Priority.MEDIUM,
                payload={"model_type": "global"},
                scheduled_time=datetime.now() + timedelta(minutes=5)
            )
        ]
        
        for task in initial_tasks:
            await self.task_queue.put(task)
    
    async def _schedule_periodic_tasks(self):
        """Schedule periodic maintenance tasks."""
        now = datetime.now()
        
        # Daily ML model retraining
        if now.hour == 2 and now.minute < 5:  # 2 AM daily
            ml_task = SystemTask(
                task_id=f"daily_ml_training_{now.date()}",
                task_type="ml_training",
                priority=Priority.MEDIUM,
                payload={"model_type": "all"},
                scheduled_time=now
            )
            await self.task_queue.put(ml_task)
        
        # Hourly system improvement check
        if now.minute < 5:  # Top of each hour
            improvement_task = SystemTask(
                task_id=f"hourly_improvement_{now.hour}",
                task_type="system_improvement",
                priority=Priority.LOW,
                payload={"scope": "incremental"},
                scheduled_time=now
            )
            await self.task_queue.put(improvement_task)
    
    async def _handle_ml_training(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ML training tasks."""
        model_type = payload.get("model_type", "global")
        
        if model_type == "global":
            result = await self.ml_orchestrator.price_predictor.train_price_prediction_model()
        elif model_type == "all":
            # Train multiple models
            results = []
            for route in ["GRU-MIA", "GRU-LAX", "GRU-NYC"]:
                result = await self.ml_orchestrator.price_predictor.train_price_prediction_model(route)
                results.append(result)
            result = {"results": results}
        else:
            result = await self.ml_orchestrator.price_predictor.train_price_prediction_model(model_type)
        
        return result
    
    async def _handle_health_check(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle health check tasks."""
        return await self.self_healing.get_system_health_report()
    
    async def _handle_system_improvement(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle system improvement tasks."""
        return await self.self_improvement.get_improvement_report()
    
    async def _handle_system_optimization(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle system optimization tasks."""
        # This would implement system-wide optimizations
        logger.info("🔧 Executing system optimization")
        
        # Trigger improvements across all subsystems
        await self.self_improvement.start()  # Restart improvement loop
        
        return {"optimization": "completed", "timestamp": datetime.now().isoformat()}
    
    async def _handle_data_analysis(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle data analysis tasks."""
        data = payload.get("data", [])
        return await self.analyze_flight_data(data)
    
    async def _check_and_adapt_system(self):
        """Check system state and adapt accordingly."""
        # Get current health
        health_report = await self.self_healing.get_system_health_report()
        overall_health = health_report.get("overall_health", "unknown")
        
        # Adapt mode based on health
        if overall_health == "failed":
            if self.mode != SystemMode.RECOVERY:
                await self.emergency_mode("System health critical")
        elif overall_health == "critical":
            self.mode = SystemMode.RECOVERY
        elif overall_health == "warning":
            self.mode = SystemMode.OPTIMIZATION
        else:
            self.mode = SystemMode.NORMAL
    
    async def _calculate_performance_score(self) -> float:
        """Calculate overall system performance score."""
        try:
            # Get health score (0-1)
            health_report = await self.self_healing.get_system_health_report()
            health_score = 1.0 if health_report.get("overall_health") == "healthy" else 0.5
            
            # Get improvement metrics
            improvement_report = await self.self_improvement.get_improvement_report()
            improvement_score = min(1.0, len(improvement_report.get("recent_improvements", [])) / 10)
            
            # Combine scores
            performance_score = (health_score * 0.6 + improvement_score * 0.4)
            
            return round(performance_score, 2)
            
        except Exception:
            return 0.5  # Default moderate score
    
    async def _update_system_metrics(self):
        """Update system metrics."""
        uptime = datetime.now() - self.start_time
        self.metrics['uptime_seconds'] = int(uptime.total_seconds())
    
    async def _check_emergency_conditions(self):
        """Check for conditions requiring emergency mode."""
        performance_score = await self._calculate_performance_score()
        
        if performance_score < self.config['emergency_mode_threshold']:
            await self.emergency_mode(f"Performance score below threshold: {performance_score}")
    
    async def _cleanup_completed_tasks(self):
        """Clean up old completed tasks."""
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.completed_tasks = [
            task for task in self.completed_tasks 
            if task.scheduled_time > cutoff_time
        ]
    
    async def _pause_non_critical_tasks(self):
        """Pause non-critical operations during emergency."""
        logger.info("⏸️ Pausing non-critical operations")
        # Implementation would pause low priority tasks
    
    async def _schedule_emergency_recovery(self):
        """Schedule emergency recovery tasks."""
        recovery_task = SystemTask(
            task_id=f"emergency_recovery_{datetime.now().timestamp()}",
            task_type="health_check",
            priority=Priority.EMERGENCY,
            payload={"emergency_mode": True},
            scheduled_time=datetime.now()
        )
        await self.task_queue.put(recovery_task)
    
    async def _send_emergency_notification(self, reason: str):
        """Send emergency notification to administrators."""
        logger.critical(f"🚨 EMERGENCY: {reason}")
        # Implementation would send notifications via email, Slack, etc.

# Global orchestrator instance
ai_orchestrator = CelestiaAIOrchestrator()

# Convenience functions for external use
async def predict_flight_price(*args, **kwargs):
    """Convenience function for flight price prediction."""
    return await ai_orchestrator.predict_flight_price(*args, **kwargs)

async def analyze_flights(*args, **kwargs):
    """Convenience function for flight analysis."""
    return await ai_orchestrator.analyze_flight_data(*args, **kwargs)

async def get_system_status():
    """Convenience function for system status."""
    return await ai_orchestrator.get_system_status()
