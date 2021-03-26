import functools
from flask import (Blueprint, flash, g, make_response, redirect,
                   render_template, request, session, url_for)

auth_bp = Blueprint('auth', __name__, template_folder='templates',
                 static_folder='static')


@auth_bp.route('/login', methods=('GET', 'POST'))
def login():
    return 'login'

def dojo_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if request.cookies.get('dojo_id') is None:
            flash('Please select a Dojo first')
            return redirect(url_for('attendance.attendanceDojoSelect'))
        return view(**kwargs)
    return wrapped_view
