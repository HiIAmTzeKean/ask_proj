from flaskapp import db
from flaskapp.models import studentStatus, student

def get_studentRecord(student_id):
    return db.session.query(student).filter_by(id=student_id).first()