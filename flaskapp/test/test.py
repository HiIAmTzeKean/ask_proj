import datetime
from flask import (Blueprint, flash, g, make_response,
    redirect, render_template, request, session, url_for)
from flaskapp import db
from flaskapp.models import Instructor

test_bp = Blueprint('test', __name__,)


@test_bp.route('/test', methods=('GET', 'POST'))
def test():
    record = Instructor.query.first()
    print(record.name)
    return 'hi'