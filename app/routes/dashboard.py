from urllib.parse import urlencode
from flask import Blueprint, render_template, redirect, url_for, flash
from ..models import Service
from . import login_required
from ..jwt_utils import generate_sso_token

bp = Blueprint('dashboard', __name__)


def get_service_audience(service):
    service_name = (service.name or '').strip().lower().replace(' ', '-')
    if service_name.startswith('tt-'):
        return service_name
    return f'tt-{service_name}'


@bp.route('/')
@login_required
def index(current_user):
    services = (
        Service.query
        .filter_by(is_active=True)
        .filter(
            (Service.required_role == 'user') |
            (Service.required_role == current_user['role'])
        )
        .order_by(Service.sort_order, Service.name)
        .all()
    )

    for service in services:
        service.launch_url = url_for('dashboard.launch_service', service_id=service.id)

    return render_template('dashboard.html', services=services, current_user=current_user)


@bp.route('/launch/<int:service_id>')
@login_required
def launch_service(current_user, service_id):
    service = Service.query.filter_by(id=service_id, is_active=True).first()
    if not service:
        flash('Service nicht gefunden oder deaktiviert.', 'danger')
        return redirect(url_for('dashboard.index'))

    if service.required_role not in ('user', current_user['role']):
        flash('Sie haben keinen Zugriff auf diesen Service.', 'danger')
        return redirect(url_for('dashboard.index'))

    service_base = (service.url or '').rstrip('/')
    audience = get_service_audience(service)
    token = generate_sso_token(current_user, audience=audience)
    query = urlencode({'token': token})
    return redirect(f'{service_base}/auth/sso?{query}')
