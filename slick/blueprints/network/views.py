from flask import flash, redirect, render_template, request, url_for

from slick.utils.session import login_required
from . import forms, manager


@login_required
def subnet_cancel(subnet_id):
    """ This function cancels the specified subnet.

    :param int subnet_id: The ID of the subnet to cancel
    """
    (success, message) = manager.cancel_subnet(subnet_id)

    category = 'error'
    if success:
        category = 'success'

    flash(message, category)
    return redirect(url_for('.subnet_index'))


@login_required
def subnet_create(vlan_id):
    """ Provides a form for creating a new subnet on a specified VLAN.

    :param int vlan_id: The ID of the VLAN on which the subnet should reside.
    """
    form = forms.CreateSubnetForm()
    form.vlan_id.data = vlan_id

    vlan = manager.get_vlan(vlan_id)

    if not vlan:
        flash('Invalid VLAN specified.', 'error')
        return redirect(url_for('.subnet_index'))

    payload = {
        'title': 'Create Subnet',
        'subheader': 'VLAN ' + str(vlan['vlanNumber']),
        'form': form,
    }

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

    return render_template("network_subnet_create.html", **payload)


@login_required
def subnet_index():
    """ Displays a tabluar list of subnets on the user's account. """
    payload = {
        'title': 'List Subnets',
        'subnets': manager.list_subnets(),
    }
    search = ''

    if request.args.get('dc'):
        search = request.args.get('dc')
    elif request.args.get('vlan'):
        search = request.args.get('vlan')

    payload['search'] = search

    return render_template("network_subnet_index.html", **payload)


@login_required
def subnet_view(subnet_id):
    """ Displays a detailed view of a single subnet.

    :param int subnet_id: The ID of the subnet to display.
    """
    subnet = manager.get_subnet(subnet_id)

    if not subnet:
        flash('Invalid subnet specified.', 'error')
        return redirect(url_for('.subnet_index'))

    payload = {
        'title': "View Subnet",
        'subheader': subnet['networkIdentifier'],
        'subnet': subnet,
    }

    return render_template("network_subnet_view.html", **payload)


@login_required
def vlan_index():
    """ Displays a tabular list of VLANs on the user's account. """
    payload = {
        'title': 'List VLANs',
        'vlans': manager.list_vlans(),
    }

    search = ''

    if request.args.get('dc'):
        search = request.args.get('dc')
    elif request.args.get('vlan'):
        search = request.args.get('vlan')

    payload['search'] = search

    return render_template("network_vlan_index.html", **payload)


@login_required
def vlan_view(vlan_id):
    """ Displays a detailed view of a specified VLAN.

    :param int vlan_id: The ID of the VLAN to display
    """
    vlan = manager.get_vlan(vlan_id)

    if not vlan:
        flash('Invalid VLAN specified.', 'error')
        return redirect(url_for('.vlan_index'))

    payload = {
        'title': "View VLAN",
        'subheader': 'VLAN ' + str(vlan['vlanNumber']),
        'vlan': vlan,
    }

    return render_template("network_vlan_view.html", **payload)
