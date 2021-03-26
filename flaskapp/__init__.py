import os
from flask import Flask
from flask_wtf.csrf import CSRFProtect


app = Flask(__name__, instance_relative_config=True,
            template_folder='templates')


# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass


# load config
app.config.from_object(os.environ['APP_SETTINGS'])
csrf = CSRFProtect(app)

# connect database to app
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

from flask_migrate import Migrate
migrate = Migrate(app, db)

from flask_mobility import Mobility
mobilize = Mobility(app)

# import models 
from flaskapp import models


# register blueprints
from .attendance import attendance
app.register_blueprint(attendance.attendance_bp)
app.add_url_rule('/', endpoint='attendance.attendanceDojoSelect')


from .performance import performance
app.register_blueprint(performance.performance_bp)

from .instructor import instructor
app.register_blueprint(instructor.instructor_bp)

from .dojo import dojo
app.register_blueprint(dojo.dojo_bp)

from .parent import parent
app.register_blueprint(parent.parent_bp)

from .auth import auth
app.register_blueprint(auth.auth_bp)

from .test import test
app.register_blueprint(test.test_bp)

# a simple page that says hello
@app.route('/hello')
def hello():
    return 'hello world'
