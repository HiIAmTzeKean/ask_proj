from flaskapp import db
from datetime import datetime
from sqlalchemy.orm import validates
from sqlalchemy.dialects.postgresql import JSON
from werkzeug.security import check_password_hash, generate_password_hash
import json

class user(db.Model):
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


class Dojo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    location = db.Column(db.Text, nullable=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructor.id', ondelete="SET NULL"))

    instructor = db.relationship('Instructor', back_populates='dojo')
    enrollment = db.relationship('Enrollment', back_populates='dojo', cascade="all, delete", passive_deletes=True)
    lesson = db.relationship('Lesson', back_populates='dojo', cascade="all, delete", passive_deletes=True)
    studentRemarks = db.relationship('StudentRemarks', back_populates='dojo', cascade="all, delete", passive_deletes=True)

    def __init__(self, name, location,instructor_id):
        self.name = name
        self.location = location
        self.instructor_id = instructor_id

    def __repr__(self):
        return '<Dojo {}>'.format(self.name)


class Student(db.Model):
    __mapper_args__ = {'polymorphic_identity': 'student'}
    # __table_args__ = (Index('my_index', "a", "b"), )
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.Text, nullable=False)
    lastName = db.Column(db.Text, nullable=False)
    belt = db.Column(db.Text, nullable=True)
    lastGrading = db.Column(db.Date, nullable=True)
    active = db.Column(db.Boolean, nullable=False, default=True) # active as a student
    membership = db.Column(db.Text, unique=True, nullable=True)
    dateOfBirth = db.Column(db.Date, nullable=True)

    belt_id = db.Column(db.Integer, db.ForeignKey('belt.id', ondelete="SET NULL"))
    belt = db.relationship('Belt', back_populates='student')

    enrollment = db.relationship('Enrollment', back_populates='student', cascade="all, delete", passive_deletes=True)
    studentStatus = db.relationship('StudentStatus', back_populates='student', cascade="all, delete", passive_deletes=True)
    studentRemarks = db.relationship('StudentRemarks', back_populates='student', cascade="all, delete", passive_deletes=True)
    
    
    def __init__(self, firstName, lastName, lastGrading, active=True):
        self.firstName = firstName
        self.lastName = lastName
        self.lastGrading = lastGrading
        self.active = active

    def __repr__(self):
        return '<Student {}>'.format(self.firstName)


class Instructor(Student):
    __mapper_args__ = {'polymorphic_identity': 'instructor'}
    id = db.Column(db.Integer, db.ForeignKey('student.id'), primary_key=True)
    email = db.Column(db.String(255), unique=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    # password = db.Column(db.Text, nullable=False)

    lesson = db.relationship('Lesson', back_populates='instructor')
    dojo = db.relationship('Dojo', back_populates='instructor')
    studentRemarks = db.relationship('StudentRemarks', back_populates='instructor', cascade="all, delete", passive_deletes=True)

    def __init__(self, username):
        self.username = username
    
    def __repr__(self):
        return '<Instructor {}>'.format(self.username)


class StudentStatus(db.Model):
    status = db.Column(db.Boolean, nullable=False, default=True)
    evaluated = db.Column(db.Boolean, default=False)

    technique = db.Column(db.Integer,  default=5)
    ukemi = db.Column(db.Integer,  default=5)
    discipline = db.Column(db.Integer, default=5)
    coordination = db.Column(db.Integer, default=5)
    knowledge = db.Column(db.Integer, default=5)
    spirit = db.Column(db.Integer,  default=5)

    student_id = db.Column(db.Integer, db.ForeignKey('student.id', ondelete="CASCADE"), primary_key=True)
    student = db.relationship('Student', back_populates='studentStatus')

    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id', ondelete="CASCADE"), primary_key=True)
    lesson = db.relationship('Lesson', back_populates='studentStatus')
    
    
    def __init__(self, status, student_id, lesson_id):
        self.status = status
        self.student_id = student_id
        self.lesson_id = lesson_id

    def __repr__(self):
        return '<studentStatus {} {}>'.format(self.status, self.student_id)


class StudentRemarks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    remarks = db.Column(db.String, nullable=False, default='')
    date = db.Column(db.Date, nullable=False)

    dojo_id = db.Column(db.Integer, db.ForeignKey('dojo.id', ondelete="SET NULL"))
    dojo = db.relationship('Dojo', back_populates='studentRemarks')

    instructor_id = db.Column(db.Integer, db.ForeignKey('instructor.id', ondelete="SET NULL"))
    instructor = db.relationship('Instructor', back_populates='studentRemarks', foreign_keys=[instructor_id])

    student_id = db.Column(db.Integer, db.ForeignKey('student.id', ondelete="CASCADE"), primary_key=True)
    student = db.relationship('Student', back_populates='studentRemarks', foreign_keys=[student_id])
    
    def __init__(self, student_id, dojo_id, instructor_id, remarks, date):
        self.student_id = student_id
        self.dojo_id = dojo_id
        self.instructor_id = instructor_id
        self.remarks = remarks
        self.date = date

    def __repr__(self):
        return '<studentRemark {}>'.format(self.student_id)


class Enrollment(db.Model):
    studentActive = db.Column(db.Boolean, nullable=False, default=True) # active in class
    
    student_id = db.Column(db.Integer, db.ForeignKey('student.id', ondelete="CASCADE"), primary_key=True)
    student = db.relationship('Student', back_populates='enrollment')

    dojo_id = db.Column(db.Integer, db.ForeignKey('dojo.id', ondelete="CASCADE"), primary_key=True)
    dojo = db.relationship('Dojo', back_populates='enrollment')

    def __init__(self, student_id, dojo_id):
        self.student_id = student_id
        self.dojo_id = dojo_id

    def __repr__(self):
        return '<Enrollment {} {}>'.format(self.student_id, self.dojo_id)


class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    term = db.Column(db.Integer, nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    techniquesTaught = db.Column(JSON, nullable=True)

    dojo_id = db.Column(db.Integer, db.ForeignKey('dojo.id', ondelete="CASCADE"), nullable=False)
    dojo = db.relationship('Dojo', back_populates='lesson')

    instructor_id = db.Column(db.Integer, db.ForeignKey('instructor.id', ondelete="SET NULL"))
    instructor = db.relationship('Instructor', back_populates='lesson')

    studentStatus = db.relationship('StudentStatus', back_populates='lesson', cascade="all, delete", passive_deletes=True)

    def __init__(self, date, term, dojo_id, instructor_id):
        self.date = date
        self.term = term
        self.dojo_id = dojo_id
        self.instructor_id = instructor_id

    def __repr__(self):
        return '<Record {} {}>'.format(self.date, self.dojo_id)


class Belt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    beltName = db.Column(db.Text, nullable=False)
    lessonNeeded = db.Column(db.Integer, nullable=False)
    timespanNeeded = db.Column(db.Integer, nullable=False) # months to wait

    student = db.relationship('Student', back_populates='belt', cascade="all, delete", passive_deletes=True)

    def __init__(self, beltName, lessonNeeded, timespanNeeded):
        self.beltName = beltName
        self.lessonNeeded = lessonNeeded
        self.timespanNeeded = timespanNeeded

    def __repr__(self):
        return '<belt {}>'.format(self.beltName)