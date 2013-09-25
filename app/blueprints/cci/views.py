from __future__ import division
import json
import math

from flask import redirect, url_for, flash, request, render_template
from flask.ext.login import login_required

from app import app
from app.utils.core import get_client
from app.utils.nested_dict import lookup
from app.blueprints.cci.forms import CreateCCIForm
from app.blueprints.cci.manager import (all_instances, all_instance_options,
                                        change_port_speed, get_instance,
                                        reboot_instance, reload_instance,
                                        launch_instance, validate_instance)


@login_required
def change_nic_speed(cci_id, nic, speed):
    """ This function will alter the port speed of the specified NIC on the
    CCI. It's designed to be called via AJAX.

    :param int instance_id: The ID of the instance to change
    :param string nic: The identifier of the network interface to change
    :param int speed: The speed to change the interface to
    """

    (success, message) = change_port_speed(cci_id, nic, speed)
    return json.dumps({'success': success, 'message': message})


@login_required
def create():
    # Setup the form choices here since we need access to the client object
    # in order to do so.
    form = CreateCCIForm()
    all_options = all_instance_options('')

    dc_options = [('', 'First Available')]
    dc_options += all_options['datacenter']
    form.datacenter.choices = dc_options

    os_options = [('', '-- Select --')] + all_options['os']
    form.os.choices = os_options

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

        (success, message) = launch_instance(**fields)
        if success:
            flash(message, 'success')

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

    return render_template('cci_add.html', title='Create Instance', form=form)


@login_required
def get_password(cci_id, username):
    """ This function is called via AJAX to retrieve the root/admin password
    for the specified machine and account.

    :param int cci_id: The CCI ID to retrieve the password for.
    :param string username: The specific admin account that owns the password.
    """

    instance = get_instance(cci_id, True)

    if not instance:
        return 'Invalid account'

    password = 'Password not found'

    for account in lookup(instance, 'operatingSystem', 'passwords'):
        if username == account['username']:
            password = account['password']

    return password


@login_required
def hard_reboot_cci(cci_id):
    (success, message) = reboot_instance(cci_id, False)
    return json.dumps({'success': success, 'message': message})


@login_required
def index(page):
    instance_filter = {
        'limit': app.config['PAGE_SIZE'],
        'offset': math.floor(app.config['PAGE_SIZE'] * (page - 1)),
    }

    account_obj = get_client()['Account']
    total_ccis = account_obj.getCurrentUser(mask='mask[id,virtualGuestCount]')
    total_ccis = total_ccis.get('virtualGuestCount')

    instances = all_instances(instance_filter)
    payload = {}
    payload['title'] = 'List Instances'
    payload['instances'] = instances
    payload['current_page'] = page
    payload['total_items'] = total_ccis

    return render_template("cci_index.html", **payload)


@login_required
def price_check():
    form = CreateCCIForm()

    fields = {}

    for field in form:
        if 'csrf_token' == field.name:
            continue

        if request.form.get(field.name):
            fields[field.name] = request.form[field.name]

    results = validate_instance(**fields)
    return render_template('cci_price_quote.html', order_template=results)


@login_required
def reload_cci(cci_id):
    (success, message) = reload_instance(cci_id)
    return json.dumps({'success': success, 'message': message})


@login_required
def soft_reboot_cci(cci_id):
    (success, message) = reboot_instance(cci_id)
    return json.dumps({'success': success, 'message': message})


@login_required
def status(cci_id):
    if not cci_id:
        return None

    instance = get_instance(cci_id)
    html = render_template('cci_instance_row.html', instance=instance)

    return json.dumps({
        'active': instance['active'],
        'row_html': html,
    })


@login_required
def view(cci_id):
    instance = get_instance(cci_id)

    payload = {}
    payload['title'] = 'View CCI'
    payload['subheader'] = instance['fqdn']
    payload['object'] = instance
    payload['module'] = 'cci_module'

    return render_template('cci_view.html', **payload)
