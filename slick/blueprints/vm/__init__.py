from flask import Blueprint

blueprint = Blueprint('vm_module', __name__, template_folder='templates',
                      static_folder='static', url_prefix='/vm')

from slick import app
from . import views, widgets

submenu = [
    ('vm_module.index', 'List Instances'),
    ('vm_module.create', 'Create Instance'),
]
app.add_menu('left', submenu, 'Compute', 1)

for widget in widgets.get_widgets():
    app.add_widget(widget)

# VM Add
blueprint.add_url_rule('/add', view_func=views.create,
                       methods=['GET', 'POST'])

# VM Cancel
blueprint.add_url_rule('/cancel/<int:vm_id>', view_func=views.cancel)

# VM List
blueprint.add_url_rule('/', view_func=views.index)
blueprint.add_url_rule('/index', view_func=views.index)

# VM Price Check (AJAX call)
blueprint.add_url_rule('/priceCheck', view_func=views.price_check,
                       methods=['GET', 'POST'])

# VM Reboot
blueprint.add_url_rule('/reboot/<int:vm_id>/hard',
                       view_func=views.hard_reboot_vm)
blueprint.add_url_rule('/reboot/<int:vm_id>/soft',
                       view_func=views.soft_reboot_vm)

# VM Reload
blueprint.add_url_rule('/reload/<int:vm_id>', view_func=views.reload_vm)

# VM Status (AJAX call)
blueprint.add_url_rule('/status', view_func=views.status)
blueprint.add_url_rule('/status/<int:vm_id>', view_func=views.status)

# VM Start (AJAX call)
blueprint.add_url_rule('/start/<int:vm_id>', view_func=views.start_vm)

# VM Stop (AJAX call)
blueprint.add_url_rule('/stop/<int:vm_id>', view_func=views.stop_vm)

# VM View
blueprint.add_url_rule('/view/<int:vm_id>', view_func=views.view)
blueprint.add_url_rule('/changeSpeed/<int:object_id>/<string:nic>/<int:speed>',
                       view_func=views.change_nic_speed)
blueprint.add_url_rule('/getPassword/', view_func=views.get_password)
blueprint.add_url_rule('/getPassword/<int:object_id>/<string:username>',
                       view_func=views.get_password)
