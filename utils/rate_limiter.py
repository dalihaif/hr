"""
API速率限制器
防止暴力破解和滥用
"""
import time
from functools import wraps
from flask import request, jsonify, g


# 简单的内存存储（生产环境建议使用Redis）
rate_limit_store = {}


def get_client_ip():
    """获取客户端IP"""
    return request.remote_addr or '127.0.0.1'


def check_rate_limit(key, max_requests, window_seconds):
    """
    检查速率限制
    :param key: 限流键（如IP地址）
    :param max_requests: 时间窗口内最大请求数
    :param window_seconds: 时间窗口（秒）
    :return: (是否允许, 剩余请求数, 重置时间)
    """
    now = time.time()
    
    if key not in rate_limit_store:
        rate_limit_store[key] = []
    
    # 清理过期的请求记录
    rate_limit_store[key] = [t for t in rate_limit_store[key] if now - t < window_seconds]
    
    # 检查是否超过限制
    if len(rate_limit_store[key]) >= max_requests:
        oldest = min(rate_limit_store[key])
        reset_time = int(oldest + window_seconds - now)
        return False, 0, reset_time
    
    # 记录当前请求
    rate_limit_store[key].append(now)
    remaining = max_requests - len(rate_limit_store[key])
    return True, remaining, 0


def rate_limit(max_requests=60, window_seconds=60):
    """
    速率限制装饰器
    :param max_requests: 时间窗口内最大请求数
    :param window_seconds: 时间窗口（秒）
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = get_client_ip()
            key = f"rate_limit:{client_ip}:{request.endpoint}"
            
            allowed, remaining, reset_time = check_rate_limit(key, max_requests, window_seconds)
            
            if not allowed:
                return jsonify({
                    'error': '请求过于频繁，请稍后再试',
                    'reset_in': reset_time
                }), 429
            
            # 在响应头中添加限流信息
            response = f(*args, **kwargs)
            if hasattr(response, 'headers'):
                response.headers['X-RateLimit-Limit'] = str(max_requests)
                response.headers['X-RateLimit-Remaining'] = str(remaining)
            return response
        
        return decorated_function
    return decorator


def login_rate_limit(max_attempts=5, lockout_minutes=15):
    """
    登录防暴力破解装饰器
    :param max_attempts: 最大尝试次数
    :param lockout_minutes: 锁定时长（分钟）
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = get_client_ip()
            key = f"login_limit:{client_ip}"
            
            # 检查是否在锁定期间
            if key in rate_limit_store:
                attempts = rate_limit_store[key]
                now = time.time()
                
                # 清理超过锁定时间的记录
                if attempts and now - attempts[-1] > lockout_minutes * 60:
                    del rate_limit_store[key]
                elif len(attempts) >= max_attempts:
                    # 计算剩余锁定时间
                    oldest = attempts[0]
                    remaining = int((oldest + lockout_minutes * 60) - now)
                    if remaining > 0:
                        return jsonify({
                            'error': f'登录失败次数过多，请{remaining}秒后再试',
                            'locked': True,
                            'remaining': remaining
                        }), 429
            
            result = f(*args, **kwargs)
            
            # 如果登录失败，记录尝试
            if hasattr(result, 'status_code') and result.status_code in (401, 404):
                if key not in rate_limit_store:
                    rate_limit_store[key] = []
                rate_limit_store[key].append(time.time())
            
            return result
        
        return decorated_function
    return decorator


def cleanup_old_records():
    """清理过期的限流记录（定期调用）"""
    now = time.time()
    keys_to_delete = []
    
    for key, timestamps in rate_limit_store.items():
        # 保留最近1小时的记录
        rate_limit_store[key] = [t for t in timestamps if now - t < 3600]
        if not rate_limit_store[key]:
            keys_to_delete.append(key)
    
    for key in keys_to_delete:
        del rate_limit_store[key]
