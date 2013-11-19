from flask import flash, redirect, render_template, request, url_for

from SoftLayer import MessagingManager

from slick.utils.core import get_client
from slick.utils.session import login_required


@login_required
def queue_list(account_id):
    manager = MessagingManager(get_client())
    mq_client = manager.get_connection(account_id)

    queues = mq_client.get_queues()['items']

    print queues

    return ''
