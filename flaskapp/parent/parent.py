import datetime
# import base64
from sqlalchemy.orm.exc import NoResultFound
from flask_mail import Message
from flask import (Blueprint, flash, redirect, make_response,
                   render_template, request, url_for)
from flask_mobility.decorators import mobile_template
from flaskapp import db, app, mail
from flaskapp.models import (Student, StudentRemarks, Answer, Enrollment,Instructor,
                             StudentStatus, Belt, Lesson, Survey,SurveyQuestion,Question)
from flaskapp.parent.form import formStudentIdentifier, formQuestions, formTesimonial
from flaskapp.performance.helper import helper_ChartView,helper_RadarView
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
            return redirect(url_for('parent.parentChartView', student_membership=messageEncode(str(form.membership.data))))
        except NoResultFound:
            flash('Membership ID and Birhtday combination is not valid, please try again!')
 
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
    studentRecord,technique,ukemi,discipline,coordination,knowledge,spirit,dateLabel,values,lessonDone,myRemarks=\
        helper_ChartView(student_membership)
    from statistics import mean
    radar_data = [mean(i) for i in [technique,ukemi,discipline,coordination,knowledge,spirit]]
    lines_data = {'technique':technique,'ukemi':ukemi,'discipline':discipline,'coordination':coordination,'knowledge':knowledge,'spirit':spirit}
    return render_template(template,
                           studentRecord=studentRecord, radar_data=radar_data,lines_data=lines_data,
                           dateLabel=dateLabel, values=values,
                           lessonDone=lessonDone, myRemarks=myRemarks)


@parent_bp.route('/parentYearEndReport/<student_membership>', methods=['GET'])
@mobile_template('{mobile/}parentYearEndReport.html')
def parentYearEndReport(student_membership, template):
    student_membership = messageDecode(student_membership)
    studentRecord,radar_data,dateLabel,values,lessonDone,myRemarks=helper_RadarView(student_membership)
    from statistics import mean
    radar_data = [mean(i) for i in radar_data]
    return render_template(template,
                           studentRecord=studentRecord, radar_data=radar_data,
                           dateLabel=dateLabel, values=values,
                           lessonDone=lessonDone, myRemarks=myRemarks)


@parent_bp.route('/parentTestimonial/<token>', methods=('GET', 'POST'))
def parentTestimonial(token):
    from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
    s = Serializer('WEBSITE_SECRET_KEY')
    try:
        membership = s.loads(token)['membership']
        form = formTesimonial(membership=membership)
    except:
        return redirect(url_for('parent.parentIdentifyStudent'))
    return render_template('parentTestimonial.html', form=form)


@parent_bp.route('/parentTestimonialSave', methods=('GET', 'POST'))
def parentTestimonialSave():
    form = formTesimonial(request.form)
    print(form.testimonial.data)
    # add to db
    return redirect(url_for('parent.parentIdentifyStudent'))


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

            msg = Message("Parents Feedback",recipients=["zhugejing505@gmail.com"])
            msg.body = form.comments.data
            mail.send(msg)
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
