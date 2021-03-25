import datetime
import json

from flask import (Blueprint, flash, g, make_response, redirect,
                   render_template, request, session, url_for)
from flaskapp import db
from flaskapp.models import Dojo, enrollment, lesson, student, studentStatus, instructor, belts
from flaskapp.instructor.form import formEditInstructor, formSearchStudent

instructor_bp = Blueprint('instructor', __name__,
                           template_folder='templates', static_folder='static')


#todo add instructor button
@instructor_bp.route('/instructorViewer', methods=('GET', 'POST'))
def instructorViewer():
    instructor_list = db.session.query(instructor).all()
    return render_template('instructor/instructorViewer.html',
                           instructor_list=instructor_list)


#todo show classes in this page as well
@instructor_bp.route('/instructorEditInstructor/<int:instructor_id>', methods=('GET', 'POST'))
def instructorEditInstructor(instructor_id):
    instructorRecord = db.session.query(instructor).filter_by(id=instructor_id).first()
    if instructorRecord.dateOfBirth:
        form = formEditInstructor(obj=instructorRecord,
                           dateOfBirth_month=int(instructorRecord.dateOfBirth.month),
                           dateOfBirth_year=int(instructorRecord.dateOfBirth.year))  # load values into form
    else:
        form = formEditInstructor(obj=instructorRecord)  # load values into form
    belt_list = db.session.query(belts.id, belts.beltName).all()
    form.belt_id.choices = [(belt.id, belt.beltName) for belt in belt_list]

    # update record in database if valid
    if form.validate_on_submit():  
        form.populate_obj(instructorRecord)
        date_str = '01{}{}'.format(form.dateOfBirth_month.data.zfill(2),form.dateOfBirth_year.data)
        instructorRecord.dateOfBirth = datetime.datetime.strptime(date_str, '%d%m%Y').date()
        db.session.commit()
        flash('Successfully updated {}!'.format(instructorRecord.firstName))
        return redirect(url_for('instructor.instructorViewer'))

    return render_template('instructor/instructorEditInstructor.html',
                           instructorRecord=instructorRecord, form=form)


@instructor_bp.route('/instructorDeleteStudent/<int:student_id>', methods=['GET'])
def instructorDeleteStudent(student_id):
    studentRecord = db.session.query(student).filter(student.id==student_id).first()
    db.session.delete(studentRecord)
    db.session.commit()
    return redirect(url_for('instructor.instructorSearchStudent'))


@instructor_bp.route('/instructorSearchStudent', methods=('GET', 'POST'))
def instructorSearchStudent():
    form = formSearchStudent()
    if request.args.get('searchStudent')=='True':
        serachString = request.args.get('serachString')
        serachBelt = request.args.get('serachBelt')
        if serachBelt == "":
            student_list = db.session.query(student).\
                filter(student.firstName.ilike('%{}%'.format(serachString))).all()
        else:
            student_list = db.session.query(student).\
                filter(student.firstName.ilike('%{}%'.format(serachString)), student.belt.ilike(serachBelt)).all()
    else:
                student_list = db.session.query(student.id,
                                    student.firstName,
                                    student.lastName,
                                    student.lastGrading,
                                    belts.beltName).\
            filter(student.belt_id == belts.id).all()
    if form.validate_on_submit():
        serachString = form.name.data
        serachBelt = form.belt.data
        return redirect(url_for('instructor.instructorSearchStudent',searchStudent='True', serachString=serachString, serachBelt=serachBelt))
    return render_template('instructor/instructorSearchStudent.html',student_list=student_list, form=form)