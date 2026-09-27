from flask import Flask, render_template, session, redirect, url_for
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

        # Check whether this is a UofT email
        if 'utoronto' in form.email.data.lower():
            session['name'] = form.name.data
            session['email'] = form.email.data

            return redirect(url_for('index'))

        else:
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
    app.run(debug=True)