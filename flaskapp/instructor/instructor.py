import datetime

from flask import (Blueprint, flash, redirect,
                   render_template, request, url_for)
from flaskapp import db
from flaskapp.models import Student, Instructor, Belt
from flaskapp.instructor.form import formEditInstructor, formSearchStudent
from flaskapp.attendance.form import formAdd_DelStudent

instructor_bp = Blueprint('instructor', __name__,
                           template_folder='templates', static_folder='static')


#todo add instructor button
@instructor_bp.route('/instructorViewer', methods=('GET', 'POST'))
def instructorViewer():
    instructor_list = db.session.query(Instructor).all()

    form = formAdd_DelStudent(dojo_id=None, belt_id=int(1))
    belt_list = db.session.query(Belt.id, Belt.beltName).all()
    form.belt_id.choices = [(belt.id, belt.beltName) for belt in belt_list]

    return render_template('instructor/instructorViewer.html',
                           instructor_list=instructor_list, form=form)


#todo show classes in this page as well
@instructor_bp.route('/instructorEditInstructor/<string:instructor_membership>', methods=('GET', 'POST'))
def instructorEditInstructor(instructor_membership):
    instructorRecord = db.session.query(Instructor).filter_by(membership=instructor_membership).first()
    if instructorRecord.dateOfBirth:
        form = formEditInstructor(obj=instructorRecord,
                           dateOfBirth_month=int(instructorRecord.dateOfBirth.month),
                           dateOfBirth_year=int(instructorRecord.dateOfBirth.year))  # load values into form
    else:
        form = formEditInstructor(obj=instructorRecord)  # load values into form
    belt_list = db.session.query(Belt.id, Belt.beltName).all()
    form.belt_id.choices = [(belt.id, belt.beltName) for belt in belt_list]

    # update record in database if valid
    if form.validate_on_submit():  
        form.populate_obj(instructorRecord)
        if form.dateOfBirth_month.data:
            date_str = '01{}{}'.format(form.dateOfBirth_month.data.zfill(2),form.dateOfBirth_year.data)
            instructorRecord.dateOfBirth = datetime.datetime.strptime(date_str, '%d%m%Y').date()
        db.session.commit()
        flash('Successfully updated {}!'.format(instructorRecord.firstName))
        return redirect(url_for('instructor.instructorViewer'))

    return render_template('instructor/instructorEditInstructor.html',
                           instructorRecord=instructorRecord, form=form)


@instructor_bp.route('/instructorDeleteStudent/<int:student_id>', methods=['GET'])
def instructorDeleteStudent(student_id):
    studentRecord = db.session.query(Student).filter_by(id=student_id).first()
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
            student_list = db.session.query(Student).\
                filter(Student.firstName.ilike('%{}%'.format(serachString))).all()
        else:
            student_list = db.session.query(Student).\
                filter(Student.firstName.ilike('%{}%'.format(serachString)), Student.belt.ilike(serachBelt)).all()
    else:
                student_list = db.session.query(Student.id,
                                    Student.firstName,
                                    Student.lastName,
                                    Student.lastGrading,
                                    Belt.beltName).\
            filter(Student.belt_id == Belt.id).all()
    if form.validate_on_submit():
        serachString = form.name.data
        serachBelt = form.belt.data
        return redirect(url_for('instructor.instructorSearchStudent',searchStudent='True', serachString=serachString, serachBelt=serachBelt))
    return render_template('instructor/instructorSearchStudent.html',student_list=student_list, form=form)