from flask import (
    Flask,
    render_template,
    session,
    redirect,
    url_for,
    flash,
    request
)
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

        # Warn if the submitted name changed
        if session.get('name') is not None:
            if session.get('name') != form.name.data:
                flash('Looks like you have changed your name!')

        # Warn if the submitted email changed
        if session.get('submitted_email') is not None:
            if session.get('submitted_email') != form.email.data:
                flash('Looks like you have changed your email!')

        session['name'] = form.name.data
        session['submitted_email'] = form.email.data

        # Valid UofT email
        if 'utoronto' in form.email.data.lower():
            session['email'] = form.email.data

            # Start a fresh chatbot conversation
            session['chat_history'] = []

            return redirect(url_for('chat'))

        # Invalid UofT email
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


@app.route('/chat', methods=['GET', 'POST'])
def chat():

    # Prevent direct access without logging in
    if not session.get('name') or not session.get('email'):
        return redirect(url_for('index'))

    chat_history = session.get('chat_history', [])

    if request.method == 'POST':
        user_message = request.form.get('message', '').strip()

        if user_message:

            # Store user's message in chat history
            chat_history.append({
                'sender': 'User',
                'message': user_message
            })

            lower_message = user_message.lower()

            # Example:
            # "My name is Alice."
            if lower_message.startswith('my name is '):

                remembered_name = user_message[11:].strip()

                # Remove punctuation from end
                remembered_name = remembered_name.rstrip('.!?')

                # Store chatbot memory in Flask session
                session['remembered_name'] = remembered_name

                bot_reply = (
                    f'Nice to meet you, {remembered_name}!'
                )

            # Example:
            # "What is my name?"
            elif 'what is my name' in lower_message:

                remembered_name = session.get('remembered_name')

                if remembered_name:
                    bot_reply = (
                        f'Your name is {remembered_name}.'
                    )
                else:
                    bot_reply = (
                        "I don't remember your name yet. "
                        "Tell me by saying 'My name is ...'"
                    )

            else:
                bot_reply = (
                    "I received your message. "
                    "You can tell me your name by saying "
                    "'My name is ...'"
                )

            # Store chatbot reply
            chat_history.append({
                'sender': 'Bot',
                'message': bot_reply
            })

            # Save updated history into Flask session
            session['chat_history'] = chat_history
            session.modified = True

            return redirect(url_for('chat'))

    return render_template(
        'chat.html',
        chat_history=chat_history
    )


@app.route('/logout')
def logout():

    # Clear all session information
    session.clear()

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )