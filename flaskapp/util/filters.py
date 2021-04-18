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
