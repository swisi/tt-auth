from flask import Blueprint, current_app, jsonify, request

from ..extensions import db
from ..models import User

bp = Blueprint('api', __name__, url_prefix='/api')


def _authorized():
    expected = current_app.config.get('INTERNAL_API_SECRET')
    provided = request.headers.get('X-TT-Internal-Secret')
    return bool(expected and provided and provided == expected)


@bp.route('/users/<int:user_id>/profile-complete', methods=['POST'])
def mark_profile_complete(user_id):
    if not _authorized():
        return jsonify({'error': 'unauthorized'}), 401

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'not_found'}), 404

    user.profile_complete = True
    if user.account_status == 'draft':
        user.account_status = 'pending'
    db.session.commit()
    return jsonify({
        'status': 'ok',
        'user_id': user.id,
        'profile_complete': user.profile_complete,
        'account_status': user.account_status,
    })
