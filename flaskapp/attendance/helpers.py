def findTerm(date):
  currentMonth = date.month
  if currentMonth <=3: return 1
  if currentMonth>3 and currentMonth<=6: return 2
  if currentMonth>6 and currentMonth<=9: return 3
  if currentMonth>9: return 4

def str_to_date(string):
  from datetime import datetime
  return datetime.strptime(string,'%Y-%m-%d').date()

def belt_type():
  return [
    ('White','White'),
    ('12 Kyu','12 Kyu'),
    ('11 Kyu','11 Kyu'),
    ('10 Kyu','10 Kyu'),
    ('9 Kyu','9 Kyu'),
    ('8 Kyu','8 Kyu'),
    ('7 Kyu','7 Kyu'),
    ('6 Kyu','6 Kyu'),
    ('5 Kyu','5 Kyu'),
    ('4 Kyu','4 Kyu'),
    ('3 Kyu','3 Kyu'),
    ('2 Kyu','2 Kyu'),
    ('1 Kyu','1 Kyu'),
    ('2 Dan','2 Dan'),
    ('3 Dan','3 Dan'),
    ('4 Dan','4 Dan'),
    ('5 Dan','5 Dan'),
    ('6 Dan','6 Dan'),
    ('7 Dan','7 Dan')
  ]