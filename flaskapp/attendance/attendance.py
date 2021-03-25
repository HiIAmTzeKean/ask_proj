import datetime
import json
from sqlalchemy.exc import IntegrityError
from flask import (Blueprint, flash, g, make_response, redirect,
                   render_template, request, session, url_for)
from flaskapp import db
from flaskapp.attendance.db_method import (delete_studentEnrollmentRecord,
                                           get_studentRecord,
                                           insert_newEnrollment,
                                           insert_newStudent,
                                           insert_studentStausRecord,
                                           update_Act_DeactEnrollment,
                                           update_attendancePresent)
from flaskapp.attendance.form import (formAdd_DelStudent, formDojoSelection,
                                      formEditDojo, formEditStudent,
                                      formSearchStudent, formStartLesson, formAddTechniquesTaught)
from flaskapp.attendance.helpers import findTerm, str_to_date, catchList, lockList, drillsList
from flaskapp.auth.auth import dojo_required
from flaskapp.models import (Dojo, enrollment, instructor, lesson, student,
                             studentStatus,belts)

attendance_bp = Blueprint('attendance', __name__,
                          template_folder='templates', static_folder='static')


@attendance_bp.route('/attendanceDojoSelect', methods=('GET', 'POST'))
def attendanceDojoSelect():
    form = formDojoSelection()
    dojo_list = db.session.query(Dojo.id, Dojo.name).all()
    form.dojo_id.choices = [(dojo.id, dojo.name) for dojo in dojo_list]
    if form.validate_on_submit():  # remove and load cookies
        dojo_id = form.dojo_id.data
        resp = make_response(redirect(url_for('attendance.attendanceStatus')))
        resp.set_cookie('dojo_id', str(dojo_id))
        resp.set_cookie('lessonStart', 'False')
        resp.set_cookie('lesson_id', str(0))
        return resp
    return render_template('attendance/attendanceDojoSelect.html',
                           dojo_list=dojo_list,
                           form=form)


@attendance_bp.route('/attendanceStatus', methods=('GET', 'POST'))
@dojo_required
def attendanceStatus():
    dojo_id = request.cookies.get('dojo_id')
    dojoRecord = db.session.query(Dojo.id, Dojo.name, Dojo.instructor_id).filter_by(id=dojo_id).first()

    # try get lesson record where dojo equal selection. sort asc.
    # if latest record completed is false, run below
    # if lesson has started, allow marking of attendance
    currentLesson = db.session.query(lesson).filter_by(dojo_id=dojo_id).order_by(lesson.id.desc()).first()
    if currentLesson is not None and currentLesson.completed == False:
        lessonRecord = currentLesson
        student_list = db.session.query(studentStatus).filter(studentStatus.lesson_id == currentLesson.id).order_by(
            studentStatus.status.desc(), studentStatus.student_id.desc()).all()

        ### second form
        techniquesTaught = formAddTechniquesTaught()
        return render_template('attendance/attendanceStatus.html', dojoRecord=dojoRecord,
            instructorRecord=currentLesson.instructor,
            student_list=student_list, lessonRecord=lessonRecord, techniquesTaught=techniquesTaught,
            catch_list=catchList(), lock_list=lockList())

    lessonRecord = lesson(date=datetime.date.today(),
                          term=findTerm(datetime.date.today()),
                          dojo_id=dojoRecord.id,
                          instructor_id=dojoRecord.instructor_id
                          )
    form = formStartLesson(obj=lessonRecord)  # Load default values
    instructor_list = db.session.query(instructor.id, instructor.firstName).all()
    form.instructor_id.choices = [(instructor.id, instructor.firstName) for instructor in instructor_list]

    if form.validate_on_submit():
        form.populate_obj(lessonRecord)
        db.session.add(lessonRecord)
        db.session.commit()
        studentId_list = db.session.query(enrollment.student_id).\
                        filter(enrollment.dojo_id == dojo_id, enrollment.studentActive==True).all()  # create record for all students in that dojo
        for studentId in studentId_list:
            insert_studentStausRecord(status=False,student_id=studentId[0],lesson_id=lessonRecord.id) # mark them all as absent
        return redirect(url_for('attendance.attendanceStatus'))

    return render_template('attendance/PreattendanceStatus.html',
                           dojoRecord=dojoRecord, form=form)


@attendance_bp.route('/attendanceStatusSummary', methods=('GET', 'POST'))
def attendanceStatusSummary():
    dojo_id = request.cookies.get('dojo_id')
    # appending techniques taught to db record
    form = formAddTechniquesTaught(request.form)
    technique_taught = {}
    for serialNum,technique in enumerate(form.techniqueList.data):
        technique_taught[serialNum] = '{} {}'.format(technique['catch'], technique['lock'])
    currentLesson = db.session.query(lesson).filter_by(dojo_id=dojo_id).order_by(lesson.id.desc()).first()
    currentLesson.completed = True
    currentLesson.techniquesTaught = json.dumps(technique_taught)
    db.session.commit()

    present_list = db.session.query(studentStatus.status).filter(
            studentStatus.lesson_id == currentLesson.id, studentStatus.status == True).all()
    absent_list = db.session.query(studentStatus.status).filter(
            studentStatus.lesson_id == currentLesson.id, studentStatus.status == False).all()
    
    resp = make_response(render_template('attendance/attendanceStatusSummary.html', absentCount=len(absent_list),
            presentCount=len(present_list), instructorName=currentLesson.instructor.firstName, dojoName=currentLesson.dojo.name))
    return resp


@attendance_bp.route('/attendancePresent', methods=('GET', 'POST'))
def attendancePresent():  # Route to change studentStatus.status
    import ast
    status = ast.literal_eval(request.form['status'])
    student_id = int(request.form['student_id'])
    lesson_id = int(request.form['lesson_id'])
    update_attendancePresent(status, student_id, lesson_id)
    studentstatus = db.session.query(studentStatus).filter(studentStatus.lesson_id == lesson_id, studentStatus.student_id == student_id).first()
    lessonRecord = db.session.query(lesson.id).filter_by(id=lesson_id).first()
    return render_template('attendance/section.html', studentstatus=studentstatus, lessonRecord=lessonRecord)


@attendance_bp.route('/attendanceLessonCancel', methods=('GET', 'POST'))
def attendanceLessonCancel():
    dojo_id = request.cookies.get('dojo_id')
    lessonRecord = db.session.query(lesson).filter_by(dojo_id=dojo_id).order_by(lesson.id.desc()).first()
    db.session.delete(lessonRecord)
    db.session.commit()
    return redirect(url_for('attendance.attendanceStatus'))
    
# ----------------------- Viewer Tab ----------------------------#


@attendance_bp.route('/attendanceViewer', methods=('GET', 'POST'))
@dojo_required
def attendanceViewer():
    dojo_id = request.cookies.get('dojo_id')
    dojoRecord = db.session.query(Dojo).filter(Dojo.id==dojo_id).first()

    form = formAdd_DelStudent(dojo_id=int(dojo_id),belt_id=int(1))
    form.dojo_id.choices = [(dojoRecord.id, dojoRecord.name)]
    belt_list = db.session.query(belts.id, belts.beltName).all()
    form.belt_id.choices = [(belt.id, belt.beltName) for belt in belt_list]

    # get list of student to display
    student_list = db.session.query(student.id,
                                    student.membership,
                                    student.firstName,
                                    student.lastGrading,
                                    belts.beltName,
                                    enrollment.studentActive)\
            .filter(student.belt_id == belts.id)\
            .filter(enrollment.dojo_id==dojo_id, enrollment.student_id == student.id)\
            .order_by(enrollment.studentActive.desc(),student.id.asc(),).all()
    
    # get last lesson's detail
    try:
        lastLessonTechniques_json = db.session.query(lesson.techniquesTaught).filter(lesson.dojo_id==dojo_id).order_by(lesson.date.desc(),lesson.id.desc()).first()[0]
        lastLessonTechniques = json.loads(lastLessonTechniques_json)
    except:
        lastLessonTechniques={}

    # ---- get number of student with null membership
    missingMembership_list = []
    for studentRecord in student_list:
        if studentRecord.membership:
            continue
        missingMembership_list.append([studentRecord.id, studentRecord.firstName])

    return render_template('attendance/attendanceViewer.html', student_list=student_list,
                           dojoRecord=dojoRecord, instructorRecord=dojoRecord.instructor,
                           lastLessonTechniques=lastLessonTechniques, missingMembership_list=missingMembership_list,
                           form=form)


@attendance_bp.route('/attendanceAdd_DelStudent/<string:add_del>', methods=('GET', 'POST'))
def attendanceAdd_DelStudent(add_del):
    if add_del == 'addNew':
        form = formAdd_DelStudent(request.form)
        record = student(None,None,None)
        form.populate_obj(record)
        db.session.add(record)
        db.session.commit()

        # Add student record to enrollemnt per dojo_id
        insert_newEnrollment(record.id, record.dojo_id)
    elif add_del == 'addExisting':
        student_id = int(request.args.get('student_id'))
        dojo_id = int(request.args.get('dojo_id'))
        insert_newEnrollment(student_id, dojo_id)
    return redirect(url_for('attendance.attendanceViewer'))


@attendance_bp.route('/attendanceRemoveStudent/<int:student_id>/<int:dojo_id>', methods=('GET', 'POST'))
def attendanceRemoveStudent(student_id,dojo_id):
    # remove relation student to enrollment
    delete_studentEnrollmentRecord(student_id, dojo_id)
    return redirect(url_for('attendance.attendanceViewer'))


@attendance_bp.route('/attendanceSearchStudent', methods=('GET', 'POST'))
def attendanceSearchStudent():
    form = formSearchStudent()
    dojo_id = request.cookies.get('dojo_id')
    if request.args.get('searchStudent')=='True':
        serachString = request.args.get('serachString')
        serachBelt = request.args.get('serachBelt')
        if serachBelt == "":
            student_list = db.session.query(student).\
                filter(student.firstName.ilike('%{}%'.format(serachString))).all()
        else:
            student_list = db.session.query(student).\
                filter(student.firstName.ilike('%{}%'.format(serachString)), student.belt.ilike(serachBelt)).all()
    
    else:
        notAvail_studentList = db.session.query(enrollment.student_id).filter(enrollment.dojo_id == dojo_id).all()
        student_list = db.session.query(student.id,
                                    student.firstName,
                                    student.lastName,
                                    student.lastGrading,
                                    belts.beltName).\
            filter(student.belt_id == belts.id, student.id.notin_(notAvail_studentList)).all()

    if form.validate_on_submit():
        serachString = form.name.data
        serachBelt = form.belt.data
        return redirect(url_for('attendance.attendanceSearchStudent',searchStudent='True', serachString=serachString, serachBelt=serachBelt))
    return render_template('attendance/attendanceSearchStudent.html',student_list=student_list, form=form)

# todo error handler for not unique membership
@attendance_bp.route('/attendanceEditStudent/<int:student_id>', methods=('GET', 'POST'))
def attendanceEditStudent(student_id): 
    studentRecord = get_studentRecord(student_id)
    enrollementRecord = db.session.query(enrollment.dojo_id).filter_by(student_id=student_id).first()  # extract dojo student is currently from
    if studentRecord.dateOfBirth:
        form = formEditStudent(obj=studentRecord,
                           dateOfBirth_month=int(studentRecord.dateOfBirth.month),
                           dateOfBirth_year=int(studentRecord.dateOfBirth.year))  # load values into form
    else:
        form = formEditStudent(obj=studentRecord)  # load values into form
    belt_list = db.session.query(belts.id, belts.beltName).all()
    form.belt_id.choices = [(belt.id, belt.beltName) for belt in belt_list]

    # update record
    if form.validate_on_submit():
        try:
            form.populate_obj(studentRecord)
            db.session.commit()
        except IntegrityError as ex:
            flash('Error: membership already exist!!')
            return redirect(url_for('attendance.attendanceEditStudent', student_id=student_id))

        date_str = '01{}{}'.format(form.dateOfBirth_month.data.zfill(2),form.dateOfBirth_year.data)
        studentRecord.dateOfBirth = datetime.datetime.strptime(date_str, '%d%m%Y').date()
        db.session.commit()
        flash('Successfully updated {}!'.format(studentRecord.firstName))
        # return back same view page
        return redirect(url_for('attendance.attendanceEditStudent', student_id=student_id))  

    return render_template('attendance/attendanceEditStudent.html', studentRecord=studentRecord,
                            enrollementRecord=enrollementRecord, form=form)


@attendance_bp.route('/attendanceEditDojo/<int:dojo_id>', methods=('GET', 'POST'))
def attendanceEditDojo(dojo_id): # edit dojo particulars
    dojoRecord = db.session.query(Dojo).filter(Dojo.id==dojo_id).first()
    form = formEditDojo(obj=dojoRecord)
    instructor_list = instructor.query.all()
    form.instructor_id.choices = [(instructor.id, instructor.firstName) for instructor in instructor_list]

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

## migrate belt over
# @attendance_bp.route('/migrate', methods=('GET', 'POST'))
# def attendancemigrate():
#     records = db.session.query(student).all()
#     for record in records:
#         currentbelt = record.belt
#         newbelt_id = db.session.query(belts.id).filter(belts.beltName == currentbelt).scalar()
#         record.belt_id = newbelt_id
#         db.session.commit()
#     return 'ok'

