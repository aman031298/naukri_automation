"""
Rate limiter to prevent being blocked
"""
import time
import random
from collections import deque
from datetime import datetime, timedelta

class RateLimiter:
    """Prevents too many requests in short time"""
    
    def __init__(self, max_requests=10, time_window=60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = deque()
    
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        now = datetime.now()
        
        # Clean old requests
        cutoff = now - timedelta(seconds=self.time_window)
        while self.requests and self.requests[0] < cutoff:
            self.requests.popleft()
        
        # Check if we need to wait
        if len(self.requests) >= self.max_requests:
            wait_time = (self.requests[0] + timedelta(seconds=self.time_window) - now).total_seconds()
            if wait_time > 0:
                time.sleep(wait_time + random.uniform(0.5, 2))
        
        # Add current request
        self.requests.append(now)
    
    def reset(self):
        """Reset the rate limiter"""
        self.requests.clear()