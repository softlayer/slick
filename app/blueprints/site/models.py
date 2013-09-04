from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Unicode(255), index=True, unique=True)
    use_two_factor = db.Column(db.Boolean, server_default='0', nullable=False)
    phone_number = db.Column(db.Unicode(45))
    use_sms = db.Column(db.Boolean, server_default='0', nullable=False)
#    cci_templates = db.relationship('CciTemplate', backref='owner',
#                                    lazy='dynamic')

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.username)
