import os
import logging
from flask import Flask
from .config import Config
from .extensions import db, migrate, limiter


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Logging
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO').upper(), logging.INFO)
    logging.basicConfig(level=log_level)

    # Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    # Blueprints
    from .routes.auth import bp as auth_bp
    from .routes.dashboard import bp as dashboard_bp
    from .routes.users import bp as users_bp
    from .routes.services import bp as services_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(services_bp)

    with app.app_context():
        if app.config.get('AUTO_CREATE_DB', True):
            db.create_all()
            _seed_default_users(app)

    return app


def _seed_default_users(app):
    """Create default admin user if no users exist."""
    from .models import User
    if User.query.count() == 0 and app.config.get('CREATE_DEFAULT_USERS', True):
        admin_username = os.environ.get('DEFAULT_ADMIN_USERNAME', 'admin')
        admin_password = os.environ.get('DEFAULT_ADMIN_PASSWORD', 'admin')
        admin = User(username=admin_username, role='admin', is_active=True)
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()
        app.logger.info(f'Default admin user "{admin_username}" created.')
