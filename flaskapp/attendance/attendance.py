import datetime
import json
from sqlalchemy.exc import IntegrityError, DataError
from flask import (Blueprint, flash, g, make_response, redirect,
                   render_template, request, url_for)
from flaskapp import app, db
from flaskapp.attendance.db_method import (delete_studentEnrollmentRecord,
                                           insert_newEnrollment,
                                           insert_studentStausRecord,
                                           update_Act_DeactEnrollment,
                                           update_attendancePresent)
from flaskapp.attendance.form import (formAdd_DelStudent, formDojoSelection,
                                      formEditDojo, formEditStudent,
                                      formSearchStudent, formStartLesson,
                                      formAddTechniquesTaught)
from flaskapp.attendance.helpers import findTerm, str_to_date, catchList, lockList, drillsList
from flaskapp.auth.auth import dojo_required
from flask_security.decorators import login_required, roles_accepted
from flask_security.core import current_user
from flaskapp.models import (Dojo, Enrollment, Instructor, Lesson, Student,
                             StudentStatus, Belt)

attendance_bp = Blueprint('attendance', __name__,
                          template_folder='templates', static_folder='static')


@attendance_bp.route('/attendanceDojoSelect', methods=('GET', 'POST'))
@login_required
def attendanceDojoSelect():
    form = formDojoSelection()
    if current_user.has_role('Admin') or current_user.has_role('HQ'):
        dojo_list = db.session.query(Dojo.id, Dojo.name).all()
        form.dojo_id.choices = [(dojo.id, dojo.name) for dojo in dojo_list]
    else:
        dojo_list = db.session.query(Dojo.id, Dojo.name).filter_by(instructor_membership=current_user.student_membership).all()
        form.dojo_id.choices = [(dojo.id, dojo.name) for dojo in dojo_list]

    if form.validate_on_submit():  # remove and load cookies
        resp = make_response(redirect(url_for('attendance.attendanceStatus')))
        resp.set_cookie('dojo_id', str(form.dojo_id.data))
        return resp
    return render_template('attendance/attendanceDojoSelect.html',
                           dojo_list=dojo_list,
                           form=form)


@attendance_bp.route('/attendanceStatus', methods=('GET', 'POST'))
@roles_accepted('Admin', 'HQ', 'Instructor', 'Helper')
@dojo_required
def attendanceStatus():
    dojo_id = request.cookies.get('dojo_id')
    dojoRecord = db.session.query(Dojo.id, Dojo.name, Dojo.instructor_membership).filter_by(id=dojo_id).first()
    instructorRecord = db.session.query(Instructor.firstName).filter(Instructor.membership==dojoRecord.instructor_membership).first()

    # try get lesson record where dojo equal selection. sort asc.
    # if latest record completed is false, run below
    # if lesson has started, allow marking of attendance
    currentLesson = db.session.query(Lesson).filter_by(dojo_id=dojo_id).order_by(Lesson.id.desc()).first()
    if currentLesson is not None and currentLesson.completed == False:
        lessonRecord = currentLesson
        student_list = db.session.query(StudentStatus).filter_by(lesson_id=currentLesson.id).order_by(
            StudentStatus.status.desc(), StudentStatus.student_membership.desc()).all()

        ### second form
        techniquesTaught = formAddTechniquesTaught()
        return render_template('attendance/attendanceStatus.html', dojoRecord=dojoRecord,
                                instructorRecord=currentLesson.instructor,
                                student_list=student_list, lessonRecord=lessonRecord,
                                techniquesTaught=techniquesTaught,
                                catch_list=catchList(), lock_list=lockList())

    lessonRecord = Lesson(date=datetime.date.today(),
                          term=findTerm(datetime.date.today()),
                          dojo_id=dojoRecord.id,
                          instructor_membership=dojoRecord.instructor_membership)

    form = formStartLesson(obj=lessonRecord)  # Load default values
    instructor_list = db.session.query(Instructor.membership, Instructor.firstName).all()
    form.instructor_membership.choices = [(instructor.membership, instructor.firstName) for instructor in instructor_list]

    if form.validate_on_submit():
        form.populate_obj(lessonRecord)
        db.session.add(lessonRecord)
        db.session.commit()
        studentMembership_list = db.session.query(Enrollment.student_membership).\
                        filter_by(dojo_id=dojo_id, studentActive=True).all()  # create record for all students in that dojo
        for studentMembership in studentMembership_list:
            insert_studentStausRecord(status=False, student_membership=studentMembership[0], lesson_id=lessonRecord.id) # mark them all as absent
        return redirect(url_for('attendance.attendanceStatus'))

    return render_template('attendance/PreattendanceStatus.html',
                           dojoRecord=dojoRecord,instructorRecord=instructorRecord, form=form)


@attendance_bp.route('/attendanceStatusSummary', methods=('GET', 'POST'))
@roles_accepted('Admin', 'HQ', 'Instructor', 'Helper')
def attendanceStatusSummary():
    dojo_id = request.cookies.get('dojo_id')

    # appending techniques taught to db record
    form = formAddTechniquesTaught(request.form)
    technique_taught = {}
    for serialNum,technique in enumerate(form.techniqueList.data):
        technique_taught[serialNum] = '{} {}'.format(technique['catch'], technique['lock'])
    currentLesson = db.session.query(Lesson).filter_by(dojo_id=dojo_id).order_by(Lesson.id.desc()).first()
    currentLesson.completed = True
    currentLesson.techniquesTaught = technique_taught
    db.session.commit()

    # find out the attendance
    presentCount = db.session.query(StudentStatus.status).filter_by(
            lesson_id = currentLesson.id, status = True).count()
    absentCount = db.session.query(StudentStatus.status).filter_by(
            lesson_id = currentLesson.id, status = False).count()
    
    # Get display details
    dojoRecord = db.session.query(Dojo.name,Dojo.instructor_membership).filter_by(id=dojo_id).first()
    instructorRecord = db.session.query(Instructor.firstName).filter_by(membership=dojoRecord.instructor_membership).first()
    return render_template('attendance/attendanceStatusSummary.html', absentCount=absentCount,
                            presentCount=presentCount,
                            instructorRecord=instructorRecord,
                            technique_taught=technique_taught,
                            dojoRecord=dojoRecord)



@attendance_bp.route('/attendancePresent', methods=('GET', 'POST'))
@roles_accepted('Admin', 'HQ', 'Instructor', 'Helper')
def attendancePresent():  # Route to change studentStatus.status
    import ast
    status = ast.literal_eval(request.form['status'])
    student_membership = str(request.form['student_membership'])
    lesson_id = int(request.form['lesson_id'])
    update_attendancePresent(status, student_membership, lesson_id)
    studentstatus = db.session.query(StudentStatus).filter_by(lesson_id=lesson_id, student_membership=student_membership).first()
    lessonRecord = db.session.query(Lesson.id).filter_by(id=lesson_id).first()
    return render_template('attendance/section.html', studentstatus=studentstatus, lessonRecord=lessonRecord)


@attendance_bp.route('/attendanceLessonCancel', methods=('GET', 'POST'))
@roles_accepted('Admin', 'HQ', 'Instructor', 'Helper')
def attendanceLessonCancel():
    dojo_id = request.cookies.get('dojo_id')
    lessonRecord = db.session.query(Lesson).filter_by(dojo_id=dojo_id).order_by(Lesson.id.desc()).first()
    db.session.delete(lessonRecord)
    db.session.commit()
    return redirect(url_for('attendance.attendanceStatus'))
    
# ----------------------- Viewer Tab ----------------------------#


@attendance_bp.route('/attendanceViewer', methods=('GET', 'POST'))
@login_required
@dojo_required
def attendanceViewer():
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

    return render_template('attendance/attendanceViewer.html', student_list=student_list,
                           dojoRecord=dojoRecord, instructorRecord=instructorRecord,
                           lastLessonTechniques=lastLessonTechniques, missingBirthday=missingBirthday,
                           form=form)


@attendance_bp.route('/attendanceAdd_DelStudent/<string:add_del>', methods=('GET', 'POST'))
@roles_accepted('Admin', 'HQ', 'Instructor', 'Helper')
def attendanceAdd_DelStudent(add_del):
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
            return redirect(url_for('attendance.attendanceViewer'))
    elif add_del == 'addExisting':
        student_membership = str(request.args.get('student_membership'))
        dojo_id = int(request.args.get('dojo_id'))
        insert_newEnrollment(student_membership, dojo_id)
    return redirect(url_for('attendance.attendanceViewer'))


@attendance_bp.route('/attendanceRemoveStudent/<string:student_membership>/<int:dojo_id>', methods=('GET', 'POST'))
@roles_accepted('Admin', 'HQ', 'Instructor', 'Helper')
def attendanceRemoveStudent(student_membership,dojo_id):
    # remove relation student to enrollment
    delete_studentEnrollmentRecord(student_membership, dojo_id)
    return redirect(url_for('attendance.attendanceViewer'))


@attendance_bp.route('/attendanceSearchStudent', methods=('GET', 'POST'))
def attendanceSearchStudent():
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
        return redirect(url_for('attendance.attendanceSearchStudent',searchStudent='True', serachString=serachString, serachBelt=serachBelt))
    return render_template('attendance/attendanceSearchStudent.html',student_list=student_list, form=form)


# todo error handler for not unique membership
@attendance_bp.route('/attendanceEditStudent/<string:student_membership>', methods=('GET', 'POST'))
@roles_accepted('Admin', 'HQ', 'Instructor', 'Helper')
def attendanceEditStudent(student_membership): 
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
            return redirect(url_for('attendance.attendanceEditStudent', student_membership=form.membership.data))
        if form.dateOfBirth_month.data and form.dateOfBirth_year.data:
            date_str = '01{}{}'.format(form.dateOfBirth_month.data.zfill(2),form.dateOfBirth_year.data)
            studentRecord.dateOfBirth = datetime.datetime.strptime(date_str, '%d%m%Y').date()
        db.session.commit()
        flash('Successfully updated {}!'.format(studentRecord.firstName))
        # return back same view page
        return redirect(url_for('attendance.attendanceEditStudent', student_membership=form.membership.data))  

    return render_template('attendance/attendanceEditStudent.html', studentRecord=studentRecord,
                            enrollementRecord=enrollementRecord, form=form)


@attendance_bp.route('/attendanceEditDojo/<int:dojoID>', methods=('GET', 'POST'))
@roles_accepted('Admin', 'HQ', 'Instructor')
def attendanceEditDojo(dojoID): # edit dojo particulars
    dojoRecord = db.session.query(Dojo).filter(Dojo.id==dojoID).first()
    form = formEditDojo(obj=dojoRecord)
    instructor_list = db.session.query(Instructor.membership, Instructor.firstName).all()
    form.instructor_membership.choices = [(instructor.membership, instructor.firstName) for instructor in instructor_list]

    if form.validate_on_submit():
        form.populate_obj(dojoRecord)
        db.session.commit()
        flash('Successfully updated!')
        return redirect(url_for('attendance.attendanceEditDojo', dojoID=dojoID))

    return render_template('attendance/attendanceEditDojo.html', dojoRecord=dojoRecord, form=form)


@attendance_bp.route('/attendanceAct_DeactEnrollment', methods=('GET', 'POST'))
@roles_accepted('Admin', 'HQ', 'Instructor', 'Helper')
def attendanceAct_DeactEnrollment():
    student_membership = str(request.args.get('student_membership'))
    dojo_id = int(request.args.get('dojo_id'))
    act_deact = str(request.args.get('act_deact'))

    update_Act_DeactEnrollment(student_membership, dojo_id, act_deact)
    return redirect(url_for('attendance.attendanceViewer'))


# todo view past lesson
# todo delete past lesson
@attendance_bp.route('/attendancePastLessonViewer', methods=('GET', 'POST'))
def attendancePastLessonViewer():
    return redirect(url_for('attendance.attendanceViewer'))
