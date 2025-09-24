"""
Real-time Monitoring Dashboard
Provides web-based dashboard for system monitoring and metrics
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from dataclasses import asdict
import time

logger = logging.getLogger(__name__)

class MonitoringDashboard:
    def __init__(self, performance_monitor, cache_manager, auth_system):
        """
        Initialize monitoring dashboard
        
        Args:
            performance_monitor: Performance monitoring system
            cache_manager: Cache management system
            auth_system: Authentication system
        """
        self.performance_monitor = performance_monitor
        self.cache_manager = cache_manager
        self.auth_system = auth_system
        
        # Configure Streamlit
        st.set_page_config(
            page_title="RAG System Monitor",
            page_icon="📊",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    def render_dashboard(self):
        """Render the main monitoring dashboard"""
        st.title("📊 RAG System Monitoring Dashboard")
        st.markdown("Real-time system performance and health monitoring")
        
        # Sidebar for controls
        self._render_sidebar()
        
        # Main dashboard content
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📈 Performance", "💾 Cache", "🔐 Auth", "🚨 Alerts", "⚙️ System"
        ])
        
        with tab1:
            self._render_performance_tab()
        
        with tab2:
            self._render_cache_tab()
        
        with tab3:
            self._render_auth_tab()
        
        with tab4:
            self._render_alerts_tab()
        
        with tab5:
            self._render_system_tab()
    
    def _render_sidebar(self):
        """Render sidebar controls"""
        st.sidebar.title("Dashboard Controls")
        
        # Refresh interval
        refresh_interval = st.sidebar.selectbox(
            "Refresh Interval",
            [5, 10, 30, 60],
            index=1,
            help="Dashboard refresh interval in seconds"
        )
        
        # Time range
        time_range = st.sidebar.selectbox(
            "Time Range",
            ["Last Hour", "Last 6 Hours", "Last 24 Hours", "Last Week"],
            index=2
        )
        
        # Auto-refresh toggle
        auto_refresh = st.sidebar.checkbox("Auto Refresh", value=True)
        
        if auto_refresh:
            time.sleep(refresh_interval)
            st.rerun()
        
        # Export data
        if st.sidebar.button("📥 Export Data"):
            self._export_data()
        
        # System actions
        st.sidebar.markdown("---")
        st.sidebar.subheader("System Actions")
        
        if st.sidebar.button("🔄 Clear Cache"):
            self.cache_manager.cache.clear()
            st.sidebar.success("Cache cleared!")
        
        if st.sidebar.button("📊 Export Metrics"):
            self._export_metrics()
    
    def _render_performance_tab(self):
        """Render performance monitoring tab"""
        st.header("📈 Performance Metrics")
        
        # Get performance stats
        stats = self.performance_monitor.get_performance_stats()
        
        if stats.get('status') == 'no_data':
            st.warning("No performance data available")
            return
        
        # Key metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Queries",
                f"{stats['query_metrics']['total_queries']:,}",
                delta=None
            )
        
        with col2:
            avg_latency = stats['query_metrics']['avg_latency']
            st.metric(
                "Avg Latency",
                f"{avg_latency:.2f}s",
                delta=f"P95: {stats['query_metrics']['p95_latency']:.2f}s"
            )
        
        with col3:
            cache_hit_rate = stats['rates']['cache_hit_rate']
            st.metric(
                "Cache Hit Rate",
                f"{cache_hit_rate:.1%}",
                delta=f"Throughput: {stats['rates']['throughput']:.1f}/hr"
            )
        
        with col4:
            error_rate = stats['rates']['error_rate']
            st.metric(
                "Error Rate",
                f"{error_rate:.1%}",
                delta="Active Alerts" if stats['active_alerts'] > 0 else None
            )
        
        # Latency distribution chart
        st.subheader("Query Latency Distribution")
        self._render_latency_chart(stats)
        
        # Component performance
        st.subheader("Component Performance")
        self._render_component_metrics(stats)
        
        # System health
        st.subheader("System Health")
        self._render_system_health(stats['system_health'])
    
    def _render_latency_chart(self, stats: Dict[str, Any]):
        """Render latency distribution chart"""
        # Create sample latency data (in production, use actual historical data)
        latencies = [stats['query_metrics']['avg_latency']] * 100
        
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=latencies,
            nbinsx=20,
            name="Latency Distribution",
            marker_color='lightblue'
        ))
        
        fig.update_layout(
            title="Query Latency Distribution",
            xaxis_title="Latency (seconds)",
            yaxis_title="Frequency",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_component_metrics(self, stats: Dict[str, Any]):
        """Render component performance metrics"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Retrieval Performance")
            retrieval_time = stats['component_metrics']['avg_retrieval_time']
            st.metric("Avg Retrieval Time", f"{retrieval_time:.3f}s")
        
        with col2:
            st.subheader("Generation Performance")
            generation_time = stats['component_metrics']['avg_generation_time']
            st.metric("Avg Generation Time", f"{generation_time:.3f}s")
        
        # Confidence scores
        st.subheader("Response Quality")
        confidence = stats['component_metrics']['avg_confidence']
        min_confidence = stats['component_metrics']['min_confidence']
        max_confidence = stats['component_metrics']['max_confidence']
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Avg Confidence", f"{confidence:.2f}")
        with col2:
            st.metric("Min Confidence", f"{min_confidence:.2f}")
        with col3:
            st.metric("Max Confidence", f"{max_confidence:.2f}")
    
    def _render_system_health(self, health: Dict[str, Any]):
        """Render system health status"""
        status = health['status']
        health_score = health['health_score']
        
        # Health score gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=health_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "System Health Score"},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        # Health details
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("CPU Usage", f"{health['cpu_percent']:.1f}%")
        with col2:
            st.metric("Memory Usage", f"{health['memory_percent']:.1f}%")
        with col3:
            st.metric("Disk Usage", f"{health['disk_percent']:.1f}%")
        
        # Issues
        if health['issues']:
            st.warning("⚠️ System Issues Detected:")
            for issue in health['issues']:
                st.write(f"• {issue}")
    
    def _render_cache_tab(self):
        """Render cache monitoring tab"""
        st.header("💾 Cache Performance")
        
        # Get cache stats
        cache_stats = self.cache_manager.get_performance_metrics()
        
        # Cache overview
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Hit Rate",
                f"{cache_stats['hit_rate']:.1%}",
                delta=f"Total: {cache_stats['total_requests']}"
            )
        
        with col2:
            st.metric(
                "Memory Hits",
                f"{cache_stats['memory_hits']}",
                delta=f"Rate: {cache_stats['memory_hit_rate']:.1%}"
            )
        
        with col3:
            st.metric(
                "Redis Hits",
                f"{cache_stats['redis_hits']}",
                delta=f"Rate: {cache_stats['redis_hit_rate']:.1%}"
            )
        
        with col4:
            st.metric(
                "Disk Hits",
                f"{cache_stats['disk_hits']}",
                delta=f"Rate: {cache_stats['disk_hit_rate']:.1%}"
            )
        
        # Cache strategy
        st.subheader("Cache Strategy")
        strategy_config = cache_stats['strategy_config']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**Current Strategy:** {cache_stats['current_strategy'].title()}")
            st.write(f"**TTL:** {strategy_config['ttl']} seconds")
            st.write(f"**Preload:** {strategy_config['preload']}")
        
        with col2:
            # Strategy selector
            new_strategy = st.selectbox(
                "Change Strategy",
                ["aggressive", "moderate", "conservative"],
                index=["aggressive", "moderate", "conservative"].index(cache_stats['current_strategy'])
            )
            
            if st.button("Update Strategy"):
                self.cache_manager.set_strategy(new_strategy)
                st.success(f"Strategy updated to {new_strategy}")
                st.rerun()
        
        # Cache levels
        st.subheader("Cache Levels")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Memory Cache")
            memory_stats = cache_stats['memory_stats']
            st.write(f"**Size:** {memory_stats['size']}/{memory_stats['max_size']}")
            st.write(f"**Total Accesses:** {memory_stats['total_accesses']}")
            st.write(f"**Avg Accesses:** {memory_stats['avg_accesses']:.1f}")
        
        with col2:
            st.subheader("Disk Cache")
            disk_stats = cache_stats['disk_stats']
            st.write(f"**Files:** {disk_stats['size']}")
            st.write(f"**Total Size:** {disk_stats['total_size_bytes'] / 1024 / 1024:.1f} MB")
            st.write(f"**Directory:** {disk_stats['cache_dir']}")
    
    def _render_auth_tab(self):
        """Render authentication monitoring tab"""
        st.header("🔐 Authentication & Rate Limiting")
        
        # User statistics
        st.subheader("User Statistics")
        
        # Get user info (simplified for demo)
        total_users = len(self.auth_system.users)
        active_users = sum(1 for user in self.auth_system.users.values() if user.is_active)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Users", total_users)
        with col2:
            st.metric("Active Users", active_users)
        with col3:
            st.metric("Inactive Users", total_users - active_users)
        
        # Rate limiting overview
        st.subheader("Rate Limiting Overview")
        
        # Create sample rate limit data
        rate_limits = {
            "Free": {"requests_per_minute": 10, "requests_per_hour": 100},
            "Basic": {"requests_per_minute": 30, "requests_per_hour": 500},
            "Premium": {"requests_per_minute": 100, "requests_per_hour": 2000},
            "Enterprise": {"requests_per_minute": 500, "requests_per_hour": 10000}
        }
        
        df = pd.DataFrame(rate_limits).T
        st.dataframe(df, use_container_width=True)
        
        # User management
        st.subheader("User Management")
        
        # Display users
        if st.button("Refresh User List"):
            st.rerun()
        
        user_data = []
        for user in self.auth_system.users.values():
            user_data.append({
                "User ID": user.user_id,
                "Username": user.username,
                "Role": user.role.value,
                "Tier": user.rate_limit_tier.value,
                "Active": user.is_active,
                "Last Active": user.last_active.isoformat() if user.last_active else "Never"
            })
        
        if user_data:
            df_users = pd.DataFrame(user_data)
            st.dataframe(df_users, use_container_width=True)
        else:
            st.info("No users found")
    
    def _render_alerts_tab(self):
        """Render alerts monitoring tab"""
        st.header("🚨 System Alerts")
        
        # Get alerts
        alerts = self.performance_monitor.get_alerts()
        
        if not alerts:
            st.success("✅ No active alerts")
            return
        
        # Alert summary
        alert_counts = {}
        for alert in alerts:
            severity = alert.severity
            alert_counts[severity] = alert_counts.get(severity, 0) + 1
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Alerts", len(alerts))
        with col2:
            st.metric("Critical", alert_counts.get('critical', 0))
        with col3:
            st.metric("Warning", alert_counts.get('warning', 0))
        with col4:
            st.metric("Info", alert_counts.get('info', 0))
        
        # Alert details
        st.subheader("Alert Details")
        
        for alert in alerts[:10]:  # Show last 10 alerts
            severity_color = {
                'critical': 'red',
                'warning': 'orange',
                'info': 'blue'
            }.get(alert.severity, 'gray')
            
            with st.expander(f"{alert.severity.upper()}: {alert.message}"):
                st.write(f"**Type:** {alert.type}")
                st.write(f"**Timestamp:** {alert.timestamp}")
                st.write(f"**Resolved:** {alert.resolved}")
                
                if alert.metadata:
                    st.write("**Metadata:**")
                    st.json(alert.metadata)
                
                if not alert.resolved:
                    if st.button(f"Resolve {alert.id}", key=f"resolve_{alert.id}"):
                        self.performance_monitor.resolve_alert(alert.id)
                        st.success("Alert resolved!")
                        st.rerun()
        
        # Recommendations
        st.subheader("Recommendations")
        recommendations = self.performance_monitor.get_recommendations()
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                st.write(f"{i}. {rec}")
        else:
            st.info("No recommendations at this time")
    
    def _render_system_tab(self):
        """Render system information tab"""
        st.header("⚙️ System Information")
        
        # System metrics
        st.subheader("System Metrics")
        
        # Get system health
        health = self.performance_monitor.get_performance_stats()['system_health']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("CPU Usage", f"{health['cpu_percent']:.1f}%")
        with col2:
            st.metric("Memory Usage", f"{health['memory_percent']:.1f}%")
        with col3:
            st.metric("Disk Usage", f"{health['disk_percent']:.1f}%")
        
        # Load average
        if health['load_average']:
            st.subheader("Load Average")
            load_avg = health['load_average']
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("1 min", f"{load_avg[0]:.2f}")
            with col2:
                st.metric("5 min", f"{load_avg[1]:.2f}")
            with col3:
                st.metric("15 min", f"{load_avg[2]:.2f}")
        
        # System actions
        st.subheader("System Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Restart Services"):
                st.info("Service restart initiated...")
        
        with col2:
            if st.button("📊 Generate Report"):
                self._generate_report()
        
        with col3:
            if st.button("🧹 Cleanup Data"):
                cleaned = self.performance_monitor.cleanup_old_data()
                st.success(f"Cleaned up {cleaned} old records")
    
    def _export_data(self):
        """Export monitoring data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"monitoring_data_{timestamp}.json"
        
        # Get all data
        data = {
            'timestamp': datetime.now().isoformat(),
            'performance_stats': self.performance_monitor.get_performance_stats(),
            'cache_stats': self.cache_manager.get_performance_metrics(),
            'alerts': [asdict(alert) for alert in self.performance_monitor.get_alerts()]
        }
        
        # Create download link
        json_str = json.dumps(data, indent=2, default=str)
        st.download_button(
            label="📥 Download Data",
            data=json_str,
            file_name=filename,
            mime="application/json"
        )
    
    def _export_metrics(self):
        """Export performance metrics"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"performance_metrics_{timestamp}.json"
        
        self.performance_monitor.export_metrics(filename)
        st.success(f"Metrics exported to {filename}")
    
    def _generate_report(self):
        """Generate system report"""
        st.info("Generating system report...")
        
        # Get comprehensive stats
        perf_stats = self.performance_monitor.get_performance_stats()
        cache_stats = self.cache_manager.get_performance_metrics()
        
        # Create report
        report = f"""
# RAG System Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Performance Summary
- Total Queries: {perf_stats['query_metrics']['total_queries']}
- Average Latency: {perf_stats['query_metrics']['avg_latency']:.2f}s
- Cache Hit Rate: {perf_stats['rates']['cache_hit_rate']:.1%}
- Error Rate: {perf_stats['rates']['error_rate']:.1%}

## System Health
- Status: {perf_stats['system_health']['status']}
- Health Score: {perf_stats['system_health']['health_score']}

## Cache Performance
- Hit Rate: {cache_stats['hit_rate']:.1%}
- Strategy: {cache_stats['current_strategy']}

## Recommendations
"""
        
        recommendations = self.performance_monitor.get_recommendations()
        for i, rec in enumerate(recommendations, 1):
            report += f"{i}. {rec}\n"
        
        st.text_area("System Report", report, height=400)
        
        # Download report
        st.download_button(
            label="📄 Download Report",
            data=report,
            file_name=f"system_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown"
        )

def run_dashboard(performance_monitor, cache_manager, auth_system):
    """Run the monitoring dashboard"""
    dashboard = MonitoringDashboard(performance_monitor, cache_manager, auth_system)
    dashboard.render_dashboard()

if __name__ == "__main__":
    # This would be run with: streamlit run monitoring_dashboard.py
    st.write("Monitoring Dashboard - Run with proper initialization")
