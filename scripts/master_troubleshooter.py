#!/usr/bin/env python3
"""
Master Troubleshooter for RAG System
Orchestrates all monitoring, testing, and repair tools
"""

import asyncio
import logging
import time
import json
import signal
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/master_troubleshooter.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class MasterTroubleshooter:
    """Master troubleshooter that orchestrates all system maintenance"""
    
    def __init__(self):
        self.start_time = time.time()
        self.monitoring_active = False
        self.health_monitor = None
        self.api_tester = None
        self.repair_tool = None
        
        # Configuration
        self.config = {
            'monitoring_interval': 60,  # seconds
            'health_check_interval': 30,  # seconds
            'api_test_interval': 300,  # 5 minutes
            'repair_threshold': 5,  # number of consecutive failures before repair
            'auto_repair': True,
            'backup_before_repair': True
        }
        
        # Statistics
        self.stats = {
            'health_checks_run': 0,
            'api_tests_run': 0,
            'repairs_performed': 0,
            'issues_detected': 0,
            'issues_resolved': 0,
            'uptime': 0
        }
        
        # Issue tracking
        self.issue_history = []
        self.consecutive_failures = 0
        self.last_successful_check = time.time()
    
    async def start_troubleshooting(self):
        """Start the master troubleshooting system"""
        logger.info("🚀 Starting Master RAG System Troubleshooter...")
        logger.info("🎯 I AM THE ULTIMATE RAG TROUBLESHOOTER")
        logger.info("🔧 CONTINUOUSLY SCANNING AND REPAIRING ALL ISSUES")
        
        self.monitoring_active = True
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        try:
            # Initialize components
            await self.initialize_components()
            
            # Run initial health check
            await self.run_initial_health_check()
            
            # Start continuous monitoring loop
            await self.monitoring_loop()
            
        except Exception as e:
            logger.error(f"Master troubleshooter error: {e}")
        finally:
            await self.shutdown()
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.monitoring_active = False
    
    async def initialize_components(self):
        """Initialize all troubleshooting components"""
        logger.info("🔧 Initializing troubleshooting components...")
        
        try:
            # Import and initialize health monitor
            from system_health_monitor import SystemHealthMonitor
            self.health_monitor = SystemHealthMonitor()
            
            # Import and initialize API tester
            from test_api_endpoints import APITester
            self.api_tester = APITester()
            
            # Import and initialize repair tool
            from system_repair_tool import SystemRepairTool
            self.repair_tool = SystemRepairTool()
            
            logger.info("✅ All components initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing components: {e}")
            raise
    
    async def run_initial_health_check(self):
        """Run initial comprehensive health check"""
        logger.info("🏥 Running initial health check...")
        
        try:
            # Run health checks
            await self.health_monitor.run_health_checks()
            
            # Run API tests
            async with self.api_tester:
                await self.api_tester.test_all_endpoints()
            
            # Check for issues
            if len(self.health_monitor.issues_found) > 0:
                logger.warning(f"⚠️  Found {len(self.health_monitor.issues_found)} issues during initial check")
                self.consecutive_failures += 1
                
                if self.config['auto_repair']:
                    await self.perform_repair()
            else:
                logger.info("✅ Initial health check passed")
                self.consecutive_failures = 0
                self.last_successful_check = time.time()
            
        except Exception as e:
            logger.error(f"Initial health check failed: {e}")
            self.consecutive_failures += 1
    
    async def monitoring_loop(self):
        """Main monitoring loop"""
        logger.info("🔄 Starting continuous monitoring loop...")
        
        health_check_counter = 0
        api_test_counter = 0
        
        while self.monitoring_active:
            try:
                current_time = time.time()
                
                # Update statistics
                self.stats['uptime'] = current_time - self.start_time
                
                # Health checks
                if health_check_counter >= self.config['health_check_interval']:
                    await self.run_health_check()
                    health_check_counter = 0
                
                # API tests
                if api_test_counter >= self.config['api_test_interval']:
                    await self.run_api_test()
                    api_test_counter = 0
                
                # Check if repair is needed
                if self.consecutive_failures >= self.config['repair_threshold']:
                    logger.warning(f"⚠️  {self.consecutive_failures} consecutive failures detected")
                    if self.config['auto_repair']:
                        await self.perform_repair()
                
                # Wait before next iteration
                await asyncio.sleep(1)
                health_check_counter += 1
                api_test_counter += 1
                
                # Log status every minute
                if int(current_time) % 60 == 0:
                    await self.log_status()
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(10)  # Wait longer on error
    
    async def run_health_check(self):
        """Run health check"""
        logger.info("🏥 Running health check...")
        
        try:
            await self.health_monitor.run_health_checks()
            self.stats['health_checks_run'] += 1
            
            if len(self.health_monitor.issues_found) > 0:
                self.consecutive_failures += 1
                self.stats['issues_detected'] += len(self.health_monitor.issues_found)
                
                # Log recent issues
                recent_issues = self.health_monitor.issues_found[-5:]
                for issue in recent_issues:
                    logger.warning(f"🚨 Issue detected: {issue['type']}")
                
            else:
                self.consecutive_failures = 0
                self.last_successful_check = time.time()
                logger.info("✅ Health check passed")
                
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            self.consecutive_failures += 1
    
    async def run_api_test(self):
        """Run API test"""
        logger.info("🧪 Running API tests...")
        
        try:
            async with self.api_tester:
                await self.api_tester.test_all_endpoints()
                await self.api_tester.test_nextjs_endpoints()
            
            self.stats['api_tests_run'] += 1
            
            # Check test results
            failed_tests = [r for r in self.api_tester.test_results if r['status'] == 'failed']
            if len(failed_tests) > 0:
                logger.warning(f"⚠️  {len(failed_tests)} API tests failed")
                self.consecutive_failures += 1
            else:
                logger.info("✅ API tests passed")
                
        except Exception as e:
            logger.error(f"API test failed: {e}")
            self.consecutive_failures += 1
    
    async def perform_repair(self):
        """Perform system repair"""
        logger.info("🔧 Performing system repair...")
        
        try:
            if self.config['backup_before_repair']:
                logger.info("📦 Creating backup before repair...")
                self.repair_tool.create_backup()
            
            # Run repair strategies
            repair_successful = False
            for issue_type, repair_func in self.repair_tool.repair_strategies.items():
                try:
                    result = repair_func()
                    if result:
                        repair_successful = True
                        logger.info(f"✅ Repair successful: {issue_type}")
                    else:
                        logger.warning(f"⚠️  Repair failed: {issue_type}")
                except Exception as e:
                    logger.error(f"Error in repair {issue_type}: {e}")
            
            if repair_successful:
                self.stats['repairs_performed'] += 1
                self.stats['issues_resolved'] += len(self.health_monitor.issues_found)
                self.consecutive_failures = 0
                logger.info("🎉 System repair completed successfully")
            else:
                logger.error("❌ System repair failed")
                
        except Exception as e:
            logger.error(f"Repair process failed: {e}")
    
    async def log_status(self):
        """Log current system status"""
        uptime_hours = self.stats['uptime'] / 3600
        success_rate = self.calculate_success_rate()
        
        logger.info(f"📊 System Status - Uptime: {uptime_hours:.1f}h, "
                   f"Health Checks: {self.stats['health_checks_run']}, "
                   f"API Tests: {self.stats['api_tests_run']}, "
                   f"Repairs: {self.stats['repairs_performed']}, "
                   f"Success Rate: {success_rate:.1f}%")
        
        if self.consecutive_failures > 0:
            logger.warning(f"⚠️  {self.consecutive_failures} consecutive failures")
        else:
            logger.info("✅ System healthy")
    
    def calculate_success_rate(self) -> float:
        """Calculate system success rate"""
        total_checks = self.stats['health_checks_run'] + self.stats['api_tests_run']
        if total_checks == 0:
            return 100.0
        
        # Assume success if no consecutive failures
        if self.consecutive_failures == 0:
            return 100.0
        
        # Calculate based on failure rate
        failure_rate = min(self.consecutive_failures / total_checks, 1.0)
        return (1.0 - failure_rate) * 100.0
    
    async def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive troubleshooting report"""
        logger.info("📊 Generating comprehensive report...")
        
        uptime_hours = self.stats['uptime'] / 3600
        success_rate = self.calculate_success_rate()
        
        # Get health monitor data
        health_report = await self.health_monitor.generate_health_report()
        
        # Get API test data
        api_report = await self.api_tester.generate_test_report()
        
        # Get repair data
        repair_report = self.repair_tool.generate_repair_report()
        
        comprehensive_report = {
            'timestamp': datetime.now().isoformat(),
            'troubleshooting_summary': {
                'total_uptime_hours': uptime_hours,
                'success_rate': success_rate,
                'total_health_checks': self.stats['health_checks_run'],
                'total_api_tests': self.stats['api_tests_run'],
                'total_repairs': self.stats['repairs_performed'],
                'issues_detected': self.stats['issues_detected'],
                'issues_resolved': self.stats['issues_resolved'],
                'consecutive_failures': self.consecutive_failures,
                'last_successful_check': datetime.fromtimestamp(self.last_successful_check).isoformat()
            },
            'health_monitor_report': health_report,
            'api_test_report': api_report,
            'repair_report': repair_report,
            'recommendations': self.generate_recommendations(),
            'system_status': 'healthy' if self.consecutive_failures == 0 else 'degraded'
        }
        
        # Save comprehensive report
        with open('logs/comprehensive_troubleshooting_report.json', 'w') as f:
            json.dump(comprehensive_report, f, indent=2)
        
        return comprehensive_report
    
    def generate_recommendations(self) -> List[str]:
        """Generate recommendations based on troubleshooting results"""
        recommendations = []
        
        if self.consecutive_failures > 0:
            recommendations.append("System has consecutive failures - investigate root cause")
        
        if self.stats['repairs_performed'] > 10:
            recommendations.append("High number of repairs performed - consider system overhaul")
        
        if self.calculate_success_rate() < 80:
            recommendations.append("Low success rate - review system configuration")
        
        if self.stats['uptime'] > 86400:  # More than 24 hours
            recommendations.append("System has been running for over 24 hours - consider restart")
        
        recommendations.append("Continue monitoring for system stability")
        recommendations.append("Review logs for patterns in failures")
        
        return recommendations
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("🛑 Shutting down master troubleshooter...")
        
        self.monitoring_active = False
        
        # Generate final report
        final_report = await self.generate_comprehensive_report()
        
        logger.info("📊 Final Report Generated:")
        logger.info(f"   Total Uptime: {final_report['troubleshooting_summary']['total_uptime_hours']:.1f} hours")
        logger.info(f"   Success Rate: {final_report['troubleshooting_summary']['success_rate']:.1f}%")
        logger.info(f"   Health Checks: {final_report['troubleshooting_summary']['total_health_checks']}")
        logger.info(f"   API Tests: {final_report['troubleshooting_summary']['total_api_tests']}")
        logger.info(f"   Repairs: {final_report['troubleshooting_summary']['total_repairs']}")
        logger.info(f"   System Status: {final_report['system_status']}")
        
        logger.info("✅ Master troubleshooter shutdown complete")

async def main():
    """Main function"""
    logger.info("🚀 Starting Master RAG System Troubleshooter...")
    
    troubleshooter = MasterTroubleshooter()
    
    try:
        await troubleshooter.start_troubleshooting()
    except KeyboardInterrupt:
        logger.info("Troubleshooter interrupted by user")
    except Exception as e:
        logger.error(f"Troubleshooter failed: {e}")
    finally:
        logger.info("Master troubleshooter stopped")

if __name__ == "__main__":
    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)
    
    asyncio.run(main())
