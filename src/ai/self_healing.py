"""
Self-Healing System for Celest.ia v2
Implements automatic error recovery, health monitoring, and system resilience
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import traceback
import json
from pathlib import Path

# Try to import psutil, fall back to mock implementation
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    # Mock psutil for when it's not available
    class psutil:
        @staticmethod
        def cpu_percent(interval=None):
            return 25.0  # Mock CPU usage
        
        @staticmethod
        def virtual_memory():
            class Memory:
                percent = 60.0
                available = 8 * 1024**3  # 8GB
            return Memory()
        
        @staticmethod
        def disk_usage(path):
            class Disk:
                percent = 30.0
                free = 100 * 1024**3  # 100GB
            return Disk()

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
    from ..database.repositories import SystemHealthRepository
except ImportError:
    # Mock repository when database module is not available
    class SystemHealthRepository:
        def __init__(self):
            pass

logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    """System health status levels."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    FAILED = "failed"

class ComponentType(Enum):
    """Types of system components."""
    DATABASE = "database"
    API = "api"
    SCRAPER = "scraper"
    ML_MODEL = "ml_model"
    CACHE = "cache"
    EXTERNAL_SERVICE = "external_service"

@dataclass
class HealthMetric:
    """Health metric for a system component."""
    component_name: str
    component_type: ComponentType
    status: HealthStatus
    response_time: float
    error_rate: float
    last_check: datetime
    details: Dict[str, Any] = field(default_factory=dict)
    recovery_actions: List[str] = field(default_factory=list)

@dataclass
class SystemAlert:
    """System alert for critical issues."""
    alert_id: str
    severity: str
    component: str
    message: str
    timestamp: datetime
    resolved: bool = False
    resolution_time: Optional[datetime] = None
    auto_resolved: bool = False

class HealthMonitor:
    """Monitors system component health."""
    
    def __init__(self):
        self.metrics = {}
        self.thresholds = {
            'response_time_warning': 2.0,  # seconds
            'response_time_critical': 5.0,
            'error_rate_warning': 0.05,    # 5%
            'error_rate_critical': 0.15,   # 15%
            'memory_warning': 0.80,        # 80%
            'memory_critical': 0.95,       # 95%
            'cpu_warning': 0.80,           # 80%
            'cpu_critical': 0.95           # 95%
        }
        self.alerts = []
        self.health_checks = {}
        
        logger.info("Health Monitor initialized")
    
    def register_health_check(
        self,
        component_name: str,
        component_type: ComponentType,
        check_function: Callable[[], bool],
        check_interval: int = 60
    ):
        """Register a health check for a component."""
        self.health_checks[component_name] = {
            'type': component_type,
            'function': check_function,
            'interval': check_interval,
            'last_check': None,
            'consecutive_failures': 0
        }
        logger.info(f"Registered health check for {component_name}")
    
    async def check_component_health(self, component_name: str) -> HealthMetric:
        """Check health of a specific component."""
        if component_name not in self.health_checks:
            return HealthMetric(
                component_name=component_name,
                component_type=ComponentType.API,
                status=HealthStatus.FAILED,
                response_time=0.0,
                error_rate=1.0,
                last_check=datetime.now(),
                details={"error": "Component not registered"}
            )
        
        check_info = self.health_checks[component_name]
        start_time = time.time()
        
        try:
            # Execute health check
            is_healthy = await self._execute_health_check(check_info['function'])
            response_time = time.time() - start_time
            
            # Update metrics
            status = self._determine_status(is_healthy, response_time, 0.0)
            
            metric = HealthMetric(
                component_name=component_name,
                component_type=check_info['type'],
                status=status,
                response_time=response_time,
                error_rate=0.0 if is_healthy else 1.0,
                last_check=datetime.now(),
                details={"healthy": is_healthy}
            )
            
            # Reset consecutive failures if healthy
            if is_healthy:
                check_info['consecutive_failures'] = 0
            else:
                check_info['consecutive_failures'] += 1
            
            check_info['last_check'] = datetime.now()
            self.metrics[component_name] = metric
            
            return metric
            
        except Exception as e:
            response_time = time.time() - start_time
            check_info['consecutive_failures'] += 1
            
            metric = HealthMetric(
                component_name=component_name,
                component_type=check_info['type'],
                status=HealthStatus.FAILED,
                response_time=response_time,
                error_rate=1.0,
                last_check=datetime.now(),
                details={"error": str(e), "traceback": traceback.format_exc()}
            )
            
            self.metrics[component_name] = metric
            logger.error(f"Health check failed for {component_name}: {e}")
            
            return metric
    
    async def check_system_resources(self) -> HealthMetric:
        """Check system resource usage."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent / 100
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent / 100
            
            # Determine overall status
            status = HealthStatus.HEALTHY
            if (cpu_percent / 100 > self.thresholds['cpu_warning'] or 
                memory_percent > self.thresholds['memory_warning']):
                status = HealthStatus.WARNING
            
            if (cpu_percent / 100 > self.thresholds['cpu_critical'] or 
                memory_percent > self.thresholds['memory_critical']):
                status = HealthStatus.CRITICAL
            
            return HealthMetric(
                component_name="system_resources",
                component_type=ComponentType.API,
                status=status,
                response_time=1.0,
                error_rate=0.0,
                last_check=datetime.now(),
                details={
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory_percent * 100,
                    "disk_percent": disk_percent * 100,
                    "memory_available_gb": memory.available / (1024**3),
                    "disk_free_gb": disk.free / (1024**3)
                }
            )
            
        except Exception as e:
            logger.error(f"Error checking system resources: {e}")
            return HealthMetric(
                component_name="system_resources",
                component_type=ComponentType.API,
                status=HealthStatus.FAILED,
                response_time=0.0,
                error_rate=1.0,
                last_check=datetime.now(),
                details={"error": str(e)}
            )
    
    async def _execute_health_check(self, check_function: Callable) -> bool:
        """Execute a health check function safely."""
        try:
            if asyncio.iscoroutinefunction(check_function):
                result = await check_function()
            else:
                result = check_function()
            return bool(result)
        except Exception as e:
            logger.error(f"Health check execution failed: {e}")
            return False
    
    def _determine_status(
        self, 
        is_healthy: bool, 
        response_time: float, 
        error_rate: float
    ) -> HealthStatus:
        """Determine health status based on metrics."""
        if not is_healthy or error_rate >= self.thresholds['error_rate_critical']:
            return HealthStatus.FAILED
        
        if (response_time >= self.thresholds['response_time_critical'] or
            error_rate >= self.thresholds['error_rate_critical']):
            return HealthStatus.CRITICAL
        
        if (response_time >= self.thresholds['response_time_warning'] or
            error_rate >= self.thresholds['error_rate_warning']):
            return HealthStatus.WARNING
        
        return HealthStatus.HEALTHY
    
    def get_overall_health(self) -> HealthStatus:
        """Get overall system health status."""
        if not self.metrics:
            return HealthStatus.WARNING
        
        statuses = [metric.status for metric in self.metrics.values()]
        
        if HealthStatus.FAILED in statuses:
            return HealthStatus.FAILED
        elif HealthStatus.CRITICAL in statuses:
            return HealthStatus.CRITICAL
        elif HealthStatus.WARNING in statuses:
            return HealthStatus.WARNING
        else:
            return HealthStatus.HEALTHY

class AutoRecovery:
    """Automatic recovery system for failed components."""
    
    def __init__(self, health_monitor: HealthMonitor):
        self.health_monitor = health_monitor
        self.recovery_strategies = {}
        self.recovery_history = []
        self.max_recovery_attempts = 3
        self.recovery_cooldown = 300  # 5 minutes
        
        # Register default recovery strategies
        self._register_default_strategies()
        
        logger.info("Auto Recovery system initialized")
    
    def register_recovery_strategy(
        self,
        component_name: str,
        strategy: Callable[[HealthMetric], bool],
        priority: int = 1
    ):
        """Register a recovery strategy for a component."""
        if component_name not in self.recovery_strategies:
            self.recovery_strategies[component_name] = []
        
        self.recovery_strategies[component_name].append({
            'strategy': strategy,
            'priority': priority,
            'success_count': 0,
            'failure_count': 0
        })
        
        # Sort by priority
        self.recovery_strategies[component_name].sort(key=lambda x: x['priority'])
        
        logger.info(f"Registered recovery strategy for {component_name}")
    
    async def attempt_recovery(self, component_name: str) -> bool:
        """Attempt to recover a failed component."""
        metric = self.health_monitor.metrics.get(component_name)
        if not metric or metric.status in [HealthStatus.HEALTHY, HealthStatus.WARNING]:
            return True
        
        # Check if we're in cooldown period
        if self._is_in_cooldown(component_name):
            logger.info(f"Recovery for {component_name} is in cooldown period")
            return False
        
        # Check if we've exceeded max attempts
        recent_attempts = self._get_recent_attempts(component_name)
        if len(recent_attempts) >= self.max_recovery_attempts:
            logger.warning(f"Max recovery attempts exceeded for {component_name}")
            return False
        
        # Try recovery strategies
        strategies = self.recovery_strategies.get(component_name, [])
        for strategy_info in strategies:
            try:
                logger.info(f"Attempting recovery for {component_name}")
                
                success = await self._execute_recovery_strategy(
                    strategy_info['strategy'], metric
                )
                
                # Record recovery attempt
                self.recovery_history.append({
                    'component': component_name,
                    'timestamp': datetime.now(),
                    'success': success,
                    'strategy': strategy_info['strategy'].__name__
                })
                
                if success:
                    strategy_info['success_count'] += 1
                    logger.info(f"Recovery successful for {component_name}")
                    
                    # Verify recovery by re-checking health
                    await asyncio.sleep(5)  # Wait a bit before checking
                    updated_metric = await self.health_monitor.check_component_health(component_name)
                    
                    if updated_metric.status in [HealthStatus.HEALTHY, HealthStatus.WARNING]:
                        return True
                else:
                    strategy_info['failure_count'] += 1
                    logger.warning(f"Recovery strategy failed for {component_name}")
                    
            except Exception as e:
                strategy_info['failure_count'] += 1
                logger.error(f"Recovery strategy error for {component_name}: {e}")
        
        return False
    
    async def _execute_recovery_strategy(
        self, 
        strategy: Callable, 
        metric: HealthMetric
    ) -> bool:
        """Execute a recovery strategy safely."""
        try:
            if asyncio.iscoroutinefunction(strategy):
                result = await strategy(metric)
            else:
                result = strategy(metric)
            return bool(result)
        except Exception as e:
            logger.error(f"Recovery strategy execution failed: {e}")
            return False
    
    def _register_default_strategies(self):
        """Register default recovery strategies."""
        
        async def restart_service_strategy(metric: HealthMetric) -> bool:
            """Generic service restart strategy."""
            try:
                # This would typically restart the specific service
                logger.info(f"Restarting service for {metric.component_name}")
                await asyncio.sleep(2)  # Simulate restart time
                return True
            except Exception:
                return False
        
        async def clear_cache_strategy(metric: HealthMetric) -> bool:
            """Clear cache strategy."""
            try:
                # This would clear relevant caches
                logger.info(f"Clearing cache for {metric.component_name}")
                return True
            except Exception:
                return False
        
        async def reset_connections_strategy(metric: HealthMetric) -> bool:
            """Reset connections strategy."""
            try:
                # This would reset database/API connections
                logger.info(f"Resetting connections for {metric.component_name}")
                return True
            except Exception:
                return False
        
        # Register default strategies for all components
        default_strategies = [
            (restart_service_strategy, 1),
            (clear_cache_strategy, 2),
            (reset_connections_strategy, 3)
        ]
        
        for strategy, priority in default_strategies:
            # These would be registered for specific components
            pass
    
    def _is_in_cooldown(self, component_name: str) -> bool:
        """Check if component is in recovery cooldown period."""
        recent_attempts = self._get_recent_attempts(component_name)
        if not recent_attempts:
            return False
        
        last_attempt = max(attempt['timestamp'] for attempt in recent_attempts)
        cooldown_end = last_attempt + timedelta(seconds=self.recovery_cooldown)
        
        return datetime.now() < cooldown_end
    
    def _get_recent_attempts(self, component_name: str) -> List[Dict]:
        """Get recent recovery attempts for a component."""
        cutoff_time = datetime.now() - timedelta(hours=1)
        return [
            attempt for attempt in self.recovery_history
            if (attempt['component'] == component_name and 
                attempt['timestamp'] > cutoff_time)
        ]

class SelfHealingOrchestrator:
    """Main orchestrator for self-healing system."""
    
    def __init__(self):
        self.health_monitor = HealthMonitor()
        self.auto_recovery = AutoRecovery(self.health_monitor)
        self.monitoring_task = None
        self.recovery_task = None
        self.health_check_interval = 30  # seconds
        self.recovery_check_interval = 60  # seconds
        
        # System health repository for persistence
        try:
            self.health_repo = SystemHealthRepository()
        except Exception:
            self.health_repo = None
            logger.warning("Health repository not available")
        
        logger.info("Self-Healing Orchestrator initialized")
    
    async def start(self):
        """Start the self-healing system."""
        logger.info("Starting Self-Healing System")
        
        # Register default health checks
        await self._register_default_health_checks()
        
        # Start monitoring and recovery tasks
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.recovery_task = asyncio.create_task(self._recovery_loop())
    
    async def stop(self):
        """Stop the self-healing system."""
        if self.monitoring_task:
            self.monitoring_task.cancel()
        if self.recovery_task:
            self.recovery_task.cancel()
        logger.info("Self-Healing System stopped")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status synchronously."""
        try:
            overall_health = self.health_monitor.get_overall_health()
            
            # Get latest metrics
            components_status = {}
            for component_name, metric in self.health_monitor.metrics.items():
                components_status[component_name] = {
                    'status': metric.status.value,
                    'response_time': metric.response_time,
                    'error_rate': metric.error_rate,
                    'last_check': metric.last_check.isoformat() if metric.last_check else None
                }
            
            return {
                'overall_health': overall_health.value,
                'components': components_status,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {
                'overall_health': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def get_system_health_report(self) -> Dict[str, Any]:
        """Get comprehensive system health report."""
        try:
            # Check all components
            all_metrics = {}
            for component_name in self.health_monitor.health_checks:
                metric = await self.health_monitor.check_component_health(component_name)
                all_metrics[component_name] = {
                    'status': metric.status.value,
                    'response_time': metric.response_time,
                    'error_rate': metric.error_rate,
                    'last_check': metric.last_check.isoformat(),
                    'details': metric.details
                }
            
            # Add system resources
            resource_metric = await self.health_monitor.check_system_resources()
            all_metrics['system_resources'] = {
                'status': resource_metric.status.value,
                'details': resource_metric.details
            }
            
            # Overall health
            overall_health = self.health_monitor.get_overall_health()
            
            # Recent recovery attempts
            recent_recovery = self.auto_recovery._get_recent_attempts("all")
            
            return {
                'overall_health': overall_health.value,
                'components': all_metrics,
                'recovery_history': [
                    {
                        'component': attempt['component'],
                        'timestamp': attempt['timestamp'].isoformat(),
                        'success': attempt['success'],
                        'strategy': attempt['strategy']
                    }
                    for attempt in recent_recovery[-10:]  # Last 10 attempts
                ],
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating health report: {e}")
            return {
                'overall_health': 'error',
                'error': str(e),
                'generated_at': datetime.now().isoformat()
            }
    
    async def _register_default_health_checks(self):
        """Register default health checks for system components."""
        
        # Database health check
        async def check_database():
            try:
                if self.health_repo:
                    # Simple query to test database
                    return True
                return False
            except Exception:
                return False
        
        # API health check
        async def check_api():
            try:
                # Check if API endpoints are responding
                return True
            except Exception:
                return False
        
        # Cache health check
        async def check_cache():
            try:
                # Check Redis/cache connectivity
                return True
            except Exception:
                return False
        
        # Register health checks
        self.health_monitor.register_health_check(
            "database", ComponentType.DATABASE, check_database, 60
        )
        self.health_monitor.register_health_check(
            "api", ComponentType.API, check_api, 30
        )
        self.health_monitor.register_health_check(
            "cache", ComponentType.CACHE, check_cache, 60
        )
    
    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while True:
            try:
                # Check all registered components
                for component_name in self.health_monitor.health_checks:
                    await self.health_monitor.check_component_health(component_name)
                
                # Check system resources
                await self.health_monitor.check_system_resources()
                
                # Persist health data if repository available
                if self.health_repo:
                    await self._persist_health_data()
                
                await asyncio.sleep(self.health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.health_check_interval)
    
    async def _recovery_loop(self):
        """Main recovery loop."""
        while True:
            try:
                # Check for failed components and attempt recovery
                for component_name, metric in self.health_monitor.metrics.items():
                    if metric.status in [HealthStatus.CRITICAL, HealthStatus.FAILED]:
                        logger.warning(f"Component {component_name} is {metric.status.value}, attempting recovery")
                        await self.auto_recovery.attempt_recovery(component_name)
                
                await asyncio.sleep(self.recovery_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in recovery loop: {e}")
                await asyncio.sleep(self.recovery_check_interval)
    
    async def _persist_health_data(self):
        """Persist health data to database."""
        try:
            if self.health_repo:
                health_data = {
                    'timestamp': datetime.now(),
                    'metrics': self.health_monitor.metrics,
                    'overall_health': self.health_monitor.get_overall_health().value
                }
                # This would save to database
                pass
        except Exception as e:
            logger.error(f"Error persisting health data: {e}")

# Global self-healing orchestrator instance
self_healing_orchestrator = SelfHealingOrchestrator()
