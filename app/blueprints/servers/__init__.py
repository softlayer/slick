from flask import Blueprint

blueprint = Blueprint('server_module', __name__, template_folder='templates',
                      url_prefix='/server')

from app import app
from app.blueprints.servers import views

submenu = [
    ('server_module.index', 'List Servers'),
    ('server_module.create_bmc', 'Create Bare Metal Cloud'),
    ('server_module.create_dedicated', 'Create Dedicated Server'),
]
app.add_menu('left', submenu, 'Servers', 1)

# Servers Add
blueprint.add_url_rule('/add/bmc', view_func=views.create_bmc,
                       methods=['GET', 'POST'])
blueprint.add_url_rule('/add/dedicated', view_func=views.create_dedicated,
                       methods=['GET', 'POST'])

# Servers List
blueprint.add_url_rule('/', view_func=views.index)
blueprint.add_url_rule('/index', view_func=views.index)

# Server Price Check (AJAX call)
blueprint.add_url_rule('/priceCheck', view_func=views.price_check,
                       methods=['GET', 'POST'])

# Server Status (AJAX call)
blueprint.add_url_rule('/status', view_func=views.status)
blueprint.add_url_rule('/status/<int:server_id>', view_func=views.status)
