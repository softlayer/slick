from flask.ext.wtf import Form
from wtforms import HiddenField
from wtforms.fields.html5 import IntegerField
from wtforms.validators import Required, NumberRange
from wtformsparsleyjs import TextField, SelectField


class ZoneRecordForm(Form):
    zone_id = HiddenField(validators=[Required()])
    record = TextField('record', validators=[Required()])
    type = SelectField('type', choices=[('A', 'A'), ('AAAA', 'AAAA'),
                                        ('CNAME', 'CNAME'), ('TXT', 'TXT'),
                                        ('NS', 'NS'), ('SOA', 'SOA'),
                                        ('MX', 'MX'), ('PTR', 'PTR'),
                                        ('SRV', 'SRV')],
                       validators=[Required()])
    data = TextField('data', validators=[Required()])
    ttl = IntegerField('ttl', validators=[Required(), NumberRange(min=0)])
