import os
from flask import Flask, render_template, request
from flask_wtf.csrf import CSRFProtect
from flask_security import Security, SQLAlchemyUserDatastore

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

# import models
from flaskapp.models import User, Role

from flaskapp.auth.form import ExtendedRegisterForm
# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore, confirm_register_form=ExtendedRegisterForm)

# mobile view
from flask_mobility import Mobility
mobilize = Mobility(app)

from flask_mail import Mail
mail = Mail(app)

# register blueprints
from .attendance import attendance
app.register_blueprint(attendance.attendance_bp)

from .performance import performance
app.register_blueprint(performance.performance_bp)

from .instructor import instructor
app.register_blueprint(instructor.instructor_bp)

from .dojo import dojo
app.register_blueprint(dojo.dojo_bp)

from .parent.parent import parent_bp
app.register_blueprint(parent_bp)

from .feedback.feedback import feedback_bp
app.register_blueprint(feedback_bp)

from .auth import auth
app.register_blueprint(auth.auth_bp)

app.add_url_rule('/', endpoint='security.login')

from .util import filters

# from flask_mail import Message
# @app.route("/lol")
# def lol():
#     msg = Message("Hello",recipients=["ngtzekean600@gmail.com"])
#     msg.body = "Hello Flask message sent from Flask-Mail"
#     mail.send(msg)
#     return 'done'

@app.errorhandler(404)
def handle_404(e):
    path = request.path

    # # go through each blueprint to find the prefix that matches the path
    # # can't use request.blueprint since the routing didn't match anything
    # for bp_name, bp in app.blueprints.items():
    #     if bp.url_prefix == None:
    #         continue
    #     if path.startswith(bp.url_prefix):
    #         # get the 404 handler registered by the blueprint
    #         handler = app.error_handler_spec.get(bp_name, {}).get(404)
    #         print(handler)
    #         if handler is not None:
    #             # if a handler was found, return it's response
    #             return handler.get(e)
    if path.startswith('/parent'):
        return render_template('404_parent.html'), 404
    # return a default response
    return render_template('404.html'), 404

@app.errorhandler(500)
def handle_500(e):
    return render_template('500.html'), 500
