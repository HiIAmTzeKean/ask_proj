import datetime
from flask import (Blueprint, flash, redirect, g,
                   render_template, request, url_for)
from flask_mobility.decorators import mobile_template
from flaskapp import db, app
from flaskapp.auth.auth import dojo_required
from flask_security import login_required
from flaskapp.models import (Dojo, Enrollment, Lesson, Student, StudentRemarks,
                             StudentStatus, Belt)
from flaskapp.performance.form import (gradePerformanceform,
                                       performanceRemarkform)
from flaskapp.performance.helper import helper_ChartView


performance_bp = Blueprint('performance', __name__,
                           template_folder='templates/performance',
                           static_folder='static', url_prefix='/performance')


@performance_bp.route('/performanceViewer', methods=('GET', 'POST'))
@dojo_required
@login_required
def performanceViewer():
    dojo_id = request.cookies.get('dojo_id')
    dojoRecord = db.session.query(Dojo).filter(Dojo.id == dojo_id).first()

    student_list = db.session.query(Student.id,
                                    Student.firstName,
                                    Student.lastGrading,
                                    Belt.beltName,
                                    Enrollment.studentActive)\
                    .filter(Student.belt_id == Belt.id)\
                    .filter(Enrollment.dojo_id == dojo_id,
                            Enrollment.student_id == Student.id,
                            Enrollment.studentActive == True)\
                    .order_by(Student.id.asc(),).all()
    return render_template('performanceViewer.html',
                           student_list=student_list,
                           dojoRecord=dojoRecord)


@performance_bp.route('/performanceRemarks/<student_id>', methods=('GET', 'POST'))
def performanceRemarks(student_id):
    studentRecord = db.session.query(Student).filter_by(id=student_id).first()
    form = performanceRemarkform()
    if form.validate_on_submit():
        dojo_id = request.cookies.get('dojo_id')
        dojoRecord = db.session.query(Dojo).filter(Dojo.id == dojo_id).first()
        remarkRecord = StudentRemarks(
            student_id=student_id,
            dojo_id=dojoRecord.id,
            instructor_id=dojoRecord.instructor.id,
            remarks=form.remark.data,
            date=form.date.data
        )
        db.session.add(remarkRecord)
        db.session.commit()
        flash('Record loaded for {}!'.format(studentRecord.firstName))
        return redirect(url_for('performance.performanceViewer'))  # return back home page

    return render_template('performanceRemarks.html',
            studentRecord=studentRecord, form=form)


@performance_bp.route('/performanceGradePerformance/<student_id>', methods=('GET', 'POST'))
def performanceGradePerformance(student_id):
    studentRecord = db.session.query(Student).filter_by(id=student_id).first()

    # with student id find out his last 5 status where he is present and not marked before
    subquery = db.session.query(StudentStatus.lesson_id)\
        .filter(StudentStatus.student_id == studentRecord.id, StudentStatus.status == True, StudentStatus.evaluated == False).\
        order_by(StudentStatus.lesson_id.desc()).limit(5).all()

    if subquery == []:
        flash('No record to grade')
        return redirect(url_for('performance.performanceViewer'))

    lessonRecord = db.session.query(Lesson).filter(Lesson.id.in_(subquery)).order_by(Lesson.id.desc()).limit(5).all()
    last_studentRecord = db.session.query(StudentStatus)\
        .filter(StudentStatus.student_id == studentRecord.id,StudentStatus.status == True,StudentStatus.evaluated == True).\
        order_by(StudentStatus.lesson_id.desc()).first()

    if last_studentRecord:
        form = gradePerformanceform(obj=last_studentRecord)
    else:
        form = gradePerformanceform()
    form.lesson_id.choices = [(lessonDone.id, '{} {}'.format(lessonDone.date, lessonDone.dojo.name)) for lessonDone in lessonRecord]

    if form.validate_on_submit():
        lesson_id = form.lesson_id.data
        student_record = db.session.query(StudentStatus).filter(StudentStatus.student_id == studentRecord.id, StudentStatus.lesson_id == lesson_id).first()
        form.populate_obj(student_record)
        student_record.evaluated = True
        db.session.commit()

        flash('Successfully updated {}\'s Record!'.format(student_record.student.firstName))
        return redirect(url_for('performance.performanceViewer')) # return back home page

    return render_template('performanceGradePerformance.html',
            studentRecord=studentRecord, form=form)


@performance_bp.route('/performanceGradeNext/<student_id>', methods=['POST'])
def performanceGradeNext(student_id):
    studentRecord = db.session.query(Student).filter_by(id=student_id).first()
    form = gradePerformanceform(request.form)
    lesson_id = form.lesson_id.data
    student_record = db.session.query(StudentStatus).filter(StudentStatus.student_id == studentRecord.id, StudentStatus.lesson_id == lesson_id).first()
    form.populate_obj(student_record)
    student_record.evaluated = True
    db.session.commit()

    flash('Successfully updated {}\'s Record!'.format(student_record.student.firstName))

    # get next student record
    student_list = db.session.query(StudentStatus).join(Student).\
                    filter(StudentStatus.lesson_id == lesson_id,
                    StudentStatus.status==True, StudentStatus.evaluated==False).order_by(Student.firstName.desc()).all()

    if student_list != []:
        return url_for('performance.performanceGradePerformance', student_id=student_list[0].student.id)
    else:
        flash('No more records left to grade for this lesson!')
        return url_for('performance.performanceViewer')


@performance_bp.route('/performanceChartView/<student_id>', methods=['GET'])
@mobile_template('{mobile/}performanceChartView.html')
def performanceChartView(student_id, template):
    studentRecord,technique,ukemi,discipline,coordination,knowledge,spirit,dateLabel,countdown,lessonDone,myRemarks=\
        helper_ChartView(request.cookies.get('dojo_id'),student_id)
    return render_template(template,
                           studentRecord=studentRecord,
                           technique=technique, ukemi=ukemi, discipline=discipline,
                           coordination=coordination, knowledge=knowledge,
                           spirit=spirit, dateLabel=dateLabel, countdown=countdown,
                           lessonDone=lessonDone, myRemarks=myRemarks)


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
