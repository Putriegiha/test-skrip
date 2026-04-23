import redis
import json
from app import db
from flask import current_app

class CacheService:
    def __init__(self, app=None):
        self.client = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        url = app.config.get('REDIS_URL')
        self.client = redis.from_url(url)

    def get(self, key):
        if not self.client:
            return None
        v = self.client.get(key)
        if not v:
            return None
        return json.loads(v)

    def set(self, key, value, ttl=300):
        if not self.client:
            return
        self.client.set(key, json.dumps(value), ex=ttl)

    def delete(self, key):
        if not self.client:
            return
        self.client.delete(key)

cache = CacheService()
