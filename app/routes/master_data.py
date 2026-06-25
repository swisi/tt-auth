import requests
from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for

from . import admin_required, login_required

bp = Blueprint('master_data', __name__, url_prefix='/master-data')


def _infra_base():
    return current_app.config.get('TT_INFRA_INTERNAL_URL', 'http://localhost:8084').rstrip('/')


def _infra_headers():
    secret = current_app.config.get('INTERNAL_API_SECRET')
    return {'X-TT-Internal-Secret': secret} if secret else {}


def _fetch_positions(include_inactive=True):
    try:
        response = requests.get(
            f'{_infra_base()}/api/master-data/positions',
            params={'include_inactive': '1' if include_inactive else '0'},
            headers=_infra_headers(),
            timeout=4,
        )
    except requests.RequestException as exc:
        current_app.logger.warning('tt-infra positions fetch failed: %s', exc)
        return [], 'Stammdaten konnten nicht geladen werden.'

    if response.status_code >= 400:
        current_app.logger.warning('tt-infra positions fetch failed: %s %s', response.status_code, response.text)
        return [], 'Stammdaten konnten nicht geladen werden.'

    payload = response.json() or {}
    return payload.get('positions', []), None


def _submit_position(method, key=None, payload=None):
    url = f'{_infra_base()}/api/master-data/positions'
    if key:
        url = f'{url}/{key}'
    try:
        response = requests.request(method, url, json=payload or {}, headers=_infra_headers(), timeout=4)
    except requests.RequestException as exc:
        current_app.logger.warning('tt-infra positions mutation failed: %s', exc)
        return False, 'Stammdaten konnten nicht gespeichert werden.'

    if response.status_code >= 400:
        current_app.logger.warning('tt-infra positions mutation failed: %s %s', response.status_code, response.text)
        if response.status_code == 409:
            return False, 'Der Schlüssel existiert bereits.'
        if response.status_code == 404:
            return False, 'Eintrag nicht gefunden.'
        return False, 'Stammdaten konnten nicht gespeichert werden.'
    return True, None


def _submit_position_reorder(order):
    url = f'{_infra_base()}/api/master-data/positions/reorder'
    try:
        response = requests.post(url, json={'order': order}, headers=_infra_headers(), timeout=4)
    except requests.RequestException as exc:
        current_app.logger.warning('tt-infra positions reorder failed: %s', exc)
        return False, 'Reihenfolge konnte nicht gespeichert werden.'

    if response.status_code >= 400:
        current_app.logger.warning('tt-infra positions reorder failed: %s %s', response.status_code, response.text)
        return False, 'Reihenfolge konnte nicht gespeichert werden.'
    return True, None


@bp.route('/positions', methods=['GET'])
@login_required
@admin_required
def positions(current_user):
    positions, error = _fetch_positions(include_inactive=True)
    if error:
        flash(error, 'danger')
    return render_template('master_data_positions.html', current_user=current_user, positions=positions)


@bp.route('/positions/new', methods=['POST'])
@login_required
@admin_required
def positions_new(current_user):
    key = (request.form.get('key') or '').strip().upper()
    label = (request.form.get('label') or '').strip()
    sort_order = request.form.get('sort_order') or '0'
    is_active = request.form.get('is_active') == 'y'
    ok, error = _submit_position('POST', payload={
        'key': key,
        'label': label,
        'sort_order': sort_order,
        'is_active': is_active,
    })
    flash('Position gespeichert.' if ok else error, 'success' if ok else 'danger')
    return redirect(url_for('master_data.positions'))


@bp.route('/positions/<string:key>/edit', methods=['POST'])
@login_required
@admin_required
def positions_edit(current_user, key):
    label = (request.form.get('label') or '').strip()
    sort_order = request.form.get('sort_order') or '0'
    is_active = request.form.get('is_active') == 'y'
    ok, error = _submit_position('PUT', key=key, payload={
        'key': key,
        'label': label,
        'sort_order': sort_order,
        'is_active': is_active,
    })
    flash('Position gespeichert.' if ok else error, 'success' if ok else 'danger')
    return redirect(url_for('master_data.positions'))


@bp.route('/positions/<string:key>/delete', methods=['POST'])
@login_required
@admin_required
def positions_delete(current_user, key):
    ok, error = _submit_position('DELETE', key=key)
    flash('Position gelöscht.' if ok else error, 'success' if ok else 'danger')
    return redirect(url_for('master_data.positions'))


@bp.route('/positions/reorder', methods=['POST'])
@login_required
@admin_required
def positions_reorder(current_user):
    order = request.form.getlist('order')
    ok, error = _submit_position_reorder(order)
    flash('Reihenfolge gespeichert.' if ok else error, 'success' if ok else 'danger')
    return redirect(url_for('master_data.positions'))
