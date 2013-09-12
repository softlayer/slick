from flask import Blueprint

from app import app
from app.blueprints.site import views

blueprint = Blueprint('site_module', __name__, template_folder='templates')

app.add_menu('left', 'site_module.index', 'Dashboard')
app.add_menu('right', 'site_module.logout', 'Logout')

blueprint.add_url_rule('/', view_func=views.index)
blueprint.add_url_rule('/index', view_func=views.index)

blueprint.add_url_rule('/login', view_func=views.login,
                       methods=['GET', 'POST'])

blueprint.add_url_rule('/logout', view_func=views.logout)
