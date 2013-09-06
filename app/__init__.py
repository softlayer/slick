from os.path import dirname, abspath, join

from flask import Flask, g
from flask.ext.login import LoginManager, current_user
from flask.ext.sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension


# We're going to extend the base Flask functionality to provide a central
# menu system.
class Slick(Flask):
    def __init__(self, *args, **kwargs):
        super(Slick, self).__init__(*args, **kwargs)
        self.left_menu = []
        self.right_menu = []

    def add_menu(self, side, url, label, order=0):
        if 'left' == side:
            self.left_menu.append((url, label, order))
        else:
            self.right_menu.append((url, label, order))


# Setup the main Flask app
app = Slick(__name__)
app.config.from_object('config')
app.static_folder = join(dirname(abspath(__file__)), "static")
app.static_url_path = "/static/"
app.jinja_env.add_extension('jinja2.ext.do')

# Create the database object
db = SQLAlchemy(app)

# Setup the login manager
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'site_module.login'

# Enable the debug toolbar
toolbar = DebugToolbarExtension(app)

# Load all of our blueprints
# TODO - I want to make this more dynamic
from app.blueprints.site import site_module
from app.blueprints.cci import cci_module

app.register_blueprint(site_module)
app.register_blueprint(cci_module)
#from app import views, models


@app.before_request
def before_request():
    g.user = current_user


@app.context_processor
def generate_menu():
    return dict(
        left_menu=sorted(app.left_menu, key=lambda x: (x[2], x[1])),
        right_menu=sorted(app.right_menu, key=lambda x: (x[2], x[1]))
    )
