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

from SoftLayer import (Client, SoftLayerAPIError, CCIManager, HardwareManager,
                       SshKeyManager)

from app import app, db, lm
from app.blueprints.site.forms import LoginForm, ProfileForm, TwoFactorForm
from app.blueprints.site.models import User
from app.utils.core import get_client
from app.utils.session import login_required

from app.utils.nexmomessage import NexmoMessage

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

        if not user.use_two_factor or user.use_two_factor == 'none':
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


def search():
    if not request.args.get('term'):
        return ''

    match_string = '<span class="text-primary">%s</span>' % \
                   request.args.get('term')
    term = re.compile(request.args.get('term'), re.IGNORECASE)

    results = []

    client = get_client()
#    hostname_regex = re.compile('\w')

    if 'vm' in app.config['installed_blueprints']:
        cci = CCIManager(client)
#        if hostname_regex.match(term):
        for vm in cci.list_instances():
            if term.match(vm['hostname']) or \
               term.match(vm['primaryIpAddress']):
                text = '%s (%s)' % (vm['fullyQualifiedDomainName'],
                                    vm['primaryIpAddress'])
                text = term.sub(match_string, text)

                results.append({'label': '<strong>VM:</strong> ' + text,
                                'value': url_for('vm_module.view',
                                                 vm_id=vm['id'])})
    if 'servers' in app.config['installed_blueprints']:
        hw = HardwareManager(client)

        for svr in hw.list_hardware():
            if term.match(svr['hostname']) or \
               term.match(svr['primaryIpAddress']):
                text = '%s (%s)' % (svr['fullyQualifiedDomainName'],
                                    svr['primaryIpAddress'])
                text = term.sub(match_string, text)

                results.append({'label': '<strong>Server:</strong> ' + text,
                                'value': url_for('server_module.view',
                                                 server_id=svr['id'])})
    if 'sshkeys' in app.config['installed_blueprints']:
        ssh = SshKeyManager(client)

        for key in ssh.list_keys():
            if term.match(key['label']) or term.match(key['fingerprint']):
                text = '%s (%s)' % (key['label'], key['fingerprint'])
                text = term.sub(match_string, text)

                results.append({'label': '<strong>SSH Key:</strong> ' + text,
                                'value': url_for('ssh_module.view',
                                                 key_id=key['id'])})

    return json.dumps(results)


def two_factor_login():
    if not g.user:
        return redirect(url_for('login'))

    if not app.config.get('sms_provider'):
        session['two_factor_passed'] = True
        flash("Two factor authentication not configured. Logging you in.",
              'success')
        return redirect(url_for('.index'))

    form = TwoFactorForm()
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
    hotp = pyotp.HOTP(app.config['OTP_SECRET'])
    counter = random.randint(1, 65536)
    return (hotp.at(counter), counter)


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
                                      _app.config['TWILIO_AUTH_TOKEN'])
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
