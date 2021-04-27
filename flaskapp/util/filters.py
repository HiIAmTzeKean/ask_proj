from flaskapp import app

@app.template_filter('remove_punctuations')
def remove_punctuations(text):
    import string
    return text.translate(str.maketrans('', '', string.punctuation)).replace(' ','')

@app.template_filter('check_next')
def check_next(myList, element):
    if myList.index(element) == len(myList)-1:
        return False
    else: return True

@app.template_filter('remove_spaces')
def remove_spaces(text):
    return text.replace(' ','')

@app.template_filter('concat_string_withoutspaces')
def concat_string_withoutspaces(text1,text2):
    return text1.replace(' ','-') + text2.replace(' ','-')

@app.template_filter('date_formatter')
def date_formatter(date,formatter="%d %b %Y"):    
    return date.strftime(formatter)