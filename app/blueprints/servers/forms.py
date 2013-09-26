from flask.ext.wtf import Form
from wtforms import FieldList, HiddenField
from wtforms.validators import Required
from wtformsparsleyjs import TextField, SelectField


class CreateBMCForm(Form):
    bare_metal = HiddenField(default='1')
    location = SelectField('Data Center', default='FIRST_AVAILABLE')
    hostname = TextField('Hostname', validators=[Required()])
    domain = TextField('Domain', validators=[Required()])
    server = SelectField('Server', validators=[Required()])
    os = SelectField('Operating System', validators=[Required()])
    port_speed = SelectField('Network Speed', validators=[Required()])
    disks = FieldList(SelectField('Disks', validators=[Required()]),
                      min_entries=1, max_entries=4)
