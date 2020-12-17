from datetime import datetime, timedelta

from flask import (Blueprint, flash, g, make_response, redirect,
                   render_template, request, session, url_for)
from flask_login import current_user, login_required

attendance_bp = Blueprint('attendance', __name__,template_folder='templates', static_folder='static')

@attendance_bp.route('/attendanceStatus', methods=('GET', 'POST'))
def attendanceStatus():
    # two buttons to mark present and absent
    # collate number of people present and absent
    return 'people who are present or absent'

@attendance_bp.route('/attendanceStatus', methods=('GET', 'POST'))
def attendanceViewer():
    # should allow for adding and del of people
    # display name, rank, number of lesson to grading
    return 'People in the class with details'
