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
