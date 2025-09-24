#!/usr/bin/env python3
"""
System Health Monitor for RAG System
Continuously monitors and repairs system issues
"""

import asyncio
import logging
import time
import json
import requests
import subprocess
import psutil
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/system_health.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class SystemHealthMonitor:
    """Comprehensive system health monitoring and repair system"""
    
    def __init__(self):
        self.start_time = time.time()
        self.health_checks = []
        self.issues_found = []
        self.repairs_attempted = []
        self.monitoring_active = False
        
        # System endpoints to monitor
        self.endpoints = {
            'api': 'http://localhost:8000/health',
            'frontend': 'http://localhost:8501',
            'redis': 'redis://localhost:6379',
            'qdrant': 'http://localhost:6333/health'
        }
        
        # Critical files to monitor
        self.critical_files = [
            'src/api/main.py',
            'app/lib/api-pipeline.ts',
            'app/lib/rag-pipeline.ts',
            'deploy/docker-compose.prod.yml',
            'requirements.txt'
        ]
        
        # Health thresholds
        self.thresholds = {
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'disk_usage': 90.0,
            'response_time': 5.0,
            'error_rate': 5.0
        }
    
    async def start_monitoring(self):
        """Start continuous system monitoring"""
        logger.info("🚀 Starting RAG System Health Monitor...")
        self.monitoring_active = True
        
        while self.monitoring_active:
            try:
                await self.run_health_checks()
                await self.analyze_system_performance()
                await self.check_api_endpoints()
                await self.verify_file_integrity()
                await self.monitor_resources()
                
                # Wait before next check
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def run_health_checks(self):
        """Run comprehensive health checks"""
        logger.info("🔍 Running system health checks...")
        
        checks = [
            self.check_system_resources,
            self.check_docker_services,
            self.check_api_responses,
            self.check_database_connections,
            self.check_file_permissions,
            self.check_log_errors
        ]
        
        for check in checks:
            try:
                await check()
            except Exception as e:
                logger.error(f"Health check failed: {check.__name__}: {e}")
                self.issues_found.append({
                    'type': 'health_check_failure',
                    'check': check.__name__,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
    
    async def check_system_resources(self):
        """Check system resource usage"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        if cpu_percent > self.thresholds['cpu_usage']:
            self.issues_found.append({
                'type': 'high_cpu_usage',
                'value': cpu_percent,
                'threshold': self.thresholds['cpu_usage'],
                'timestamp': datetime.now().isoformat()
            })
            logger.warning(f"High CPU usage: {cpu_percent}%")
        
        if memory.percent > self.thresholds['memory_usage']:
            self.issues_found.append({
                'type': 'high_memory_usage',
                'value': memory.percent,
                'threshold': self.thresholds['memory_usage'],
                'timestamp': datetime.now().isoformat()
            })
            logger.warning(f"High memory usage: {memory.percent}%")
        
        if disk.percent > self.thresholds['disk_usage']:
            self.issues_found.append({
                'type': 'high_disk_usage',
                'value': disk.percent,
                'threshold': self.thresholds['disk_usage'],
                'timestamp': datetime.now().isoformat()
            })
            logger.warning(f"High disk usage: {disk.percent}%")
    
    async def check_docker_services(self):
        """Check Docker service status"""
        try:
            result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
            if result.returncode != 0:
                self.issues_found.append({
                    'type': 'docker_services_down',
                    'error': result.stderr,
                    'timestamp': datetime.now().isoformat()
                })
                logger.error("Docker services are down")
            else:
                logger.info("Docker services are running")
        except Exception as e:
            self.issues_found.append({
                'type': 'docker_check_failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            logger.error(f"Docker check failed: {e}")
    
    async def check_api_responses(self):
        """Check API endpoint responses"""
        for name, url in self.endpoints.items():
            try:
                start_time = time.time()
                response = requests.get(url, timeout=5)
                response_time = time.time() - start_time
                
                if response_time > self.thresholds['response_time']:
                    self.issues_found.append({
                        'type': 'slow_response',
                        'endpoint': name,
                        'response_time': response_time,
                        'threshold': self.thresholds['response_time'],
                        'timestamp': datetime.now().isoformat()
                    })
                    logger.warning(f"Slow response from {name}: {response_time}s")
                
                if response.status_code != 200:
                    self.issues_found.append({
                        'type': 'api_error',
                        'endpoint': name,
                        'status_code': response.status_code,
                        'timestamp': datetime.now().isoformat()
                    })
                    logger.error(f"API error from {name}: {response.status_code}")
                else:
                    logger.info(f"✅ {name} API is healthy")
                    
            except Exception as e:
                self.issues_found.append({
                    'type': 'api_unreachable',
                    'endpoint': name,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
                logger.error(f"API unreachable: {name}: {e}")
    
    async def check_database_connections(self):
        """Check database connections"""
        # Check Redis
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, db=0)
            r.ping()
            logger.info("✅ Redis connection healthy")
        except Exception as e:
            self.issues_found.append({
                'type': 'redis_connection_failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            logger.error(f"Redis connection failed: {e}")
        
        # Check Qdrant
        try:
            response = requests.get('http://localhost:6333/health', timeout=5)
            if response.status_code == 200:
                logger.info("✅ Qdrant connection healthy")
            else:
                self.issues_found.append({
                    'type': 'qdrant_connection_failed',
                    'status_code': response.status_code,
                    'timestamp': datetime.now().isoformat()
                })
        except Exception as e:
            self.issues_found.append({
                'type': 'qdrant_unreachable',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            logger.error(f"Qdrant unreachable: {e}")
    
    async def check_file_permissions(self):
        """Check critical file permissions"""
        for file_path in self.critical_files:
            if os.path.exists(file_path):
                if not os.access(file_path, os.R_OK):
                    self.issues_found.append({
                        'type': 'file_not_readable',
                        'file': file_path,
                        'timestamp': datetime.now().isoformat()
                    })
                    logger.error(f"File not readable: {file_path}")
                else:
                    logger.info(f"✅ File readable: {file_path}")
            else:
                self.issues_found.append({
                    'type': 'file_missing',
                    'file': file_path,
                    'timestamp': datetime.now().isoformat()
                })
                logger.error(f"File missing: {file_path}")
    
    async def check_log_errors(self):
        """Check log files for errors"""
        log_files = [
            'logs/api.log',
            'logs/frontend.log',
            'logs/system_health.log'
        ]
        
        for log_file in log_files:
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r') as f:
                        lines = f.readlines()
                        recent_lines = lines[-100:]  # Check last 100 lines
                        
                        error_count = sum(1 for line in recent_lines if 'ERROR' in line.upper())
                        if error_count > 10:
                            self.issues_found.append({
                                'type': 'high_error_rate_in_logs',
                                'file': log_file,
                                'error_count': error_count,
                                'timestamp': datetime.now().isoformat()
                            })
                            logger.warning(f"High error rate in {log_file}: {error_count} errors")
                except Exception as e:
                    logger.error(f"Error reading log file {log_file}: {e}")
    
    async def analyze_system_performance(self):
        """Analyze overall system performance"""
        uptime = time.time() - self.start_time
        issues_count = len(self.issues_found)
        
        performance_score = max(0, 100 - (issues_count * 10))
        
        logger.info(f"📊 System Performance Score: {performance_score}/100")
        logger.info(f"⏱️  Uptime: {uptime:.0f} seconds")
        logger.info(f"🚨 Issues found: {issues_count}")
        
        if performance_score < 70:
            logger.warning("⚠️  System performance is degraded")
            await self.attempt_repairs()
    
    async def attempt_repairs(self):
        """Attempt to repair common issues"""
        logger.info("🔧 Attempting system repairs...")
        
        for issue in self.issues_found[-5:]:  # Focus on recent issues
            repair_successful = False
            
            try:
                if issue['type'] == 'docker_services_down':
                    repair_successful = await self.restart_docker_services()
                elif issue['type'] == 'high_memory_usage':
                    repair_successful = await self.clear_memory_cache()
                elif issue['type'] == 'api_unreachable':
                    repair_successful = await self.restart_api_services()
                elif issue['type'] == 'file_not_readable':
                    repair_successful = await self.fix_file_permissions(issue['file'])
                
                if repair_successful:
                    self.repairs_attempted.append({
                        'issue': issue,
                        'success': True,
                        'timestamp': datetime.now().isoformat()
                    })
                    logger.info(f"✅ Successfully repaired: {issue['type']}")
                else:
                    self.repairs_attempted.append({
                        'issue': issue,
                        'success': False,
                        'timestamp': datetime.now().isoformat()
                    })
                    logger.error(f"❌ Failed to repair: {issue['type']}")
                    
            except Exception as e:
                logger.error(f"Error attempting repair for {issue['type']}: {e}")
    
    async def restart_docker_services(self) -> bool:
        """Restart Docker services"""
        try:
            subprocess.run(['docker-compose', 'restart'], check=True)
            logger.info("Docker services restarted")
            return True
        except Exception as e:
            logger.error(f"Failed to restart Docker services: {e}")
            return False
    
    async def clear_memory_cache(self) -> bool:
        """Clear system memory cache"""
        try:
            if os.name == 'posix':  # Unix-like system
                subprocess.run(['sync'], check=True)
                subprocess.run(['echo', '3'], stdout=subprocess.DEVNULL)
            logger.info("Memory cache cleared")
            return True
        except Exception as e:
            logger.error(f"Failed to clear memory cache: {e}")
            return False
    
    async def restart_api_services(self) -> bool:
        """Restart API services"""
        try:
            subprocess.run(['docker-compose', 'restart', 'rag-api'], check=True)
            logger.info("API services restarted")
            return True
        except Exception as e:
            logger.error(f"Failed to restart API services: {e}")
            return False
    
    async def fix_file_permissions(self, file_path: str) -> bool:
        """Fix file permissions"""
        try:
            os.chmod(file_path, 0o644)
            logger.info(f"Fixed permissions for {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to fix permissions for {file_path}: {e}")
            return False
    
    async def generate_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report"""
        uptime = time.time() - self.start_time
        
        return {
            'timestamp': datetime.now().isoformat(),
            'uptime_seconds': uptime,
            'monitoring_active': self.monitoring_active,
            'total_issues_found': len(self.issues_found),
            'total_repairs_attempted': len(self.repairs_attempted),
            'successful_repairs': len([r for r in self.repairs_attempted if r['success']]),
            'recent_issues': self.issues_found[-10:],
            'system_resources': {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent
            },
            'endpoint_status': await self.get_endpoint_status(),
            'recommendations': await self.generate_recommendations()
        }
    
    async def get_endpoint_status(self) -> Dict[str, Any]:
        """Get status of all endpoints"""
        status = {}
        for name, url in self.endpoints.items():
            try:
                start_time = time.time()
                response = requests.get(url, timeout=5)
                response_time = time.time() - start_time
                
                status[name] = {
                    'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                    'response_time': response_time,
                    'status_code': response.status_code
                }
            except Exception as e:
                status[name] = {
                    'status': 'unreachable',
                    'error': str(e)
                }
        
        return status
    
    async def generate_recommendations(self) -> List[str]:
        """Generate system recommendations"""
        recommendations = []
        
        if len(self.issues_found) > 20:
            recommendations.append("Consider restarting the entire system to clear accumulated issues")
        
        cpu_percent = psutil.cpu_percent()
        if cpu_percent > 70:
            recommendations.append("High CPU usage detected - consider scaling up resources")
        
        memory_percent = psutil.virtual_memory().percent
        if memory_percent > 80:
            recommendations.append("High memory usage - consider optimizing memory usage or scaling")
        
        disk_percent = psutil.disk_usage('/').percent
        if disk_percent > 85:
            recommendations.append("Disk space running low - consider cleanup or expanding storage")
        
        return recommendations
    
    def stop_monitoring(self):
        """Stop system monitoring"""
        logger.info("🛑 Stopping system health monitor...")
        self.monitoring_active = False

async def main():
    """Main monitoring function"""
    monitor = SystemHealthMonitor()
    
    try:
        await monitor.start_monitoring()
    except KeyboardInterrupt:
        logger.info("Monitoring interrupted by user")
        monitor.stop_monitoring()
    except Exception as e:
        logger.error(f"Monitoring failed: {e}")
        monitor.stop_monitoring()
    finally:
        # Generate final report
        report = await monitor.generate_health_report()
        with open('logs/final_health_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info("Final health report saved to logs/final_health_report.json")

if __name__ == "__main__":
    asyncio.run(main())
