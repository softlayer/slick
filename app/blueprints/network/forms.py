from flask.ext.wtf import Form
from wtforms import HiddenField, RadioField
from wtforms.validators import Required
from wtformsparsleyjs import SelectField


class CreateSubnetForm(Form):
    vlan_id = HiddenField()
    subnet_type = RadioField(choices=[('public', 'Public'),
                                      ('private', 'Private')],
                             validators=[Required()])
    quantity = SelectField('Quantity', validators=[Required()],
                           choices=[('4', '4'), ('8', '8'), ('16', '16'),
                                    ('32', '32')])
