import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'belarus-tourism-secret-key-2026'
    SQLALCHEMY_DATABASE_URI = (
        'mysql+pymysql://root:123456@localhost:3306/belarus_tourism'
        '?charset=utf8mb4'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'max_overflow': 20,
    }
    SQLALCHEMY_ECHO = False

    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-belarus-2026'
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours
    JWT_REFRESH_TOKEN_EXPIRES = 2592000  # 30 days

    # DeepSeek API
    DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY') or 'sk-cd436ed4f8c44e8f9e81755f06e19d24'
    DEEPSEEK_API_URL = 'https://api.deepseek.com/v1/chat/completions'
