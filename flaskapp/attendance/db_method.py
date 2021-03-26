from flaskapp import db
from flaskapp.models import Dojo, StudentStatus, Student, Enrollment


def get_dojoInstructorName(dojo_id):
    # get instructor id from dojo table
    found_id = db.session.query(
        Dojo.instructor_id).filter_by(id=dojo_id).scalar()
    # get name from student table
    dojoInstructor = db.session.query(
        Student.lastName).filter_by(id=found_id).scalar()
    return dojoInstructor


def get_dojoInstructorId(dojo_id):
    # get instructor id from dojo table
    found_id = db.session.query(
        Dojo.instructor_id).filter_by(id=dojo_id).scalar()
    return found_id


def insert_studentStausRecord(status,student_id,lesson_id):
    lastRecord = db.session.query(StudentStatus).\
                filter(StudentStatus.student_id==student_id, StudentStatus.status==True).\
                order_by(StudentStatus.lesson_id.desc()).first()
    # insert last performance as current performance
    if lastRecord:
        record = StudentStatus(status, student_id, lesson_id)
        record.technique = lastRecord.technique
        record.ukemi = lastRecord.ukemi
        record.knowledge = lastRecord.knowledge
        record.coordination =lastRecord.coordination
        record.discipline =lastRecord.discipline
        record.spirit =lastRecord.spirit
    else:
        record = StudentStatus(status, student_id, lesson_id)
    db.session.add(record)
    db.session.commit()
    return


def update_attendancePresent(status,student_id,lesson_id):
    record = StudentStatus.query.filter_by(student_id=student_id, lesson_id=lesson_id).update({StudentStatus.status: status})
    db.session.commit()
    return


def update_Act_DeactEnrollment(student_id, dojo_id, act_deact):
    record = db.session.query(Enrollment).filter_by(student_id=student_id,dojo_id=dojo_id).first()
    if act_deact == 'act':
        record.studentActive = True
    elif act_deact == 'deact':
        record.studentActive = False
    db.session.commit()
    return


def insert_newEnrollment(student_id,dojo_id):
    record = Enrollment(student_id,dojo_id)
    db.session.add(record)
    db.session.commit()
    return


def get_studentRecord(student_id):
    return db.session.query(Student).filter_by(id=student_id).first()


def delete_studentEnrollmentRecord(student_id,dojo_id):
    record = db.session.query(Enrollment).filter_by(student_id=student_id, dojo_id=dojo_id).first()
    db.session.delete(record)
    db.session.commit()
    return
