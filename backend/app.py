from flask import Flask
from config import Config
from extensions import init_extensions
from blueprints.auth.routes import auth_bp
from blueprints.dashboard.routes import dashboard_bp
from blueprints.nlp.routes import nlp_bp
from blueprints.documents.routes import documents_bp
from middleware.security import validate_request, csrf_protect

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    init_extensions(app)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(nlp_bp, url_prefix='/nlp')
    app.register_blueprint(documents_bp, url_prefix='/documents')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
