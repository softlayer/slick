from flask import flash, redirect, render_template, request, url_for

from SoftLayer import NetworkManager

from slick.utils.core import get_client
from slick.utils.session import login_required
from .forms import CreateSubnetForm
from .manager import cancel_subnet, create_subnet


@login_required
def subnet_cancel(subnet_id):
    (success, message) = cancel_subnet(subnet_id)

    category = 'error'
    if success:
        category = 'success'

    flash(message, category)
    return redirect(url_for('.subnet_index'))


@login_required
def subnet_create(vlan_id):
    form = CreateSubnetForm()
    form.vlan_id.data = vlan_id

    mgr = NetworkManager(get_client())
    vlan = mgr.get_vlan(vlan_id)

    payload = {}
    payload['title'] = 'Create Subnet'
    payload['subheader'] = 'VLAN ' + str(vlan['vlanNumber'])
    payload['form'] = form

    if form.validate_on_submit():
        fields = {
            'type': form.subnet_type.data,
            'quantity': form.quantity.data,
            'vlan_id': form.vlan_id.data,
        }

        (success, message) = create_subnet(**fields)
        if success:
            flash(message, 'success')

            return redirect(url_for(".vlan_index"))
        else:
            flash(message, 'error')

    if form.errors:
        flash('There are validation errors with your submission.', 'error')

    return render_template("network_subnet_create.html", **payload)


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
    elif request.args.get('vlan'):
        search = request.args.get('vlan')

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
