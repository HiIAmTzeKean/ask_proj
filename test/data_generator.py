from random import randint

# generate dojo
def generateDojo():
    for i in range(11):
        print('({},\'Dojo{}\',\'Location{}\', 0),'.format(i, i, i))


def generateStudent():
    for i in range(100):
        print('({},\'Person{}\',\'{} Kyu\',True),'.format(
            i, i, randint(0, 10)))

def generateEnrollment():
    for i in range(100):
        print('({},{}),'.format(
            i, randint(0, 10)))

def findDate():
  import datetime
  todayDate = datetime.datetime.today()
  print(todayDate.month)

if __name__ == "__main__":
    generateDojo()
