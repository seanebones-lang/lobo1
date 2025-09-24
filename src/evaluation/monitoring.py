"""
Monitoring system for RAG operations using MLflow and custom logging.
"""

import time
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import pandas as pd
import numpy as np

try:
    import mlflow
    import mlflow.sklearn
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    logger.warning("MLflow not available. Install with: pip install mlflow")

logger = logging.getLogger(__name__)


class RAGMonitor:
    """Monitoring system for RAG operations."""
    
    def __init__(
        self,
        experiment_name: str = "rag_system",
        tracking_uri: Optional[str] = None,
        use_mlflow: bool = True
    ):
        """
        Initialize RAG monitor.
        
        Args:
            experiment_name: Name of the MLflow experiment
            tracking_uri: MLflow tracking URI
            use_mlflow: Whether to use MLflow for tracking
        """
        self.experiment_name = experiment_name
        self.use_mlflow = use_mlflow and MLFLOW_AVAILABLE
        self.session_id = f"session_{int(time.time())}"
        
        # Initialize MLflow if available
        if self.use_mlflow:
            try:
                if tracking_uri:
                    mlflow.set_tracking_uri(tracking_uri)
                
                # Create or get experiment
                try:
                    experiment = mlflow.get_experiment_by_name(experiment_name)
                    if experiment is None:
                        experiment_id = mlflow.create_experiment(experiment_name)
                    else:
                        experiment_id = experiment.experiment_id
                except Exception:
                    experiment_id = mlflow.create_experiment(experiment_name)
                
                mlflow.set_experiment(experiment_name)
                logger.info(f"MLflow experiment '{experiment_name}' initialized")
                
            except Exception as e:
                logger.error(f"Error initializing MLflow: {e}")
                self.use_mlflow = False
        
        # Local metrics storage
        self.metrics_history = []
        self.query_history = []
        
        logger.info(f"RAG Monitor initialized with MLflow: {self.use_mlflow}")
    
    def log_query(
        self,
        query: str,
        response: str,
        sources: List[Dict[str, Any]],
        confidence: float,
        processing_time: float,
        model_used: Optional[str] = None,
        tokens_used: int = 0,
        user_feedback: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log a query and its response.
        
        Args:
            query: User query
            response: Generated response
            sources: Source documents used
            confidence: Confidence score
            processing_time: Time taken for processing
            model_used: Model used for generation
            tokens_used: Number of tokens used
            user_feedback: User feedback score (1-5)
            metadata: Additional metadata
        """
        timestamp = datetime.utcnow().isoformat()
        
        # Create log entry
        log_entry = {
            "timestamp": timestamp,
            "session_id": self.session_id,
            "query": query,
            "response": response,
            "sources_count": len(sources),
            "confidence": confidence,
            "processing_time": processing_time,
            "model_used": model_used,
            "tokens_used": tokens_used,
            "user_feedback": user_feedback,
            "metadata": metadata or {}
        }
        
        # Store locally
        self.query_history.append(log_entry)
        
        # Log to MLflow if available
        if self.use_mlflow:
            try:
                with mlflow.start_run(run_name=f"query_{int(time.time())}"):
                    # Log parameters
                    mlflow.log_param("query_length", len(query))
                    mlflow.log_param("response_length", len(response))
                    mlflow.log_param("sources_count", len(sources))
                    mlflow.log_param("model_used", model_used or "unknown")
                    
                    # Log metrics
                    mlflow.log_metric("confidence", confidence)
                    mlflow.log_metric("processing_time", processing_time)
                    mlflow.log_metric("tokens_used", tokens_used)
                    mlflow.log_metric("response_length", len(response))
                    
                    if user_feedback is not None:
                        mlflow.log_metric("user_feedback", user_feedback)
                    
                    # Log artifacts
                    if metadata:
                        mlflow.log_dict(metadata, "metadata.json")
                    
            except Exception as e:
                logger.error(f"Error logging to MLflow: {e}")
        
        logger.info(f"Logged query: {query[:50]}... (confidence: {confidence:.3f})")
    
    def log_metrics(
        self,
        metrics: Dict[str, Any],
        run_name: Optional[str] = None
    ):
        """
        Log custom metrics.
        
        Args:
            metrics: Dictionary of metrics to log
            run_name: Name for the MLflow run
        """
        timestamp = datetime.utcnow().isoformat()
        
        # Store locally
        metrics_entry = {
            "timestamp": timestamp,
            "session_id": self.session_id,
            "metrics": metrics
        }
        self.metrics_history.append(metrics_entry)
        
        # Log to MLflow if available
        if self.use_mlflow:
            try:
                with mlflow.start_run(run_name=run_name or f"metrics_{int(time.time())}"):
                    for metric_name, value in metrics.items():
                        if isinstance(value, (int, float)):
                            mlflow.log_metric(metric_name, value)
                        else:
                            mlflow.log_param(metric_name, str(value))
                    
            except Exception as e:
                logger.error(f"Error logging metrics to MLflow: {e}")
    
    def log_system_health(
        self,
        health_data: Dict[str, Any]
    ):
        """Log system health metrics."""
        self.log_metrics({
            "system_uptime": health_data.get("uptime", 0),
            "total_queries": len(self.query_history),
            "average_confidence": np.mean([q["confidence"] for q in self.query_history]) if self.query_history else 0,
            "average_processing_time": np.mean([q["processing_time"] for q in self.query_history]) if self.query_history else 0
        }, run_name="system_health")
    
    def get_query_analytics(self) -> Dict[str, Any]:
        """Get analytics for query history."""
        if not self.query_history:
            return {"message": "No queries logged yet"}
        
        df = pd.DataFrame(self.query_history)
        
        analytics = {
            "total_queries": len(df),
            "average_confidence": df["confidence"].mean(),
            "average_processing_time": df["processing_time"].mean(),
            "average_tokens_used": df["tokens_used"].mean(),
            "average_sources_count": df["sources_count"].mean(),
            "confidence_distribution": {
                "min": df["confidence"].min(),
                "max": df["confidence"].max(),
                "std": df["confidence"].std()
            },
            "processing_time_distribution": {
                "min": df["processing_time"].min(),
                "max": df["processing_time"].max(),
                "std": df["processing_time"].std()
            },
            "model_usage": df["model_used"].value_counts().to_dict(),
            "user_feedback": {
                "average": df["user_feedback"].mean() if "user_feedback" in df.columns else None,
                "count": df["user_feedback"].count() if "user_feedback" in df.columns else 0
            }
        }
        
        return analytics
    
    def get_performance_trends(self, window_size: int = 10) -> Dict[str, Any]:
        """Get performance trends over time."""
        if len(self.query_history) < window_size:
            return {"message": f"Need at least {window_size} queries for trend analysis"}
        
        df = pd.DataFrame(self.query_history)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp")
        
        # Calculate rolling averages
        df["confidence_rolling"] = df["confidence"].rolling(window=window_size).mean()
        df["processing_time_rolling"] = df["processing_time"].rolling(window=window_size).mean()
        
        trends = {
            "confidence_trend": df["confidence_rolling"].dropna().tolist(),
            "processing_time_trend": df["processing_time_rolling"].dropna().tolist(),
            "timestamps": df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S").tolist(),
            "window_size": window_size
        }
        
        return trends
    
    def export_data(self, output_path: str):
        """Export monitoring data to file."""
        export_data = {
            "session_id": self.session_id,
            "experiment_name": self.experiment_name,
            "query_history": self.query_history,
            "metrics_history": self.metrics_history,
            "analytics": self.get_query_analytics(),
            "export_timestamp": datetime.utcnow().isoformat()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        logger.info(f"Monitoring data exported to {output_path}")
    
    def get_anomaly_detection(self) -> Dict[str, Any]:
        """Detect anomalies in query performance."""
        if len(self.query_history) < 5:
            return {"message": "Need at least 5 queries for anomaly detection"}
        
        df = pd.DataFrame(self.query_history)
        
        anomalies = {
            "low_confidence_queries": [],
            "slow_queries": [],
            "high_token_usage": []
        }
        
        # Low confidence queries (below 25th percentile)
        confidence_threshold = df["confidence"].quantile(0.25)
        low_confidence = df[df["confidence"] < confidence_threshold]
        anomalies["low_confidence_queries"] = low_confidence[["timestamp", "query", "confidence"]].to_dict("records")
        
        # Slow queries (above 75th percentile)
        time_threshold = df["processing_time"].quantile(0.75)
        slow_queries = df[df["processing_time"] > time_threshold]
        anomalies["slow_queries"] = slow_queries[["timestamp", "query", "processing_time"]].to_dict("records")
        
        # High token usage (above 75th percentile)
        if "tokens_used" in df.columns:
            token_threshold = df["tokens_used"].quantile(0.75)
            high_tokens = df[df["tokens_used"] > token_threshold]
            anomalies["high_token_usage"] = high_tokens[["timestamp", "query", "tokens_used"]].to_dict("records")
        
        return anomalies
    
    def generate_report(self) -> str:
        """Generate a comprehensive monitoring report."""
        report = []
        
        # Header
        report.append("# RAG System Monitoring Report")
        report.append(f"Generated at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Session ID: {self.session_id}")
        report.append("")
        
        # Analytics
        analytics = self.get_query_analytics()
        report.append("## System Analytics")
        report.append(f"Total Queries: {analytics.get('total_queries', 0)}")
        report.append(f"Average Confidence: {analytics.get('average_confidence', 0):.3f}")
        report.append(f"Average Processing Time: {analytics.get('average_processing_time', 0):.3f}s")
        report.append(f"Average Tokens Used: {analytics.get('average_tokens_used', 0):.1f}")
        report.append("")
        
        # Performance trends
        trends = self.get_performance_trends()
        if "message" not in trends:
            report.append("## Performance Trends")
            report.append("Confidence and processing time trends are available in the data.")
            report.append("")
        
        # Anomaly detection
        anomalies = self.get_anomaly_detection()
        if "message" not in anomalies:
            report.append("## Anomaly Detection")
            
            low_conf_count = len(anomalies.get("low_confidence_queries", []))
            slow_count = len(anomalies.get("slow_queries", []))
            high_token_count = len(anomalies.get("high_token_usage", []))
            
            report.append(f"Low Confidence Queries: {low_conf_count}")
            report.append(f"Slow Queries: {slow_count}")
            report.append(f"High Token Usage Queries: {high_token_count}")
            report.append("")
        
        # Model usage
        model_usage = analytics.get("model_usage", {})
        if model_usage:
            report.append("## Model Usage")
            for model, count in model_usage.items():
                report.append(f"- {model}: {count} queries")
            report.append("")
        
        return "\n".join(report)
    
    def clear_history(self):
        """Clear monitoring history."""
        self.query_history = []
        self.metrics_history = []
        logger.info("Monitoring history cleared")


class PerformanceTracker:
    """Track performance metrics for RAG components."""
    
    def __init__(self):
        self.metrics = {}
        self.start_times = {}
    
    def start_timer(self, operation: str):
        """Start timing an operation."""
        self.start_times[operation] = time.time()
    
    def end_timer(self, operation: str) -> float:
        """End timing an operation and return duration."""
        if operation not in self.start_times:
            return 0.0
        
        duration = time.time() - self.start_times[operation]
        del self.start_times[operation]
        
        # Store metric
        if operation not in self.metrics:
            self.metrics[operation] = []
        self.metrics[operation].append(duration)
        
        return duration
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        result = {}
        for operation, times in self.metrics.items():
            result[operation] = {
                "count": len(times),
                "total_time": sum(times),
                "average_time": np.mean(times),
                "min_time": np.min(times),
                "max_time": np.max(times),
                "std_time": np.std(times)
            }
        return result
    
    def reset(self):
        """Reset all metrics."""
        self.metrics = {}
        self.start_times = {}

