from flask.ext.wtf import Form
from wtforms import TextAreaField
from wtforms.validators import DataRequired, Required
from wtformsparsleyjs import TextField


class AddSshKeyForm(Form):
    label = TextField('Label', validators=[DataRequired(), Required()])
    key = TextAreaField('Public Key', validators=[DataRequired()])
    notes = TextAreaField('Notes')
