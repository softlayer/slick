from flask import render_template, request
from flask.ext.login import login_required

from SoftLayer import NetworkManager

from app.utils.core import get_client


@login_required
def subnet_index():
    mgr = NetworkManager(get_client())

    mask = [
        'hardware',
        'datacenter',
        'ipAddressCount',
        'virtualGuests',
        'networkVlan',
    ]

    payload = {}
    payload['title'] = 'List Subnets'
    payload['subnets'] = mgr.list_subnets(mask='mask[%s]' % ','.join(mask))

    search = ''

    if request.args.get('dc'):
        search = request.args.get('dc')

    payload['search'] = search

    return render_template("network_subnet_index.html", **payload)


@login_required
def vlan_index():
    mgr = NetworkManager(get_client())

    payload = {}
    payload['title'] = 'List VLANs'
    payload['vlans'] = mgr.list_vlans()

    search = ''

    if request.args.get('dc'):
        search = request.args.get('dc')

    payload['search'] = search

    return render_template("network_vlan_index.html", **payload)
