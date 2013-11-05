from flask import render_template

#from app import app
from app.utils.core import get_client
#from app.utils.date import parse_date
from app.utils.nested_dict import lookup


def get_widgets():
    return [TicketDataWidget()]


class TicketDataWidget(object):
    def __init__(self):
        self.css_class = 'col-md-3'
        self.javascript = ('ticket_module.static', 'js/stats_widget.js')
        self.title = 'Ticket Statistics'

    def render(self):
        mask = set([
            'openTickets[id, status[name], group[name]]',
            'ticketsClosedTodayCount',
            'ticketsClosedInTheLastThreeDaysCount',
        ])
        stats = get_client()['Account'].getObject(mask='mask[%s]' %
                                                  ','.join(mask))

        tickets = {
            'closed_today': stats['ticketsClosedTodayCount'],
            'closed_3days': stats['ticketsClosedInTheLastThreeDaysCount'],
            'open': {
                'total': len(stats['openTickets']),
            },
        }

        for ticket in stats['openTickets']:
            category = lookup(ticket, 'group', 'name')

            if not category:
                category = 'Other'

            if category not in tickets['open']:
                tickets['open'][category] = 0

            tickets['open'][category] += 1

        return render_template('ticket_widget_stats.html', tickets=tickets)
