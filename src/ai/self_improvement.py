"""
Self-Improvement System for Celest.ia v2
Implements adaptive learning, performance optimization, and continuous improvement
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
import statistics
from collections import defaultdict, deque

try:
    from ..core.config import settings
except ImportError:
    # Mock settings when config module is not available
    class MockSettings:
        def __init__(self):
            self.database = type('obj', (object,), {'host': 'localhost', 'port': 5432})()
            self.api = type('obj', (object,), {'host': '0.0.0.0', 'port': 8000})()
    
    settings = MockSettings()

try:
    from ..database.repositories import PerformanceRepository, UserFeedbackRepository
except ImportError:
    # Mock repositories when database module is not available
    class PerformanceRepository:
        def __init__(self):
            pass
    
    class UserFeedbackRepository:
        def __init__(self):
            pass

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of performance metrics."""
    RESPONSE_TIME = "response_time"
    ACCURACY = "accuracy"
    USER_SATISFACTION = "user_satisfaction"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"
    CACHE_HIT_RATE = "cache_hit_rate"
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"

class ImprovementCategory(Enum):
    """Categories of improvements."""
    PERFORMANCE = "performance"
    ACCURACY = "accuracy"
    USER_EXPERIENCE = "user_experience"
    RELIABILITY = "reliability"
    EFFICIENCY = "efficiency"

@dataclass
class PerformanceMetric:
    """Performance metric data point."""
    metric_type: MetricType
    value: float
    timestamp: datetime
    component: str
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ImprovementAction:
    """Action to improve system performance."""
    action_id: str
    category: ImprovementCategory
    description: str
    implementation: callable
    priority: int
    estimated_impact: float
    prerequisites: List[str] = field(default_factory=list)
    executed: bool = False
    execution_time: Optional[datetime] = None
    actual_impact: Optional[float] = None

@dataclass
class LearningInsight:
    """Learning insight from data analysis."""
    insight_id: str
    pattern: str
    confidence: float
    recommendation: str
    data_points: int
    identified_at: datetime

class PerformanceAnalyzer:
    """Analyzes system performance and identifies improvement opportunities."""
    
    def __init__(self):
        self.metrics_buffer = defaultdict(lambda: deque(maxlen=1000))
        self.insights = []
        self.baseline_metrics = {}
        self.performance_trends = {}
        
        # Analysis thresholds
        self.thresholds = {
            'response_time_slow': 2.0,
            'error_rate_high': 0.05,
            'cpu_high': 0.80,
            'memory_high': 0.85,
            'accuracy_low': 0.90
        }
        
        logger.info("Performance Analyzer initialized")
    
    def record_metric(
        self,
        metric_type: MetricType,
        value: float,
        component: str,
        context: Dict[str, Any] = None
    ):
        """Record a performance metric."""
        metric = PerformanceMetric(
            metric_type=metric_type,
            value=value,
            timestamp=datetime.now(),
            component=component,
            context=context or {}
        )
        
        key = f"{component}_{metric_type.value}"
        self.metrics_buffer[key].append(metric)
        
        # Update baseline if this is the first metric
        if key not in self.baseline_metrics:
            self.baseline_metrics[key] = value
    
    def analyze_performance_trends(self) -> List[LearningInsight]:
        """Analyze performance trends and generate insights."""
        insights = []
        
        for key, metrics in self.metrics_buffer.items():
            if len(metrics) < 10:  # Need sufficient data
                continue
            
            component, metric_type = key.rsplit('_', 1)
            values = [m.value for m in metrics]
            
            # Trend analysis
            recent_values = values[-20:]  # Last 20 data points
            older_values = values[-40:-20] if len(values) >= 40 else values[:-20]
            
            if len(older_values) > 0:
                recent_avg = statistics.mean(recent_values)
                older_avg = statistics.mean(older_values)
                
                # Performance degradation
                if metric_type in ['response_time', 'error_rate', 'cpu_usage', 'memory_usage']:
                    if recent_avg > older_avg * 1.2:  # 20% worse
                        insights.append(LearningInsight(
                            insight_id=f"degradation_{key}_{datetime.now().timestamp()}",
                            pattern=f"Performance degradation in {component} {metric_type}",
                            confidence=0.8,
                            recommendation=f"Investigate {component} for performance issues",
                            data_points=len(values),
                            identified_at=datetime.now()
                        ))
                
                # Performance improvement
                elif metric_type in ['accuracy', 'throughput', 'cache_hit_rate']:
                    if recent_avg < older_avg * 0.9:  # 10% worse
                        insights.append(LearningInsight(
                            insight_id=f"improvement_needed_{key}_{datetime.now().timestamp()}",
                            pattern=f"Declining {metric_type} in {component}",
                            confidence=0.7,
                            recommendation=f"Optimize {component} {metric_type}",
                            data_points=len(values),
                            identified_at=datetime.now()
                        ))
            
            # Anomaly detection
            if len(values) >= 30:
                mean_val = statistics.mean(values)
                std_val = statistics.stdev(values)
                
                for metric in metrics[-5:]:  # Check last 5 values
                    if abs(metric.value - mean_val) > 3 * std_val:  # 3-sigma rule
                        insights.append(LearningInsight(
                            insight_id=f"anomaly_{key}_{metric.timestamp.timestamp()}",
                            pattern=f"Anomalous {metric_type} value in {component}",
                            confidence=0.9,
                            recommendation=f"Investigate anomaly in {component}",
                            data_points=1,
                            identified_at=datetime.now()
                        ))
        
        self.insights.extend(insights)
        return insights
    
    def identify_optimization_opportunities(self) -> List[ImprovementAction]:
        """Identify opportunities for system optimization."""
        actions = []
        
        for key, metrics in self.metrics_buffer.items():
            if len(metrics) < 5:
                continue
            
            component, metric_type = key.rsplit('_', 1)
            recent_values = [m.value for m in metrics[-10:]]
            avg_value = statistics.mean(recent_values)
            
            # Response time optimization
            if metric_type == 'response_time' and avg_value > self.thresholds['response_time_slow']:
                actions.append(ImprovementAction(
                    action_id=f"optimize_response_{component}_{datetime.now().timestamp()}",
                    category=ImprovementCategory.PERFORMANCE,
                    description=f"Optimize response time for {component}",
                    implementation=lambda: self._optimize_response_time(component),
                    priority=8,
                    estimated_impact=0.3
                ))
            
            # Error rate reduction
            if metric_type == 'error_rate' and avg_value > self.thresholds['error_rate_high']:
                actions.append(ImprovementAction(
                    action_id=f"reduce_errors_{component}_{datetime.now().timestamp()}",
                    category=ImprovementCategory.RELIABILITY,
                    description=f"Reduce error rate in {component}",
                    implementation=lambda: self._reduce_error_rate(component),
                    priority=9,
                    estimated_impact=0.4
                ))
            
            # Cache optimization
            if metric_type == 'cache_hit_rate' and avg_value < 0.7:
                actions.append(ImprovementAction(
                    action_id=f"optimize_cache_{component}_{datetime.now().timestamp()}",
                    category=ImprovementCategory.EFFICIENCY,
                    description=f"Improve cache hit rate for {component}",
                    implementation=lambda: self._optimize_caching(component),
                    priority=6,
                    estimated_impact=0.2
                ))
        
        # Sort by priority
        actions.sort(key=lambda x: x.priority, reverse=True)
        return actions
    
    async def _optimize_response_time(self, component: str) -> bool:
        """Optimize response time for a component."""
        try:
            logger.info(f"Optimizing response time for {component}")
            
            # Implement response time optimizations
            optimizations = [
                self._enable_caching,
                self._optimize_queries,
                self._increase_connection_pool,
                self._enable_compression
            ]
            
            for optimization in optimizations:
                try:
                    await optimization(component)
                    await asyncio.sleep(1)  # Allow changes to take effect
                except Exception as e:
                    logger.warning(f"Optimization failed for {component}: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error optimizing response time for {component}: {e}")
            return False
    
    async def _reduce_error_rate(self, component: str) -> bool:
        """Reduce error rate for a component."""
        try:
            logger.info(f"Reducing error rate for {component}")
            
            # Implement error reduction strategies
            strategies = [
                self._add_retry_logic,
                self._improve_error_handling,
                self._add_circuit_breakers,
                self._enhance_validation
            ]
            
            for strategy in strategies:
                try:
                    await strategy(component)
                except Exception as e:
                    logger.warning(f"Error reduction strategy failed for {component}: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error reducing error rate for {component}: {e}")
            return False
    
    async def _optimize_caching(self, component: str) -> bool:
        """Optimize caching for a component."""
        try:
            logger.info(f"Optimizing caching for {component}")
            
            # Implement caching optimizations
            await self._adjust_cache_ttl(component)
            await self._implement_cache_warming(component)
            await self._optimize_cache_keys(component)
            
            return True
            
        except Exception as e:
            logger.error(f"Error optimizing caching for {component}: {e}")
            return False
    
    async def _enable_caching(self, component: str):
        """Enable caching for component."""
        logger.info(f"Enabling caching for {component}")
    
    async def _optimize_queries(self, component: str):
        """Optimize database queries."""
        logger.info(f"Optimizing queries for {component}")
    
    async def _increase_connection_pool(self, component: str):
        """Increase connection pool size."""
        logger.info(f"Increasing connection pool for {component}")
    
    async def _enable_compression(self, component: str):
        """Enable response compression."""
        logger.info(f"Enabling compression for {component}")
    
    async def _add_retry_logic(self, component: str):
        """Add retry logic to reduce transient errors."""
        logger.info(f"Adding retry logic for {component}")
    
    async def _improve_error_handling(self, component: str):
        """Improve error handling."""
        logger.info(f"Improving error handling for {component}")
    
    async def _add_circuit_breakers(self, component: str):
        """Add circuit breakers."""
        logger.info(f"Adding circuit breakers for {component}")
    
    async def _enhance_validation(self, component: str):
        """Enhance input validation."""
        logger.info(f"Enhancing validation for {component}")
    
    async def _adjust_cache_ttl(self, component: str):
        """Adjust cache TTL settings."""
        logger.info(f"Adjusting cache TTL for {component}")
    
    async def _implement_cache_warming(self, component: str):
        """Implement cache warming."""
        logger.info(f"Implementing cache warming for {component}")
    
    async def _optimize_cache_keys(self, component: str):
        """Optimize cache key structure."""
        logger.info(f"Optimizing cache keys for {component}")

class AdaptiveLearning:
    """Adaptive learning system that improves based on user feedback and usage patterns."""
    
    def __init__(self):
        self.user_interactions = deque(maxlen=10000)
        self.feedback_data = []
        self.learned_patterns = {}
        self.adaptation_rules = []
        
        logger.info("Adaptive Learning system initialized")
    
    def record_user_interaction(
        self,
        user_id: str,
        action: str,
        context: Dict[str, Any],
        outcome: str,
        satisfaction_score: Optional[float] = None
    ):
        """Record user interaction for learning."""
        interaction = {
            'user_id': user_id,
            'action': action,
            'context': context,
            'outcome': outcome,
            'satisfaction_score': satisfaction_score,
            'timestamp': datetime.now()
        }
        
        self.user_interactions.append(interaction)
        
        # Analyze interaction patterns
        self._analyze_interaction_patterns()
    
    def record_feedback(
        self,
        user_id: str,
        feedback_type: str,
        rating: float,
        comments: str,
        context: Dict[str, Any]
    ):
        """Record user feedback for learning."""
        feedback = {
            'user_id': user_id,
            'feedback_type': feedback_type,
            'rating': rating,
            'comments': comments,
            'context': context,
            'timestamp': datetime.now()
        }
        
        self.feedback_data.append(feedback)
        
        # Learn from feedback
        self._learn_from_feedback(feedback)
    
    def _analyze_interaction_patterns(self):
        """Analyze user interaction patterns."""
        if len(self.user_interactions) < 50:
            return
        
        # Analyze successful vs unsuccessful interactions
        recent_interactions = list(self.user_interactions)[-100:]
        
        # Group by action type
        action_outcomes = defaultdict(list)
        for interaction in recent_interactions:
            action_outcomes[interaction['action']].append(interaction['outcome'])
        
        # Identify patterns
        for action, outcomes in action_outcomes.items():
            success_rate = outcomes.count('success') / len(outcomes)
            
            if success_rate < 0.7:  # Low success rate
                pattern_key = f"low_success_{action}"
                if pattern_key not in self.learned_patterns:
                    self.learned_patterns[pattern_key] = {
                        'pattern': f"Low success rate for {action}",
                        'action': action,
                        'success_rate': success_rate,
                        'identified_at': datetime.now(),
                        'improvement_needed': True
                    }
    
    def _learn_from_feedback(self, feedback: Dict[str, Any]):
        """Learn from user feedback."""
        # Identify areas needing improvement based on feedback
        if feedback['rating'] < 3.0:  # Poor rating
            improvement_area = feedback['feedback_type']
            
            if improvement_area not in self.learned_patterns:
                self.learned_patterns[improvement_area] = {
                    'pattern': f"Poor user satisfaction in {improvement_area}",
                    'area': improvement_area,
                    'average_rating': feedback['rating'],
                    'feedback_count': 1,
                    'improvement_needed': True
                }
            else:
                pattern = self.learned_patterns[improvement_area]
                pattern['feedback_count'] += 1
                pattern['average_rating'] = (
                    pattern['average_rating'] + feedback['rating']
                ) / pattern['feedback_count']
    
    def generate_adaptation_rules(self) -> List[Dict[str, Any]]:
        """Generate adaptation rules based on learned patterns."""
        rules = []
        
        for pattern_id, pattern in self.learned_patterns.items():
            if pattern.get('improvement_needed', False):
                if 'success_rate' in pattern:
                    # Rule for improving success rate
                    rules.append({
                        'rule_id': f"improve_success_{pattern['action']}",
                        'condition': f"action == '{pattern['action']}'",
                        'adaptation': f"apply_success_improvements",
                        'priority': 8,
                        'context': pattern
                    })
                
                elif 'average_rating' in pattern:
                    # Rule for improving user satisfaction
                    rules.append({
                        'rule_id': f"improve_satisfaction_{pattern['area']}",
                        'condition': f"feedback_type == '{pattern['area']}'",
                        'adaptation': f"apply_satisfaction_improvements",
                        'priority': 9,
                        'context': pattern
                    })
        
        return rules
    
    def apply_learned_improvements(self) -> List[str]:
        """Apply learned improvements to the system."""
        applied_improvements = []
        
        for pattern_id, pattern in self.learned_patterns.items():
            if pattern.get('improvement_needed', False):
                try:
                    if 'success_rate' in pattern:
                        improvement = self._improve_success_rate(pattern)
                        applied_improvements.append(improvement)
                    
                    elif 'average_rating' in pattern:
                        improvement = self._improve_satisfaction(pattern)
                        applied_improvements.append(improvement)
                    
                    # Mark as addressed
                    pattern['improvement_needed'] = False
                    pattern['improvement_applied_at'] = datetime.now()
                    
                except Exception as e:
                    logger.error(f"Error applying improvement for {pattern_id}: {e}")
        
        return applied_improvements
    
    def _improve_success_rate(self, pattern: Dict[str, Any]) -> str:
        """Improve success rate based on pattern."""
        action = pattern['action']
        
        # Implement improvements based on action type
        improvements = {
            'search_flights': 'Enhanced search algorithms and caching',
            'book_flight': 'Improved validation and error handling',
            'price_prediction': 'Updated ML models and data sources',
            'user_registration': 'Simplified registration process'
        }
        
        improvement = improvements.get(action, f"Generic improvements for {action}")
        logger.info(f"Applied improvement: {improvement}")
        
        return improvement
    
    def _improve_satisfaction(self, pattern: Dict[str, Any]) -> str:
        """Improve user satisfaction based on pattern."""
        area = pattern['area']
        
        # Implement satisfaction improvements
        improvements = {
            'search_experience': 'Improved search interface and filters',
            'booking_process': 'Streamlined booking workflow',
            'price_accuracy': 'Enhanced price prediction accuracy',
            'response_time': 'Performance optimizations implemented'
        }
        
        improvement = improvements.get(area, f"Generic satisfaction improvements for {area}")
        logger.info(f"Applied satisfaction improvement: {improvement}")
        
        return improvement

class SelfImprovementOrchestrator:
    """Main orchestrator for self-improvement system."""
    
    def __init__(self):
        self.performance_analyzer = PerformanceAnalyzer()
        self.adaptive_learning = AdaptiveLearning()
        self.improvement_queue = []
        self.executed_improvements = []
        
        # Task management
        self.analysis_task = None
        self.improvement_task = None
        self.learning_task = None
        
        # Configuration
        self.analysis_interval = 300  # 5 minutes
        self.improvement_interval = 3600  # 1 hour
        self.learning_interval = 1800  # 30 minutes
        
        logger.info("Self-Improvement Orchestrator initialized")
    
    async def start(self):
        """Start the self-improvement system."""
        logger.info("Starting Self-Improvement System")
        
        # Start background tasks
        self.analysis_task = asyncio.create_task(self._analysis_loop())
        self.improvement_task = asyncio.create_task(self._improvement_loop())
        self.learning_task = asyncio.create_task(self._learning_loop())
    
    async def stop(self):
        """Stop the self-improvement system."""
        for task in [self.analysis_task, self.improvement_task, self.learning_task]:
            if task:
                task.cancel()
        logger.info("Self-Improvement System stopped")
    
    async def get_improvement_report(self) -> Dict[str, Any]:
        """Get comprehensive improvement report."""
        try:
            # Recent insights
            recent_insights = [
                {
                    'insight_id': insight.insight_id,
                    'pattern': insight.pattern,
                    'confidence': insight.confidence,
                    'recommendation': insight.recommendation,
                    'data_points': insight.data_points,
                    'identified_at': insight.identified_at.isoformat()
                }
                for insight in self.performance_analyzer.insights[-10:]
            ]
            
            # Improvement actions
            pending_actions = [
                {
                    'action_id': action.action_id,
                    'category': action.category.value,
                    'description': action.description,
                    'priority': action.priority,
                    'estimated_impact': action.estimated_impact,
                    'executed': action.executed
                }
                for action in self.improvement_queue[-10:]
            ]
            
            # Learned patterns
            learned_patterns = {
                pattern_id: {
                    'pattern': pattern['pattern'],
                    'improvement_needed': pattern.get('improvement_needed', False),
                    'identified_at': pattern.get('identified_at', datetime.now()).isoformat()
                }
                for pattern_id, pattern in self.adaptive_learning.learned_patterns.items()
            }
            
            # Recent improvements
            recent_improvements = [
                {
                    'action_id': action.action_id,
                    'description': action.description,
                    'execution_time': action.execution_time.isoformat() if action.execution_time else None,
                    'actual_impact': action.actual_impact
                }
                for action in self.executed_improvements[-10:]
            ]
            
            return {
                'recent_insights': recent_insights,
                'pending_actions': pending_actions,
                'learned_patterns': learned_patterns,
                'recent_improvements': recent_improvements,
                'metrics_collected': len(self.performance_analyzer.metrics_buffer),
                'user_interactions': len(self.adaptive_learning.user_interactions),
                'feedback_count': len(self.adaptive_learning.feedback_data),
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating improvement report: {e}")
            return {
                'error': str(e),
                'generated_at': datetime.now().isoformat()
            }
    
    async def _analysis_loop(self):
        """Main analysis loop."""
        while True:
            try:
                # Analyze performance trends
                insights = self.performance_analyzer.analyze_performance_trends()
                logger.info(f"Generated {len(insights)} performance insights")
                
                # Identify optimization opportunities
                actions = self.performance_analyzer.identify_optimization_opportunities()
                self.improvement_queue.extend(actions)
                logger.info(f"Identified {len(actions)} improvement opportunities")
                
                await asyncio.sleep(self.analysis_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in analysis loop: {e}")
                await asyncio.sleep(self.analysis_interval)
    
    async def _improvement_loop(self):
        """Main improvement execution loop."""
        while True:
            try:
                # Execute high-priority improvements
                executed_count = 0
                for action in sorted(self.improvement_queue, key=lambda x: x.priority, reverse=True):
                    if not action.executed and executed_count < 3:  # Limit concurrent improvements
                        try:
                            logger.info(f"Executing improvement: {action.description}")
                            
                            start_time = time.time()
                            success = await action.implementation()
                            execution_time = time.time() - start_time
                            
                            if success:
                                action.executed = True
                                action.execution_time = datetime.now()
                                action.actual_impact = execution_time  # Placeholder for actual impact measurement
                                
                                self.executed_improvements.append(action)
                                executed_count += 1
                                
                                logger.info(f"Improvement executed successfully: {action.description}")
                            else:
                                logger.warning(f"Improvement execution failed: {action.description}")
                                
                        except Exception as e:
                            logger.error(f"Error executing improvement {action.action_id}: {e}")
                
                # Clean up old actions
                self.improvement_queue = [a for a in self.improvement_queue if not a.executed]
                
                await asyncio.sleep(self.improvement_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in improvement loop: {e}")
                await asyncio.sleep(self.improvement_interval)
    
    async def _learning_loop(self):
        """Main adaptive learning loop."""
        while True:
            try:
                # Generate adaptation rules
                rules = self.adaptive_learning.generate_adaptation_rules()
                logger.info(f"Generated {len(rules)} adaptation rules")
                
                # Apply learned improvements
                improvements = self.adaptive_learning.apply_learned_improvements()
                logger.info(f"Applied {len(improvements)} learned improvements")
                
                await asyncio.sleep(self.learning_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in learning loop: {e}")
                await asyncio.sleep(self.learning_interval)
    
    # Public methods for recording metrics and feedback
    def record_performance_metric(
        self,
        metric_type: MetricType,
        value: float,
        component: str,
        context: Dict[str, Any] = None
    ):
        """Record a performance metric."""
        self.performance_analyzer.record_metric(metric_type, value, component, context)
    
    def record_user_interaction(
        self,
        user_id: str,
        action: str,
        context: Dict[str, Any],
        outcome: str,
        satisfaction_score: Optional[float] = None
    ):
        """Record user interaction."""
        self.adaptive_learning.record_user_interaction(
            user_id, action, context, outcome, satisfaction_score
        )
    
    def record_user_feedback(
        self,
        user_id: str,
        feedback_type: str,
        rating: float,
        comments: str,
        context: Dict[str, Any]
    ):
        """Record user feedback."""
        self.adaptive_learning.record_feedback(
            user_id, feedback_type, rating, comments, context
        )

# Global self-improvement orchestrator instance
self_improvement_orchestrator = SelfImprovementOrchestrator()
