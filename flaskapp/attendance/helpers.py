def findTerm(date):
  currentMonth = date.month
  if currentMonth <=3: return 1
  if currentMonth>3 and currentMonth<=6: return 2
  if currentMonth>6 and currentMonth<=9: return 3
  if currentMonth>9: return 4

def str_to_date(string):
  from datetime import datetime
  return datetime.strptime(string,'%Y-%m-%d').date()
