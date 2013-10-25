from flask import render_template

from app import app
from app.utils.core import get_client


def get_widgets():
    data = WidgetData()

    return [ServerStatusWidget(data), BandwidthWidget(data)]


class BandwidthWidget(object):
    def __init__(self, data):
        self.css_class = 'col-md-6'
        self.data = data
        self.javascript = ('vm_module.static', 'js/bandwidth_widget.js')
        self.title = 'Top 10 Devices by Data Transferred'

    def render(self):
        stats = self.data.get_widget_data()

        bandwidth = []
        for vm in sorted(stats['virtualGuests'], reverse=True,
                         key=lambda k:
                         k.get('outboundPublicBandwidthUsage', 0)):
            if len(bandwidth) > 10:
                break
            bandwidth.append(
                (vm['hostname'],
                 round(float(vm['outboundPublicBandwidthUsage']), 2),
                 round(float(vm['projectedPublicBandwidthUsage']), 2)))

        if 'servers' in app.config['installed_blueprints']:
            for server in sorted(stats['hardware'], reverse=True,
                                 key=lambda k:
                                 k.get('outboundPublicBandwidthUsage', 0)):
                if len(bandwidth) > 20:
                    break
                bandwidth.append(
                    (server['hostname'],
                     round(float(server['outboundPublicBandwidthUsage']), 2),
                     round(float(server['projectedPublicBandwidthUsage']), 2)))

        bandwidth = sorted(bandwidth, key=lambda k: k[1], reverse=True)[0:10]
        return render_template('vm_widget_bandwidth.html', bandwidth=bandwidth)


class ServerStatusWidget(object):
    def __init__(self, data):
        self.css_class = 'col-md-4'
        self.data = data
        self.no_body = True
        self.title = 'System Overview'

    def render(self):
        vm_statuses = {
            'active': 0,
            'transaction': 0,
            'down': 0,
            'total': 0,
        }

        stats = self.data.get_widget_data()
        for vm in stats['virtualGuests']:
            vm_statuses['total'] += 1
            if vm.get('activeTransaction'):
                vm_statuses['transaction'] += 1
            elif vm['status']['keyName'] == 'ACTIVE':
                vm_statuses['active'] += 1
            else:
                vm_statuses['down'] += 1

        payload = {
            'stats': stats,
            'title': self.title,
            'vm': vm_statuses,
        }

        if 'servers' in app.config['installed_blueprints']:
            server_statuses = {
                'active': 0,
                'transaction': 0,
                'down': 0,
                'total': 0,
            }

            for server in stats['hardware']:
                server_statuses['total'] += 1
                if server.get('activeTransaction'):
                    server_statuses['transaction'] += 1
                elif server['hardwareStatus']['status'] == 'ACTIVE':
                    server_statuses['active'] += 1
                else:
                    server_statuses['down'] += 1

            payload['server'] = server_statuses

        return render_template('vm_widget_server_status.html', **payload)


class WidgetData(object):
    def __init__(self):
        self.data = None

    def get_widget_data(self):
        if not self.data:
            mask = set([
                'hardware(SoftLayer_Hardware_Server)[id, datacenter[id, name],'
                'hardwareStatus, hostname, outboundPublicBandwidthUsage, '
                'projectedPublicBandwidthUsage, '
                'operatingSystem[softwareLicense[softwareDescription[name]]]]',
                'virtualGuests[id, datacenter[id, name], hostname, status,'
                'outboundPublicBandwidthUsage, projectedPublicBandwidthUsage,'
                'operatingSystem[softwareLicense[softwareDescription[name]]],'
                'activeTransaction]',
            ])

            account = get_client()['Account']
            self.data = account.getObject(mask='mask[%s]' % ','.join(mask))

        return self.data
