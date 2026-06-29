"""
系统配置文件
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """应用配置类"""
    
    # 密钥配置
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dlhr_2026_secret_key_aes256')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt_secret_2026')
    
    # 数据库配置
    DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'hospital_hr.db')
    
    # Redis配置
    REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
    REDIS_DB = 0
    
    # Celery配置
    CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/1'
    CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/2'
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TIMEZONE = 'Asia/Shanghai'
    
    # JWT配置
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1小时
    JWT_REFRESH_TOKEN_EXPIRES = 86400 * 30  # 30天
    
    # 备份配置
    BACKUP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backups')
    
    # CORS配置（Vue前端地址）
    FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:5173')
    
    # Vue构建输出目录
    VUE_DIST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend', 'dist')
