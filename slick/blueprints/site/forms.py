from flask.ext.wtf import Form
from wtforms import RadioField
from wtforms.fields.html5 import TelField
from wtforms.validators import Required
from wtformsparsleyjs import (TextField, PasswordField, BooleanField,
                              SelectField)


class LoginForm(Form):
    username = TextField('username', validators=[Required()])
    password = PasswordField('password', validators=[Required()])
    remember_me = BooleanField('remember_me', default=False)


class ProfileForm(Form):
    use_two_factor = RadioField(choices=[('none', 'No'), ('sms', 'SMS'),
                                         ('authenticator',
                                          'Google Authenticator')],
                                validators=[Required()])
    phone_number = TelField('phone_number', validators=[Required()])


class SecurityQuestionForm(Form):
    question_id = SelectField('question_id')
    answer = TextField('answer', validators=[Required()])


class TwoFactorForm(Form):
    passcode = TextField('passcode', validators=[Required()])
