import datetime

from flask import (Blueprint, flash, redirect,
                   render_template, url_for)
from flaskapp import db
from flaskapp.models import Dojo, Instructor
from flaskapp.dojo.form import formEditDojo
from flask_security.decorators import roles_accepted

dojo_bp = Blueprint('dojo', __name__,
                    template_folder='templates',
                    static_folder='static',
                    url_prefix='/dojo')


@dojo_bp.route('/dojoViewer', methods=('GET', 'POST'))
@roles_accepted('Admin', 'HQ')
def dojoViewer():
    dojo_list = db.session.query(Dojo).order_by(Dojo.name.desc()).all()
    return render_template('dojo/dojoViewer.html', dojo_list=dojo_list)


@dojo_bp.route('/dojoEditDojo/<int:dojo_id>', methods=('GET', 'POST'))
@roles_accepted('Admin', 'HQ')
def dojoEditDojo(dojo_id):
    dojoRecord = db.session.query(Dojo).filter_by(id=dojo_id).first()
    form = formEditDojo(obj=dojoRecord) # load values into form
    instructor_list = Instructor.query.all()
    form.instructor_membership.choices = [(instructor.membership, instructor.firstName) for instructor in instructor_list]
    if form.validate_on_submit():  # update record in database if valid
        form.populate_obj(dojoRecord)
        db.session.commit()
        flash('Successfully updated!')
        return redirect(url_for('dojo.dojoEditDojo', dojo_id=dojo_id)) # return back same view page
    return render_template('dojo/dojoEditDojo.html', dojoRecord=dojoRecord, form=form)


@dojo_bp.route('/dojoAddDojo', methods=('GET', 'POST'))
@roles_accepted('Admin', 'HQ')
def dojoAddDojo():
    dojoRecord = Dojo(None,None)
    form = formEditDojo(obj=dojoRecord)
    instructor_list = Instructor.query.all()
    form.instructor_membership.choices = [(instructor.membership, instructor.firstName) for instructor in instructor_list]
    if form.validate_on_submit():
        form.populate_obj(dojoRecord)
        db.session.add(dojoRecord)
        db.session.commit()
        flash('Successfully added!')
        return redirect(url_for('dojo.dojoViewer'))
    return render_template('dojo/dojoAddDojo.html', form=form)


@dojo_bp.route('/dojoDelDojo/<int:dojo_id>', methods=('GET', 'POST'))
@roles_accepted('Admin', 'HQ')
def dojoDelDojo(dojo_id):
    dojoRecord = db.session.query(Dojo).filter_by(id=dojo_id).first()
    db.session.delete(dojoRecord)
    db.session.commit()
    flash('Successfully deleted!')
    return redirect(url_for('dojo.dojoViewer'))
