from flask import Blueprint

blueprint = Blueprint('ticket_module', __name__, template_folder='templates',
                      static_folder='static', url_prefix='/tickets')

from app import app
from . import views, widgets

for widget in widgets.get_widgets():
    app.add_widget(widget)

# Tickets List
blueprint.add_url_rule('/', view_func=views.index)
blueprint.add_url_rule('/index', view_func=views.index)
