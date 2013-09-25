from flask import g, redirect, url_for, flash, request, render_template, \
    session
from flask.ext.login import login_user, logout_user, login_required

from SoftLayer import Client, SoftLayerAPIError

from app import db, lm
from app.blueprints.site.forms import LoginForm
from app.blueprints.site.models import User
from app.utils.core import get_client


@login_required
def index():
    user = g.user
    client = get_client()
    user = client['Account'].getCurrentUser(mask='mask[permissions]')
#    for perm in user['permissions']:
#        if 'UPGRADE' in perm['keyName']:
#            print perm['keyName'],'-',perm['name']
    return render_template("site_index.html", title='Home', user=user)


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
    # @TODO - This always displays
#    flash("LOGIN FAILED!")
    return render_template('site_login.html',
                           title='Sign In',
                           form=form)


def logout():
    logout_user()
    return redirect(url_for('.index'))


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


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
