from flask.ext.wtf import Form
from wtforms import HiddenField
from wtforms.fields.html5 import IntegerField
from wtforms.validators import Required, NumberRange
from wtformsparsleyjs import TextField, SelectField


class ZoneRecordForm(Form):
    zone_id = HiddenField()
    record = TextField('Record', validators=[Required()])
    type = SelectField('Type', choices=[('A', 'A'), ('AAAA', 'AAAA'),
                                        ('CNAME', 'CNAME'), ('TXT', 'TXT'),
                                        ('NS', 'NS'), ('SOA', 'SOA'),
                                        ('MX', 'MX'), ('PTR', 'PTR'),
                                        ('SRV', 'SRV')],
                       validators=[Required()])
    data = TextField('Data', validators=[Required()])
    ttl = IntegerField('TTL', validators=[Required(), NumberRange(min=0)])
