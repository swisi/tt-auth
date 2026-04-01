from flask import Blueprint, render_template
from ..models import Service
from . import login_required

bp = Blueprint('dashboard', __name__)


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
    return render_template('dashboard.html', services=services, current_user=current_user)
