"""Monitoring and Logging Configuration for ConsumeSafe."""

import logging
import logging.handlers
import json
from datetime import datetime
from typing import Optional
import os

# ============= LOGGING CONFIGURATION =============

def setup_logging(
    log_level: str = "INFO",
    log_format: str = "json",
    log_file: Optional[str] = None,
    app_name: str = "consumesafe"
) -> logging.Logger:
    """
    Configure comprehensive logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Format type - 'json' or 'text'
        log_file: Path to log file (if None, only console logging)
        app_name: Application name for identification
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(app_name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    logger.handlers = []
    
    # Create formatters
    if log_format == "json":
        formatter = JsonFormatter(app_name)
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_file:
        try:
            os.makedirs(os.path.dirname(log_file) or '.', exist_ok=True)
            
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=10
            )
            file_handler.setLevel(getattr(logging, log_level.upper()))
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except (PermissionError, OSError):
            # Skip file logging if logs directory cannot be created (e.g., in Kubernetes)
            pass
    
    return logger


class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def __init__(self, app_name: str = "consumesafe"):
        super().__init__()
        self.app_name = app_name
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "app": self.app_name,
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_data["user_id"] = record.user_id
        if hasattr(record, 'request_id'):
            log_data["request_id"] = record.request_id
        if hasattr(record, 'duration_ms'):
            log_data["duration_ms"] = record.duration_ms
        
        return json.dumps(log_data)


# ============= PROMETHEUS METRICS =============

class PrometheusMetrics:
    """Prometheus metrics collection for ConsumeSafe."""
    
    # Request metrics
    REQUEST_COUNT = None
    REQUEST_DURATION = None
    REQUEST_SIZE = None
    RESPONSE_SIZE = None
    
    # API-specific metrics
    SEARCH_COUNT = None
    SEARCH_DURATION = None
    BOYCOTT_CHECK_COUNT = None
    
    # AI metrics
    CHAT_COUNT = None
    CHAT_DURATION = None
    RECOMMENDATION_COUNT = None
    SENTIMENT_ANALYSIS_COUNT = None
    
    # Error metrics
    ERROR_COUNT = None
    VALIDATION_ERROR_COUNT = None
    
    # Data metrics
    PRODUCTS_TOTAL = None
    CATEGORIES_TOTAL = None
    
    @classmethod
    def initialize(cls):
        """Initialize Prometheus metrics."""
        # Prevent multiple initializations
        if hasattr(cls, '_initialized') and cls._initialized:
            return
        
        try:
            from prometheus_client import Counter, Histogram, Gauge
            
            # Request metrics
            cls.REQUEST_COUNT = Counter(
                'consumesafe_requests_total',
                'Total requests',
                ['method', 'endpoint', 'status']
            )
            cls.REQUEST_DURATION = Histogram(
                'consumesafe_request_duration_seconds',
                'Request duration in seconds',
                ['method', 'endpoint']
            )
            cls.REQUEST_SIZE = Histogram(
                'consumesafe_request_size_bytes',
                'Request size in bytes',
                ['method', 'endpoint']
            )
            cls.RESPONSE_SIZE = Histogram(
                'consumesafe_response_size_bytes',
                'Response size in bytes',
                ['method', 'endpoint']
            )
            
            # API-specific metrics
            cls.SEARCH_COUNT = Counter(
                'consumesafe_search_total',
                'Total search requests'
            )
            cls.SEARCH_DURATION = Histogram(
                'consumesafe_search_duration_seconds',
                'Search duration in seconds'
            )
            cls.BOYCOTT_CHECK_COUNT = Counter(
                'consumesafe_boycott_check_total',
                'Total boycott checks'
            )
            
            # AI metrics
            cls.CHAT_COUNT = Counter(
                'consumesafe_ai_chat_total',
                'Total chat requests',
                ['intent']
            )
            cls.CHAT_DURATION = Histogram(
                'consumesafe_ai_chat_duration_seconds',
                'Chat response time in seconds'
            )
            cls.RECOMMENDATION_COUNT = Counter(
                'consumesafe_ai_recommendation_total',
                'Total recommendation requests'
            )
            cls.SENTIMENT_ANALYSIS_COUNT = Counter(
                'consumesafe_ai_sentiment_total',
                'Total sentiment analyses'
            )
            
            # Error metrics
            cls.ERROR_COUNT = Counter(
                'consumesafe_errors_total',
                'Total errors',
                ['type', 'endpoint']
            )
            cls.VALIDATION_ERROR_COUNT = Counter(
                'consumesafe_validation_errors_total',
                'Total validation errors',
                ['field']
            )
            
            # Data metrics
            cls.PRODUCTS_TOTAL = Gauge(
                'consumesafe_products_total',
                'Total boycotted products',
                ['category']
            )
            cls.CATEGORIES_TOTAL = Gauge(
                'consumesafe_categories_total',
                'Total categories'
            )
            
            cls._initialized = True
            return True
        except ImportError:
            return False


# ============= STRUCTURED LOGGING HELPERS =============

class RequestLogger:
    """Helper for logging HTTP requests and responses."""
    
    @staticmethod
    def log_request(
        logger: logging.Logger,
        method: str,
        path: str,
        query_params: dict = None,
        user_id: str = None,
        request_id: str = None
    ):
        """Log incoming request."""
        extra = {
            'user_id': user_id,
            'request_id': request_id,
        }
        logger.info(
            f"Incoming {method} {path}",
            extra=extra
        )
    
    @staticmethod
    def log_response(
        logger: logging.Logger,
        status_code: int,
        duration_ms: float,
        request_id: str = None
    ):
        """Log response."""
        extra = {
            'request_id': request_id,
            'duration_ms': duration_ms,
        }
        logger.info(
            f"Response {status_code} ({duration_ms}ms)",
            extra=extra
        )
    
    @staticmethod
    def log_error(
        logger: logging.Logger,
        error_type: str,
        message: str,
        request_id: str = None,
        details: dict = None
    ):
        """Log error."""
        extra = {
            'request_id': request_id,
        }
        if details:
            extra['details'] = details
        logger.error(f"{error_type}: {message}", extra=extra)


class AIServiceLogger:
    """Helper for logging AI service operations."""
    
    @staticmethod
    def log_chat(
        logger: logging.Logger,
        user_message: str,
        intent: str,
        duration_ms: float,
        request_id: str = None
    ):
        """Log chat interaction."""
        extra = {'request_id': request_id, 'duration_ms': duration_ms}
        logger.info(
            f"Chat: intent={intent}, duration={duration_ms}ms",
            extra=extra
        )
    
    @staticmethod
    def log_recommendation(
        logger: logging.Logger,
        user_history_size: int,
        recommendations_count: int,
        duration_ms: float
    ):
        """Log recommendation generation."""
        logger.info(
            f"Recommendations: {recommendations_count} "
            f"from {user_history_size} items ({duration_ms}ms)"
        )
    
    @staticmethod
    def log_sentiment(
        logger: logging.Logger,
        sentiment: str,
        category: str,
        duration_ms: float
    ):
        """Log sentiment analysis."""
        logger.info(
            f"Sentiment: {sentiment}, category={category} ({duration_ms}ms)"
        )


# ============= ALERTING CONFIGURATION =============

class AlertRules:
    """Prometheus alert rules in text format."""
    
    RULES_YAML = """
groups:
- name: consumesafe_alerts
  interval: 30s
  rules:
  
  # High error rate alert
  - alert: HighErrorRate
    expr: rate(consumesafe_errors_total[5m]) > 0.05
    for: 5m
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value | humanizePercentage }}"
  
  # High response time alert
  - alert: SlowResponseTime
    expr: histogram_quantile(0.95, consumesafe_request_duration_seconds) > 1
    for: 5m
    annotations:
      summary: "Slow response time"
      description: "95th percentile response time is {{ $value }}s"
  
  # High search latency
  - alert: SlowSearch
    expr: histogram_quantile(0.95, consumesafe_search_duration_seconds) > 0.5
    for: 5m
    annotations:
      summary: "Slow search performance"
      description: "Search latency is {{ $value }}s"
  
  # AI service errors
  - alert: AIServiceErrors
    expr: rate(consumesafe_errors_total{type=~"ai_.*"}[5m]) > 0.02
    for: 5m
    annotations:
      summary: "AI service errors detected"
      description: "AI error rate is {{ $value | humanizePercentage }}"
  
  # Memory usage (if using Kubernetes)
  - alert: HighMemoryUsage
    expr: container_memory_usage_bytes{pod="consumesafe-api"} > 500000000
    for: 5m
    annotations:
      summary: "High memory usage"
      description: "Memory usage is {{ humanize $value }}B"
  
  # Low disk space
  - alert: LowDiskSpace
    expr: node_filesystem_avail_bytes{mountpoint="/"} < 1000000000
    for: 5m
    annotations:
      summary: "Low disk space"
      description: "Available disk space is {{ humanize $value }}B"
"""


# ============= DASHBOARD CONFIGURATION =============

GRAFANA_DASHBOARD = {
    "dashboard": {
        "title": "ConsumeSafe Monitoring",
        "panels": [
            {
                "title": "Requests per Second",
                "targets": [
                    {
                        "expr": "rate(consumesafe_requests_total[1m])"
                    }
                ]
            },
            {
                "title": "Error Rate",
                "targets": [
                    {
                        "expr": "rate(consumesafe_errors_total[5m])"
                    }
                ]
            },
            {
                "title": "Response Time (p95)",
                "targets": [
                    {
                        "expr": "histogram_quantile(0.95, consumesafe_request_duration_seconds)"
                    }
                ]
            },
            {
                "title": "AI Chat Requests",
                "targets": [
                    {
                        "expr": "rate(consumesafe_ai_chat_total[5m])"
                    }
                ]
            },
            {
                "title": "Search Performance",
                "targets": [
                    {
                        "expr": "rate(consumesafe_search_total[5m])"
                    }
                ]
            }
        ]
    }
}


# ============= INITIALIZATION =============

def initialize_monitoring():
    """Initialize all monitoring components."""
    # Setup logging
    logger = setup_logging(
        log_level=os.getenv('LOG_LEVEL', 'INFO'),
        log_format=os.getenv('LOG_FORMAT', 'json'),
        log_file=os.getenv('LOG_FILE', 'logs/consumesafe.log')
    )
    
    # Initialize Prometheus metrics
    prometheus_enabled = PrometheusMetrics.initialize()
    
    if prometheus_enabled:
        logger.info("Prometheus metrics initialized")
    else:
        logger.warning("Prometheus not available, metrics disabled")
    
    return logger


if __name__ == "__main__":
    # Example usage
    logger = initialize_monitoring()
    logger.info("Monitoring system initialized")
    logger.info("Alert rules available in AlertRules.RULES_YAML")
