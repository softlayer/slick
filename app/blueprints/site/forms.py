from flask.ext.wtf import Form
from wtforms import RadioField
from wtforms.fields.html5 import TelField
from wtforms.validators import Required
from wtformsparsleyjs import TextField, PasswordField, BooleanField


class LoginForm(Form):
    username = TextField('username', validators=[Required()])
    password = PasswordField('password', validators=[Required()])
    remember_me = BooleanField('remember_me', default=False)


class ProfileForm(Form):
    use_two_factor = RadioField(choices=[('0', 'No'), ('1', 'Yes')],
                                validators=[Required()])
    phone_number = TelField('phone_number', validators=[Required()])


class TwoFactorForm(Form):
    passcode = TextField('passcode', validators=[Required()])
