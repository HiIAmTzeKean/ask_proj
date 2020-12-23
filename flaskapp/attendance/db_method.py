from flaskapp import db
from flaskapp.models import dojo, studentStatus, student


def get_dojoName(dojo_id):
    dojoName = db.session.query(dojo.name).filter_by(id=dojo_id).scalar()
    return dojoName


def get_dojoInstructor(dojo_id):
    dojoInstructor = db.session.query(
        dojo.instructor).filter_by(id=dojo_id).scalar()
    return dojoInstructor


def get_dojoInfo(dojo_id,dojoName=False,dojoInstructor=False):
    if dojoName == True:
        return get_dojoName(dojo_id)
    if dojoInstructor == True:
        return get_dojoInstructor(dojo_id)
    return get_dojoName(dojo_id), get_dojoInstructor(dojo_id)


def insert_attendancePresent(date, status, term, student_id, dojo_id):
    presentFlag = get_attendancePresent(date, student_id)
    if presentFlag:
        update_attendancePresent(record=presentFlag, status=status)
        return
    record = studentStatus(date, status, term, student_id, dojo_id)
    db.session.add(record)
    db.session.commit()
    return


def update_attendancePresent(record, status):
    record.status = status
    db.session.commit()
    return


def get_attendancePresent(date, student_id):
    return db.session.query(studentStatus).filter_by(date=date, student_id=student_id).first()


def update_activateStudent(record):
    record.active = True
    db.session.commit()
    return


def update_deactivateStudent(record):
    record.active = False
    db.session.commit()
    return


def update_Act_DeactStudent(student_id, act_deact):
    record = db.session.query(student).filter_by(id=student_id).first()
    if act_deact == 'act':
        update_activateStudent(record)
    elif act_deact == 'deact':
        update_deactivateStudent(record)
    else:
        pass
    return


def insert_newStudent(name, lastGrading, dojo_id, belt='0'):
    record = student(name, lastGrading, dojo_id, active=True, belt=belt)
    db.session.add(record)
    db.session.commit()
    return


def get_student(student_id):
    return db.session.query(student).filter_by(id=student_id).first()


def delete_student(student_id):
    record = get_student(student_id)
    db.session.delete(record)
    db.session.commit()
    return

def update_student(student_id, name, belt, lastGrading, dojo_id):
    record = get_student(student_id)
    record.name = name
    record.belt = belt
    record.lastGrading = lastGrading
    record.dojo_id = dojo_id
    db.session.commit()
    return
