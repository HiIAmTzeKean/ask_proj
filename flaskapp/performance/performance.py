import datetime
from flask import (Blueprint, flash, g, make_response,
                   redirect, render_template, request, session, url_for)
from flaskapp import db
from flaskapp.models import student, studentStatus, dojo, enrollment
from flaskapp.performance.db_method import get_dojoInfo
from flaskapp.performance.form import formGradePerformance

performance_bp = Blueprint('performance', __name__,
                           template_folder='templates', static_folder='static')


@performance_bp.route('/performanceViewer', methods=('GET', 'POST'))
def performanceViewer():
    dojo_id = request.cookies.get('dojo_id')
    dojoName = get_dojoInfo(dojo_id, True)
    gradePerformanceform = formGradePerformance()
    # form should allow user to select up to the past 3 lessons to grade
    # lesson default will be the lastest lesson student took

    studentId_list = db.session.query(enrollment.student_id).filter(enrollment.dojo_id == dojo_id).all()
    student_list = db.session.query(student).filter(student.id.in_(studentId_list)).order_by(student.active.desc(), student.belt.asc()).all()
    return render_template('performance/performanceViewer.html', student_list=student_list, dojoName=dojoName, gradePerformanceform=gradePerformanceform)


@performance_bp.route('/performanceGradePerformance', methods=('GET', 'POST'))
def performanceGradePerformance():
    return 'performanceGradePerformance'

@performance_bp.route('/performanceChartView', methods=('GET', 'POST'))
def performanceChartView():
    return 'performanceChartView'
