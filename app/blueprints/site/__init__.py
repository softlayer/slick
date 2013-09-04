from flask import Blueprint, url_for

site_module = Blueprint('site_module', __name__, template_folder='templates')

from app import app
from app.blueprints.site import views

app.add_menu('left', 'site_module.index', 'Dashboard')
app.add_menu('right', 'site_module.logout', 'Logout')