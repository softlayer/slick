from flask.ext.wtf import Form
from wtforms import TextAreaField
from wtforms.validators import DataRequired, Required
from wtformsparsleyjs import StringField


class AddSshKeyForm(Form):
    label = StringField('Label', validators=[DataRequired(), Required()])
    key = TextAreaField('Public Key', validators=[DataRequired()])
    notes = TextAreaField('Notes')
