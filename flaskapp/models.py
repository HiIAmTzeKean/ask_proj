from flaskapp import db
from sqlalchemy.dialects.postgresql import JSON
from flask_security import UserMixin, RoleMixin
from sqlalchemy.dialects.postgresql import JSONB


roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.Text, nullable=False)
    active = db.Column(db.Boolean(), default=True)
    confirmed_at = db.Column(db.DateTime())

    student_membership = db.Column(db.Text, db.ForeignKey('student.membership', ondelete="CASCADE",onupdate="CASCADE"))
    student = db.relationship('Student', back_populates='user')

    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'),
                            cascade="all, delete", passive_deletes=True)

    
class Student(db.Model):
    __mapper_args__ = {'polymorphic_identity': 'student'}
    id = db.Column(db.Integer, primary_key=True)
    membership = db.Column(db.Text, unique=True)
    firstName = db.Column(db.Text)
    lastName = db.Column(db.Text, nullable=True)
    belt = db.Column(db.Text, nullable=True)
    lastGrading = db.Column(db.Date, nullable=True)
    active = db.Column(db.Boolean, nullable=False, default=True) # active as a student
    dateOfBirth = db.Column(db.Date, nullable=True)

    belt_id = db.Column(db.Integer, db.ForeignKey('belt.id', ondelete="SET NULL",onupdate="CASCADE"))
    belt = db.relationship('Belt', back_populates='student')

    user = db.relationship('User', back_populates='student', cascade="all, delete", passive_deletes=True)
    instructor = db.relationship('Instructor', back_populates='student', cascade="all, delete", passive_deletes=True)
    enrollment = db.relationship('Enrollment', back_populates='student', cascade="all, delete", passive_deletes=True)
    studentStatus = db.relationship('StudentStatus', back_populates='student', cascade="all, delete", passive_deletes=True)
    studentRemarks = db.relationship('StudentRemarks', back_populates='student', cascade="all, delete", passive_deletes=True)
    answers = db.relationship('Answer', back_populates='student', cascade="all, delete", passive_deletes=True)
    
    
    def __init__(self, firstName, lastName, lastGrading, active=True):
        self.firstName = firstName
        self.lastName = lastName
        self.lastGrading = lastGrading
        self.active = active

    def __repr__(self):
        return '<Student {}>'.format(self.firstName)


class Instructor(Student):
    __mapper_args__ = {'polymorphic_identity': 'instructor'}
    mymembership = db.Column(db.String, db.ForeignKey('student.membership',ondelete="CASCADE",onupdate="CASCADE"), primary_key=True, unique=True)

    student = db.relationship('Student', back_populates='instructor')
    lesson = db.relationship('Lesson', back_populates='instructor')
    dojo = db.relationship('Dojo', back_populates='instructor')
    studentRemarks = db.relationship('StudentRemarks', back_populates='instructor', cascade="all, delete", passive_deletes=True)
    
    def __repr__(self):
        return '<Instructor {}>'.format(self.mymembership)


class Dojo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    location = db.Column(db.Text, nullable=False)
    region = db.Column(db.Text, nullable=True)
    isHQ = db.Column(db.Boolean, nullable=True, default=True)
    
    instructor_membership = db.Column(db.Text, db.ForeignKey('instructor.mymembership', ondelete="SET NULL",onupdate="CASCADE"))
    instructor = db.relationship('Instructor', back_populates='dojo')

    enrollment = db.relationship('Enrollment', back_populates='dojo', cascade="all, delete", passive_deletes=True)
    lesson = db.relationship('Lesson', back_populates='dojo', cascade="all, delete", passive_deletes=True)
    studentRemarks = db.relationship('StudentRemarks', back_populates='dojo', cascade="all, delete", passive_deletes=True)

    def __init__(self, name, region, isHQ=True):
        self.name = name
        self.region = region
        self.isHQ = isHQ

    def __repr__(self):
        return '<Dojo {}>'.format(self.name)


class StudentStatus(db.Model):
    status = db.Column(db.Boolean, nullable=False, default=True)
    evaluated = db.Column(db.Boolean, default=False)

    technique = db.Column(db.Integer,nullable=False, default=5)
    ukemi = db.Column(db.Integer, nullable=False, default=5)
    discipline = db.Column(db.Integer, nullable=False, default=5)
    coordination = db.Column(db.Integer, nullable=False, default=5)
    knowledge = db.Column(db.Integer, nullable=False, default=5)
    spirit = db.Column(db.Integer, nullable=False,  default=5)

    student_membership = db.Column(db.Text, db.ForeignKey('student.membership', ondelete="CASCADE",onupdate="CASCADE"), primary_key=True)
    student = db.relationship('Student', back_populates='studentStatus')

    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id', ondelete="CASCADE"), primary_key=True)
    lesson = db.relationship('Lesson', back_populates='studentStatus')
    
    
    def __init__(self, status, student_membership, lesson_id):
        self.status = status
        self.student_membership = student_membership
        self.lesson_id = lesson_id

    def __repr__(self):
        return '<studentStatus {} {}>'.format(self.status, self.student_membership)


class StudentRemarks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    remarks = db.Column(db.String, nullable=False, default='')
    date = db.Column(db.Date, nullable=False)

    dojo_id = db.Column(db.Integer, db.ForeignKey('dojo.id', ondelete="SET NULL"))
    dojo = db.relationship('Dojo', back_populates='studentRemarks')

    instructor_membership = db.Column(db.Text, db.ForeignKey('instructor.mymembership', ondelete="SET NULL",onupdate="CASCADE"))
    instructor = db.relationship('Instructor', back_populates='studentRemarks', foreign_keys=[instructor_membership])

    student_membership = db.Column(db.Text, db.ForeignKey('student.membership', ondelete="CASCADE",onupdate="CASCADE"), primary_key=True)
    student = db.relationship('Student', back_populates='studentRemarks', foreign_keys=[student_membership])

    
    def __init__(self, student_membership, dojo_id, instructor_id, remarks, date):
        self.student_membership = student_membership
        self.dojo_id = dojo_id
        self.instructor_id = instructor_id
        self.remarks = remarks
        self.date = date

    def __repr__(self):
        return '<studentRemark {}>'.format(self.student_membership)


class Enrollment(db.Model):
    # active in class
    studentActive = db.Column(db.Boolean, nullable=False, default=True)
    

    student_membership = db.Column(db.Text, db.ForeignKey('student.membership', ondelete="CASCADE",onupdate="CASCADE"), primary_key=True)
    student = db.relationship('Student', back_populates='enrollment')

    dojo_id = db.Column(db.Integer, db.ForeignKey('dojo.id', ondelete="CASCADE",onupdate="CASCADE"), primary_key=True)
    dojo = db.relationship('Dojo', back_populates='enrollment')

    def __init__(self, student_membership, dojo_id):
        self.student_membership = student_membership
        self.dojo_id = dojo_id

    def __repr__(self):
        return '<Enrollment {} {}>'.format(self.student_membership, self.dojo_id)


class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    term = db.Column(db.Integer, nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    techniquesTaught = db.Column(JSONB, nullable=True)

    dojo_id = db.Column(db.Integer, db.ForeignKey('dojo.id', ondelete="CASCADE",onupdate="CASCADE"), nullable=False)
    dojo = db.relationship('Dojo', back_populates='lesson')


    instructor_membership = db.Column(db.Text, db.ForeignKey('instructor.mymembership', ondelete="SET NULL",onupdate="CASCADE"))
    instructor = db.relationship('Instructor', back_populates='lesson')

    studentStatus = db.relationship('StudentStatus', back_populates='lesson', cascade="all, delete", passive_deletes=True)

    def __init__(self, date, term, dojo_id, instructor_membership):
        self.date = date
        self.term = term
        self.dojo_id = dojo_id
        self.instructor_membership = instructor_membership

    def __repr__(self):
        return '<Record {} {}>'.format(self.date, self.dojo_id)


class Belt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    beltName = db.Column(db.Text, nullable=False)
    beltColor = db.Column(db.Text, nullable=True)
    lessonNeeded = db.Column(db.Integer, nullable=False)
    timespanNeeded = db.Column(db.Integer, nullable=False) # months to wait

    student = db.relationship('Student', back_populates='belt', cascade="all, delete", passive_deletes=True)

    def __init__(self, beltName, lessonNeeded, timespanNeeded):
        self.beltName = beltName
        self.lessonNeeded = lessonNeeded
        self.timespanNeeded = timespanNeeded

    def __repr__(self):
        return '<belt {}>'.format(self.beltName)


class Survey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    isOpen = db.Column(db.Boolean, nullable=False, default=True)
    survey_question = db.relationship('SurveyQuestion', back_populates='survey', cascade="all, delete", passive_deletes=True)

    answers = db.relationship('Answer', back_populates='survey')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Survey {}>'.format(self.name)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    questionType = db.Column(db.Text, nullable=False)
    questionCategory = db.Column(db.Text, nullable=False)
    survey_question = db.relationship('SurveyQuestion', back_populates='question', cascade="all, delete", passive_deletes=True)

    def __init__(self, name, questionType):
        self.name = name
        self.questionType = questionType

    def __repr__(self):
        return '<Survey {}>'.format(self.name)


class SurveyQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('survey.id', ondelete="CASCADE",onupdate="CASCADE"))
    survey = db.relationship('Survey', back_populates='survey_question')

    question_id = db.Column(db.Integer, db.ForeignKey('question.id', ondelete="CASCADE",onupdate="CASCADE"))
    question = db.relationship('Question', back_populates='survey_question')

    def __init__(self, survey_id, question_id):
        self.survey_id = survey_id
        self.question_id = question_id

    def __repr__(self):
        return '<Survey_Question {}>'.format(self.id)


class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    studentAnswer = db.Column(JSONB, nullable=False)

    student_membership = db.Column(db.Text, db.ForeignKey('student.membership', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    student = db.relationship('Student', back_populates='answers')

    survey_id = db.Column(db.Integer, db.ForeignKey('survey.id', ondelete="CASCADE",onupdate="CASCADE"), nullable=False)
    survey = db.relationship('Survey', back_populates='answers')

    def __init__(self, date, studentAnswer, student_membership, survey_id):
        self.date = date
        self.studentAnswer = studentAnswer
        self.student_membership = student_membership
        self.survey_id = survey_id

    def __repr__(self):
        return '<Answer {}>'.format(self.id)
