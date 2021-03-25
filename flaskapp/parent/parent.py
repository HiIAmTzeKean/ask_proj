import datetime
from sqlalchemy.orm.exc import NoResultFound
from flask import (Blueprint, flash, redirect,
                   render_template, request, url_for)
from flask_mobility.decorators import mobile_template
from flaskapp import db, app
from flaskapp.models import (lesson, student, studentRemarks,
                             studentStatus, belts)
from flaskapp.parent.form import formStudentIdentifier


parent_bp = Blueprint('parent', __name__,
                      template_folder='templates/parent',
                      static_folder='static', url_prefix='/parent')


@parent_bp.route('/parentIdentifyStudent', methods=('GET', 'POST'))
def parentIdentifyStudent():
    # select child
    form = formStudentIdentifier()
    if form.validate_on_submit():
        try:
            studentRecord = db.session.query(student.id).\
                filter(student.membership == form.membership.data).one()
        except NoResultFound:

            flash('Membership ID is not valid, please contact instructor incharge!')
            return redirect(url_for('parent.parentIdentifyStudent'))
        return redirect(url_for('parent.parentChartView', studentID=studentRecord.id))
    return render_template('parentIdentifyStudent.html',form=form)


@parent_bp.route('/parentChartView/<studentID>', methods=['GET'])
@mobile_template('{mobile/}parentChartView.html')
def parentChartView(studentID, template):
    dojo_id = request.cookies.get('dojo_id')
    # ---- get student details
    studentRecord = db.session.query(student.firstName,
                                     student.lastGrading,
                                     belts.beltName,
                                     belts.timespanNeeded)\
        .filter(student.id == studentID, student.belt_id == belts.id).first()

    # ---- get performance details
    subquery = db.session.query(studentStatus.technique,
                                studentStatus.ukemi,
                                studentStatus.discipline,
                                studentStatus.coordination,
                                studentStatus.knowledge,
                                studentStatus.spirit,
                                lesson.date).\
        filter(studentStatus.student_id == studentID,
               studentStatus.status == True,
               studentStatus.evaluated == True,
               studentStatus.lesson_id == lesson.id,
               lesson.dojo_id == dojo_id).\
        order_by(lesson.date.asc()).limit(10).all()

    technique, ukemi, discipline, coordination, knowledge, spirit, dateLabel = processChartRecords(subquery)
    dateLabel = processDateLabel(dateLabel)

    # ---- get remarks
    myRemarks = db.session.query(studentRemarks.remarks,
                                 studentRemarks.date).\
        filter_by(student_id=studentID).\
        order_by(studentRemarks.date.asc()).all()

    # ---- get number of days to grading
    countdown = daysToGrading(studentRecord)

    return render_template(template,
                           studentRecord=studentRecord,
                           technique=technique, ukemi=ukemi,
                           discipline=discipline,
                           coordination=coordination, knowledge=knowledge,
                           spirit=spirit, dateLabel=dateLabel,
                           countdown=countdown,
                           lessonDone=gradingEligible(studentID),
                           myRemarks=myRemarks)


def gradingEligible(student_id):
    # get last grading date
    lastGradingDate = db.session.query(student.lastGrading).\
        filter(student.id == student_id).scalar()
    if lastGradingDate:
        # get lesson id after lastGrading date
        lessonID_start = db.session.query(lesson.id).\
            filter(lesson.date > lastGradingDate).\
            order_by(lesson.id.asc()).first()
        # count number of records student have
        if lessonID_start:
            lessonsDone = db.session.query(studentStatus.status).filter(studentStatus.student_id == student_id,studentStatus.lesson_id>lessonID_start,studentStatus.status==True).count()
            return lessonsDone
        else:
            return 0
    else:
        lessonsDone = db.session.query(studentStatus.status).filter(studentStatus.student_id == student_id,studentStatus.status==True).count()
        return lessonsDone


def processDateLabel(dateLabel):
    try:
        return [label if (i+1)%(len(dateLabel)//5)==0 else '' for i,label in enumerate(dateLabel)]
    except:
        return None


def processChartRecords(subquery):
    if subquery == []:
        return [],[],[],[],[],[],[]
    return [list(i) for i in zip(*subquery)]
        

def daysToGrading(studentRecord):
    if studentRecord.lastGrading:
        return int(datetime.date.today().month) - int(studentRecord.lastGrading.month) + studentRecord.timespanNeeded
    else:
        return None
