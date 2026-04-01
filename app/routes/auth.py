from flask import Blueprint, render_template, redirect, url_for, request, flash, make_response
from ..extensions import limiter
from ..models import User
from ..forms import LoginForm
from ..jwt_utils import generate_jwt, set_jwt_cookie, clear_jwt_cookie, get_jwt_from_request, validate_jwt

bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['GET', 'POST'])
@limiter.limit('20/minute', methods=['POST'])
def login():
    # Already logged in → redirect to dashboard
    token = get_jwt_from_request()
    if token and validate_jwt(token):
        return redirect(url_for('dashboard.index'))

    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(username=form.username.data, is_active=True).first()
        if user and user.check_password(form.password.data):
            token = generate_jwt(user)
            response = make_response(redirect(url_for('dashboard.index')))
            set_jwt_cookie(response, token)
            return response
        flash('Ungültiger Benutzername oder Passwort.', 'danger')

    return render_template('login.html', form=form)


@bp.route('/logout')
def logout():
    response = make_response(redirect(url_for('auth.login')))
    clear_jwt_cookie(response)
    return response
