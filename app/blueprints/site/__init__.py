from flask import Blueprint, g

from app import app
from app.blueprints.site import views

blueprint = Blueprint('site_module', __name__, template_folder='templates')

app.add_menu('left', 'site_module.index', 'Dashboard', 0)

blueprint.add_url_rule('/', view_func=views.index)
blueprint.add_url_rule('/index', view_func=views.index)

blueprint.add_url_rule('/auth_qr_code.png', view_func=views.auth_qr_code)

blueprint.add_url_rule('/login', view_func=views.login,
                       methods=['GET', 'POST'])

blueprint.add_url_rule('/logout', view_func=views.logout)

blueprint.add_url_rule('/login/twofactor',
                       view_func=views.two_factor_login,
                       methods=['GET', 'POST'])

blueprint.add_url_rule('/profile', view_func=views.profile,
                       methods=['GET', 'POST'])

blueprint.add_url_rule('/search', view_func=views.search,
                       methods=['GET', 'POST'])
