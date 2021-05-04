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
    values = ['Technique','Ukemi','Discipline','Coordination','Knowledge','Spirit']
    from statistics import mean
    radar_data = [mean(i) for i in [technique,ukemi,discipline,coordination,knowledge,spirit]]
    lines_data = {'Technique':technique,'Ukemi':ukemi,'Discipline':discipline,'Coordination':coordination,'Knowledge':knowledge,'Spirit':spirit}

    lessonDone=lessonAfterGrading(student_membership)

    return (studentRecord,
            radar_data, lines_data, dateLabel, values,
            lessonDone, myRemarks)


def helper_RadarView(student_membership, dojo_id=None):
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

    radar_data,dateLabel = processChartRecords_Radar(subquery)
    dateLabel = processDateLabel(dateLabel)

    # ---- get remarks
    myRemarks = db.session.query(StudentRemarks.remarks,
                                 StudentRemarks.date).\
                        filter_by(student_membership=student_membership).order_by(StudentRemarks.date.asc()).all()

    # ---- get number of days to grading
    values = ['Technique','Ukemi','Discipline','Coordination','Knowledge','Spirit']

    lessonDone=lessonAfterGrading(student_membership)
    
    return (studentRecord,radar_data,
            dateLabel, values,
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
    if dateLabel == []:
        return []
    else:
        dateLabel = [i.strftime("%d-%b") for i in dateLabel]
        return dateLabel


def processChartRecords(subquery):
    if subquery == []:
        return [], [], [], [], [], [], []
    return [list(i) for i in zip(*subquery)]


def processChartRecords_Radar(subquery):
    if subquery == []:
        return [], []
    temp = [list(i) for i in zip(*subquery)]
    print(temp)
    return temp[0:-1],temp[-1]   


def daysToGrading(studentRecord):
    if studentRecord.lastGrading:
        return int(datetime.date.today().month) - int(studentRecord.lastGrading.month) + studentRecord.timespanNeeded
    else:
        return None
