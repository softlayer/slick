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

# CCI price check (AJAX call)
blueprint.add_url_rule('/priceCheck', view_func=views.price_check,
                       methods=['GET', 'POST'])

# CCI reload
blueprint.add_url_rule('/reload/<int:cci_id>', view_func=views.reload_cci)

# CCI status (AJAX call)
blueprint.add_url_rule('/status', view_func=views.status)
blueprint.add_url_rule('/status/<int:cci_id>', view_func=views.status)
