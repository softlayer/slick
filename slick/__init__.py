import importlib
from os import listdir
from os.path import dirname, abspath, join, isdir, exists

from flask import Flask, g
from flask.ext.login import LoginManager, current_user
from flask.ext.sqlalchemy import SQLAlchemy

twilio_enabled = True
try:
    from twilio import TwilioRestException
    from twilio.rest import TwilioRestClient
except ImportError:
    twilio_enabled = False


# We're going to extend the base Flask functionality to provide a central
# menu system.
class Slick(Flask):
    def __init__(self, *args, **kwargs):
        super(Slick, self).__init__(*args, **kwargs)
        self.left_menu = []
        self.right_menu = []
        self.widgets = []

    def add_menu(self, side, url, label, order=0):
        menu = self.left_menu
        if 'right' == side:
            menu = self.right_menu

        item_found = False
        for i, data in enumerate(menu):
            if label == data[1] and isinstance(data[0], list):
                new_url = data[0] + url
                menu[i] = (new_url, data[1], data[2])
                item_found = True

        if not item_found:
            menu.append((url, label, order))

    def add_widget(self, widget):
        self.widgets.append(widget)


# Setup the main Flask app
app = Slick(__name__)
app.config.from_envvar('SLICK_CONFIG_FILE')
app.static_folder = join(dirname(abspath(__file__)), "static")
app.static_url_path = "/static/"
app.jinja_env.add_extension('jinja2.ext.do')

if not app.config.get('TWILIO_AUTH_TOKEN'):
    twilio_enabled = False

if twilio_enabled:
    app.config['sms_provider'] = 'twilio'
elif not twilio_enabled and app.config.get('NEXMO_KEY'):
    app.config['sms_provider'] = 'nexmo'
else:
    app.config['sms_provider'] = None

# Create the database object
db = SQLAlchemy(app)

# Setup the login manager
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'site_module.login'

# Load all of our blueprints
BLUEPRINT_PATH = app.config.get('BLUEPRINT_PATH',
                                join(abspath(dirname(__file__)), 'blueprints'))
@app.before_request
def before_request():
    g.user = current_user


@app.context_processor
def generate_menu():
    return dict(
        left_menu=sorted(app.left_menu, key=lambda x: (x[2], x[1])),
        right_menu=sorted(app.right_menu, key=lambda x: (x[2], x[1]),
                          reverse=True)
    )


# Load pluggable blueprints. This is adapted from code in:
# https://bitbucket.org/philpem/horizon/
app.config['installed_blueprints'] = []

for name in listdir(BLUEPRINT_PATH):
    if isdir(join(BLUEPRINT_PATH, name)) and exists(join(BLUEPRINT_PATH,
                                                         name, '__init__.py')):
        module = importlib.import_module('slick.blueprints.' + name)

        if hasattr(module, 'blueprint'):
            app.config['installed_blueprints'].append(name)
            app.register_blueprint(module.blueprint)
