import datetime
import base64
from sqlalchemy.orm.exc import NoResultFound
from flask import (Blueprint, flash, redirect,
                   render_template, request, url_for)
from flask_mobility.decorators import mobile_template
from flaskapp import db, app
from flaskapp.models import (Student, StudentRemarks,
                             StudentStatus, Belt, Lesson)
from flaskapp.parent.form import formStudentIdentifier
from flaskapp.performance.helper import helper_ChartView


parent_bp = Blueprint('parent', __name__,
                      template_folder='templates/parent',
                      static_folder='static', url_prefix='/parent')


@parent_bp.route('/parentIdentifyStudent', methods=('GET', 'POST'))
def parentIdentifyStudent():
    form = formStudentIdentifier()
    if form.validate_on_submit():
        try:
            studentRecord = db.session.query(Student.id).\
                filter_by(membership = form.membership.data).one()
        except NoResultFound:

            flash('Membership ID is not valid, please contact instructor incharge!')
            return redirect(url_for('parent.parentIdentifyStudent'))

        return redirect(url_for('parent.parentChartView', studentID=messageEncode(str(studentRecord.id))))
    return render_template('parentIdentifyStudent.html',form=form)


@parent_bp.route('/parentChartView/<studentID>', methods=['GET'])
@mobile_template('{mobile/}parentChartView.html')
def parentChartView(studentID, template):
    studentID = messageDecode(studentID)

    studentRecord,technique,ukemi,discipline,coordination,knowledge,spirit,dateLabel,countdown,lessonDone,myRemarks=\
        helper_ChartView(request.cookies.get('dojo_id'),studentID)

    return render_template(template,
                           studentRecord=studentRecord,
                           technique=technique, ukemi=ukemi, discipline=discipline,
                           coordination=coordination, knowledge=knowledge,
                           spirit=spirit, dateLabel=dateLabel, countdown=countdown,
                           lessonDone=lessonDone, myRemarks=myRemarks)


def messageEncode(message):
    message_bytes = message.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    return base64_bytes.decode('ascii')

def messageDecode(message):
    base64_bytes = message.encode('ascii')
    message_bytes = base64.b64decode(base64_bytes)
    return int(message_bytes.decode('ascii'))