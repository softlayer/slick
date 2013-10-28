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
def subnet_view(subnet_id):
    mgr = NetworkManager(get_client())
    subnet = mgr.get_subnet(subnet_id)

    payload = {}
    payload['title'] = "View Subnet"
    payload['subheader'] = subnet['networkIdentifier']
    payload['subnet'] = subnet

    return render_template("network_subnet_view.html", **payload)


@login_required
def vlan_index():
    mgr = NetworkManager(get_client())

    payload = {}
    payload['title'] = 'List VLANs'
    payload['vlans'] = mgr.list_vlans()

    search = ''

    if request.args.get('dc'):
        search = request.args.get('dc')
    elif request.args.get('vlan'):
        search = request.args.get('vlan')

    payload['search'] = search

    return render_template("network_vlan_index.html", **payload)


@login_required
def vlan_view(vlan_id):
    mgr = NetworkManager(get_client())
    vlan = mgr.get_vlan(vlan_id)

    payload = {}
    payload['title'] = "View VLAN"
    payload['subheader'] = 'VLAN ' + str(vlan['vlanNumber'])
    payload['vlan'] = vlan

    return render_template("network_vlan_view.html", **payload)
