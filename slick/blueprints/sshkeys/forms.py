from flask.ext.wtf import Form
from wtforms import TextAreaField
from wtforms.validators import Required
from wtformsparsleyjs import TextField


class AddSshKeyForm(Form):
    label = TextField('label', validators=[Required()])
    key = TextAreaField('key', validators=[Required()])
    notes = TextAreaField('notes')
