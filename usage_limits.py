import redis
import tiktoken
from datetime import datetime, timedelta
import os
from functools import wraps
from flask import request, jsonify

# Initialize Redis
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
redis_client = redis.from_url(redis_url)

# Constants
DAILY_LIMIT_PER_IP = 5  # Maximum requests per IP per day
MONTHLY_TOKEN_LIMIT = 100000  # Maximum tokens per month
RATE_LIMIT_WINDOW = 86400  # 24 hours in seconds

def count_tokens(text):
    """Count tokens in text using tiktoken"""
    enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
    return len(enc.encode(text))

def get_monthly_key():
    """Get the key for monthly token tracking"""
    now = datetime.now()
    return f"monthly_tokens:{now.year}:{now.month}"

def check_rate_limit():
    """Decorator to check rate limits"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            ip = request.remote_addr
            
            # Check daily limit per IP
            daily_key = f"daily:{ip}:{datetime.now().strftime('%Y-%m-%d')}"
            daily_count = redis_client.get(daily_key)
            
            if daily_count and int(daily_count) >= DAILY_LIMIT_PER_IP:
                return jsonify({
                    'error': 'Daily limit exceeded. Please try again tomorrow.',
                    'remaining_requests': 0,
                    'reset_time': redis_client.ttl(daily_key)
                }), 429

            # Get monthly token usage
            monthly_key = get_monthly_key()
            monthly_tokens = redis_client.get(monthly_key)
            monthly_tokens = int(monthly_tokens) if monthly_tokens else 0

            if monthly_tokens >= MONTHLY_TOKEN_LIMIT:
                return jsonify({
                    'error': 'Monthly token limit exceeded. Please try again next month.',
                    'current_usage': monthly_tokens,
                    'limit': MONTHLY_TOKEN_LIMIT
                }), 429

            # Increment daily counter
            pipe = redis_client.pipeline()
            pipe.incr(daily_key)
            pipe.expire(daily_key, RATE_LIMIT_WINDOW)
            pipe.execute()

            return f(*args, **kwargs)
        return decorated_function
    return decorator

def track_token_usage(tokens):
    """Track token usage for the current month"""
    monthly_key = get_monthly_key()
    redis_client.incrby(monthly_key, tokens)
    # Set expiry to 60 days to ensure the key gets cleaned up
    redis_client.expire(monthly_key, 60 * 24 * 60 * 60)

def get_usage_stats():
    """Get current usage statistics"""
    ip = request.remote_addr
    daily_key = f"daily:{ip}:{datetime.now().strftime('%Y-%m-%d')}"
    monthly_key = get_monthly_key()

    daily_count = redis_client.get(daily_key)
    monthly_tokens = redis_client.get(monthly_key)

    return {
        'daily_requests': {
            'current': int(daily_count) if daily_count else 0,
            'limit': DAILY_LIMIT_PER_IP,
            'remaining': DAILY_LIMIT_PER_IP - (int(daily_count) if daily_count else 0)
        },
        'monthly_tokens': {
            'current': int(monthly_tokens) if monthly_tokens else 0,
            'limit': MONTHLY_TOKEN_LIMIT,
            'remaining': MONTHLY_TOKEN_LIMIT - (int(monthly_tokens) if monthly_tokens else 0)
        }
    }
