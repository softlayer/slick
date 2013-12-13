import json
import pyotp
import qrcode
import random
import re
import StringIO
from urllib import quote_plus
import urlparse

from flask import (g, redirect, url_for, flash, request, render_template,
                   session, Response)
from flask.ext.login import login_user, logout_user

from slick import app, db, lm
from slick.utils.core import get_client
from slick.utils.session import login_required
from slick.utils.nexmomessage import NexmoMessage
from . import forms, manager, models

try:
    from twilio import TwilioRestException
    from twilio.rest import TwilioRestClient
except ImportError:
    pass


@login_required
def auth_qr_code():
    domain = urlparse.urlparse(request.url).netloc
    if not domain:
        domain = 'slick.sftlyr.ws'
    totp = pyotp.TOTP(app.config['OTP_SECRET'])

    code = totp.provisioning_uri('%s@%s' % (g.user.username, domain))

    img = qrcode.make(code)
    stream = StringIO.StringIO()
    img.save(stream)
    return Response(stream.getvalue(), mimetype='image/png')


@login_required
def index():
    user = g.user

    widgets = []
    for widget in sorted(app.widgets):
        widgets.append(widget)

    return render_template("site_index.html", title='Home', user=user,
                           widgets=widgets)


def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('.index'))
    form = forms.LoginForm()
    if form.validate_on_submit():
        auth = manager.authenticate_with_password(form.username.data,
                                                  form.password.data)
        if not auth:
            flash('Invalid credentials, please try again.', 'error')
            return logout()
        elif 'security_question' == auth:
            session['un'] = form.username.data
            session['pw'] = form.password.data
            session['remember'] = form.remember_me.data
            session['security_question_answered'] = False
            flash('Please answer one of your security questions to proceed.',
                  'success')
            return redirect(url_for('.security_question'))
        else:
            session['security_question_answered'] = True

        user = _perform_login(form.username.data, form.remember_me.data)

        _check_two_factor(user)
        flash('Login successful', 'success')

        return redirect(request.args.get('next') or
                        url_for('.index'))

    return render_template('site_login.html',
                           title='Sign In',
                           hide_title=True,
                           form=form)


def logout():
    logout_user()
    return redirect(url_for('.index'))


@lm.user_loader
def load_user(id):
    return models.User.query.get(int(id))


@login_required
def profile():
    user = g.user
    form = forms.ProfileForm(request.form, user)
    if form.validate_on_submit():
        user.use_two_factor = form.use_two_factor.data
        user.phone_number = form.phone_number.data
        db.session.add(user)
        db.session.commit()

        flash("Profile updated.", 'success')
        return redirect(url_for('.index'))

    payload = {
        'title': 'Profile',
        'form': form,
    }

    return render_template('site_profile.html', **payload)


def search():
    if not request.args.get('term'):
        return ''

    results = manager.global_search(request.args.get('term'))

    return json.dumps(results)


def security_question():
    if not g.user:
        return redirect(url_for('login'))
    elif (session.get('use_two_factor') and
          not session.get('two_factor_passed')):
        return redirect(url_for('.two_factor_login'))
    elif session.get('security_question_answered'):
        return redirect(url_for('.index'))

    form = forms.SecurityQuestionForm()
    questions = manager.get_questions()

    choices = []
    for q in questions:
        choices.append((str(q['id']), q['question']))
    form.question_id.choices = choices

    payload = {
        'form': form,
        'questions': questions,
        'title': 'Security Question',
    }

    if form.validate_on_submit():
        auth = manager.authenticate_with_password(session['un'],
                                                  session['pw'],
                                                  form.question_id.data,
                                                  form.answer.data)

        if auth and auth != 'security_question':
            session['security_question_answered'] = True

            user = _perform_login(session['un'], session.get('remember'))

            del(session['un'])
            del(session['pw'])
            if session.get('remember'):
                del(session['remember'])

            _check_two_factor(user)

            flash("Authentication successful.", 'success')
            return redirect(session.get('next_page') or url_for('.index'))
        else:
            flash("Incorrect security question/answer specified.", 'error')

    return render_template('site_security_question.html', **payload)


def two_factor_login():
    if not g.user:
        return redirect(url_for('login'))

    if not app.config.get('sms_provider'):
        session['two_factor_passed'] = True
        flash("Two factor authentication not configured. Logging you in.",
              'success')
        return redirect(url_for('.index'))

    form = forms.TwoFactorForm()
    payload = {
        'title': 'Two-Factor Authentication',
        'form': form,
    }

    if g.user.use_two_factor == 'sms':
        payload['use_sms'] = True

        if not session.get('sms_code_sent') or request.args.get('generate'):
            (passcode, counter) = _generate_passcode()
            session['two_factor_counter'] = counter
            (success, message) = _send_passcode(passcode)
            if success:
                session['sms_code_sent'] = True
                flash(message, 'success')
            else:
                flash(message, 'error')

    if form.validate_on_submit():
        if _validate_passcode(form.passcode.data):
            session['two_factor_counter'] = None
            session['two_factor_passed'] = True
            flash("Authentication successful.", 'success')
            return redirect(request.args.get('next') or
                            url_for('.index'))
        else:
            flash('Invalid passcode', 'error')

    return render_template('site_two_factor.html', **payload)


def _check_two_factor(user):
    session['use_two_factor'] = True
    session['two_factor_passed'] = False

    if not user.use_two_factor or user.use_two_factor == 'none':
        session['use_two_factor'] = False
        session['two_factor_passed'] = True

    if session['use_two_factor']:
        session['next_page'] = request.args.get('next')
        return redirect(url_for('.two_factor_login'))


def _generate_passcode():
    hotp = pyotp.HOTP(app.config['OTP_SECRET'])
    counter = random.randint(1, 65536)
    return (hotp.at(counter), counter)


def _perform_login(username, remember):
    client = get_client()
    if not client['Account'].getObject():
        flash('Invalid credentials, please try again.', 'error')
        return logout()

    user = models.User.query.filter_by(username=username).first()
    if user is None:
        user = models.User(username=username)
        db.session.add(user)
        db.session.commit()
    login_user(user, remember=remember)

    return user


def _send_passcode(passcode):
    user = g.user
    passcode = str(passcode)

    if user.use_two_factor != 'none' and user.phone_number:
        # TODO - Maybe move all this stuff out into wrapper modules
        sms_body = "Your login token is: " + passcode

        passcode = re.sub('(.)', "\g<1>,,,", passcode)
        voice_body = "Message[0]=Your temporary passcode is " + passcode + \
                     ". To repeat, your passcode is " + passcode + "."

        if app.config.get('TWILIO_AUTH_TOKEN'):
            f_number = random.choice(app.config['TWILIO_FROM_NUMBERS'])
            client = TwilioRestClient(app.config['TWILIO_ACCOUNT_SID'],
                                      app.config['TWILIO_AUTH_TOKEN'])
            if user.use_two_factor == 'sms':
                try:
                    success = True
                    message = 'The passcode has been sent to your phone ' \
                              'number on record. This code will expire soon.'
                    result = client.sms.messages.create(body=sms_body,
                                                        to=user.phone_number,
                                                        from_=f_number)
                except TwilioRestException as e:
                    success = False
                    message = 'There was an error sending your passcode: ' \
                              + e.msg
            else:
                voice_url = 'http://twimlets.com/message?'
                voice_url += quote_plus(voice_body, safe='=')

                try:
                    success = True
                    message = 'The passcode has been sent to your phone ' \
                              'number on record.'
                    client.calls.create(to=user.phone_number, from_=f_number,
                                        url=voice_url)
                except TwilioRestException as e:
                    success = False
                    message = 'There was an error sending your passcode: ' \
                              + e.msg
        elif app.config.get('NEXMO_KEY'):
            f_number = random.choice(app.config['NEXMO_FROM_NUMBERS'])
            request = {
                'reqtype': 'json',
                'api_secret': app.config.get('NEXMO_SECRET'),
                'from': f_number,
                'to': '1' + user.phone_number,
                'api_key': app.config.get('NEXMO_KEY'),
            }

            request['text'] = sms_body
            sms1 = NexmoMessage(request).send_request()

            # TODO - I need to figure out how to deal with bounced messages
            success = True
            message = 'The passcode has been sent to your phone number ' \
                      'on record.'
        return (success, message)

    return (False, 'Two factor authentication not configured.')


def _validate_passcode(passcode):
    passcode = int(passcode)
    if session.get('two_factor_counter'):
        hotp = pyotp.HOTP(app.config['OTP_SECRET'])
        return hotp.verify(passcode, session['two_factor_counter'])
    else:
        totp = pyotp.TOTP(app.config['OTP_SECRET'])
        return totp.verify(passcode)
