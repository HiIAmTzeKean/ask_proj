from flaskapp import db, LoginManager
from datetime import datetime
from sqlalchemy.orm import validates
from sqlalchemy.dialects.postgresql import JSON
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash


class user(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    clearance = db.Column(db.Integer, nullable=False)

    @validates('clearance')
    def validate_clearance(self, key, clearance):
        if not 1 <= clearance <= 3:
            raise AssertionError(
                'Clearance should be an int value form 1 to 3')
        return clearance @ validates('clearance')

    def __init__(self, username='', password='', clearance=3):
        self.username = username
        self.password = generate_password_hash(password).decode('utf8')

    def check_password(self, password_str):
        # return check_password_hash(self.password, password_str)
        return self.password == password_str

    def __repr__(self):
        return '<User {}>'.format(self.username)


class dojo(db.Model):
    '''
    name
    '''
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    instructor = db.Column(db.Text, nullable=False)

    student = db.relationship('student', back_populates='dojo')
    studentStatus = db.relationship('studentStatus', back_populates='dojo')

    def __init__(self, name, instructor):
        self.name = name
        self.instructor = instructor


    def __repr__(self):
        return '<Dojo {}>'.format(self.name)


class student(db.Model):
    '''
    name
    belt
    active
    last grading date
    Aggregate performance score
    '''
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    belt = db.Column(db.Text, nullable=False)
    lastGrading = db.Column(db.Date)
    active = db.Column(db.Boolean, nullable=False, default=True)

    dojo_id = db.Column(db.Integer, db.ForeignKey('dojo.id'), nullable=False)
    dojo = db.relationship('dojo', back_populates='student')
    
    studentStatus = db.relationship('studentStatus', back_populates='student')

    def __init__(self, name, lastGrading, dojo_id, active=True, belt='0'):
        self.name = name
        self.belt = belt
        self.lastGrading = lastGrading
        self.active = active
        self.dojo_id = dojo_id

    def __repr__(self):
        return '<Student {}>'.format(self.name)


class studentStatus(db.Model):
    '''
    date: date of record
    stauts: if student was present
    performance: {'Technique':0,'Ukemi':0,'Discipline':0,
    'Coordination':0,'Knowledge':0,'Spirit':0}
    term: {'term':1, 'year':YYYY}
    '''
    __tablename = "personnel_status"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Boolean, nullable=False, default=True)
    performance = db.Column(JSON)
    term = db.Column(JSON, nullable=False)

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    student = db.relationship('student', back_populates='studentStatus')

    dojo_id = db.Column(db.Integer, db.ForeignKey('dojo.id'), nullable=False)
    dojo = db.relationship('dojo', back_populates='studentStatus')

    def __init__(self, date, status, term, student_id, dojo_id, performance = None):
        self.date = date
        self.status = status
        self.performance = performance
        self.term = term
        self.student_id = student_id
        self.dojo_id = dojo_id

    def __repr__(self):
        return '<Record {} {}>'.format(self.date, self.student_id)
