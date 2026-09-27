from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email
from datetime import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

bootstrap = Bootstrap(app)
moment = Moment(app)


class NameForm(FlaskForm):
    name = StringField(
        'What is your name?',
        validators=[DataRequired()]
    )

    email = StringField(
        'What is your UofT Email address?',
        validators=[DataRequired(), Email()]
    )

    submit = SubmitField('Submit')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    message = None

    if form.validate_on_submit():

        # Warn whenever the submitted name is different
        # from the previously submitted name
        if session.get('name') is not None:
            if session.get('name') != form.name.data:
                flash('Looks like you have changed your name!')

        # Warn whenever the submitted email is different
        # from the previously submitted email
        if session.get('submitted_email') is not None:
            if session.get('submitted_email') != form.email.data:
                flash('Looks like you have changed your email!')

        # Remember what was submitted
        session['name'] = form.name.data
        session['submitted_email'] = form.email.data

        # Check for UofT email
        if 'utoronto' in form.email.data.lower():
            session['email'] = form.email.data

            return redirect(url_for('index'))

        else:
            # Keep previous warning format
            session['email'] = None
            message = 'Please fill in a UofT email address.'

    return render_template(
        'index.html',
        form=form,
        name=session.get('name'),
        email=session.get('email'),
        message=message,
        current_time=datetime.utcnow()
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)