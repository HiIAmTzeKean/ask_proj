from random import randint

# generate dojo
def generateDojo():
    for i in range(11):
        print('({},\'Dojo{}\',\'Location{}\', 0),'.format(i, i, i))


def generateStudent():
    for i in range(100):
        print('({},\'Person{}\',\'Surname\',\'{} Kyu\',True),'.format(
            i, i, randint(0, 10)))

def generateEnrollment():
    for i in range(100):
        print('(TRUE,{},{}),'.format(
            i, i%10))

def findDate():
  import datetime
  todayDate = datetime.date.today()
  print(todayDate  - timedelta(days=days_to_subtract))

def generateLesson():
    # date starts from 10 days before today
    # term = 1
    # loop through all dojo_id
    import datetime
    count = 1
    for j in range (10):
        # per date
        lessonDate = datetime.date.today() - datetime.timedelta(days=(10-j))
        for i in range(10):
            # per dojo
            
            print("({},'{}',{},{},{}),".format(
                count, lessonDate, 1, i, 0))
            count+=1

def generatestudentStatus():
    for i in range(100):
        print('(TRUE,{},{}),'.format(
            i, i%10))



if __name__ == "__main__":
    generateStudent()
