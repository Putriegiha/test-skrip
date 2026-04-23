import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///dev.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    FASTTEXT_MODEL_PATH = os.environ.get('FASTTEXT_MODEL_PATH', 'models/cc.id.300.bin')
    LIKE_WEIGHT = 0.10
    WISHLIST_WEIGHT = 0.05
    TOP_N = 10
