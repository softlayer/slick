from flask import Blueprint

blueprint = Blueprint('mq_module', __name__, template_folder='templates',
                      url_prefix='/mq')

from slick import app
from . import views, widgets

#submenu = [
#    ('mq_module.subnet_index', 'List Subnets'),
#    ('network_module.vlan_index', 'List VLANs'),
#]
#app.add_menu('right', submenu, 'Messaging', 4)

for widget in widgets.get_widgets():
    app.add_widget(widget)

# Queue list
blueprint.add_url_rule('/queue/list/<string:account_id>',
                       view_func=views.queue_list)
