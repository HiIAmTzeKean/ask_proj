import datetime
import json
from werkzeug.datastructures import MultiDict

from flask import (Blueprint, flash, g, make_response, redirect,
                   render_template, request, session, url_for)
from flaskapp import db
from flaskapp.auth.auth import dojo_required
from flaskapp.models import dojo, enrollment, lesson, student, studentStatus, studentRemarks
from flaskapp.performance.db_method import get_studentRecord
from flaskapp.performance.form import gradePerformanceform, performanceRemarkform

performance_bp = Blueprint('performance', __name__,
                           template_folder='templates', static_folder='static')


@performance_bp.route('/performanceViewer', methods=('GET', 'POST'))
@dojo_required
def performanceViewer():
    dojo_id = request.cookies.get('dojo_id')
    dojoRecord = db.session.query(dojo).filter(dojo.id == dojo_id).first()
    student_list = db.session.query(enrollment).join(student).\
                    filter(enrollment.dojo_id == dojo_id,
                    enrollment.studentActive == True).order_by(student.firstName.desc()).all()

    return render_template('performance/performanceViewer.html',
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

    return render_template('performance/performanceRemarks.html',
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

    if request.method == 'GET':
        lessonRecord = db.session.query(lesson).filter(lesson.id.in_(subquery)).order_by(lesson.id.desc()).limit(5).all()
        # get student's last record to load form fields
        last_studentRecord = db.session.query(studentStatus)\
            .filter(studentStatus.student_id == studentRecord.id,studentStatus.status == True,studentStatus.evaluated == True).\
            order_by(studentStatus.lesson_id.desc()).first()
        if last_studentRecord:
            lastPerformance = json.loads(last_studentRecord.performance)
            lastPerformance.update({'lesson_id':lessonRecord[0].id})
            form = gradePerformanceform(formdata=MultiDict(lastPerformance))
        else: 
            form = gradePerformanceform()
        form.lesson_id.choices = [(lessonDone.id, '{} {}'.format(lessonDone.date, lessonDone.dojo.name)) for lessonDone in lessonRecord]

    else:
        lesson_id = request.form["lesson_id"]
        performanceScore = {'technique':request.form["technique"],
                            'ukemi':request.form["ukemi"],
                            'discipline':request.form["discipline"],
                            'coordination':request.form["coordination"],
                            'knowledge':request.form["knowledge"],
                            'spirit':request.form["spirit"]
                            }
        student_record = db.session.query(studentStatus).filter(studentStatus.student_id == studentRecord.id, studentStatus.lesson_id == lesson_id).first()
        student_record.performance = json.dumps(performanceScore)
        student_record.evaluated = True
        db.session.commit()

        flash('Successfully updated {}\'s Record!'.format(student_record.student.firstName))
        return redirect(url_for('performance.performanceViewer')) # return back home page

    return render_template('performance/performanceGradePerformance.html',
            studentRecord=studentRecord, form=form)


@performance_bp.route('/performanceGradeNext/<student_id>', methods=['POST'])
def performanceGradeNext(student_id):
    studentRecord = get_studentRecord(student_id)
    lesson_id = request.form["lesson_id"]
    performanceScore = {'technique':request.form["technique"],
                        'ukemi':request.form["ukemi"],
                        'discipline':request.form["discipline"],
                        'coordination':request.form["coordination"],
                        'knowledge':request.form["knowledge"],
                        'spirit':request.form["spirit"]
                        }
    student_record = db.session.query(studentStatus).filter(studentStatus.student_id == studentRecord.id, studentStatus.lesson_id == lesson_id).first()
    student_record.performance = json.dumps(performanceScore)
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


@performance_bp.route('/performanceChartView/<student_id>', methods=('GET', 'POST'))
def performanceChartView(student_id):
    studentRecord = get_studentRecord(student_id)

    subquery = db.session.query(studentStatus).\
        filter(studentStatus.student_id == studentRecord.id, studentStatus.status == True).\
        join(lesson, studentStatus.lesson_id == lesson.id).order_by(lesson.date.asc()).all()

    dateLabel = [i.lesson.date.strftime("%x") for i in subquery]
    technique = []
    ukemi = []
    discipline = []
    coordination = []
    knowledge = []
    spirit = []

    for i in subquery:
        temp = json.loads(i.performance)
        technique.append(int(temp['technique']))
        ukemi.append(int(temp['ukemi']))
        discipline.append(int(temp['discipline']))
        coordination.append(int(temp['coordination']))
        knowledge.append(int(temp['knowledge']))
        spirit.append(int(temp['spirit']))
        
    return render_template('performance/performanceChartView.html',
                           studentRecord=studentRecord,
                           technique=technique, ukemi=ukemi, discipline=discipline,
                           coordination=coordination, knowledge=knowledge,
                           spirit=spirit, dateLabel=dateLabel)
