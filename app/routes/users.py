from flask import Blueprint, render_template, redirect, url_for, request, flash
from ..extensions import db
from ..models import User
from ..forms import UserForm
from . import login_required, admin_required

bp = Blueprint('users', __name__, url_prefix='/users')


@bp.route('/')
@login_required
@admin_required
def index(current_user):
    users = User.query.order_by(User.username).all()
    return render_template('users.html', users=users, current_user=current_user)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new(current_user):
    form = UserForm(request.form)
    if request.method == 'POST' and form.validate():
        if User.query.filter_by(username=form.username.data).first():
            flash(f'Benutzername "{form.username.data}" ist bereits vergeben.', 'danger')
        elif not form.password.data:
            flash('Passwort ist erforderlich beim Erstellen eines Benutzers.', 'danger')
        else:
            user = User(username=form.username.data, role=form.role.data, is_active=form.is_active.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash(f'Benutzer "{user.username}" erstellt.', 'success')
            return redirect(url_for('users.index'))
    return render_template('user_form.html', form=form, action='Erstellen', current_user=current_user)


@bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(current_user, user_id):
    user = db.session.get(User, user_id)
    if not user:
        flash('Benutzer nicht gefunden.', 'danger')
        return redirect(url_for('users.index'))
    form = UserForm(request.form, obj=user)
    if request.method == 'POST' and form.validate():
        existing = User.query.filter_by(username=form.username.data).first()
        if existing and existing.id != user.id:
            flash(f'Benutzername "{form.username.data}" ist bereits vergeben.', 'danger')
        else:
            user.username = form.username.data
            user.role = form.role.data
            user.is_active = form.is_active.data
            if form.password.data:
                user.set_password(form.password.data)
            db.session.commit()
            flash(f'Benutzer "{user.username}" aktualisiert.', 'success')
            return redirect(url_for('users.index'))
    return render_template('user_form.html', form=form, action='Bearbeiten', user=user, current_user=current_user)


@bp.route('/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(current_user, user_id):
    user = db.session.get(User, user_id)
    if not user:
        flash('Benutzer nicht gefunden.', 'danger')
    elif str(user_id) == current_user['sub']:
        flash('Du kannst deinen eigenen Account nicht löschen.', 'danger')
    else:
        db.session.delete(user)
        db.session.commit()
        flash(f'Benutzer "{user.username}" gelöscht.', 'success')
    return redirect(url_for('users.index'))
