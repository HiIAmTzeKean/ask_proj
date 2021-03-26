from flaskapp import db
from flaskapp.models import Student

def get_studentRecord(student_id):
    return db.session.query(Student).filter_by(id=student_id).first()