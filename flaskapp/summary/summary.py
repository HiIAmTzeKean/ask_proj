import datetime
from sqlalchemy.exc import IntegrityError, DataError
from flask import (Blueprint, flash, g, make_response, redirect,
                   render_template, request, url_for, send_from_directory)
from flaskapp import app, db
from flaskapp.attendance.db_method import (delete_studentEnrollmentRecord,
                                           insert_newEnrollment,
                                           insert_studentStausRecord,
                                           update_Act_DeactEnrollment,
                                           update_attendancePresent)
from flaskapp.attendance.form import (formAdd_DelStudent,formEditStudent,
                                      formSearchStudent)
from flaskapp.auth.auth import dojo_required
from flask_security.decorators import login_required, roles_accepted
from flask_security.core import current_user
from flaskapp.models import (Dojo, Enrollment, Instructor, Lesson, Student,
                             StudentStatus, Belt)

summary_bp = Blueprint('summary', __name__,
                          template_folder='templates', static_folder='static')

@summary_bp.route('/summary', methods=('GET', 'POST'))
@login_required
@dojo_required
def summary():
    dojo_id = request.cookies.get('dojo_id')
    dojoRecord = db.session.query(Dojo.id, Dojo.instructor_membership, Dojo.name).filter(Dojo.id==dojo_id).first()
    instructorRecord = db.session.query(Instructor.firstName).filter(Instructor.membership==dojoRecord.instructor_membership).first()

    form = formAdd_DelStudent(dojo_id=int(dojo_id), belt_id=int(1))
    form.dojo_id.choices = [(dojoRecord.id, dojoRecord.name)]
    belt_list = db.session.query(Belt.id, Belt.beltName).all()
    form.belt_id.choices = [(belt.id, belt.beltName) for belt in belt_list]

    # get list of student to display
    student_list = db.session.query(Student.membership,
                                    Student.firstName,
                                    Student.lastGrading,
                                    Student.dateOfBirth,
                                    Belt.beltName,
                                    Belt.beltColor,
                                    Enrollment.studentActive)\
            .filter(Student.belt_id == Belt.id)\
            .filter(Enrollment.dojo_id==dojo_id, Enrollment.student_membership == Student.membership)\
            .order_by(Enrollment.studentActive.desc(),Student.id.asc(),).all()
    
    # get last lesson's detail
    try:
        lastLessonTechniques = db.session.query(Lesson.techniquesTaught).\
            filter_by(dojo_id=dojo_id).order_by(Lesson.date.desc(), Lesson.id.desc()).first()[0]
    except:
        lastLessonTechniques={}

    # ---- get number of student with null membership
    missingBirthday = []
    for studentRecord in student_list:
        if not studentRecord.dateOfBirth:
            missingBirthday.append([studentRecord.membership, studentRecord.firstName])

    return render_template('summary/summaryViewer.html', student_list=student_list,
                           dojoRecord=dojoRecord, instructorRecord=instructorRecord,
                           lastLessonTechniques=lastLessonTechniques, missingBirthday=missingBirthday,
                           form=form)


@summary_bp.route('/summaryReport', methods=('GET', 'POST'))
@roles_accepted('Admin', 'HQ', 'Instructor', 'Helper')
def summaryReport():
    import pandas as pd
    import pathlib
    import os
    dojo_id = request.cookies.get('dojo_id')
    dojoRecord = db.session.query(Dojo.id, Dojo.instructor_membership, Dojo.name).filter(Dojo.id==dojo_id).first()
    student_list = db.session.query(Student.membership,
                                    Student.firstName,
                                    Student.lastGrading,
                                    Student.dateOfBirth,
                                    Belt.beltName,
                                    Enrollment.studentActive)\
            .filter(Student.belt_id == Belt.id)\
            .filter(Enrollment.dojo_id==dojo_id, Enrollment.student_membership == Student.membership)\
            .order_by(Enrollment.studentActive.desc(),Student.id.asc(),).all()
    df = pd.DataFrame (student_list, columns=['Membership','FirstName','LastGrading','DOB','Belt','Enrollment'])
    print(pathlib.Path().absolute())
    print(os.path.join(pathlib.Path().absolute(), app.config['CLIENT_REPORT'], "output.csv"))
    
    df.to_csv(os.path.join(pathlib.Path().absolute(), app.config['CLIENT_REPORT'], "output.csv"), index=False)

    return send_from_directory(os.path.join(pathlib.Path().absolute(), app.config['CLIENT_REPORT']), filename="output.csv", as_attachment=True)


@summary_bp.route('/summaryAdd_DelStudent/<string:add_del>', methods=('GET', 'POST'))
@roles_accepted('Admin', 'HQ', 'Instructor', 'Helper')
def summaryAdd_DelStudent(add_del):
    if add_del == 'addNew':
        form = formAdd_DelStudent(request.form)
        try:
            if request.args.get('redirectInstructor') == 'True':
                record = Instructor(None,None,None)
                form.populate_obj(record)
                if form.dateOfBirth_month.data and form.dateOfBirth_year.data:
                    date_str = '01{}{}'.format(form.dateOfBirth_month.data.zfill(2),form.dateOfBirth_year.data)
                    record.dateOfBirth = datetime.datetime.strptime(date_str, '%d%m%Y').date()
                db.session.add(record)
                db.session.commit()
                return redirect(url_for('instructor.instructorViewer'))

            record = Student(None,None,None)
            form.populate_obj(record)
            if form.dateOfBirth_month.data and form.dateOfBirth_year.data:
                date_str = '01{}{}'.format(form.dateOfBirth_month.data.zfill(2),form.dateOfBirth_year.data)
                record.dateOfBirth = datetime.datetime.strptime(date_str, '%d%m%Y').date()
            db.session.add(record)
            db.session.commit()
            
            if record.dojo_id:
                insert_newEnrollment(record.membership, form.dojo_id.data)
        except IntegrityError as e:
            app.logger.info(str(e))
            flash('Error: membership already exist!!')
            return redirect(url_for('summary.summary'))
    elif add_del == 'addExisting':
        student_membership = str(request.args.get('student_membership'))
        dojo_id = int(request.args.get('dojo_id'))
        insert_newEnrollment(student_membership, dojo_id)
    return redirect(url_for('summary.summary'))


@summary_bp.route('/summaryRemoveStudent/<string:student_membership>/<int:dojo_id>', methods=('GET', 'POST'))
@roles_accepted('Admin', 'HQ', 'Instructor', 'Helper')
def summaryRemoveStudent(student_membership,dojo_id):
    # remove relation student to enrollment
    delete_studentEnrollmentRecord(student_membership, dojo_id)
    return redirect(url_for('summary.summary'))


@summary_bp.route('/summarySearchStudent', methods=('GET', 'POST'))
def summarySearchStudent():
    form = formSearchStudent()
    dojo_id = request.cookies.get('dojo_id')
    if request.args.get('searchStudent')=='True':
        serachString = request.args.get('serachString')
        serachBelt = request.args.get('serachBelt')
        if serachBelt == "":
            student_list = db.session.query(Student).\
                filter(Student.firstName.ilike('%{}%'.format(serachString))).all()
        else:
            student_list = db.session.query(Student).\
                filter(Student.firstName.ilike('%{}%'.format(serachString)), Student.belt.ilike(serachBelt)).all()
    
    else:
        notAvail_studentList = db.session.query(Enrollment.student_membership).filter(Enrollment.dojo_id == dojo_id).all()
        student_list = db.session.query(Student.id,
                                    Student.membership,
                                    Student.firstName,
                                    Student.lastName,
                                    Student.lastGrading,
                                    Belt.beltName).\
            filter(Student.belt_id == Belt.id, Student.membership.notin_(notAvail_studentList)).all()

    if form.validate_on_submit():
        serachString = form.name.data
        serachBelt = form.belt.data
        return redirect(url_for('summary.summarySearchStudent',searchStudent='True', serachString=serachString, serachBelt=serachBelt))
    return render_template('summary/summarySearchStudent.html',student_list=student_list, form=form)


# todo error handler for not unique membership
@summary_bp.route('/summaryEditStudent/<string:student_membership>', methods=('GET', 'POST'))
@roles_accepted('Admin', 'HQ', 'Instructor', 'Helper')
def summaryEditStudent(student_membership): 
    studentRecord = db.session.query(Student).filter_by(membership=student_membership).first()
    enrollementRecord = db.session.query(Enrollment.dojo_id).\
                        filter_by(student_membership=student_membership).first()  # extract dojo student is currently from
    if studentRecord.dateOfBirth:
        form = formEditStudent(obj=studentRecord,
                           dateOfBirth_month=int(studentRecord.dateOfBirth.month),
                           dateOfBirth_year=int(studentRecord.dateOfBirth.year))  # load values into form
    else:
        form = formEditStudent(obj=studentRecord)  # load values into form
    belt_list = db.session.query(Belt.id, Belt.beltName).all()
    form.belt_id.choices = [(belt.id, belt.beltName) for belt in belt_list]

    # update record
    if form.validate_on_submit():
        try:
            form.populate_obj(studentRecord)
            db.session.commit()
        except IntegrityError as e:
            flash('Error: membership already exist!!')
            return redirect(url_for('summary.summaryEditStudent', student_membership=form.membership.data))
        if form.dateOfBirth_month.data and form.dateOfBirth_year.data:
            date_str = '01{}{}'.format(form.dateOfBirth_month.data.zfill(2),form.dateOfBirth_year.data)
            studentRecord.dateOfBirth = datetime.datetime.strptime(date_str, '%d%m%Y').date()
        db.session.commit()
        flash('Successfully updated {}!'.format(studentRecord.firstName))
        # return back same view page
        return redirect(url_for('summary.summaryEditStudent', student_membership=form.membership.data))  

    return render_template('summary/summaryEditStudent.html', studentRecord=studentRecord,
                            enrollementRecord=enrollementRecord, form=form)


@summary_bp.route('/summaryAct_DeactEnrollment', methods=('GET', 'POST'))
@roles_accepted('Admin', 'HQ', 'Instructor', 'Helper')
def summaryAct_DeactEnrollment():
    student_membership = str(request.args.get('student_membership'))
    dojo_id = int(request.args.get('dojo_id'))
    act_deact = str(request.args.get('act_deact'))

    update_Act_DeactEnrollment(student_membership, dojo_id, act_deact)
    return redirect(url_for('summary.summary'))


# todo view past lesson
# todo delete past lesson
@summary_bp.route('/summaryPastLessonViewer', methods=('GET', 'POST'))
def summaryPastLessonViewer():
    return redirect(url_for('summary.summary'))
