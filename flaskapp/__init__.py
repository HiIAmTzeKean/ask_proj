import os
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap

app = Flask(__name__, instance_relative_config=True, template_folder='templates')

# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

# load config
app.config.from_pyfile('config.py', silent=False)

#register blueprints
from .attendance import attendance
app.register_blueprint(attendance.attendance_bp)
app.add_url_rule('/', endpoint='attendance.attendanceStatus')

from .auth import auth
app.register_blueprint(auth.auth_bp)

# a simple page that says hello
@app.route('/hello')
def hello():
    return 'hello world'
