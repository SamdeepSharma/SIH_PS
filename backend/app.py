"""Main application entry point."""
import os
import logging
from flask import Flask, jsonify, request, abort, session
from celery import Celery
from werkzeug.exceptions import HTTPException
from config import Config
from extensions import init_extensions
from blueprints.auth.routes import auth_bp
from blueprints.dashboard.routes import dashboard_bp
from blueprints.nlp.routes import nlp_bp
from blueprints.documents.routes import documents_bp
from middleware.security import validate_request, csrf_protect


def create_app(config_class=Config):
    """
    Application factory function to create and configure the Flask app.
    :param config_class: The configuration class to use.
    :return: Configured Flask app.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions (e.g., database, migrations, etc.)
    init_extensions(app)

    # Register blueprints with the application
    register_blueprints(app)

    # Register global middleware
    configure_global_middleware(app)

    # Register error handlers
    register_error_handlers(app)

    return app


def register_blueprints(app):
    """
    Register all blueprints for the application.
    :param app: The Flask app instance.
    """
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(nlp_bp, url_prefix='/nlp')
    app.register_blueprint(documents_bp, url_prefix='/documents')


def configure_global_middleware(app):
    """
    Configure global middleware for the app, such as security headers, CSRF protection, etc.
    :param app: The Flask app instance.
    """
    @app.before_request
    @validate_request
    @csrf_protect
    def before_request():
        """Global request validation, security enforcement, and additional logic."""

        # Log the incoming request details
        logging.info("Request Method: %s, Path: %s, Remote Addr: %s",
                     request.method, request.path, request.remote_addr)

        # Check if the user is authenticated
        if not session.get('user_id'):
            logging.warning("Unauthorized access attempt detected.")
            abort(401, description="Unauthorized")

        # Rate limiting logic
        client_ip = request.remote_addr
        if not check_rate_limit(client_ip):
            logging.warning("Rate limit exceeded for IP: %s", client_ip)
            abort(429, description="Too many requests, slow down!")

        # Additional checks can be added here


def check_rate_limit(client_ip):
    """
    Placeholder function to check if a client IP has exceeded the rate limit.
    This should be replaced with your actual rate-limiting logic.
    :param client_ip: The IP address of the client making the request.
    :return: True if the request is within the rate limit, False otherwise.
    """
    # Implement your rate limiting logic here
    return True


def register_error_handlers(app):
    """
    Register error handlers for the application.
    :param app: The Flask app instance.
    """
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """Handle HTTP errors and return JSON responses."""
        logging.error("HTTP Exception: %s", error)
        response = error.get_response()
        response.data = jsonify({
            "code": error.code,
            "name": error.name,
            "description": error.description
        })
        response.content_type = "application/json"
        return response, error.code

    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle non-HTTP errors and return JSON responses."""
        logging.error("Unhandled Exception: %s", str(error))
        return jsonify({
            "code": 500,
            "name": "Internal Server Error",
            "description": "An unexpected error has occurred. Please try again later."
        }), 500


def make_celery(app):
    """
    Configure and return a Celery instance.
    :param app: The Flask app instance.
    :return: Configured Celery instance.
    """
    celery_instance = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )
    celery_instance.conf.update(app.config)
    celery_instance.autodiscover_tasks(['services.async_tasks'])

    # Optional: Add custom logging for Celery
    setup_celery_logging(celery_instance)

    return celery_instance


def configure_logging():
    """
    Configure logging for the application.
    """
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s [%(levelname)s] %(message)s',
                        handlers=[logging.StreamHandler()])


def setup_celery_logging(celery_instance):
    """
    Setup logging for Celery.
    :param celery_instance: The Celery instance.
    """
    logger = logging.getLogger('celery')
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def configure_app(app):
    """
    Additional configuration for the app.
    This can include setting up security headers, CSRF protection, etc.
    :param app: The Flask app instance.
    """
    @app.after_request
    def apply_security_headers(response):
        """
        Apply security-related headers to each response.
        """
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        return response


# Main application execution
if __name__ == '__main__':
    configure_logging()
    flask_app = create_app()  # Rename to avoid 'redefined-outer-name' pylint warning
    configure_app(flask_app)
    celery_app = make_celery(flask_app)  # Renamed to avoid 'redefined-outer-name' pylint warning
    flask_app.run(host='0.0.0.0', port=int(os.getenv('PORT', '5000')),
                  debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true')
