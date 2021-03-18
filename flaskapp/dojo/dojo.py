import datetime

from flask import (Blueprint, flash, g, make_response, redirect,
                   render_template, request, session, url_for)
from flaskapp import db
from flaskapp.models import (dojo,instructor)
from flaskapp.dojo.form import formEditDojo, formConfirmAction

dojo_bp = Blueprint('dojo', __name__,
                    template_folder='templates',
                    static_folder='static',
                    url_prefix='/dojo')


#todo add dojo button
@dojo_bp.route('/dojoViewer', methods=('GET', 'POST'))
def dojoViewer():
    dojo_list = db.session.query(dojo).all()
    return render_template('dojo/dojoViewer.html', dojo_list=dojo_list)


@dojo_bp.route('/dojoEditDojo/<int:dojo_id>', methods=('GET', 'POST'))
def dojoEditDojo(dojo_id):
    dojoRecord = db.session.query(dojo).filter_by(id=dojo_id).first()
    form = formEditDojo(obj=dojoRecord) # load values into form
    instructor_list = instructor.query.all()
    form.instructor_id.choices = [(instructor.id, instructor.firstName) for instructor in instructor_list]
    if form.validate_on_submit():  # update record in database if valid
        form.populate_obj(dojoRecord)
        db.session.commit()
        flash('Successfully updated!')
        return redirect(url_for('dojo.dojoEditDojo', dojo_id=dojo_id)) # return back same view page
    return render_template('dojo/dojoEditDojo.html', dojoRecord=dojoRecord, form=form)


@dojo_bp.route('/dojoAddDojo', methods=('GET', 'POST'))
def dojoAddDojo():
    dojoRecord = dojo(None,None,None)
    form = formEditDojo(obj=dojoRecord)
    instructor_list = instructor.query.all()
    form.instructor_id.choices = [(instructor.id, instructor.firstName) for instructor in instructor_list]
    if form.validate_on_submit():
        form.populate_obj(dojoRecord)
        db.session.add(dojoRecord)
        db.session.commit()
        flash('Successfully added!')
        return redirect(url_for('dojo.dojoViewer'))
    return render_template('dojo/dojoAddDojo.html', form=form)

#create a confirm delete page
@dojo_bp.route('/dojoDelDojo/<int:dojo_id>', methods=('GET', 'POST'))
def dojoDelDojo(dojo_id):
    dojoRecord = db.session.query(dojo).filter_by(id=dojo_id).first()
    db.session.delete(dojoRecord)
    db.session.commit()
    flash('Successfully deleted!')
    return redirect(url_for('dojo.dojoViewer'))
