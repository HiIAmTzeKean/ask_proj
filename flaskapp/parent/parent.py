import datetime
# import base64
from sqlalchemy.orm.exc import NoResultFound
from flask import (Blueprint, flash, redirect, make_response,
                   render_template, request, url_for)
from flask_mobility.decorators import mobile_template
from flaskapp import db, app
from flaskapp.models import (Student, StudentRemarks, Answer, Enrollment,Instructor,
                             StudentStatus, Belt, Lesson, Survey,SurveyQuestion,Question)
from flaskapp.parent.form import formStudentIdentifier, formQuestions
from flaskapp.performance.helper import helper_ChartView
from flaskapp.parent.helper import messageEncode, messageDecode


parent_bp = Blueprint('parent', __name__,
                      template_folder='templates/parent',
                      static_folder='static', url_prefix='/parent')


@parent_bp.route('/parentIdentifyStudent', methods=('GET', 'POST'))
def parentIdentifyStudent():
    form = formStudentIdentifier()
    if form.validate_on_submit():
        try:
            studentRecord = db.session.query(Student.id).\
                filter_by(membership = form.membership.data,
                          dateOfBirth = datetime.datetime.strptime('01{}{}'.format(form.dateOfBirth_month.data.zfill(2),form.dateOfBirth_year.data), '%d%m%Y').date()).\
                one()
        except NoResultFound:
            flash('Membership ID and Birhtday combination is not valid, please try again!')
            return redirect(url_for('parent.parentIdentifyStudent'))

        return redirect(url_for('parent.parentChartView', student_membership=messageEncode(str(form.membership.data))))
    return render_template('parentIdentifyStudent.html',form=form)


@parent_bp.route('/parentGradingDates', methods=('GET', 'POST'))
def parentGradingDates():
    from bs4 import BeautifulSoup
    import requests
    url='http://www.aikido.com.sg/grading-information.html'
    html_content = requests.get(url).text
    soup = BeautifulSoup(html_content, "lxml")
    gradingData = soup.find_all("table")[1].tbody.find_all("tr")
    details = []
    for row in gradingData:
        for td in row.find_all("td"):
            details.append(td.text)

    processedDetails =[[],[],[]]
    for no,date in enumerate(details):
        processedDetails[no//4].append(date)
    return render_template('parentGradingDates.html', processedDetails=processedDetails)


@parent_bp.route('/parentChartView/<student_membership>', methods=['GET'])
@mobile_template('{mobile/}parentChartView.html')
def parentChartView(student_membership, template):
    student_membership = messageDecode(student_membership)
    studentRecord,technique,ukemi,discipline,coordination,knowledge,spirit,dateLabel,countdown,lessonDone,myRemarks=\
        helper_ChartView(student_membership)

    return render_template(template,
                           studentRecord=studentRecord,
                           technique=technique, ukemi=ukemi, discipline=discipline,
                           coordination=coordination, knowledge=knowledge,
                           spirit=spirit, dateLabel=dateLabel, countdown=countdown,
                           lessonDone=lessonDone, myRemarks=myRemarks)


# todo reset form after submit
@parent_bp.route('/parentFeedback', methods=('GET', 'POST'))
def parentFeedback():
    form = formQuestions(request.form)

    if form.validate_on_submit():
        date_str = '01{}{}'.format(form.dateOfBirth_month.data.zfill(2),form.dateOfBirth_year.data)
        birthday_data = datetime.datetime.strptime(date_str, '%d%m%Y').date()
        # find out if student exist first

        if db.session.query(Student).filter_by(membership=form.membership.data, dateOfBirth=birthday_data).first() != None:
            answer_dict = {}
            for i in request.form:
                if 'questions' in i:
                    answer_dict[i.lstrip('questions-')] = request.form[i]
            record = Answer(date=form.date.data, studentAnswer=answer_dict, student_membership=form.membership.data, survey_id=request.cookies.get('survey_id'))
            db.session.add(record)
            db.session.commit()
        
            flash('Thank you for the feedback!')
            request.form = {}
            return redirect(url_for('parent.parentIdentifyStudent'))
        flash('Sorry, but the Membership ID does not tally with the given birthday!')

    surveyRecord = db.session.query(Survey).filter_by(name = 'Parent Feedback').first()
    question_id = db.session.query(SurveyQuestion.question_id).filter_by(survey_id = surveyRecord.id).all()
    questionList = db.session.query(Question.id, Question.name, Question.questionType, Question.questionCategory).filter(Question.id.in_(question_id)).all()
    questionBank = {}
    for num,i in enumerate(questionList):
        form.questions.append_entry()
        form.questions[num].id = 'questions-{}'.format(i.id)
        form.questions[num].name = 'questions-{}'.format(i.id)
        form.questions[num].label = i.name
        form.questions.label = i.name

        if i.questionCategory in questionBank:
            questionBank[i.questionCategory].append([i.id, i.name, i.questionType])
        else:
            questionBank[i.questionCategory] = [[i.id, i.name, i.questionType]]

    resp = make_response(render_template('parentFeedback.html', questionBank=questionBank, form=form))
    resp.set_cookie('survey_id', str(surveyRecord.id))
    return resp


@parent_bp.route("/lol")
def lol():
    studentstatues = db.session.query(StudentStatus).all()
    for i in studentstatues:
        i.student_membership = i.student.membership
    db.session.commit()
    studentenrollemnt = db.session.query(Enrollment).all()
    for i in studentenrollemnt:
        i.student_membership = i.student.membership
    db.session.commit()
    Studentremarks = db.session.query(StudentRemarks).all()
    for i in Studentremarks:
        i.student_membership = i.student.membership
    db.session.commit() 

    instr = db.session.query(Instructor).all()
    for i in instr:
        i.student_membership = i.membership
    db.session.commit()

    lessons = db.session.query(Lesson).all()
    for i in lessons:
        i.instructor_membership = i.instructor.membership
    db.session.commit()
    return 'done'

@parent_bp.route("/lol2")
def lol2():
    import json
    lessons = db.session.query(Lesson).all()
    for i in lessons:
        if i.techniquesTaught:
            i.techniquesTaught = json.loads(i.techniquesTaught)
    db.session.commit()
    return 'done'
