import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

csrf = CSRFProtect()
from app.services.cache_service import cache as cache_service

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
    app.config.from_object('app.config.Config')

    db.init_app(app)
    try:
        csrf.init_app(app)
    except Exception:
        pass
    # init redis cache
    try:
        cache_service.init_app(app)
    except Exception:
        pass

    # register blueprints (placeholders)
    try:
        from app.routes import auth, onboarding, rekomendasi, search, wishlist
        app.register_blueprint(auth.bp)
        app.register_blueprint(onboarding.bp)
        app.register_blueprint(rekomendasi.bp)
        app.register_blueprint(search.bp)
        app.register_blueprint(wishlist.bp)
    except Exception:
        # Blueprints may not exist yet during scaffold
        pass

    return app
