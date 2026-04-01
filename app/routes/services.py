from flask import Blueprint, render_template, redirect, url_for, request, flash
from ..extensions import db
from ..models import Service
from ..forms import ServiceForm
from . import login_required, admin_required

bp = Blueprint('services', __name__, url_prefix='/services')


@bp.route('/')
@login_required
@admin_required
def index(current_user):
    services = Service.query.order_by(Service.sort_order, Service.name).all()
    return render_template('services.html', services=services, current_user=current_user)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new(current_user):
    form = ServiceForm(request.form)
    if request.method == 'POST' and form.validate():
        if Service.query.filter_by(name=form.name.data).first():
            flash(f'Service "{form.name.data}" existiert bereits.', 'danger')
        else:
            service = Service(
                name=form.name.data,
                url=form.url.data,
                icon=form.icon.data or 'grid',
                description=form.description.data or '',
                required_role=form.required_role.data,
                is_active=form.is_active.data,
                sort_order=form.sort_order.data or 0,
            )
            db.session.add(service)
            db.session.commit()
            flash(f'Service "{service.name}" erstellt.', 'success')
            return redirect(url_for('services.index'))
    return render_template('service_form.html', form=form, action='Erstellen', current_user=current_user)


@bp.route('/<int:service_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(current_user, service_id):
    service = db.session.get(Service, service_id)
    if not service:
        flash('Service nicht gefunden.', 'danger')
        return redirect(url_for('services.index'))
    form = ServiceForm(request.form, obj=service)
    if request.method == 'POST' and form.validate():
        existing = Service.query.filter_by(name=form.name.data).first()
        if existing and existing.id != service.id:
            flash(f'Service "{form.name.data}" existiert bereits.', 'danger')
        else:
            service.name = form.name.data
            service.url = form.url.data
            service.icon = form.icon.data or 'grid'
            service.description = form.description.data or ''
            service.required_role = form.required_role.data
            service.is_active = form.is_active.data
            service.sort_order = form.sort_order.data or 0
            db.session.commit()
            flash(f'Service "{service.name}" aktualisiert.', 'success')
            return redirect(url_for('services.index'))
    return render_template('service_form.html', form=form, action='Bearbeiten', service=service, current_user=current_user)


@bp.route('/<int:service_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(current_user, service_id):
    service = db.session.get(Service, service_id)
    if not service:
        flash('Service nicht gefunden.', 'danger')
    else:
        db.session.delete(service)
        db.session.commit()
        flash(f'Service "{service.name}" gelöscht.', 'success')
    return redirect(url_for('services.index'))
