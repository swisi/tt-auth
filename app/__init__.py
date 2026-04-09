import os
import logging
from flask import Flask
from sqlalchemy.exc import IntegrityError
from .config import Config
from .extensions import db, migrate, limiter


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    if not app.config.get('SECRET_KEY'):
        if app.debug or app.testing:
            app.logger.warning('SECRET_KEY is not set; running in insecure development mode.')
        else:
            raise RuntimeError('SECRET_KEY must be set in production.')

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
            _seed_default_services(app)
            _bootstrap_platform_admin_access(app)

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
        try:
            db.session.commit()
            app.logger.info(f'Default admin user "{admin_username}" created.')
        except IntegrityError:
            db.session.rollback()
            app.logger.info(f'Default admin user "{admin_username}" already exists.')


def _seed_default_services(app):
    """Create default dashboard services if they are missing."""
    if not app.config.get('CREATE_DEFAULT_SERVICES', True):
        return

    from .models import Service

    default_services = [
        {
            'name': 'agenda',
            'url': app.config.get('DEFAULT_AGENDA_URL', 'http://localhost:8086'),
            'icon': 'calendar-check',
            'description': 'Trainingsverwaltung und Live-Agenda',
            'required_role': 'user',
            'sort_order': 10,
        },
        {
            'name': 'analytics',
            'url': app.config.get('DEFAULT_ANALYTICS_URL', 'http://localhost:8087'),
            'icon': 'bar-chart-line',
            'description': 'Spielanalyse, Scouting Reports und Videoauswertung',
            'required_role': 'user',
            'sort_order': 20,
        },
    ]

    created = []
    for service_data in default_services:
        existing = Service.query.filter_by(name=service_data['name']).first()
        if existing:
            continue
        db.session.add(Service(is_active=True, **service_data))
        created.append(service_data['name'])

    if not created:
        return

    try:
        db.session.commit()
        app.logger.info('Default services created: %s', ', '.join(created))
    except IntegrityError:
        db.session.rollback()
        app.logger.info('Default service creation raced with another worker; continuing.')


def _bootstrap_platform_admin_access(app):
    """Bootstrap initial service access for existing platform admins.

    This only runs for admins who do not have any explicit service access yet.
    """
    from .models import User, Service, ServiceAccess

    admins = User.query.filter_by(role='admin', is_active=True).all()
    services = Service.query.filter_by(is_active=True).all()
    if not admins or not services:
        return

    changed = False
    for admin in admins:
        has_explicit_access = ServiceAccess.query.filter_by(user_id=admin.id).first()
        if has_explicit_access:
            continue
        for service in services:
            db.session.add(ServiceAccess(user_id=admin.id, service_id=service.id, role='admin', is_active=True))
            changed = True

    if changed:
        try:
            db.session.commit()
            app.logger.info('Bootstrapped initial service access for platform admins.')
        except IntegrityError:
            db.session.rollback()
