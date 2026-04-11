from urllib.parse import urljoin, urlparse

from flask import Blueprint, render_template, redirect, url_for, request, flash, make_response
from ..extensions import limiter
from ..models import User
from ..forms import LoginForm
from ..jwt_utils import generate_jwt, set_jwt_cookie, clear_jwt_cookie, get_jwt_from_request, validate_jwt

bp = Blueprint('auth', __name__)


def is_safe_internal_url(target):
    if not target:
        return False
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


@bp.route('/login', methods=['GET', 'POST'])
@limiter.limit('20/minute', methods=['POST'])
def login():
    next_page = request.args.get('next', '').strip()
    if next_page and not is_safe_internal_url(next_page):
        next_page = ''

    # Already logged in → redirect to dashboard
    token = get_jwt_from_request()
    if token and validate_jwt(token):
        return redirect(next_page or url_for('dashboard.index'))

    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(username=form.username.data, is_active=True).first()
        if user and user.check_password(form.password.data):
            token = generate_jwt(user)
            response = make_response(redirect(next_page or url_for('dashboard.index')))
            set_jwt_cookie(response, token)
            return response
        flash('Ungültiger Benutzername oder Passwort.', 'danger')

    return render_template('login.html', form=form, next_page=next_page)


@bp.route('/logout')
def logout():
    response = make_response(redirect(url_for('auth.login')))
    clear_jwt_cookie(response)
    return response
