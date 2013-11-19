from flask.ext.wtf import Form
from wtforms import FieldList, HiddenField
from wtforms.validators import Required
from wtformsparsleyjs import TextField, SelectField


class CreateHourlyForm(Form):
    bare_metal = HiddenField(default='1')
    location = SelectField('Data Center', default='FIRST_AVAILABLE')
    hostname = TextField('Hostname', validators=[Required()])
    domain = TextField('Domain', validators=[Required()])
    server = SelectField('Server', validators=[Required()])
    os = SelectField('Operating System', validators=[Required()])
    port_speed = SelectField('Network Speed', validators=[Required()])
    # TODO - This could be turned into a regular SelectField
    disks = FieldList(SelectField('Disks', validators=[Required()]),
                      min_entries=1, max_entries=4)


class CreateMonthlyForm(Form):
    package_id = HiddenField(validators=[Required()])
    location = SelectField('Data Center', default='FIRST_AVAILABLE')
    hostname = TextField('Hostname', validators=[Required()])
    domain = TextField('Domain', validators=[Required()])
    server = SelectField('CPU', validators=[Required()])
    ram = SelectField('Memory', validators=[Required()])
    os = SelectField('Operating System', validators=[Required()])
    port_speed = SelectField('Network Speed', validators=[Required()])
    disks = FieldList(SelectField('Disks', validators=[Required()]),
                      min_entries=1)
    disk_controller = SelectField('Disk Controller', validators=[Required()])

    @classmethod
    def add_disk(cls, required=True):
        validators = []
        if required:
            validators.append(Required())

        new_field = SelectField('Disk', validators=validators)

        cls.disks.append_entry(new_field)

        print cls.disks
