from slick import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Unicode(255), index=True, unique=True)
    use_two_factor = db.Column(db.Enum('none', 'sms', 'voice',
                                       'authenticator'),
                               server_default='none', nullable=False)
    phone_number = db.Column(db.Unicode(45))
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
