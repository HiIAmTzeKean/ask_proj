import datetime
import json

from flask import (Blueprint, flash, g, make_response, redirect,
                   render_template, request, session, url_for)
from flaskapp import db
from flaskapp.auth.auth import dojo_required
from flaskapp.models import dojo, enrollment, lesson, student, studentStatus
from flaskapp.performance.db_method import get_studentRecord
from flaskapp.performance.form import gradePerformanceform

performance_bp = Blueprint('performance', __name__,
                           template_folder='templates', static_folder='static')


@performance_bp.route('/performanceViewer', methods=('GET', 'POST'))
@dojo_required
def performanceViewer():
    dojo_id = request.cookies.get('dojo_id')
    dojoRecord = db.session.query(dojo).filter(dojo.id == dojo_id).first()
    student_list = db.session.query(enrollment).join(student).\
                    filter(enrollment.dojo_id == dojo_id,
                    enrollment.studentActive == True).all()

    return render_template('performance/performanceViewer.html',
                           student_list=student_list,
                           dojoRecord=dojoRecord)


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
    form = gradePerformanceform()
    form.lesson_id.choices = [(lessonDone.id, '{} {}'.format(lessonDone.date, lessonDone.dojo.name)) for lessonDone in lessonRecord]

    if form.validate_on_submit(): # update record in database if valid
        lesson_id = form.lesson_id.data
        technique = form.technique.data
        ukemi = form.ukemi.data
        discipline = form.discipline.data
        coordination = form.coordination.data
        knowledge = form.knowledge.data
        spirit = form.spirit.data

        performanceScore = {'technique':technique, 'ukemi':ukemi, 'discipline':discipline, 'coordination':coordination, 'knowledge':knowledge, 'spirit':spirit}
        student_record = db.session.query(studentStatus).filter(studentStatus.student_id == studentRecord.id, studentStatus.lesson_id == lesson_id).first()
        student_record.performance = json.dumps(performanceScore)
        student_record.evaluated = True
        db.session.commit()

        flash('Successfully updated!')
        return redirect(url_for('performance.performanceGradePerformance', student_id=student_id)) # return back same view page

    return render_template('performance/performanceGradePerformance.html',
            studentRecord=studentRecord, form=form)


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
