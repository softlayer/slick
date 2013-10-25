from flask import render_template

from SoftLayer import NetworkManager

from app.utils.core import get_client


def get_widgets():
    return [NetworkSummaryWidget()]


class NetworkSummaryWidget(object):
    def __init__(self):
        self.css_class = 'col-md-6'
        self.no_body = True
        self.title = 'Network Summary by Datacenter'

    def render(self):
        mgr = NetworkManager(get_client())
        return render_template('network_widget_summary.html',
                               stats=mgr.summary_by_datacenter())
