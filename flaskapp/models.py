from flaskapp import db, login_manager
from datetime import datetime
from sqlalchemy.orm import validates
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import check_password_hash, generate_password_hash

class user(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    clearance = db.Column(db.Integer, nullable=False)

    @validates('clearance')
    def validate_clearance(self, key, clearance):
        if not 1 <= clearance <= 3:
            raise AssertionError('Clearance should be an int value form 1 to 3') 
        return clearance @validates('clearance')

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
    
    student = db.relationship('student', back_populates='dojo')

    def __init__(self, belt, name, fmw_id, active=True):
        self.name = name
        
    def __repr__(self):
        return '<Dojo {}>'.format(self.name)

class student(db.Model):
    '''
    name
    belt
    active
    last grading date
    performance score
    '''
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    belt = db.Column(db.Text, nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)

    dojo_id = db.Column(db.Integer, db.ForeignKey('dojo.id'), nullable=False)
    dojo = db.relationship('dojo',back_populates='student')
    status = db.relationship('student_Status', back_populates='student')

    def __init__(self, belt, name, fmw_id, active=True):
        self.belt = belt
        self.name = name
        self.active = active
        self.dojo_id = dojo_id
        
    def __repr__(self):
        return '<Student {}>'.format(self.name)

class student_Status(db.Model):
    '''
    date: date of record
    stauts: if student was present
    term: 1/2/3/4 _space_ year
    '''
    __tablename = "personnel_status"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Boolean, nullable=False, default=True)

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    student = db.relationship('student', back_populates='status')
    
    def __init__(self, date, status, personnel_id):
        self.date = date
        self.status = status
        self.student_id = student_id

    def __repr__(self):
        return '<Record {}>'.format(self.date)