from flask import Blueprint

from slick import app
from . import views

blueprint = Blueprint('ssl_module', __name__, template_folder='templates',
                      url_prefix='/ssl')

submenu = [
    ('ssl_module.index', 'SSL Certs'),
]

app.add_menu('right', submenu, 'Services', 2)

# Cert Delete
blueprint.add_url_rule('/delete/<int:cert_id>', view_func=views.delete)

# Cert List
blueprint.add_url_rule('/', view_func=views.index)
blueprint.add_url_rule('/index', view_func=views.index)

# Cert View
blueprint.add_url_rule('/view/<int:cert_id>', view_func=views.view)
