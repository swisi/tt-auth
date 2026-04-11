from urllib.parse import urlencode
from flask import Blueprint, render_template, redirect, url_for, flash, request
from ..models import Service, ServiceAccess
from . import login_required
from ..jwt_utils import generate_sso_token

bp = Blueprint('dashboard', __name__)


@bp.route('/health')
def health():
    return {'status': 'ok'}, 200


def get_service_audience(service):
    service_name = (service.name or '').strip().lower().replace(' ', '-')
    if service_name.startswith('tt-'):
        return service_name
    return f'tt-{service_name}'


@bp.route('/')
@login_required
def index(current_user):
    requested_service = (request.args.get('next_service') or '').strip().lower()
    requested_target = (request.args.get('next') or '').strip()
    service_access = (
        ServiceAccess.query
        .join(Service, Service.id == ServiceAccess.service_id)
        .filter(
            ServiceAccess.user_id == int(current_user['sub']),
            ServiceAccess.is_active.is_(True),
            Service.is_active.is_(True),
        )
        .order_by(Service.sort_order, Service.name)
        .all()
    )

    services = []
    for access in service_access:
        service = access.service
        launch_kwargs = {'service_id': service.id}
        if requested_target:
            launch_kwargs['next'] = requested_target
        service.launch_url = url_for('dashboard.launch_service', **launch_kwargs)
        service.assigned_role = access.role
        service.audience = get_service_audience(service)
        services.append(service)

    if requested_service:
        matching_service = next((service for service in services if service.audience == requested_service), None)
        if matching_service:
            launch_kwargs = {'service_id': matching_service.id}
            if requested_target:
                launch_kwargs['next'] = requested_target
            return redirect(url_for('dashboard.launch_service', **launch_kwargs))

    return render_template('dashboard.html', services=services, current_user=current_user)


@bp.route('/launch/<int:service_id>')
@login_required
def launch_service(current_user, service_id):
    service = Service.query.filter_by(id=service_id, is_active=True).first()
    if not service:
        flash('Service nicht gefunden oder deaktiviert.', 'danger')
        return redirect(url_for('dashboard.index'))

    access = ServiceAccess.query.filter_by(
        user_id=int(current_user['sub']),
        service_id=service.id,
        is_active=True,
    ).first()
    if not access:
        flash('Sie haben keinen Zugriff auf diesen Service.', 'danger')
        return redirect(url_for('dashboard.index'))

    service_base = (service.url or '').rstrip('/')
    audience = get_service_audience(service)
    token = generate_sso_token(
        current_user,
        audience=audience,
        service_role=access.role,
        platform_role=current_user.get('role'),
    )
    query_params = {'token': token}
    next_target = (request.args.get('next') or '').strip()
    if next_target:
        query_params['next'] = next_target
    query = urlencode(query_params)
    return redirect(f'{service_base}/auth/sso?{query}')
