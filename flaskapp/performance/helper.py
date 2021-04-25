from flaskapp import db
from flaskapp.models import (Lesson, Student, StudentRemarks,
                             StudentStatus, Belt)
import datetime


def helper_ChartView(student_membership, dojo_id=None):
    # ---- get student details
    studentRecord = db.session.query(Student.firstName,
                                     Student.lastGrading,
                                     Belt.beltName,
                                     Belt.beltColor,
                                     Belt.timespanNeeded)\
                        .filter(Student.membership==student_membership, Student.belt_id==Belt.id).first()

    # ---- get performance details
    if dojo_id != None:
        subquery = db.session.query(StudentStatus.technique,
                                    StudentStatus.ukemi,
                                    StudentStatus.discipline,
                                    StudentStatus.coordination,
                                    StudentStatus.knowledge,
                                    StudentStatus.spirit,
                                    Lesson.date).\
                    filter(StudentStatus.student_membership == student_membership,
                            StudentStatus.status == True,
                            StudentStatus.evaluated == True,
                            StudentStatus.lesson_id == Lesson.id,
                            Lesson.dojo_id == dojo_id).\
                    order_by(Lesson.date.asc()).limit(10).all()
    else:
        subquery = db.session.query(StudentStatus.technique,
                                    StudentStatus.ukemi,
                                    StudentStatus.discipline,
                                    StudentStatus.coordination,
                                    StudentStatus.knowledge,
                                    StudentStatus.spirit,
                                    Lesson.date).\
                    filter(StudentStatus.student_membership == student_membership,
                            StudentStatus.status == True,
                            StudentStatus.evaluated == True,
                            StudentStatus.lesson_id == Lesson.id).\
                    order_by(Lesson.date.asc()).limit(10).all()

    technique,ukemi,discipline,coordination,knowledge,spirit,dateLabel = processChartRecords(subquery)
    dateLabel = processDateLabel(dateLabel)

    # ---- get remarks
    myRemarks = db.session.query(StudentRemarks.remarks,
                                 StudentRemarks.date).\
                        filter_by(student_membership=student_membership).order_by(StudentRemarks.date.asc()).all()

    # ---- get number of days to grading
    countdown = daysToGrading(studentRecord)

    lessonDone=lessonAfterGrading(student_membership)

    return (studentRecord,
            technique, ukemi, discipline,
            coordination, knowledge,
            spirit, dateLabel, countdown,
            lessonDone, myRemarks)


def lessonAfterGrading(student_membership):
    # get last grading date
    lastGradingDate = db.session.query(Student.lastGrading).filter(Student.membership == student_membership).scalar()
    if lastGradingDate:
        # get lesson id after lastGrading date
        lessonID_start = db.session.query(Lesson.id).filter(Lesson.date>lastGradingDate).order_by(Lesson.id.asc()).first()
        # count number of records student have
        if lessonID_start:
            lessonsDone = db.session.query(StudentStatus.status).filter(StudentStatus.student_membership == student_membership,StudentStatus.lesson_id>lessonID_start,StudentStatus.status==True).count()
            return lessonsDone
        else:
            return 0
    else:
        lessonsDone = db.session.query(StudentStatus.status).filter(StudentStatus.student_membership == student_membership,StudentStatus.status==True).count()
        return lessonsDone


def processDateLabel(dateLabel):
    # print(dateLabel)
    if dateLabel == []:
        return []
    elif len(dateLabel)<5:
        return dateLabel
    else:
        return [label if (i+1)%(len(dateLabel)//5)==0 else '' for i,label in enumerate(dateLabel)]


def processChartRecords(subquery):
    if subquery == []:
        return [], [], [], [], [], [], []
    return [list(i) for i in zip(*subquery)]
        

def daysToGrading(studentRecord):
    if studentRecord.lastGrading:
        return int(datetime.date.today().month) - int(studentRecord.lastGrading.month) + studentRecord.timespanNeeded
    else:
        return None
