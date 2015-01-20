from flask.ext.wtf import Form
from wtforms import RadioField, HiddenField, TextAreaField
from wtforms.validators import Required
from wtformsparsleyjs import StringField, SelectField


class CreateVMForm(Form):
    datacenter = SelectField('Data Center')
    hostname = StringField('Hostname', validators=[Required()])
    domain = StringField('Domain', validators=[Required()])
    os = SelectField('Operating System', validators=[Required()])
    cpus = SelectField('CPUs', validators=[Required()])
    memory = SelectField('Memory (GB)', validators=[Required()])
    network = RadioField(choices=[('10', '10Mbps'), ('100', '100Mbps'),
                                  ('1000', '1000 Mbps')])
    tag = StringField('Tags')


class EditVMForm(Form):
    vm_id = HiddenField(validators=[Required()])
    hostname = StringField('Hostname', validators=[Required()])
    domain = StringField('Domain', validators=[Required()])
    notes = TextAreaField('notes')
    userdata = TextAreaField('userdata')
