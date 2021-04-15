import datetime

from flask import (Blueprint, flash, redirect,
                   render_template, request, url_for)
from flaskapp import db
from flaskapp.models import SurveyQuestion, Answer, Question


feedback_bp = Blueprint('feedback', __name__,
                           template_folder='templates',
                           static_folder='static',
                           url_prefix='/feedback')


#todo add feedback button
@feedback_bp.route('/feedbackViewer', methods=('GET', 'POST'))
def feedbackViewer():
    survey_id = 1
    questionids = db.session.query(SurveyQuestion.question_id).filter(SurveyQuestion.survey_id == survey_id).all()
    questions = db.session.query(Question.name).filter(Question.id.in_(questionids)).all()
    questions = [r for r, in questions]
    records = db.session.query(Answer.studentAnswer).filter(Answer.survey_id==survey_id).all()
    if records == None:
        flash('No feed back yet!')
        return redirect(url_for('auth.authUserViewer'))
    records = next(zip(*records))

    temp = []
    for i in records:
        counter = []
        holder = list(i.values())
        for j in range(1,11):
            counter.append(holder.count(str(j)))
        temp.append(counter)

    # studentAnswer = {1:1, 2:1}
    # store each qn as {name: '', Ans: [1,2,3,4,..10] }
    answer_dict = {}
    for ans,qn in zip(temp, questions):
        answer_dict[qn] = ans
    print(answer_dict)

    # x axis 1-10
    # y axis count per score
    scale = [i for i in range(1,11)]
    score = []
    for item in answer_dict:
        score.append(answer_dict[item])
    return render_template("chart.html", scale=scale, answer_dict=answer_dict, questions=questions)