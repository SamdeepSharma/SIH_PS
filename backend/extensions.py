"""Extensions module."""
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_cors import CORS
from flask_redis import FlaskRedis
from celery import Celery

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()
limiter = Limiter(key_func=lambda: 'global')
cors = CORS()
redis_client = FlaskRedis()
celery = Celery(__name__)

def init_extensions(app):
    """
    Initialize the extensions used in the application.
    Parameters:
    - app: The Flask application object.
    Returns:
    - None
    """
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    cors.init_app(app)
    redis_client.init_app(app)
    celery.conf.update(app.config)
