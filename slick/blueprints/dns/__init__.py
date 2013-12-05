from flask import Blueprint

from slick import app
from . import views

blueprint = Blueprint('dns_module', __name__, template_folder='templates',
                      url_prefix='/dns')

submenu = [
    ('dns_module.index', 'Zone Management'),
]

app.add_menu('right', submenu, 'Services', 2)


# Zone List
blueprint.add_url_rule('/', view_func=views.index)
blueprint.add_url_rule('/index', view_func=views.index)

# Zone View
blueprint.add_url_rule('/view/<int:zone_id>', view_func=views.zone_view)

# Record Add
blueprint.add_url_rule('/record/add/<int:zone_id>', view_func=views.record_add,
                       methods=['GET', 'POST'])

# Record Delete
blueprint.add_url_rule('/record/delete/<int:record_id>',
                       view_func=views.record_delete)

# Record Edit
blueprint.add_url_rule('/record/<int:record_id>', view_func=views.record_edit)
