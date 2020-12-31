import datetime
from flask import (Blueprint, flash, g, make_response,
    redirect, render_template, request, session, url_for)
from flaskapp import db
from flaskapp.models import student, studentStatus, dojo, instructor

test_bp = Blueprint('test', __name__,)


@test_bp.route('/test', methods=('GET', 'POST'))
def test():
    record = instructor.query.first()
    print(record.name)
    return 'hi'