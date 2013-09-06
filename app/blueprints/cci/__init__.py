from flask import Blueprint

cci_module = Blueprint('cci_module', __name__, template_folder='templates',
                       url_prefix='/cci')

from app import app
from app.blueprints.cci import views

submenu = [
    ('cci_module.index', 'List Instances'),
    ('cci_module.create', 'Create Instance'),
]
app.add_menu('left', submenu, 'Compute', 1)
