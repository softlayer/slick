from flask import render_template

from slick.utils.core import get_client
from slick.utils.date import parse_date
from slick.utils.session import login_required


@login_required
def index():
    account = get_client()['Account']

    mask = set([
        'openTickets[id, modifyDate, title, createDate, status[name], '
        'group[name]]',
    ])
    tickets = account.getObject(mask='mask[%s]' % ','.join(mask))

    payload = {}
    payload['title'] = 'List Tickets'
    payload['tickets'] = tickets['openTickets']
    payload['parse_date'] = parse_date

    return render_template("ticket_index.html", **payload)
