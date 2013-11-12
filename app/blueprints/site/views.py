import pyotp
import qrcode
import random
import re
import StringIO
from urllib import quote_plus
import urlparse

from flask import (g, redirect, url_for, flash, request, render_template,
                   session, Response)
from flask.ext.login import login_user, logout_user, login_required

from SoftLayer import Client, SoftLayerAPIError

from app import app, db, lm
from app.blueprints.site.forms import LoginForm, ProfileForm, TwoFactorForm
from app.blueprints.site.models import User
from app.utils.core import get_client

from app.utils.nexmomessage import NexmoMessage

try:
    from twilio import TwilioRestException
    from twilio.rest import TwilioRestClient
except ImportError:
    pass


@login_required
def auth_qr_code():
    code = _generate_passcode(True)
    img = qrcode.make(code)
    stream = StringIO.StringIO()
    img.save(stream)
    return Response(stream.getvalue(), mimetype='image/png')


@login_required
def index():
    user = g.user

    widgets = []
    for widget in app.widgets:
        widgets.append(widget)

    return render_template("site_index.html", title='Home', user=user,
                           widgets=widgets)


def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('.index'))
    form = LoginForm()
    if form.validate_on_submit():
        auth = _authenticate_with_password(form.username.data,
                                           form.password.data)
        if not auth:
            flash('Invalid credentials, please try again.', 'error')
            return logout()
        elif 'security_question' == auth:
            session['un'] = form.username.data
            session['pw'] = form.password.data
            session['security_question_answered'] = False
            flash('Please answer one of your security questions to proceed.',
                  'success')
            return redirect(url_for('.security_question'))
        else:
            session['security_question_answered'] = True

        client = get_client()
        if not client['Account'].getObject():
            flash('Invalid credentials, please try again.', 'error')
            return logout()

        user = User.query.filter_by(username=form.username.data).first()
        if user is None:
            user = User(username=form.username.data)
            db.session.add(user)
            db.session.commit()
        login_user(user, remember=form.remember_me.data)
        flash('Login successful', 'success')

        session['use_two_factor'] = True
        session['two_factor_passed'] = False

        if not user.use_two_factor:
            session['use_two_factor'] = False
            session['two_factor_passed'] = True

        if session['use_two_factor']:
            session['next_page'] = request.args.get('next')
            return redirect(url_for('.two_factor_login'))

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
    return User.query.get(int(id))


@login_required
def profile():
    user = g.user
    form = ProfileForm(request.form, user)
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


@login_required
def two_factor_login():
    if not app.config.get('sms_provider'):
        session['two_factor_passed'] = True
        flash("Two factor authentication not configured. Logging you in.",
              'success')
        return redirect(url_for('.index'))

#    if not session.get('two_factor_passcode'):
#        session['two_factor_passcode'] = _generate_passcode()
#        (success, message) = _send_passcode(session['two_factor_passcode'])

    passcode = _generate_passcode()
    form = TwoFactorForm()
    if form.validate_on_submit():
        if form.passcode.data == passcode:
            session['two_factor_passed'] = True
            flash("Authentication successful.", 'success')
            return redirect(request.args.get('next') or
                            url_for('.index'))

    payload = {
        'title': 'Two-Factor Authentication',
        'form': form,
    }

    return render_template('site_two_factor.html', **payload)


def _authenticate_with_password(username, password, question_id=None,
                                answer=None):
    client = Client()
    try:
        (user_id, user_hash) = client.authenticate_with_password(username,
                                                                 password,
                                                                 question_id,
                                                                 answer)
        session['sl_user_id'] = user_id
        session['sl_user_hash'] = user_hash
    except SoftLayerAPIError as e:
        c = 'SoftLayer_Exception_User_Customer_InvalidSecurityQuestionAnswer'
        if e.faultCode == c:
            return 'security_question'

        return False

    return True


def _generate_passcode(url=False):
    user = g.user
    domain = urlparse.urlparse(request.url).netloc
    if not domain:
       domain = 'slick.sftlyr.ws'
    totp = pyotp.TOTP(app.config['TOTP_SECRET'])

    if url:
        return totp.provisioning_uri('%s@%s' % (g.user.username, domain))
    return str(totp.now())


def _send_passcode(passcode):
    user = g.user

    if user.use_two_factor != 'none' and user.phone_number:
        # TODO - Maybe move all this stuff out into wrapper modules
        sms_body = "Your login token is: " + passcode

        passcode = re.sub('(.)', "\g<1>,,,", passcode)
        voice_body = "Message[0]=Your temporary passcode is " + passcode + \
                     ". To repeat, your passcode is " + passcode + "."

        if app.config.get('TWILIO_AUTH_TOKEN'):
            f_number = random.choice(app.config['TWILIO_FROM_NUMBERS'])
            client = TwilioRestClient(app.config['TWILIO_ACCOUNT_SID'],
                                      _app.config['TWILIO_AUTH_TOKEN'])
            if user.use_two_factor == 'sms':
                try:
                    success = True
                    message = 'The passcode has been sent to your phone ' \
                              'number on record.'
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
