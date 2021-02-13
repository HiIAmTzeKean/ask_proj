import datetime
import json

from flask import (Blueprint, flash, g, make_response, redirect,
                   render_template, request, session, url_for)
from flaskapp import db
from flaskapp.models import dojo, enrollment, lesson, student, studentStatus, instructor
from flaskapp.instructor.form import formEditInstructor

instructor_bp = Blueprint('instructor', __name__,
                           template_folder='templates', static_folder='static')


#todo add instructor button
@instructor_bp.route('/instructorViewer', methods=('GET', 'POST'))
def instructorViewer():
    instructor_list = db.session.query(instructor).all()
    return render_template('instructor/instructorViewer.html',
                           instructor_list=instructor_list)

#todo show classes in this page as well
@instructor_bp.route('/instructorEditInstructor/<instructor_id>', methods=('GET', 'POST'))
def instructorEditInstructor(instructor_id):
    instructorRecord = db.session.query(instructor).filter_by(id=instructor_id).first()
    form = formEditInstructor(obj=instructorRecord) # load values into form
    if form.validate_on_submit():  # update record in database if valid
        form.populate_obj(instructorRecord)
        db.session.commit()
        flash('Successfully updated!')
        return redirect(url_for('instructor.instructorEditInstructor', instructor_id=instructor_id)) # return back same view page
    return render_template('instructor/instructorEditInstructor.html', instructorRecord=instructorRecord,form=form)

#todo
@instructor_bp.route('/instructorSearchStudent', methods=('GET', 'POST'))
def instructorSearchStudent():
    form = formSearchStudent()
    if request.args.get('searchStudent')=='True':
        serachString = request.args.get('serachString')
        serachBelt = request.args.get('serachBelt')
        student_list = db.session.query(student).filter(student.name.ilike('%{}%'.format(serachString))).all() # case insensitive
    else:
        student_list = db.session.query(student).all()
    if form.validate_on_submit():
        serachString = form.name.data
        serachBelt = form.belt.data
        return redirect(url_for('instructor.instructorSearchStudent',searchStudent='True', serachString=serachString, serachBelt=serachBelt))
    return render_template('instructor/instructorSearchStudent.html',student_list=student_list, form=form)