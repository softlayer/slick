from flask import Blueprint

from app import app
from . import views

blueprint = Blueprint('ssh_module', __name__, template_folder='templates',
                      url_prefix='/ssh')

submenu = [
    ('ssh_module.index', 'SSH Keys'),
]

app.add_menu('right', submenu, 'Services', 2)

# Key Delete
blueprint.add_url_rule('/delete/<int:key_id>', view_func=views.delete)

# Key List
blueprint.add_url_rule('/', view_func=views.index)
blueprint.add_url_rule('/index', view_func=views.index)
