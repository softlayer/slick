from flask import render_template

from SoftLayer import MessagingManager

from slick.utils.core import get_client


def get_widgets():
    return [MQSummaryWidget()]


class MQSummaryWidget(object):
    def __init__(self):
        self.width = 'small'
        self.height = 'large'
        self.no_body = True
        self.title = 'Message Queue Summary'

    def render(self):
        mgr = MessagingManager(get_client())
        return render_template('mq_widget_summary.html',
                               accounts=mgr.list_accounts())
