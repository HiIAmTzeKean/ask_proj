import functools
from flask import (Blueprint, flash, g, make_response, redirect,
                   render_template, request, session, url_for)
from flaskapp import app, db, user_datastore
from flask_security.utils import hash_password, verify_password, login_user
from flask_security.decorators import roles_accepted
from flaskapp.models import Role, User, roles_users

auth_bp = Blueprint('auth', __name__, template_folder='templates/auth',
                 static_folder='static')


@auth_bp.route('/authAddRole', methods=('GET', 'POST'))
def authAddRole():
    roleName = request.args.get('roleName')
    email = request.args.get('email')
    user = user_datastore.find_user(email=email)
    role = user_datastore.find_or_create_role(roleName)
    user_datastore.add_role_to_user(user, role=role)
    db.session.commit()
    return redirect(url_for('auth.authUserViewer'))


@auth_bp.route('/authRemoveRole', methods=('GET', 'POST'))
def authRemoveRole():
    roleName = request.args.get('roleName')
    email = request.args.get('email')
    user = user_datastore.find_user(email=email)
    role = user_datastore.find_or_create_role(roleName)
    result = user_datastore.remove_role_from_user(user, role=role)
    db.session.commit()
    if result:
        flash('Successfully removed role {} from {}'.format(roleName, user.firstName))
    return redirect(url_for('auth.authUserViewer'))


@auth_bp.route('/authUserViewer', methods=('GET', 'POST'))
@roles_accepted('Admin', 'HQ')
def authUserViewer():
    user_list = db.session.query(User).filter().all()
    return render_template('authUserViewer.html',user_list=user_list)


@auth_bp.route('/authRoleEdit', methods=('GET', 'POST'))
def authRoleEdit():
    return 'hello'



def dojo_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if request.cookies.get('dojo_id') is None:
            flash('Please select a Dojo first')
            return redirect(url_for('attendance.attendanceDojoSelect'))
        return view(**kwargs)
    return wrapped_view
