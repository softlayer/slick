from __future__ import division
import json

from flask import redirect, url_for, flash, request, render_template

from slick.utils.core import get_client
from slick.utils.nested_dict import lookup
from slick.utils.session import login_required
from . import forms, manager


@login_required
def change_nic_speed(object_id, nic, speed):
    """ This function will alter the port speed of the specified NIC on the
    VM. It's designed to be called via AJAX.

    :param int object_id: The ID of the instance to change
    :param string nic: The identifier of the network interface to change
    :param int speed: The speed to change the interface to
    """

    (success, message) = manager.change_port_speed(object_id, nic, speed)
    return json.dumps({'success': success, 'message': message})


@login_required
def cancel(vm_id):
    """ This function will cancel the specified virtual machine.

    :param int vm_id: The ID of the instance to change
    """

    (success, message) = manager.cancel_instance(vm_id)
    return json.dumps({'success': success, 'message': message})


@login_required
def create():
    """ Provides an interface for creating a new virtual machine. """

    # Setup the form choices here since we need access to the client object
    # in order to do so.
    form = forms.CreateVMForm()
    all_options = manager.all_instance_options('')

    dc_options = [('', 'First Available')]
    dc_options += all_options['datacenter']
    form.datacenter.choices = dc_options

    os_groups = {}
    for os in all_options['os']:
        group = os[0].split('_')[0].lower()
        if group not in os_groups:
            os_groups[group] = []
        os_groups[group].append(os)

    form.os.choices = all_options['os']
#    os_options = [('', '-- Select --')] + all_options['os']
#    form.os.choices = os_options

    cpu_options = [('', '-- Select --')] + all_options['cpus']
    form.cpus.choices = cpu_options

    ram_options = [('', '-- Select --')] + all_options['memory']
    form.memory.choices = ram_options

    if form.validate_on_submit():
        fields = {}
        for field in form:
            if 'csrf_token' == field.name:
                continue

            fields[field.name] = field.data

        (success, message) = manager.launch_instance(**fields)
        if success:
            flash(message, 'success')

            # TODO - This is not implemented yet
            if request.form.get('save_template'):
                template_name = request.form.get('template_title')

                fields['title'] = template_name
                _save_template(fields)

                flash('Configuration saved for future use.', 'success')

            return redirect(url_for(".index"))
        else:
            flash(message, 'error')

    if form.errors:
        flash('There are validation errors with your submission.', 'error')

    os_names = {
        'centos': 'CentOS',
        'vyattace': 'Vyatta CE',
        'win': 'Windows',
    }

    payload = {
        'title': 'Create Instance',
        'form': form,
        'os_groups': os_groups,
        'os_names': os_names,
    }
    return render_template('vm_add.html', **payload)


@login_required
def edit(vm_id):
    """ Provides an interface for a user to update some information about an
    existing virtual machine.

    :param int vm_id: The ID of the VM to edit
    """
    instance = manager.get_instance(vm_id)

    if not instance:
        flash('Invalid virtual machine specified.', 'error')
        return redirect(url_for('.index'))

    instance['vm_id'] = instance['id']

    form = forms.EditVMForm(**instance)

    if form.validate_on_submit():
        fields = {}
        for field in form:
            if 'csrf_token' == field.name:
                continue

            fields[field.name] = field.data

        (success, message) = manager.edit_instance(**fields)
        if success:
            flash(message, 'success')

            return redirect(url_for(".index"))
        else:
            flash(message, 'error')

    if form.errors:
        flash('There are validation errors with your submission.', 'error')

    payload = {
        'title': 'Edit Instance',
        'form': form,
        'instance': instance,
    }

    return render_template('vm_edit.html', **payload)


@login_required
def get_password(object_id, username):
    """ This function is called via AJAX to retrieve the root/admin password
    for the specified machine and account.

    :param int object_id: The VM ID to retrieve the password for.
    :param string username: The specific admin account that owns the password.
    """

    instance = manager.get_instance(object_id, True)

    if not instance:
        return 'Invalid account'

    password = 'Password not found'

    for account in lookup(instance, 'operatingSystem', 'passwords'):
        if username == account['username']:
            password = account['password']

    return password


@login_required
def hard_reboot_vm(vm_id):
    """ AJAX call to hard reboot a VM.

    :param int vm_id: The ID of the VM to reboot
    """
    (success, message) = manager.reboot_instance(vm_id, False)
    return json.dumps({'success': success, 'message': message})


@login_required
def index():
    """ This function creates a tabular list of all VMs on the user's account.
    """
    instances = manager.all_instances()
    payload = {
        'title': 'List Instances',
        'instances': instances,
        'submenu': [(url_for('.create'), 'Create Instance')],
    }

    search = ''

    if request.args.get('dc'):
        search = request.args.get('dc')

    payload['search'] = search

    return render_template("vm_index.html", **payload)


@login_required
def price_check():
    """ AJAX call to perform a price check on a new VM order. It takes in the
    entire VM creation form, runs it through the validation API call, and then
    returns the results for display.
    """

    form = forms.CreateVMForm()

    fields = {}

    for field in form:
        if 'csrf_token' == field.name:
            continue

        if request.form.get(field.name):
            fields[field.name] = request.form[field.name]

    results = manager.validate_instance(**fields)
    return render_template('vm_price_quote.html', order_template=results)


@login_required
def reload_vm(vm_id):
    """ AJAX call to reload a VM.

    :param int vm_id: The ID of the VM to reload
    """
    (success, message) = manager.reload_instance(vm_id)
    return json.dumps({'success': success, 'message': message})


@login_required
def soft_reboot_vm(vm_id):
    """ AJAX call to soft reboot a VM.

    :param int vm_id: The ID of the VM to reboot
    """
    (success, message) = manager.reboot_instance(vm_id)
    return json.dumps({'success': success, 'message': message})


@login_required
def start_vm(vm_id):
    """ AJAX call to start a halted VM.

    :param int vm_id: The ID of the VM to start
    """
    (success, message) = manager.start_vm(vm_id)
    return json.dumps({'success': success, 'message': message})


@login_required
def stop_vm(vm_id):
    """ AJAX call to stop a running VM.

    :param int vm_id: The ID of the VM to stop
    """
    (success, message) = manager.stop_vm(vm_id)
    return json.dumps({'success': success, 'message': message})


@login_required
def status(vm_id):
    """ AJAX call to run a status check against a single VM. This is used with
    a Javascript timer to update the index for VMs that have active
    transactions.

    :param int vm_id: The ID of the VM you want the status for
    """
    if not vm_id:
        return None

    instance = manager.get_instance(vm_id)
    if not instance:
        return ''

    html = render_template('vm_instance_row.html', instance=instance)

    return json.dumps({
        'active': instance['active'],
        'row_html': html,
    })


@login_required
def view(vm_id):
    """ Provides a complete view page for a single VM.

    :param int vm_id: The ID of the VM to view
    """
    instance = manager.get_instance(vm_id)

    payload = {
        'title': 'View VM',
        'subheader': instance['fqdn'],
        'object': instance,
        'module': 'vm_module',
        'submenu': [(url_for('.edit', vm_id=vm_id), 'Edit')],
    }

    return render_template('shared/object_view.html', **payload)
