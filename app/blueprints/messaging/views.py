from flask import flash, redirect, render_template, request, url_for

from SoftLayer import MessagingManager

from app.utils.core import get_client
from app.utils.session import login_required
#from .forms import CreateSubnetForm
#from .manager import cancel_subnet, create_subnet


@login_required
def queue_list(account_id):
    manager = MessagingManager(get_client())
    mq_client = manager.get_connection(account_id)

    queues = mq_client.get_queues()['items']

    print queues

    return ''
