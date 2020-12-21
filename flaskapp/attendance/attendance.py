import datetime
from flask import (Blueprint, flash, g, make_response, redirect, render_template, request, session, url_for)
from flaskapp import db
from flaskapp.models import student, studentStatus, dojo
from flaskapp.attendance.form import formDojoSelection, formAdd_DelStudent
from flaskapp.attendance.helpers import findTerm
from flaskapp.attendance.db_method import get_dojoInfo, insert_attendancePresent, update_Act_DeactStudent
from sqlalchemy import and_, not_


attendance_bp = Blueprint('attendance', __name__,template_folder='templates', static_folder='static')

@attendance_bp.route('/attendanceDojoSelect', methods=('GET', 'POST'))
def attendanceDojoSelect():
    form = formDojoSelection()
    dojo_list = dojo.query.all()
    form.dojoName.choices = [(dojo.id, dojo.name) for dojo in dojo_list]

    if form.validate_on_submit():
        dojo_id = form.dojoName.data
        resp = make_response(redirect(url_for('attendance.attendanceStatus')))
        resp.set_cookie('dojo_id', dojo_id)
        return resp
    return render_template('attendance/attendanceDojoSelect.html', dojo_list=dojo_list, form=form)

@attendance_bp.route('/attendanceStatus', methods=('GET', 'POST'))
def attendanceStatus():
    # two buttons to mark present and absent
    # collate number of people present and absent
    dojo_id = request.cookies.get('dojo_id')
    dojoName,dojoInstructor = get_dojoInfo(dojo_id)

    # find out who has been marked and who has not been marked
    marked_list = db.session.query(studentStatus,student).join(studentStatus, student.id == studentStatus.student_id).filter(
        studentStatus.dojo_id==dojo_id, studentStatus.date==datetime.date.today()).order_by(studentStatus.status.desc(), student.name.desc()).all()
    marked_ids = db.session.query(studentStatus.student_id).filter(studentStatus.dojo_id==dojo_id, studentStatus.date==datetime.date.today()).all()
    unmarked_list = db.session.query(student).filter(student.dojo_id==dojo_id, student.id.notin_(marked_ids)).order_by(student.name.desc()).all()

    return render_template('attendance/attendanceStatus.html', dojoName=dojoName, dojoInstructor=dojoInstructor, marked_list=marked_list, unmarked_list=unmarked_list)

@attendance_bp.route('/attendancePresent', methods=('GET', 'POST'))
def attendancePresent():
    import ast
    date = datetime.date.today()
    term = findTerm(date)
    status = ast.literal_eval(request.args.get('present'))
    student_id = int(request.args.get('student_id'))
    dojo_id = int(request.args.get('dojo_id'))
    
    insert_attendancePresent(date, status, term, student_id, dojo_id)
    return redirect(url_for('attendance.attendanceStatus'))

@attendance_bp.route('/attendanceViewer', methods=('GET', 'POST'))
def attendanceViewer():
    dojo_id = request.cookies.get('dojo_id')
    dojoName,dojoInstructor = get_dojoInfo(dojo_id)
    Add_DelStudent = formAdd_DelStudent()

    if Add_DelStudent.validate_on_submit():
        print('im here now')
        name = Add_DelStudent.name.date
        lastGrading = Add_DelStudent.lastGrading.data
        return redirect(url_for('attendance.attendanceAdd_DelStudent', name=name,lastGrading=lastGrading,dojo_id=dojo_id))
    
    student_list = db.session.query(student).filter_by(dojo_id=dojo_id).order_by(student.active.desc(),student.belt.asc()).all()
    return render_template('attendance/attendanceViewer.html', student_list=student_list, dojoName=dojoName, dojoInstructor=dojoInstructor, Add_DelStudent=Add_DelStudent)

@attendance_bp.route('/attendanceAdd_DelStuden', methods=('GET', 'POST'))
def attendanceAdd_DelStudent():
    name = str(request.args.get('name'))
    lastGrading = request.args.get('lastGrading')
    dojo_id = int(request.args.get('dojo_id'))
    print(lastGrading)
    # insert_newStudent(name, lastGrading, dojo_id, belt='0')
    return redirect(url_for('attendance.attendanceStatus'))

@attendance_bp.route('/attendanceAct_DeactStudent', methods=('GET', 'POST'))
def attendanceAct_DeactStudent():
    student_id = int(request.args.get('student_id'))
    act_deact = str(request.args.get('act_deact'))

    update_Act_DeactStudent(student_id, act_deact)
    return redirect(url_for('attendance.attendanceViewer'))
