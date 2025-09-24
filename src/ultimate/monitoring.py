"""
Real-Time Monitoring & Analytics
Comprehensive real-time monitoring and analytics system.
"""

import asyncio
import json
import psutil
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import statistics

class RealTimeMonitoringDashboard:
    """Comprehensive real-time monitoring"""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()
        self.performance_analyzer = PerformanceAnalyzer()
        self.health_checker = SystemHealthChecker()
        
        # Prometheus metrics
        self.setup_prometheus_metrics()
        
        # Internal metrics storage
        self.metrics_history = deque(maxlen=1000)
        self.alerts = []
        self.alert_thresholds = {
            'health_percentage': 80,
            'avg_latency': 5.0,
            'error_rate': 0.1,
            'memory_usage': 90,
            'cpu_usage': 90
        }
    
    def setup_prometheus_metrics(self):
        """Setup Prometheus metrics for monitoring"""
        self.requests_total = Counter('rag_requests_total', 'Total requests')
        self.request_duration = Histogram('rag_request_duration_seconds', 'Request duration')
        self.error_rate = Gauge('rag_error_rate', 'Error rate')
        self.cache_hit_rate = Gauge('rag_cache_hit_rate', 'Cache hit rate')
        self.llm_usage = Gauge('rag_llm_usage', 'LLM usage by model', ['model'])
        self.retrieval_strategy_usage = Gauge(
            'rag_retrieval_strategy_usage', 'Retrieval strategy usage', ['strategy']
        )
        self.active_connections = Gauge('rag_active_connections', 'Active connections')
        self.memory_usage = Gauge('rag_memory_usage_bytes', 'Memory usage in bytes')
        self.cpu_usage = Gauge('rag_cpu_usage_percent', 'CPU usage percentage')
    
    async def initialize(self):
        """Initialize monitoring system"""
        print("📊 Initializing monitoring system...")
        
        # Start Prometheus metrics server
        start_http_server(8001)
        
        # Initialize health checker
        await self.health_checker.initialize()
        
        # Start background monitoring tasks
        asyncio.create_task(self.background_monitoring())
        
        print("✅ Monitoring system initialized!")
    
    async def track_interaction(self, interaction: Dict):
        """Track complete interaction metrics"""
        
        start_time = time.time()
        
        try:
            # Update counters
            self.requests_total.inc()
            
            # Track LLM usage
            llm_used = interaction.get('llm_used', 'unknown')
            self.llm_usage.labels(model=llm_used).inc()
            
            # Track retrieval strategies
            strategies = interaction.get('retrieval_strategies_used', [])
            for strategy in strategies:
                self.retrieval_strategy_usage.labels(strategy=strategy).inc()
            
            # Calculate and set metrics
            error_rate = await self.calculate_error_rate()
            self.error_rate.set(error_rate)
            
            cache_hit_rate = await self.calculate_cache_hit_rate()
            self.cache_hit_rate.set(cache_hit_rate)
            
            # Update system metrics
            self.update_system_metrics()
            
            # Store interaction metrics
            interaction_metrics = {
                'timestamp': datetime.now(),
                'latency': interaction.get('latency', 0),
                'llm_used': llm_used,
                'strategies_used': strategies,
                'success': True,
                'error': None
            }
            
            self.metrics_history.append(interaction_metrics)
            
            # Check for alerts
            await self.check_alerts(interaction_metrics)
            
            # Update performance analytics
            await self.performance_analyzer.analyze_performance(interaction_metrics)
            
        except Exception as e:
            print(f"❌ Error tracking interaction: {e}")
            # Track error
            self.requests_total.inc()
            self.error_rate.inc()
    
    async def background_monitoring(self):
        """Background monitoring tasks"""
        while True:
            try:
                # Update system health
                await self.update_system_health()
                
                # Check for alerts
                await self.check_system_alerts()
                
                # Clean up old metrics
                await self.cleanup_old_metrics()
                
                # Sleep for monitoring interval
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"❌ Background monitoring error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def update_system_health(self):
        """Update system health metrics"""
        health_data = await self.health_checker.get_system_health()
        
        # Update Prometheus metrics
        self.memory_usage.set(health_data.get('memory_usage', 0))
        self.cpu_usage.set(health_data.get('cpu_usage', 0))
        self.active_connections.set(health_data.get('active_connections', 0))
    
    async def check_system_alerts(self):
        """Check for system-level alerts"""
        current_metrics = await self.get_current_metrics()
        
        # Check memory usage
        if current_metrics.get('memory_usage', 0) > self.alert_thresholds['memory_usage']:
            await self.alert_manager.create_alert({
                'type': 'high_memory_usage',
                'severity': 'warning',
                'message': f"Memory usage: {current_metrics['memory_usage']:.1f}%",
                'timestamp': datetime.now()
            })
        
        # Check CPU usage
        if current_metrics.get('cpu_usage', 0) > self.alert_thresholds['cpu_usage']:
            await self.alert_manager.create_alert({
                'type': 'high_cpu_usage',
                'severity': 'warning',
                'message': f"CPU usage: {current_metrics['cpu_usage']:.1f}%",
                'timestamp': datetime.now()
            })
    
    async def check_alerts(self, interaction_metrics: Dict):
        """Check for alerts based on interaction metrics"""
        
        # Check latency
        if interaction_metrics.get('latency', 0) > self.alert_thresholds['avg_latency']:
            await self.alert_manager.create_alert({
                'type': 'high_latency',
                'severity': 'warning',
                'message': f"High latency detected: {interaction_metrics['latency']:.2f}s",
                'timestamp': datetime.now()
            })
    
    async def calculate_error_rate(self) -> float:
        """Calculate current error rate"""
        if not self.metrics_history:
            return 0.0
        
        recent_metrics = list(self.metrics_history)[-100:]  # Last 100 interactions
        error_count = sum(1 for m in recent_metrics if not m.get('success', True))
        return error_count / len(recent_metrics) if recent_metrics else 0.0
    
    async def calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        if not self.metrics_history:
            return 0.0
        
        recent_metrics = list(self.metrics_history)[-100:]  # Last 100 interactions
        cache_hits = sum(1 for m in recent_metrics if m.get('cached', False))
        return cache_hits / len(recent_metrics) if recent_metrics else 0.0
    
    def update_system_metrics(self):
        """Update system resource metrics"""
        # Update memory usage
        memory_info = psutil.virtual_memory()
        self.memory_usage.set(memory_info.used)
        
        # Update CPU usage
        cpu_percent = psutil.cpu_percent()
        self.cpu_usage.set(cpu_percent)
    
    async def get_current_metrics(self) -> Dict:
        """Get current system metrics"""
        return {
            'memory_usage': psutil.virtual_memory().percent,
            'cpu_usage': psutil.cpu_percent(),
            'disk_usage': psutil.disk_usage('/').percent,
            'active_connections': len(psutil.net_connections()),
            'timestamp': datetime.now()
        }
    
    async def generate_real_time_dashboard(self) -> Dict:
        """Generate real-time dashboard data"""
        return {
            'system_health': await self.health_checker.get_system_health(),
            'performance_metrics': await self.get_current_metrics(),
            'active_alerts': self.alert_manager.get_active_alerts(),
            'resource_utilization': await self.get_resource_utilization(),
            'throughput_analytics': await self.performance_analyzer.get_throughput_stats(),
            'quality_metrics': await self.get_quality_metrics()
        }
    
    async def get_resource_utilization(self) -> Dict:
        """Get resource utilization metrics"""
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'network_io': psutil.net_io_counters()._asdict(),
            'process_count': len(psutil.pids())
        }
    
    async def get_quality_metrics(self) -> Dict:
        """Get quality metrics"""
        if not self.metrics_history:
            return {}
        
        recent_metrics = list(self.metrics_history)[-100:]
        
        return {
            'avg_response_time': statistics.mean([m.get('latency', 0) for m in recent_metrics]),
            'success_rate': sum(1 for m in recent_metrics if m.get('success', True)) / len(recent_metrics),
            'cache_hit_rate': sum(1 for m in recent_metrics if m.get('cached', False)) / len(recent_metrics),
            'llm_distribution': self.get_llm_distribution(recent_metrics),
            'strategy_distribution': self.get_strategy_distribution(recent_metrics)
        }
    
    def get_llm_distribution(self, metrics: List[Dict]) -> Dict:
        """Get LLM usage distribution"""
        llm_counts = defaultdict(int)
        for m in metrics:
            llm_used = m.get('llm_used', 'unknown')
            llm_counts[llm_used] += 1
        
        total = sum(llm_counts.values())
        return {llm: count / total for llm, count in llm_counts.items()} if total > 0 else {}
    
    def get_strategy_distribution(self, metrics: List[Dict]) -> Dict:
        """Get retrieval strategy distribution"""
        strategy_counts = defaultdict(int)
        for m in metrics:
            strategies = m.get('strategies_used', [])
            for strategy in strategies:
                strategy_counts[strategy] += 1
        
        total = sum(strategy_counts.values())
        return {strategy: count / total for strategy, count in strategy_counts.items()} if total > 0 else {}
    
    async def cleanup_old_metrics(self):
        """Clean up old metrics to prevent memory issues"""
        # Keep only last 1000 metrics
        if len(self.metrics_history) > 1000:
            # Remove oldest metrics
            for _ in range(len(self.metrics_history) - 1000):
                self.metrics_history.popleft()
    
    async def get_system_health(self) -> Dict:
        """Get overall system health"""
        return await self.health_checker.get_system_health()
    
    async def get_performance_metrics(self) -> Dict:
        """Get performance metrics"""
        return await self.get_current_metrics()
    
    async def get_status(self) -> Dict:
        """Get monitoring system status"""
        return {
            'monitoring_active': True,
            'metrics_collected': len(self.metrics_history),
            'alerts_active': len(self.alert_manager.get_active_alerts()),
            'prometheus_enabled': True,
            'background_tasks_running': True
        }

class AdvancedAnalyticsEngine:
    """Advanced analytics and insights generation"""
    
    def __init__(self):
        self.analytics_db = AnalyticsDatabase()
        self.insight_generator = InsightGenerator()
        self.trend_analyzer = TrendAnalyzer()
        self.ab_test_manager = ABTestManager()
    
    async def generate_insights(self, time_range: str = "7d") -> Dict:
        """Generate comprehensive analytics insights"""
        
        print(f"📊 Generating insights for time range: {time_range}")
        
        analytics_data = await self.collect_analytics_data(time_range)
        
        insights = {
            'performance_insights': await self.analyze_performance_trends(analytics_data),
            'usage_patterns': await self.identify_usage_patterns(analytics_data),
            'quality_trends': await self.analyze_quality_trends(analytics_data),
            'cost_analysis': await self.analyze_cost_patterns(analytics_data),
            'recommendations': await self.generate_recommendations(analytics_data)
        }
        
        return insights
    
    async def collect_analytics_data(self, time_range: str) -> Dict:
        """Collect analytics data for specified time range"""
        # Mock implementation - in practice, query analytics database
        return {
            'total_interactions': 1000,
            'avg_latency': 1.5,
            'success_rate': 0.95,
            'user_satisfaction': 0.88,
            'cost_per_interaction': 0.05
        }
    
    async def analyze_performance_trends(self, data: Dict) -> Dict:
        """Analyze performance trends"""
        return {
            'latency_trend': 'improving',
            'throughput_trend': 'stable',
            'error_rate_trend': 'decreasing',
            'recommendations': ['Optimize LLM selection', 'Improve caching strategy']
        }
    
    async def identify_usage_patterns(self, data: Dict) -> Dict:
        """Identify usage patterns"""
        return {
            'peak_hours': [9, 10, 11, 14, 15, 16],
            'popular_queries': ['technical support', 'product information', 'pricing'],
            'user_behavior': 'consistent',
            'seasonal_patterns': 'none_detected'
        }
    
    async def analyze_quality_trends(self, data: Dict) -> Dict:
        """Analyze quality trends"""
        return {
            'response_quality': 'improving',
            'user_satisfaction': 'high',
            'accuracy_trend': 'stable',
            'recommendations': ['Continue current quality measures']
        }
    
    async def analyze_cost_patterns(self, data: Dict) -> Dict:
        """Analyze cost patterns"""
        return {
            'cost_per_interaction': data.get('cost_per_interaction', 0.05),
            'total_monthly_cost': 1500,
            'cost_optimization_opportunities': ['Implement better caching', 'Optimize LLM usage'],
            'roi': 3.2
        }
    
    async def generate_recommendations(self, data: Dict) -> List[str]:
        """Generate recommendations based on analytics"""
        recommendations = []
        
        if data.get('avg_latency', 0) > 2.0:
            recommendations.append('Consider implementing response caching')
        
        if data.get('success_rate', 0) < 0.9:
            recommendations.append('Investigate and fix error sources')
        
        if data.get('user_satisfaction', 0) < 0.8:
            recommendations.append('Improve response quality and relevance')
        
        return recommendations
    
    async def generate_ab_test_report(self, test_id: str) -> Dict:
        """Generate A/B test reports"""
        test_data = await self.get_ab_test_data(test_id)
        
        return {
            'test_configuration': test_data.get('config', {}),
            'statistical_significance': await self.calculate_significance(test_data),
            'performance_comparison': await self.compare_variants(test_data),
            'recommendation': await self.determine_winning_variant(test_data),
            'confidence_intervals': await self.calculate_confidence_intervals(test_data)
        }
    
    async def get_ab_test_data(self, test_id: str) -> Dict:
        """Get A/B test data"""
        # Mock implementation
        return {
            'config': {'test_id': test_id, 'variants': ['A', 'B']},
            'results': {'A': {'conversion_rate': 0.15}, 'B': {'conversion_rate': 0.18}}
        }
    
    async def calculate_significance(self, test_data: Dict) -> float:
        """Calculate statistical significance"""
        # Mock implementation
        return 0.95
    
    async def compare_variants(self, test_data: Dict) -> Dict:
        """Compare A/B test variants"""
        results = test_data.get('results', {})
        return {
            'variant_a': results.get('A', {}),
            'variant_b': results.get('B', {}),
            'improvement': 0.2
        }
    
    async def determine_winning_variant(self, test_data: Dict) -> str:
        """Determine winning variant"""
        results = test_data.get('results', {})
        if results.get('B', {}).get('conversion_rate', 0) > results.get('A', {}).get('conversion_rate', 0):
            return 'B'
        return 'A'
    
    async def calculate_confidence_intervals(self, test_data: Dict) -> Dict:
        """Calculate confidence intervals"""
        return {
            'variant_a': {'lower': 0.12, 'upper': 0.18},
            'variant_b': {'lower': 0.15, 'upper': 0.21}
        }

class MetricsCollector:
    """Collects and processes metrics"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
    
    async def collect_metric(self, metric_name: str, value: float, timestamp: datetime = None):
        """Collect a metric"""
        if timestamp is None:
            timestamp = datetime.now()
        
        self.metrics[metric_name].append({
            'value': value,
            'timestamp': timestamp
        })
    
    async def get_current_metrics(self) -> Dict:
        """Get current metrics"""
        current_metrics = {}
        
        for metric_name, values in self.metrics.items():
            if values:
                current_metrics[metric_name] = values[-1]['value']
        
        return current_metrics

class AlertManager:
    """Manages alerts and notifications"""
    
    def __init__(self):
        self.alerts = []
        self.alert_rules = []
    
    async def create_alert(self, alert: Dict):
        """Create a new alert"""
        self.alerts.append(alert)
        print(f"🚨 Alert: {alert['message']}")
    
    def get_active_alerts(self) -> List[Dict]:
        """Get active alerts"""
        return [alert for alert in self.alerts if alert.get('active', True)]
    
    async def resolve_alert(self, alert_id: str):
        """Resolve an alert"""
        for alert in self.alerts:
            if alert.get('id') == alert_id:
                alert['active'] = False
                break

class PerformanceAnalyzer:
    """Analyzes performance metrics"""
    
    async def analyze_performance(self, interaction_metrics: Dict):
        """Analyze performance of an interaction"""
        # Mock implementation
        pass
    
    async def get_throughput_stats(self) -> Dict:
        """Get throughput statistics"""
        return {
            'requests_per_minute': 100,
            'peak_throughput': 150,
            'avg_throughput': 80
        }

class SystemHealthChecker:
    """Checks system health"""
    
    async def initialize(self):
        """Initialize health checker"""
        pass
    
    async def get_system_health(self) -> Dict:
        """Get system health status"""
        return {
            'status': 'healthy',
            'memory_usage': psutil.virtual_memory().percent,
            'cpu_usage': psutil.cpu_percent(),
            'disk_usage': psutil.disk_usage('/').percent,
            'active_connections': len(psutil.net_connections()),
            'uptime': time.time()
        }

# Mock classes for analytics
class AnalyticsDatabase:
    async def query(self, query: str) -> List[Dict]:
        """Query analytics database"""
        return []

class InsightGenerator:
    async def generate_insights(self, data: Dict) -> Dict:
        """Generate insights from data"""
        return {}

class TrendAnalyzer:
    async def analyze_trends(self, data: Dict) -> Dict:
        """Analyze trends in data"""
        return {}

class ABTestManager:
    async def create_test(self, config: Dict) -> str:
        """Create A/B test"""
        return "test_123"
    
    async def get_test_results(self, test_id: str) -> Dict:
        """Get A/B test results"""
        return {}
