from flask import (Blueprint, flash, g, make_response, redirect,
                   render_template, request, session, url_for)
from flask_login import current_user, login_required

auth_bp = Blueprint('auth', __name__, template_folder='templates',
                 static_folder='static')


@auth_bp.route('/login', methods=('GET', 'POST'))
def login():
    return 'login'
