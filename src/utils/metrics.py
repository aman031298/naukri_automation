"""
Performance monitoring and metrics
"""
import time
from datetime import datetime
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class Metrics:
    """Collect and track performance metrics"""
    
    _instance = None
    _metrics = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._metrics = {}
        return cls._instance
    
    def record(self, name: str, value: float):
        """Record a metric"""
        if name not in self._metrics:
            self._metrics[name] = []
        self._metrics[name].append({
            'value': value,
            'timestamp': datetime.now().isoformat()
        })
    
    def get(self, name: str, limit: int = 10):
        """Get metrics for a name"""
        return self._metrics.get(name, [])[-limit:]
    
    def get_stats(self, name: str):
        """Get statistics for a metric"""
        values = [m['value'] for m in self._metrics.get(name, [])]
        if not values:
            return {}
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'total': sum(values)
        }
    
    def clear(self):
        """Clear all metrics"""
        self._metrics.clear()
    
    def report(self):
        """Generate metrics report"""
        report = {}
        for name in self._metrics:
            report[name] = self.get_stats(name)
        return report

def timed(metric_name: str):
    """Decorator to time function execution"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start
            Metrics().record(metric_name, duration)
            logger.debug(f"⏱️ {metric_name} took {duration:.2f}s")
            return result
        return wrapper
    return decorator