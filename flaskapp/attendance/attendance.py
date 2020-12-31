import datetime
from flask import (Blueprint, flash, g, make_response,
    redirect, render_template, request, session, url_for)
from flaskapp import db
from flaskapp.models import student, studentStatus, dojo, lesson, instructor, enrollment
from flaskapp.attendance.form import formDojoSelection, formAdd_DelStudent, formEditStudent, formStartLesson, formEditDojo, formSearchStudent
from flaskapp.attendance.helpers import findTerm, str_to_date
from flaskapp.attendance.db_method import (insert_studentStausRecord, update_attendancePresent, insert_newEnrollment,
    update_Act_DeactEnrollment, insert_newStudent, get_studentRecord, delete_studentEnrollmentRecord, update_student, get_dojoInstructorId)
from sqlalchemy import and_, not_


attendance_bp = Blueprint('attendance', __name__,
                          template_folder='templates', static_folder='static')


@attendance_bp.route('/attendanceDojoSelect', methods=('GET', 'POST'))
def attendanceDojoSelect():
    form = formDojoSelection()
    dojo_list = dojo.query.all()
    form.dojo_id.choices = [(dojo.id, dojo.name) for dojo in dojo_list]
    if form.validate_on_submit(): # remove and load cookies
        dojo_id = form.dojo_id.data
        resp = make_response(redirect(url_for('attendance.attendanceStatus')))
        resp.set_cookie('dojo_id', str(dojo_id))
        resp.set_cookie('lessonStart', 'False')
        resp.set_cookie('lesson_id', str(0))
        return resp
    return render_template('attendance/attendanceDojoSelect.html', dojo_list=dojo_list, form=form)

#todo utilise dojo table to extract needed data
@attendance_bp.route('/attendanceStatus', methods=('GET', 'POST'))
def attendanceStatus():
    dojo_id = request.cookies.get('dojo_id')
    dojoName = db.session.query(dojo.name).filter_by(id=dojo_id).scalar()
    if request.cookies.get('lessonStart')=='True': # if lesson has started, allow marking of attendance
        lesson_id = int(request.cookies.get('lesson_id')) # get all studentStatus record using lesson_id
        lessonRecord = db.session.query(lesson).filter_by(id=lesson_id).first()
        dojoInstructor = db.session.query(instructor.name).filter_by(id=lessonRecord.instructor_id).scalar()
        student_list = db.session.query(studentStatus).filter(studentStatus.lesson_id == lesson_id).order_by(studentStatus.status.desc(), studentStatus.student_id.desc()).all()
        return render_template('attendance/attendanceStatus.html', dojoName=dojoName, dojoInstructor=dojoInstructor, lessonDate=lessonRecord.date, student_list=student_list)

    # elif lesson not started, return form to submit lesson details
    # init lesson record which the form will fill up
    lessonRecord = lesson(date=datetime.date.today(),term=findTerm(datetime.date.today()),dojo_id=dojo_id,instructor_id=get_dojoInstructorId(dojo_id))
    form = formStartLesson(obj=lessonRecord, instructor_id=get_dojoInstructorId(dojo_id))
    instructor_list = instructor.query.all()
    form.instructor_id.choices = [(instructor.id, instructor.name) for instructor in instructor_list]
    
    if form.validate_on_submit(): # once form is submitted, return cookie to save lessonStart and lessonID
        form.populate_obj(lessonRecord)
        db.session.add(lessonRecord)
        db.session.commit()
        activeStudent_list = db.session.query(enrollemnt.student_id).filter(enrollemnt.studentActive==True).all()
        studentId_list = db.session.query(enrollment.student_id).filter(enrollment.dojo_id == dojo_id,
                            enrollment.student_id.in_(activeStudent_list)).all()  # create record for all students in that dojo
        for studentId in studentId_list:
            insert_studentStausRecord(status=False,student_id=studentId[0],lesson_id=lessonRecord.id) # mark them all as absent
        resp = make_response(redirect(url_for('attendance.attendanceStatus')))
        resp.set_cookie('lessonStart', 'True')
        resp.set_cookie('lesson_id', str(lessonRecord.id))
        return resp
    return render_template('attendance/attendanceStatus.html', dojoName=dojoName, lessonStart='False', form=form)


@attendance_bp.route('/attendancePresent', methods=('GET', 'POST'))
def attendancePresent(): # Route to change studentStatus.status
    import ast
    status = ast.literal_eval(request.args.get('present'))
    student_id = int(request.args.get('student_id'))
    lesson_id = int(request.args.get('lesson_id'))
    update_attendancePresent(status,student_id, lesson_id)
    return redirect(url_for('attendance.attendanceStatus'))

#todo consider the case that student is already existing and must be found from database when being added
@attendance_bp.route('/attendanceViewer', methods=('GET', 'POST'))
def attendanceViewer():
    dojo_id = request.cookies.get('dojo_id')
    dojoRecord = db.session.query(dojo).filter(dojo.id==dojo_id).first()
    form = formAdd_DelStudent()
    dojo_list = dojo.query.all()
    form.dojo_id.choices = [(dojo.id, dojo.name) for dojo in dojo_list]
    
    if form.validate_on_submit(): # Add new user into database
        name = form.name.data
        belt = form.belt.data
        return redirect(url_for('attendance.attendanceAdd_DelStudent', name=name, dojo_id=dojo_id, belt=belt,add_del='add'))

    studentId_list = db.session.query(enrollment.student_id).filter(enrollment.dojo_id==dojo_id).all()
    student_list = db.session.query(student).filter(student.id.in_(studentId_list)).order_by(student.belt.asc()).all()
    return render_template('attendance/attendanceViewer.html', student_list=student_list, dojoRecord=dojoRecord, form=form)

#todo only super user can delete student record
@attendance_bp.route('/attendanceAdd_DelStudent/<string:add_del>', methods=('GET', 'POST'))
def attendanceAdd_DelStudent(add_del):
    if add_del == 'add':
        name = str(request.args.get('name'))
        lastGrading = None
        belt = str(request.args.get('belt'))
        dojo_id = int(request.args.get('dojo_id'))
        record = student(name, lastGrading, dojo_id, active=True, belt=belt)
        db.session.add(record)
        db.session.commit()
        insert_newEnrollment(record.id, dojo_id)
    elif add_del == 'del':
        student_id = int(request.args.get('student_id'))
        dojo_id = int(request.args.get('dojo_id'))
        delete_studentEnrollmentRecord(student_id, dojo_id)
    elif add_del == 'addExisting':
        student_id = int(request.args.get('student_id'))
        dojo_id = int(request.args.get('dojo_id'))
        insert_newEnrollment(student_id, dojo_id)
    return redirect(url_for('attendance.attendanceViewer'))

#todo allow for search by belt
@attendance_bp.route('/attendanceSearchStudent', methods=('GET', 'POST'))
def attendanceSearchStudent():
    form = formSearchStudent()
    if request.args.get('searchStudent')=='True':
        serachString = request.args.get('serachString')
        student_list = db.session.query(student).filter(student.name.ilike('%{}%'.format(serachString))).all() # case insensitive
    else:
        student_list = db.session.query(student).all()
    if form.validate_on_submit():
        serachString = form.name.data
        return redirect(url_for('attendance.attendanceSearchStudent',searchStudent='True', serachString=serachString))
    return render_template('attendance/attendanceSearchStudent.html',student_list=student_list, form=form)


@attendance_bp.route('/attendanceEditStudent/<student_id>', methods=('GET', 'POST'))
def attendanceEditStudent(student_id):
    studentRecord = get_studentRecord(student_id)
    enrollementRecord = db.session.query(enrollment).filter_by(student_id=student_id).first() # extract dojo student is currently from
    form = formEditStudent(obj=studentRecord, dojo_id=enrollementRecord.dojo_id) # load values into form
    dojo_list = dojo.query.all()
    form.dojo_id.choices = [(dojo.id, dojo.name) for dojo in dojo_list] # load in other choices into select field

    if form.validate_on_submit(): # update record in database if valid
        form.populate_obj(studentRecord)
        if enrollementRecord.dojo_id!=form.dojo_id.data: # update enrollment record
            enrollementRecord.dojo_id = form.dojo_id.data
        db.session.commit()
        flash('Successfully updated!')
    
        return redirect(url_for('attendance.attendanceEditStudent', student_id=student_id)) # return back same view page
    return render_template('attendance/attendanceEditStudent.html', studentRecord=studentRecord, enrollementRecord=enrollementRecord,form=form)


@attendance_bp.route('/attendanceEditDojo/<dojo_id>', methods=('GET', 'POST'))
def attendanceEditDojo(dojo_id): #edit dojo particulars
    dojoRecord = db.session.query(dojo).filter(dojo.id==dojo_id).first()
    form = formEditDojo(obj=dojoRecord)
    instructor_list = instructor.query.all()
    form.instructor_id.choices = [(instructor.id, instructor.name) for instructor in instructor_list]
    if form.validate_on_submit():
        form.populate_obj(dojoRecord)
        db.session.commit()
        flash('Successfully updated!')
        return redirect(url_for('attendance.attendanceEditDojo', dojo_id=dojo_id))
    return render_template('attendance/attendanceEditDojo.html', dojoRecord=dojoRecord, form=form)


@attendance_bp.route('/attendanceAct_DeactEnrollment', methods=('GET', 'POST'))
def attendanceAct_DeactEnrollment():
    student_id = int(request.args.get('student_id'))
    dojo_id = int(request.args.get('dojo_id'))
    act_deact = str(request.args.get('act_deact'))

    update_Act_DeactEnrollment(student_id, dojo_id, act_deact)
    return redirect(url_for('attendance.attendanceViewer'))
