from flask.ext.wtf import Form
from wtforms import RadioField
from wtforms.fields.html5 import TelField
from wtforms.validators import Required
from wtformsparsleyjs import (TextField, PasswordField, BooleanField,
                              SelectField)


class LoginForm(Form):
    username = TextField('Username', validators=[Required()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Remember Me', default=False)


class ProfileForm(Form):
    use_two_factor = RadioField('Use Two Factor',
                                choices=[('none', 'No'), ('sms', 'SMS'),
                                         ('authenticator',
                                          'Google Authenticator')],
                                validators=[Required()])
    phone_number = TelField('Phone Number', validators=[Required()])


class SecurityQuestionForm(Form):
    question_id = SelectField('Question', 'question_id')
    answer = TextField('Answer', validators=[Required()])


class TwoFactorForm(Form):
    passcode = TextField('Passcode', validators=[Required()])
