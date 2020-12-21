from random import randint

# generate dojo
def generateDojo():
    for i in range(10):
        print('({},\'Dojo{}\',\'Robin\'),'.format(i, i))


def generateStudent():
    for i in range(100):
        print('(\'Person{}\',\'{} Kyu\',True,{}),'.format(
            i, randint(1, 10), randint(1, 10)))

def findDate():
  import datetime
  todayDate = datetime.datetime.today()
  print(todayDate.month)

if __name__ == "__main__":
    findDate()
