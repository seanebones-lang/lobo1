"""
Performance Monitoring System
Tracks system performance, metrics, and alerts
"""

import time
import psutil
import threading
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from statistics import mean, median, stdev
import logging
import json
from collections import deque, defaultdict

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    timestamp: datetime
    query_latency: float
    retrieval_time: float
    generation_time: float
    total_time: float
    cache_hit: bool
    response_length: int
    confidence_score: float
    memory_usage: float
    cpu_usage: float
    active_connections: int
    error_occurred: bool
    error_message: Optional[str] = None

@dataclass
class SystemMetrics:
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    network_io: Dict[str, int]
    active_processes: int
    load_average: List[float]

@dataclass
class Alert:
    id: str
    type: str
    severity: str
    message: str
    timestamp: datetime
    resolved: bool = False
    metadata: Dict[str, Any] = None

class PerformanceMonitor:
    def __init__(self, max_history: int = 1000, alert_thresholds: Optional[Dict[str, float]] = None):
        """
        Initialize performance monitor
        
        Args:
            max_history: Maximum number of metrics to keep in memory
            alert_thresholds: Custom alert thresholds
        """
        self.max_history = max_history
        self.metrics_history: deque = deque(maxlen=max_history)
        self.system_metrics_history: deque = deque(maxlen=max_history)
        self.alerts: List[Alert] = []
        self.alert_counter = 0
        
        # Default alert thresholds
        self.thresholds = alert_thresholds or {
            'query_latency': 10.0,  # seconds
            'cpu_usage': 80.0,     # percent
            'memory_usage': 85.0,   # percent
            'confidence_score': 0.5, # minimum confidence
            'error_rate': 0.1       # 10% error rate
        }
        
        # Performance tracking
        self.session_stats = defaultdict(int)
        self.error_counts = defaultdict(int)
        
        # Start system monitoring thread
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_system, daemon=True)
        self.monitor_thread.start()
    
    def record_query(self, metrics: PerformanceMetrics) -> None:
        """Record query performance metrics"""
        self.metrics_history.append(metrics)
        
        # Update session stats
        self.session_stats['total_queries'] += 1
        if metrics.cache_hit:
            self.session_stats['cache_hits'] += 1
        if metrics.error_occurred:
            self.session_stats['errors'] += 1
            if metrics.error_message:
                self.error_counts[metrics.error_message] += 1
        
        # Check for alerts
        self._check_alerts(metrics)
    
    def _monitor_system(self) -> None:
        """Monitor system resources in background thread"""
        while self.monitoring_active:
            try:
                system_metrics = self._collect_system_metrics()
                self.system_metrics_history.append(system_metrics)
                self._check_system_alerts(system_metrics)
            except Exception as e:
                logger.error(f"Error in system monitoring: {e}")
            
            time.sleep(30)  # Check every 30 seconds
    
    def _collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network_io = psutil.net_io_counters()._asdict()
            
            # Get load average (Unix-like systems)
            try:
                load_avg = list(psutil.getloadavg())
            except AttributeError:
                load_avg = [0.0, 0.0, 0.0]  # Windows doesn't have load average
            
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_usage_percent=disk.percent,
                network_io=network_io,
                active_processes=len(psutil.pids()),
                load_average=load_avg
            )
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=0.0,
                memory_percent=0.0,
                disk_usage_percent=0.0,
                network_io={},
                active_processes=0,
                load_average=[0.0, 0.0, 0.0]
            )
    
    def _check_alerts(self, metrics: PerformanceMetrics) -> None:
        """Check for performance alerts"""
        alerts_created = []
        
        # High latency alert
        if metrics.query_latency > self.thresholds['query_latency']:
            alerts_created.append(self._create_alert(
                'high_latency',
                'warning',
                f'Query latency exceeded threshold: {metrics.query_latency:.2f}s'
            ))
        
        # Low confidence alert
        if metrics.confidence_score < self.thresholds['confidence_score']:
            alerts_created.append(self._create_alert(
                'low_confidence',
                'warning',
                f'Low confidence response: {metrics.confidence_score:.2f}'
            ))
        
        # Error alert
        if metrics.error_occurred:
            alerts_created.append(self._create_alert(
                'error',
                'error',
                f'Query failed: {metrics.error_message or "Unknown error"}'
            ))
        
        # High memory usage alert
        if metrics.memory_usage > self.thresholds['memory_usage']:
            alerts_created.append(self._create_alert(
                'high_memory',
                'warning',
                f'High memory usage: {metrics.memory_usage:.1f}%'
            ))
        
        # High CPU usage alert
        if metrics.cpu_usage > self.thresholds['cpu_usage']:
            alerts_created.append(self._create_alert(
                'high_cpu',
                'warning',
                f'High CPU usage: {metrics.cpu_usage:.1f}%'
            ))
        
        self.alerts.extend(alerts_created)
    
    def _check_system_alerts(self, metrics: SystemMetrics) -> None:
        """Check for system-level alerts"""
        alerts_created = []
        
        # High CPU usage
        if metrics.cpu_percent > self.thresholds['cpu_usage']:
            alerts_created.append(self._create_alert(
                'system_high_cpu',
                'warning',
                f'System CPU usage high: {metrics.cpu_percent:.1f}%'
            ))
        
        # High memory usage
        if metrics.memory_percent > self.thresholds['memory_usage']:
            alerts_created.append(self._create_alert(
                'system_high_memory',
                'warning',
                f'System memory usage high: {metrics.memory_percent:.1f}%'
            ))
        
        # High disk usage
        if metrics.disk_usage_percent > 90:
            alerts_created.append(self._create_alert(
                'high_disk_usage',
                'critical',
                f'Disk usage high: {metrics.disk_usage_percent:.1f}%'
            ))
        
        self.alerts.extend(alerts_created)
    
    def _create_alert(self, alert_type: str, severity: str, message: str) -> Alert:
        """Create a new alert"""
        self.alert_counter += 1
        return Alert(
            id=f"alert_{self.alert_counter}",
            type=alert_type,
            severity=severity,
            message=message,
            timestamp=datetime.now(),
            metadata={'threshold': self.thresholds.get(alert_type, 'unknown')}
        )
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        if not self.metrics_history:
            return {'status': 'no_data'}
        
        # Calculate statistics from recent metrics
        recent_metrics = list(self.metrics_history)[-100:]  # Last 100 queries
        
        latencies = [m.query_latency for m in recent_metrics]
        retrieval_times = [m.retrieval_time for m in recent_metrics]
        generation_times = [m.generation_time for m in recent_metrics]
        confidence_scores = [m.confidence_score for m in recent_metrics]
        
        # Calculate rates
        total_queries = len(recent_metrics)
        cache_hits = sum(1 for m in recent_metrics if m.cache_hit)
        errors = sum(1 for m in recent_metrics if m.error_occurred)
        
        cache_hit_rate = cache_hits / total_queries if total_queries > 0 else 0
        error_rate = errors / total_queries if total_queries > 0 else 0
        
        # Calculate percentiles
        def percentile(data, p):
            if not data:
                return 0
            sorted_data = sorted(data)
            index = int((p / 100) * len(sorted_data))
            return sorted_data[min(index, len(sorted_data) - 1)]
        
        return {
            'query_metrics': {
                'total_queries': total_queries,
                'avg_latency': mean(latencies) if latencies else 0,
                'median_latency': median(latencies) if latencies else 0,
                'p95_latency': percentile(latencies, 95),
                'p99_latency': percentile(latencies, 99),
                'max_latency': max(latencies) if latencies else 0,
                'min_latency': min(latencies) if latencies else 0,
                'std_latency': stdev(latencies) if len(latencies) > 1 else 0
            },
            'component_metrics': {
                'avg_retrieval_time': mean(retrieval_times) if retrieval_times else 0,
                'avg_generation_time': mean(generation_times) if generation_times else 0,
                'avg_confidence': mean(confidence_scores) if confidence_scores else 0,
                'min_confidence': min(confidence_scores) if confidence_scores else 0,
                'max_confidence': max(confidence_scores) if confidence_scores else 0
            },
            'rates': {
                'cache_hit_rate': cache_hit_rate,
                'error_rate': error_rate,
                'throughput': total_queries / 3600  # queries per hour
            },
            'session_stats': dict(self.session_stats),
            'error_breakdown': dict(self.error_counts),
            'active_alerts': len([a for a in self.alerts if not a.resolved]),
            'system_health': self._get_system_health()
        }
    
    def _get_system_health(self) -> Dict[str, Any]:
        """Get current system health status"""
        if not self.system_metrics_history:
            return {'status': 'unknown'}
        
        latest_system = self.system_metrics_history[-1]
        
        health_score = 100
        issues = []
        
        # Check CPU
        if latest_system.cpu_percent > 80:
            health_score -= 20
            issues.append('High CPU usage')
        elif latest_system.cpu_percent > 60:
            health_score -= 10
            issues.append('Elevated CPU usage')
        
        # Check Memory
        if latest_system.memory_percent > 90:
            health_score -= 30
            issues.append('Critical memory usage')
        elif latest_system.memory_percent > 80:
            health_score -= 15
            issues.append('High memory usage')
        
        # Check Disk
        if latest_system.disk_usage_percent > 95:
            health_score -= 25
            issues.append('Critical disk usage')
        elif latest_system.disk_usage_percent > 85:
            health_score -= 10
            issues.append('High disk usage')
        
        # Determine status
        if health_score >= 90:
            status = 'excellent'
        elif health_score >= 70:
            status = 'good'
        elif health_score >= 50:
            status = 'fair'
        else:
            status = 'poor'
        
        return {
            'status': status,
            'health_score': health_score,
            'issues': issues,
            'cpu_percent': latest_system.cpu_percent,
            'memory_percent': latest_system.memory_percent,
            'disk_percent': latest_system.disk_usage_percent,
            'load_average': latest_system.load_average
        }
    
    def get_alerts(self, severity: Optional[str] = None, 
                   resolved: Optional[bool] = None) -> List[Alert]:
        """Get alerts with optional filtering"""
        filtered_alerts = self.alerts
        
        if severity:
            filtered_alerts = [a for a in filtered_alerts if a.severity == severity]
        
        if resolved is not None:
            filtered_alerts = [a for a in filtered_alerts if a.resolved == resolved]
        
        return sorted(filtered_alerts, key=lambda x: x.timestamp, reverse=True)
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.resolved = True
                return True
        return False
    
    def get_throughput_metrics(self, time_window: int = 3600) -> Dict[str, Any]:
        """Get throughput metrics for specified time window"""
        cutoff_time = datetime.now() - timedelta(seconds=time_window)
        recent_metrics = [m for m in self.metrics_history if m.timestamp > cutoff_time]
        
        if not recent_metrics:
            return {'queries_per_hour': 0, 'avg_response_time': 0}
        
        queries_per_hour = len(recent_metrics) * (3600 / time_window)
        avg_response_time = mean([m.query_latency for m in recent_metrics])
        
        return {
            'queries_per_hour': queries_per_hour,
            'avg_response_time': avg_response_time,
            'time_window_seconds': time_window,
            'total_queries': len(recent_metrics)
        }
    
    def export_metrics(self, filepath: str) -> None:
        """Export metrics to JSON file"""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'performance_stats': self.get_performance_stats(),
            'recent_metrics': [asdict(m) for m in list(self.metrics_history)[-100:]],
            'system_metrics': [asdict(m) for m in list(self.system_metrics_history)[-50:]],
            'alerts': [asdict(a) for a in self.alerts[-50:]]
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
    
    def cleanup_old_data(self, max_age_hours: int = 24) -> int:
        """Clean up old metrics and alerts"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        # Clean up old metrics
        old_metrics = [m for m in self.metrics_history if m.timestamp < cutoff_time]
        for metric in old_metrics:
            self.metrics_history.remove(metric)
        
        # Clean up old system metrics
        old_system_metrics = [m for m in self.system_metrics_history if m.timestamp < cutoff_time]
        for metric in old_system_metrics:
            self.system_metrics_history.remove(metric)
        
        # Clean up old alerts
        old_alerts = [a for a in self.alerts if a.timestamp < cutoff_time and a.resolved]
        for alert in old_alerts:
            self.alerts.remove(alert)
        
        return len(old_metrics) + len(old_system_metrics) + len(old_alerts)
    
    def stop_monitoring(self) -> None:
        """Stop system monitoring"""
        self.monitoring_active = False
        if self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
    
    def get_recommendations(self) -> List[str]:
        """Get performance improvement recommendations"""
        recommendations = []
        stats = self.get_performance_stats()
        
        # Check cache hit rate
        if stats['rates']['cache_hit_rate'] < 0.3:
            recommendations.append("Consider increasing cache TTL or implementing more aggressive caching")
        
        # Check error rate
        if stats['rates']['error_rate'] > 0.05:
            recommendations.append("High error rate detected - investigate error logs and improve error handling")
        
        # Check latency
        if stats['query_metrics']['avg_latency'] > 5.0:
            recommendations.append("High average latency - consider optimizing retrieval or generation processes")
        
        # Check confidence scores
        if stats['component_metrics']['avg_confidence'] < 0.7:
            recommendations.append("Low confidence scores - consider improving retrieval quality or prompt engineering")
        
        # Check system health
        system_health = stats['system_health']
        if system_health['status'] in ['fair', 'poor']:
            recommendations.append(f"System health is {system_health['status']} - consider scaling resources")
        
        return recommendations
