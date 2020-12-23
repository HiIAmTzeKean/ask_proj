import datetime
from flask import (Blueprint, flash, g, make_response,
    redirect, render_template, request, session, url_for)
from flaskapp import db
from flaskapp.models import student, studentStatus, dojo
from flaskapp.attendance.form import formDojoSelection, formAdd_DelStudent, formEditStudent, formGradePerformance
from flaskapp.attendance.helpers import findTerm, str_to_date
from flaskapp.attendance.db_method import (get_dojoInfo, insert_attendancePresent,
    update_Act_DeactStudent, insert_newStudent, get_student, delete_student, update_student)
from sqlalchemy import and_, not_


attendance_bp = Blueprint('attendance', __name__,
                          template_folder='templates', static_folder='static')


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
    dojo_id = request.cookies.get('dojo_id')
    dojoName, dojoInstructor = get_dojoInfo(dojo_id)

    # find out who has been marked and who has not been marked
    marked_list = db.session.query(studentStatus, student).join(studentStatus, student.id==studentStatus.student_id).filter(
        studentStatus.dojo_id==dojo_id, studentStatus.date==datetime.date.today(), student.active==True).order_by(studentStatus.status.desc(), student.name.desc()).all()
    
    # get the id of those who are already marked
    # using that list of id, find out who has not been marked
    marked_ids = db.session.query(studentStatus.student_id).filter(
        studentStatus.dojo_id == dojo_id, studentStatus.date == datetime.date.today()).all()
    unmarked_list = db.session.query(student).filter(
        student.dojo_id==dojo_id, student.id.notin_(marked_ids), student.active==True).order_by(student.name.desc()).all()

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
    dojoName, dojoInstructor = get_dojoInfo(dojo_id)
    form = formAdd_DelStudent()
    if form.validate_on_submit():
        name = form.name.data
        belt = form.belt.data
        return redirect(url_for('attendance.attendanceAdd_DelStudent', name=name, dojo_id=dojo_id, belt=belt,add_del='add'))

    student_list = db.session.query(student).filter_by(dojo_id=dojo_id).order_by(
        student.active.desc(), student.belt.asc()).all()
    return render_template('attendance/attendanceViewer.html',
                           student_list=student_list, dojoName=dojoName, dojoInstructor=dojoInstructor, form=form)


@attendance_bp.route('/attendanceAdd_DelStudent/<string:add_del>', methods=('GET', 'POST'))
def attendanceAdd_DelStudent(add_del):
    if add_del == 'add':
        name = str(request.args.get('name'))
        lastGrading = None
        belt = str(request.args.get('belt'))
        dojo_id = int(request.args.get('dojo_id'))
        insert_newStudent(name, lastGrading, dojo_id, belt=belt)
    else:
        student_id = int(request.args.get('student_id'))
        delete_student(student_id)
    return redirect(url_for('attendance.attendanceViewer'))


@attendance_bp.route('/attendanceEditStudent/<student_id>', methods=('GET', 'POST'))
def attendanceEditStudent(student_id):
    student = get_student(student_id)
    form = formEditStudent(obj=student)
    dojo_list = dojo.query.all()
    form.dojo_id.choices = [(dojo.id, dojo.name) for dojo in dojo_list]

    if request.method == 'POST' and form.validate():
        form.populate_obj(student)
        db.session.commit()
        flash('Successfully updated!')
        return redirect(url_for('attendance.attendanceEditStudent', student_id=student_id))

    return render_template('attendance/attendanceEditStudent.html', student=student, form=form)


@attendance_bp.route('/attendanceAct_DeactStudent', methods=('GET', 'POST'))
def attendanceAct_DeactStudent():
    student_id = int(request.args.get('student_id'))
    act_deact = str(request.args.get('act_deact'))

    update_Act_DeactStudent(student_id, act_deact)
    return redirect(url_for('attendance.attendanceViewer'))
