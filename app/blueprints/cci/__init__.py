from flask import Blueprint

blueprint = Blueprint('cci_module', __name__, template_folder='templates',
                      url_prefix='/cci')

from app import app
from app.blueprints.cci import views

submenu = [
    ('cci_module.index', 'List Instances'),
    ('cci_module.create', 'Create Instance'),
]
app.add_menu('left', submenu, 'Compute', 1)

# CCI Add
blueprint.add_url_rule('/add', view_func=views.create,
                       methods=['GET', 'POST'])

# CCI List
blueprint.add_url_rule('/', view_func=views.index, defaults={'page': 1})
blueprint.add_url_rule('/index', view_func=views.index, defaults={'page': 1})
blueprint.add_url_rule('/index/page/<int:page>', view_func=views.index)

# CCI Price Check (AJAX call)
blueprint.add_url_rule('/priceCheck', view_func=views.price_check,
                       methods=['GET', 'POST'])

# CCI Reboot
blueprint.add_url_rule('/reboot/<int:cci_id>/hard',
                       view_func=views.hard_reboot_cci)
blueprint.add_url_rule('/reboot/<int:cci_id>/soft',
                       view_func=views.soft_reboot_cci)

# CCI Reload
blueprint.add_url_rule('/reload/<int:cci_id>', view_func=views.reload_cci)

# CCI Status (AJAX call)
blueprint.add_url_rule('/status', view_func=views.status)
blueprint.add_url_rule('/status/<int:cci_id>', view_func=views.status)

# CCI View
blueprint.add_url_rule('/view/<int:cci_id>', view_func=views.view)
blueprint.add_url_rule('/changeSpeed/<int:cci_id>/<string:nic>/<int:speed>',
                       view_func=views.change_nic_speed)
blueprint.add_url_rule('/getPassword/', view_func=views.get_password)
blueprint.add_url_rule('/getPassword/<int:cci_id>/<string:username>',
                       view_func=views.get_password)
