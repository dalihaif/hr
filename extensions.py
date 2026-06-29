"""
扩展模块初始化
包含Redis、Celery等扩展的初始化
"""
import redis
from celery import Celery
from config import Config

# ============================================================
# Redis配置
# ============================================================
redis_pool = redis.ConnectionPool(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    db=Config.REDIS_DB,
    decode_responses=True,
    max_connections=50
)

redis_client = redis.Redis(connection_pool=redis_pool)

def init_redis():
    """测试Redis连接"""
    try:
        redis_client.ping()
        print("✓ Redis连接成功")
        return True
    except Exception as e:
        print(f"✗ Redis连接失败: {e}")
        print("  提示: 请确保Redis服务器已启动")
        print("  Windows: 下载并运行Redis for Windows")
        print("  Docker: docker run -d -p 6379:6379 redis:latest")
        return False

# ============================================================
# Celery配置
# ============================================================
celery_app = Celery('hospital_hr')
celery_app.config_from_object(Config)

# 自动发现任务
celery_app.autodiscover_tasks(['tasks'])

def init_celery():
    """测试Celery配置"""
    print("✓ Celery配置完成")
    print(f"  Broker: {Config.CELERY_BROKER_URL}")
    print(f"  Backend: {Config.CELERY_RESULT_BACKEND}")
