import datetime
from flask import (Blueprint, flash, g, make_response, redirect,
                   render_template, request, session, url_for)
from flaskapp import db, app
from flaskapp.auth.auth import dojo_required
from flaskapp.models import (dojo, enrollment, lesson, student, studentRemarks,
                             studentStatus, belts)
from flaskapp.performance.db_method import get_studentRecord
from flaskapp.performance.form import (gradePerformanceform,
                                       performanceRemarkform)

performance_bp = Blueprint('performance', __name__,
                           template_folder='templates/performance',
                           static_folder='static',url_prefix='/performance')


@performance_bp.route('/performanceViewer', methods=('GET', 'POST'))
@dojo_required
def performanceViewer():
    dojo_id = request.cookies.get('dojo_id')
    dojoRecord = db.session.query(dojo).filter(dojo.id == dojo_id).first()
    # student_list = db.session.query(enrollment).join(student).\
    #                 filter(enrollment.dojo_id == dojo_id,
    #                 enrollment.studentActive == True).order_by(student.firstName.desc()).all()

    student_list = db.session.query(student.id,
                                student.firstName,
                                student.lastGrading,
                                belts.beltName,enrollment.studentActive)\
        .filter(student.belt_id == belts.id)\
        .filter(enrollment.dojo_id==dojo_id,enrollment.student_id == student.id)\
        .order_by(enrollment.studentActive.desc(),student.id.asc(),).all()
    return render_template('performanceViewer.html',
                           student_list=student_list,
                           dojoRecord=dojoRecord)


@performance_bp.route('/performanceRemarks/<student_id>', methods=('GET', 'POST'))
def performanceRemarks(student_id):
    studentRecord = get_studentRecord(student_id)
    form = performanceRemarkform()
    if form.validate_on_submit():
        dojo_id=request.cookies.get('dojo_id')
        dojoRecord = db.session.query(dojo).filter(dojo.id == dojo_id).first()
        remarkRecord = studentRemarks(
            student_id = student_id,
            dojo_id=dojoRecord.id,
            instructor_id=dojoRecord.instructor.id,
            remarks=form.remark.data,
            date=form.date.data
        )
        db.session.add(remarkRecord)
        db.session.commit()
        flash('Record loaded for {}!'.format(studentRecord.firstName))
        return redirect(url_for('performance.performanceViewer')) # return back home page

    return render_template('performanceRemarks.html',
            studentRecord=studentRecord, form=form)


@performance_bp.route('/performanceGradePerformance/<student_id>', methods=('GET', 'POST'))
def performanceGradePerformance(student_id):
    studentRecord = get_studentRecord(student_id)

    # with student id find out his last 5 status where he is present and not marked before
    subquery = db.session.query(studentStatus.lesson_id)\
        .filter(studentStatus.student_id == studentRecord.id, studentStatus.status == True, studentStatus.evaluated == False).\
        order_by(studentStatus.lesson_id.desc()).limit(5).all()

    if subquery == []:
        flash('No record to grade')
        return redirect(url_for('performance.performanceViewer'))

    lessonRecord = db.session.query(lesson).filter(lesson.id.in_(subquery)).order_by(lesson.id.desc()).limit(5).all()
    last_studentRecord = db.session.query(studentStatus)\
        .filter(studentStatus.student_id == studentRecord.id,studentStatus.status == True,studentStatus.evaluated == True).\
        order_by(studentStatus.lesson_id.desc()).first()

    if last_studentRecord:
        form = gradePerformanceform(obj=last_studentRecord)
    else:
        form = gradePerformanceform()
    form.lesson_id.choices = [(lessonDone.id, '{} {}'.format(lessonDone.date, lessonDone.dojo.name)) for lessonDone in lessonRecord]

    if form.validate_on_submit():
        lesson_id = form.lesson_id.data
        student_record = db.session.query(studentStatus).filter(studentStatus.student_id == studentRecord.id, studentStatus.lesson_id == lesson_id).first()
        form.populate_obj(student_record)
        student_record.evaluated = True
        db.session.commit()

        flash('Successfully updated {}\'s Record!'.format(student_record.student.firstName))
        return redirect(url_for('performance.performanceViewer')) # return back home page

    return render_template('performanceGradePerformance.html',
            studentRecord=studentRecord, form=form)


@performance_bp.route('/performanceGradeNext/<student_id>', methods=['POST'])
def performanceGradeNext(student_id):
    studentRecord = get_studentRecord(student_id)
    form = gradePerformanceform(request.form)
    lesson_id = form.lesson_id.data
    student_record = db.session.query(studentStatus).filter(studentStatus.student_id == studentRecord.id, studentStatus.lesson_id == lesson_id).first()
    form.populate_obj(student_record)
    student_record.evaluated = True
    db.session.commit()

    flash('Successfully updated {}\'s Record!'.format(student_record.student.firstName))

    # get next student record
    student_list = db.session.query(studentStatus).join(student).\
                    filter(studentStatus.lesson_id == lesson_id,
                    studentStatus.status==True, studentStatus.evaluated==False).order_by(student.firstName.desc()).all()

    if student_list != []:
        return url_for('performance.performanceGradePerformance', student_id=student_list[0].student.id)
    else:
        flash('No more records left to grade for this lesson!')
        return url_for('performance.performanceViewer')


@performance_bp.route('/performanceChartView/<student_id>', methods=['GET'])
def performanceChartView(student_id):
    # ---- get student details
    studentRecord = db.session.query(student.firstName,
                                     student.lastGrading,
                                     belts.beltName,
                                     belts.timespanNeeded).filter(student.id==student_id, student.belt_id == belts.id).first()

    # ---- get performance details
    subquery = db.session.query(studentStatus.technique,
                                studentStatus.ukemi,
                                studentStatus.discipline,
                                studentStatus.coordination,
                                studentStatus.knowledge,
                                studentStatus.spirit,
                                lesson.date).\
                filter(studentStatus.student_id == student_id,
                        studentStatus.status == True,
                        studentStatus.lesson_id == lesson.id).\
                order_by(lesson.date.asc()).all()
    
    technique,ukemi,discipline,coordination,knowledge,spirit,dateLabel = [list(i) for i in zip(*subquery)]

    # ---- get remarks
    myRemarks = db.session.query(studentRemarks.remarks,
                                 studentRemarks.date).filter_by(student_id=student_id).all()

    if studentRecord.lastGrading:
        countdown = int(studentRecord.lastGrading.month) - studentRecord.timespanNeeded
    else:
        countdown = None
    return render_template('performanceChartView.html',
                           studentRecord=studentRecord,
                           technique=technique, ukemi=ukemi, discipline=discipline,
                           coordination=coordination, knowledge=knowledge,
                           spirit=spirit, dateLabel=dateLabel, countdown = countdown,
                           lessonDone=gradingEligible(student_id),
                           myRemarks=myRemarks)


@performance_bp.route('/performanceRemarksView/<student_id>', methods=['GET'])
def performanceRemarksView(student_id):
    studentRecord = get_studentRecord(student_id)
    remarks = db.session.query(studentRemarks).\
                filter(studentRemarks.student_id == student_id).\
                order_by(studentRemarks.date.asc()).all()
    return render_template('performanceChartView.html',
                           studentRecord=studentRecord,
                           remarks=remarks, dateLabel=dateLabel)


@performance_bp.route('/performanceBokeh/<student_id>', methods=('GET', 'POST'))
def performanceBokeh(student_id):
    from bokeh.io import output_file, show
    from bokeh.layouts import gridplot
    from bokeh.plotting import figure
    import os
    filename = os.path.join(app.root_path, str(url_for('performance.static', filename='test.html'))[1:])
    output_file(filename)

    p = figure(plot_width=400,plot_height=400,x_axis_type='datetime')
    p.line(y =  [i for i in range(20)], x = [i for i in range(20)], color="navy")
    p2 = figure(plot_width=400,plot_height=400,x_axis_type='datetime')
    p2.line(y =  [i for i in range(20)], x = [i for i in range(20)], color="navy")
    p3 = figure(plot_width=400,plot_height=400,x_axis_type='datetime')
    p3.line(y =  [i for i in range(20)], x = [i for i in range(20)], color="navy")
    grid = gridplot([[p, p3], [None, p2]], plot_width=250, plot_height=250)
    show(grid)
    return 'h'


def gradingEligible(student_id):
    # get last grading date
    lastGradingDate = db.session.query(student.lastGrading).filter(student.id == student_id).scalar()
    if lastGradingDate:
        # get lesson id after lastGrading date
        lessonID_start = db.session.query(lesson.id).filter(lesson.date>lastGradingDate).order_by(lesson.id.asc()).first()
        # count number of records student have
        if lessonID_start:
            lessonsDone = db.session.query(studentStatus.status).filter(studentStatus.student_id == student_id,studentStatus.lesson_id>lessonID_start,studentStatus.status==True).count()
            return lessonsDone
        else:
            return 0
    else:
        lessonsDone = db.session.query(studentStatus.status).filter(studentStatus.student_id == student_id,studentStatus.status==True).count()
        return lessonsDone