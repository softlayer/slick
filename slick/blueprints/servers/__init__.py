from flask import Blueprint

blueprint = Blueprint('server_module', __name__, template_folder='templates',
                      url_prefix='/server')

from slick import app
from . import views

submenu = [
    ('server_module.index', 'List Servers'),
    ('server_module.create_hourly', 'Create Hourly Bare Metal'),
    ('server_module.create_monthly', 'Create Monthly Bare Metal'),
]
app.add_menu('left', submenu, 'Servers', 1)

# Servers Add
blueprint.add_url_rule('/add/hourly', view_func=views.create_hourly,
                       methods=['GET', 'POST'])
blueprint.add_url_rule('/add/monthly', view_func=views.create_monthly)
blueprint.add_url_rule('/add/monthly/<int:package_id>',
                       view_func=views.create_monthly, methods=['GET', 'POST'])

# Servers List
blueprint.add_url_rule('/', view_func=views.index)
blueprint.add_url_rule('/index', view_func=views.index)

# Server Price Check (AJAX call)
blueprint.add_url_rule('/priceCheck/<string:server_type>',
                       view_func=views.price_check, methods=['GET', 'POST'])

# Server Reboot
blueprint.add_url_rule('/reboot/<int:server_id>/hard',
                       view_func=views.hard_reboot_server)
blueprint.add_url_rule('/reboot/<int:server_id>/soft',
                       view_func=views.soft_reboot_server)

# Server Reload
blueprint.add_url_rule('/reload/<int:server_id>',
                       view_func=views.server_reload)

# Server Status (AJAX call)
blueprint.add_url_rule('/status', view_func=views.status)
blueprint.add_url_rule('/status/<int:server_id>', view_func=views.status)

# Server View
blueprint.add_url_rule('/view/<int:server_id>', view_func=views.view)
blueprint.add_url_rule('/changeSpeed/<int:object_id>/<string:nic>/<int:speed>',
                       view_func=views.change_nic_speed)
blueprint.add_url_rule('/getPassword/', view_func=views.get_password)
blueprint.add_url_rule('/getPassword/<int:object_id>/<string:username>',
                       view_func=views.get_password)
