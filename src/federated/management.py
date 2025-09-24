"""
Federation Management and Health Monitoring
Manage federation configuration, node membership, and health monitoring.
"""

from typing import Dict, List, Optional, Any
import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from dataclasses import dataclass
import time
from collections import defaultdict, deque
import statistics

@dataclass
class NodeHealthStatus:
    node_id: str
    is_healthy: bool
    latency: float
    last_check: datetime
    consecutive_failures: int
    uptime_percentage: float

class FederationManager:
    """Manage federation configuration and node membership"""
    
    def __init__(self, config_path: str = "federation_config.json"):
        self.config_path = config_path
        self.config = self.load_config()
        self.health_checker = NodeHealthChecker()
        self.load_balancer = FederationLoadBalancer()
        self.auto_discovery = AutoDiscoveryService()
    
    def load_config(self) -> Dict:
        """Load federation configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                'nodes': {},
                'policies': {
                    'privacy': 'strict',
                    'load_balancing': 'round_robin',
                    'failure_handling': 'fallback',
                    'health_check_interval': 30,
                    'max_consecutive_failures': 3
                },
                'domains': {},
                'discovery': {
                    'enabled': True,
                    'service_endpoint': 'http://discovery-service:8080',
                    'auto_register': True
                }
            }
    
    def save_config(self):
        """Save federation configuration"""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    async def auto_discover_nodes(self, discovery_service: str = None) -> List[Dict]:
        """Automatically discover available federated nodes"""
        
        discovery_endpoint = discovery_service or self.config.get('discovery', {}).get('service_endpoint')
        if not discovery_endpoint:
            print("No discovery service configured")
            return []
        
        try:
            services = await self.auto_discovery.query_discovery_service(discovery_endpoint)
            discovered_nodes = []
            
            for service in services:
                node_config = {
                    'node_id': service['id'],
                    'endpoint': service['endpoint'],
                    'data_domain': service.get('domain', 'general'),
                    'capabilities': service.get('capabilities', ['basic_search']),
                    'privacy_level': service.get('privacy_level', 'public'),
                    'latency': service.get('avg_latency', 1.0)
                }
                
                # Verify node is reachable and functional
                if await self.health_checker.check_node_health(node_config):
                    discovered_nodes.append(node_config)
                    print(f"✅ Discovered and verified node: {node_config['node_id']}")
                else:
                    print(f"❌ Node {node_config['node_id']} failed health check")
            
            return discovered_nodes
        
        except Exception as e:
            print(f"Node discovery failed: {e}")
            return []
    
    async def optimize_federation_topology(self) -> Dict:
        """Optimize federation topology based on performance data"""
        
        performance_data = await self.health_checker.get_performance_report()
        topology_suggestions = {}
        
        for domain in self.config.get('domains', {}):
            domain_nodes = [
                node for node in self.config['nodes'].values() 
                if node.get('data_domain') == domain
            ]
            
            if len(domain_nodes) > 3:  # If we have many nodes in this domain
                # Suggest creating node groups for load balancing
                topology_suggestions[domain] = {
                    'suggestion': 'create_node_group',
                    'current_nodes': len(domain_nodes),
                    'recommended_groups': max(2, len(domain_nodes) // 3),
                    'reason': 'Too many nodes in single domain, consider grouping'
                }
        
        # Analyze performance bottlenecks
        slow_nodes = [
            node_id for node_id, status in performance_data.items()
            if status.get('avg_latency', 0) > 5.0
        ]
        
        if slow_nodes:
            topology_suggestions['performance'] = {
                'suggestion': 'optimize_slow_nodes',
                'slow_nodes': slow_nodes,
                'reason': 'Nodes with high latency detected'
            }
        
        return topology_suggestions
    
    def add_node(self, node_config: Dict) -> bool:
        """Add a new node to the federation"""
        try:
            node_id = node_config['node_id']
            self.config['nodes'][node_id] = node_config
            self.save_config()
            print(f"✅ Added node {node_id} to federation")
            return True
        except Exception as e:
            print(f"❌ Failed to add node: {e}")
            return False
    
    def remove_node(self, node_id: str) -> bool:
        """Remove a node from the federation"""
        try:
            if node_id in self.config['nodes']:
                del self.config['nodes'][node_id]
                self.save_config()
                print(f"✅ Removed node {node_id} from federation")
                return True
            else:
                print(f"❌ Node {node_id} not found in federation")
                return False
        except Exception as e:
            print(f"❌ Failed to remove node: {e}")
            return False

class NodeHealthChecker:
    """Monitor health and performance of federated nodes"""
    
    def __init__(self):
        self.health_status = {}
        self.performance_history = defaultdict(lambda: deque(maxlen=100))
        self.health_check_interval = 30  # seconds
        self.max_consecutive_failures = 3
    
    async def check_node_health(self, node_config: Dict) -> bool:
        """Check if a node is healthy and responsive"""
        node_id = node_config['node_id']
        endpoint = node_config['endpoint']
        
        try:
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{endpoint}/health", timeout=5) as response:
                    latency = time.time() - start_time
                    
                    is_healthy = response.status == 200
                    self.record_health_status(node_id, is_healthy, latency)
                    
                    if is_healthy:
                        print(f"✅ Node {node_id} is healthy (latency: {latency:.3f}s)")
                    else:
                        print(f"❌ Node {node_id} health check failed (status: {response.status})")
                    
                    return is_healthy
        
        except Exception as e:
            self.record_health_status(node_id, False, 0)
            print(f"❌ Node {node_id} health check error: {e}")
            return False
    
    def record_health_status(self, node_id: str, healthy: bool, latency: float):
        """Record node health status"""
        now = datetime.now()
        
        if node_id not in self.health_status:
            self.health_status[node_id] = NodeHealthStatus(
                node_id=node_id,
                is_healthy=healthy,
                latency=latency,
                last_check=now,
                consecutive_failures=0,
                uptime_percentage=100.0
            )
        else:
            status = self.health_status[node_id]
            status.last_check = now
            status.latency = latency
            
            if healthy:
                status.consecutive_failures = 0
                status.is_healthy = True
            else:
                status.consecutive_failures += 1
                if status.consecutive_failures >= self.max_consecutive_failures:
                    status.is_healthy = False
        
        # Record performance history
        self.performance_history[node_id].append({
            'timestamp': now,
            'healthy': healthy,
            'latency': latency
        })
        
        # Update uptime percentage
        self.update_uptime_percentage(node_id)
    
    def update_uptime_percentage(self, node_id: str):
        """Update uptime percentage for a node"""
        if node_id not in self.performance_history:
            return
        
        history = self.performance_history[node_id]
        if not history:
            return
        
        # Calculate uptime over last 24 hours
        cutoff_time = datetime.now() - timedelta(hours=24)
        recent_checks = [h for h in history if h['timestamp'] > cutoff_time]
        
        if recent_checks:
            healthy_checks = sum(1 for h in recent_checks if h['healthy'])
            uptime = (healthy_checks / len(recent_checks)) * 100
            self.health_status[node_id].uptime_percentage = uptime
    
    def get_health_status(self, node_id: str) -> Optional[NodeHealthStatus]:
        """Get health status for a specific node"""
        return self.health_status.get(node_id)
    
    def get_all_health_status(self) -> Dict[str, NodeHealthStatus]:
        """Get health status for all nodes"""
        return dict(self.health_status)
    
    async def get_performance_report(self) -> Dict:
        """Get comprehensive performance report"""
        report = {}
        
        for node_id, status in self.health_status.items():
            history = list(self.performance_history[node_id])
            
            if history:
                latencies = [h['latency'] for h in history if h['healthy']]
                avg_latency = statistics.mean(latencies) if latencies else 0
                max_latency = max(latencies) if latencies else 0
                min_latency = min(latencies) if latencies else 0
            else:
                avg_latency = max_latency = min_latency = 0
            
            report[node_id] = {
                'is_healthy': status.is_healthy,
                'uptime_percentage': status.uptime_percentage,
                'avg_latency': avg_latency,
                'max_latency': max_latency,
                'min_latency': min_latency,
                'consecutive_failures': status.consecutive_failures,
                'last_check': status.last_check.isoformat(),
                'total_checks': len(history)
            }
        
        return report
    
    def get_metrics(self) -> Dict:
        """Get current performance metrics"""
        total_nodes = len(self.health_status)
        healthy_nodes = sum(1 for status in self.health_status.values() if status.is_healthy)
        
        return {
            'total_nodes': total_nodes,
            'healthy_nodes': healthy_nodes,
            'unhealthy_nodes': total_nodes - healthy_nodes,
            'health_percentage': (healthy_nodes / total_nodes * 100) if total_nodes > 0 else 0
        }

class FederationLoadBalancer:
    """Load balancer for federated nodes"""
    
    def __init__(self):
        self.load_balancing_strategies = {
            'round_robin': self.round_robin_selection,
            'least_connections': self.least_connections_selection,
            'weighted_round_robin': self.weighted_round_robin_selection,
            'latency_based': self.latency_based_selection
        }
        self.connection_counts = defaultdict(int)
        self.last_selected = {}
    
    def select_nodes(self, available_nodes: List[Dict], strategy: str = 'round_robin', count: int = 3) -> List[Dict]:
        """Select nodes using specified load balancing strategy"""
        
        if not available_nodes:
            return []
        
        if strategy not in self.load_balancing_strategies:
            strategy = 'round_robin'
        
        return self.load_balancing_strategies[strategy](available_nodes, count)
    
    def round_robin_selection(self, nodes: List[Dict], count: int) -> List[Dict]:
        """Round-robin node selection"""
        selected = []
        start_index = self.last_selected.get('round_robin', 0)
        
        for i in range(count):
            index = (start_index + i) % len(nodes)
            selected.append(nodes[index])
        
        self.last_selected['round_robin'] = (start_index + count) % len(nodes)
        return selected
    
    def least_connections_selection(self, nodes: List[Dict], count: int) -> List[Dict]:
        """Select nodes with least active connections"""
        sorted_nodes = sorted(nodes, key=lambda n: self.connection_counts[n['node_id']])
        return sorted_nodes[:count]
    
    def weighted_round_robin_selection(self, nodes: List[Dict], count: int) -> List[Dict]:
        """Weighted round-robin based on node capacity"""
        # Simple implementation - in practice, use actual capacity metrics
        weights = [1.0] * len(nodes)  # Equal weights for now
        total_weight = sum(weights)
        
        selected = []
        current_weight = 0
        
        for i, node in enumerate(nodes):
            current_weight += weights[i]
            if current_weight >= (len(selected) + 1) * (total_weight / count):
                selected.append(node)
                if len(selected) >= count:
                    break
        
        return selected
    
    def latency_based_selection(self, nodes: List[Dict], count: int) -> List[Dict]:
        """Select nodes based on latency"""
        sorted_nodes = sorted(nodes, key=lambda n: n.get('latency', 1.0))
        return sorted_nodes[:count]
    
    def record_connection(self, node_id: str):
        """Record a connection to a node"""
        self.connection_counts[node_id] += 1
    
    def record_disconnection(self, node_id: str):
        """Record a disconnection from a node"""
        if self.connection_counts[node_id] > 0:
            self.connection_counts[node_id] -= 1

class AutoDiscoveryService:
    """Service discovery for federated nodes"""
    
    def __init__(self):
        self.discovery_cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    async def query_discovery_service(self, endpoint: str) -> List[Dict]:
        """Query discovery service for available nodes"""
        
        # Check cache first
        cache_key = f"discovery_{endpoint}"
        if cache_key in self.discovery_cache:
            cached_data, timestamp = self.discovery_cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return cached_data
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{endpoint}/services", timeout=10) as response:
                    if response.status == 200:
                        services = await response.json()
                        # Cache the results
                        self.discovery_cache[cache_key] = (services, time.time())
                        return services
                    else:
                        print(f"Discovery service returned status {response.status}")
                        return []
        
        except Exception as e:
            print(f"Failed to query discovery service: {e}")
            return []
    
    def register_node(self, node_info: Dict, discovery_endpoint: str):
        """Register a node with the discovery service"""
        # This would typically make a POST request to register the node
        # For now, just print the registration
        print(f"Registering node {node_info['node_id']} with discovery service")

class FederationMonitor:
    """Monitor federation-wide metrics and health"""
    
    def __init__(self):
        self.metrics_history = deque(maxlen=1000)
        self.alerts = []
        self.alert_thresholds = {
            'health_percentage': 80,
            'avg_latency': 5.0,
            'error_rate': 0.1
        }
    
    def record_metrics(self, metrics: Dict):
        """Record federation metrics"""
        self.metrics_history.append({
            'timestamp': datetime.now(),
            'metrics': metrics
        })
        
        # Check for alerts
        self.check_alerts(metrics)
    
    def check_alerts(self, metrics: Dict):
        """Check metrics against alert thresholds"""
        for threshold_name, threshold_value in self.alert_thresholds.items():
            if threshold_name in metrics:
                if threshold_name == 'health_percentage' and metrics[threshold_name] < threshold_value:
                    self.alerts.append({
                        'type': 'low_health',
                        'message': f'Federation health below threshold: {metrics[threshold_name]}%',
                        'timestamp': datetime.now(),
                        'severity': 'warning'
                    })
                elif threshold_name == 'avg_latency' and metrics[threshold_name] > threshold_value:
                    self.alerts.append({
                        'type': 'high_latency',
                        'message': f'Average latency above threshold: {metrics[threshold_name]}s',
                        'timestamp': datetime.now(),
                        'severity': 'warning'
                    })
                elif threshold_name == 'error_rate' and metrics[threshold_name] > threshold_value:
                    self.alerts.append({
                        'type': 'high_error_rate',
                        'message': f'Error rate above threshold: {metrics[threshold_name]}',
                        'timestamp': datetime.now(),
                        'severity': 'critical'
                    })
    
    def get_alerts(self, severity: str = None) -> List[Dict]:
        """Get alerts, optionally filtered by severity"""
        if severity:
            return [alert for alert in self.alerts if alert['severity'] == severity]
        return list(self.alerts)
    
    def get_metrics_summary(self) -> Dict:
        """Get summary of federation metrics"""
        if not self.metrics_history:
            return {}
        
        recent_metrics = list(self.metrics_history)[-10:]  # Last 10 entries
        
        return {
            'total_metrics_recorded': len(self.metrics_history),
            'recent_health': [m['metrics'].get('health_percentage', 0) for m in recent_metrics],
            'recent_latency': [m['metrics'].get('avg_latency', 0) for m in recent_metrics],
            'active_alerts': len([a for a in self.alerts if a['severity'] == 'critical']),
            'last_updated': recent_metrics[-1]['timestamp'].isoformat() if recent_metrics else None
        }
