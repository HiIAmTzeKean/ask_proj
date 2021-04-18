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
    questionids = [r[0] for r in questionids]
    questions = db.session.query(Question.name,Question.id).filter(Question.id.in_(questionids)).all()
    # questions = [r for r, in questions]
    records = db.session.query(Answer.studentAnswer).filter(Answer.survey_id==survey_id).all()

    if records == []:
        flash('No feedback yet!')
        return redirect(url_for('auth.authUserViewer'))
    records = next(zip(*records))

    # holder = {}
    # for questionRecord in questionids:
    #     holder[str(questionRecord.question_id)]=[]

    # for record in records:
    #     for item in holder:
    #         holder[item].append(int(record.get(item)))
    holder = {}
    for record in records:
        for questionRecordID in questionids:
            if str(questionRecordID) not in holder:
                holder[str(questionRecordID)] = [0 for i in range(10)]
                holder[str(questionRecordID)][int(record.get(str(questionRecordID)))-1]+=1
                continue
            # holder[str(questionRecordID)].append(int(record.get(str(questionRecordID))))
            holder[str(questionRecordID)][int(record.get(str(questionRecordID)))-1]+=1

                
    # studentAnswer = {1:1, 2:1}
    # store each qn as {name: '', Ans: [1,2,3,4,..10] }
    answer_dict = {}
    for questionRecord in questions:
        answer_dict[questionRecord.name] = holder.get(str(questionRecord.id))

    # x axis 1-10
    # y axis count per score
    scale = [i for i in range(1,11)]
    questions = [r.name for r in questions]
    return render_template("chart.html", scale=scale, answer_dict=answer_dict, questions=questions)