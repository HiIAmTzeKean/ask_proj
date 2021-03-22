from flaskapp import db
from flaskapp.models import dojo, studentStatus, student, enrollment


def get_dojoInstructorName(dojo_id):
    # get instructor id from dojo table
    found_id = db.session.query(
        dojo.instructor_id).filter_by(id=dojo_id).scalar()
    # get name from student table
    dojoInstructor = db.session.query(
        student.lastName).filter_by(id=found_id).scalar()
    return dojoInstructor


def get_dojoInstructorId(dojo_id):
    # get instructor id from dojo table
    found_id = db.session.query(
        dojo.instructor_id).filter_by(id=dojo_id).scalar()
    return found_id


def insert_studentStausRecord(status,student_id,lesson_id):
    lastRecord = db.session.query(studentStatus).\
                filter(studentStatus.student_id==student_id, studentStatus.status==True).\
                order_by(studentStatus.lesson_id.desc()).first()
    # insert last performance as current performance
    if lastRecord:
        record = studentStatus(status, student_id, lesson_id,lastRecord.performance)
    else:
        record = studentStatus(status, student_id, lesson_id)
    db.session.add(record)
    db.session.commit()
    return


def update_attendancePresent(status,student_id,lesson_id):
    record = studentStatus.query.filter_by(student_id=student_id, lesson_id=lesson_id).update({studentStatus.status: status})
    db.session.commit()
    return


def update_Act_DeactEnrollment(student_id, dojo_id, act_deact):
    record = db.session.query(enrollment).filter_by(student_id=student_id,dojo_id=dojo_id).first()
    if act_deact == 'act':
        record.studentActive = True
    elif act_deact == 'deact':
        record.studentActive = False
    db.session.commit()
    return


def insert_newStudent(firstName, lastName, lastGrading, dojo_id, belt='0'):
    record = student(firstName, lastName, lastGrading, dojo_id, active=True, belt=belt)
    db.session.add(record)
    db.session.commit()
    return


def insert_newEnrollment(student_id,dojo_id):
    record = enrollment(student_id,dojo_id)
    db.session.add(record)
    db.session.commit()
    return


def get_studentRecord(student_id):
    return db.session.query(student).filter_by(id=student_id).first()


def delete_studentEnrollmentRecord(student_id,dojo_id):
    record = db.session.query(enrollment).filter_by(student_id=student_id,dojo_id=dojo_id).first()
    db.session.delete(record)
    db.session.commit()
    return
