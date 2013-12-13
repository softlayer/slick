import json

from flask import redirect, url_for, flash, request, render_template
from SoftLayer import SoftLayerAPIError
from wtformsparsleyjs import SelectField
from wtforms.validators import Required

from slick.utils.nested_dict import lookup
from slick.utils.session import login_required
from . import forms, manager


@login_required
def change_nic_speed(object_id, nic, speed):
    """ This function will alter the port speed of the specified NIC on the
    server. It's designed to be called via AJAX.

    :param int object_id: The ID of the instance to change
    :param string nic: The identifier of the network interface to change
    :param int speed: The speed to change the interface to
    """

    (success, message) = manager.change_port_speed(object_id, nic, speed)
    return json.dumps({'success': success, 'message': message})


@login_required
def create_hourly():
    """ This presents a form for creating an hourly bare metal server,
    previously known as a bare metal cloud (BMC).
    """
    # Setup the form choices here since we need access to the client object
    # in order to do so.
    form = forms.CreateHourlyForm()
    all_options = manager.get_hourly_create_options('')

    dc_options = []
    for dc in all_options['locations']:
        dc_options.append((dc['keyname'], dc['long_name']))
    form.location.choices = dc_options

    form.server.choices = _process_category_items(all_options, 'server_core')
    form.os.choices = _process_category_items(all_options, 'os')
    form.port_speed.choices = _process_category_items(all_options,
                                                      'port_speed')
    for entry in form.disks.entries:
        entry.choices = _process_category_items(all_options, 'disk0')

    if form.validate_on_submit():
        fields = _extract_fields_from_form(form)

        (success, message) = manager.place_order(**fields)
        if success:
            flash(message, 'success')

            # TODO - This isn't implemented yet
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

    return render_template('server_hourly_add.html',
                           title='Order Hourly Server', form=form)


@login_required
def create_monthly(package_id=None):
    """ This presents a form for ordering a monthly dedicated server. """

    # If we don't have a package ID yet, show the chassis selection page.
    if not package_id:
        payload = {}
        payload['title'] = 'Order Monthly Server - Select Chassis'
        payload['options'] = manager.get_available_monthly_server_packages()

        return render_template("server_monthly_add_package.html", **payload)

    payload = {}
    form = forms.CreateMonthlyForm(package_id=package_id)

    all_options = manager.get_monthly_create_options('', package_id)

    dc_options = []
    for dc in all_options['locations']:
        dc_options.append((dc['keyname'], dc['long_name']))
    form.location.choices = dc_options

    form.server.choices = _process_category_items(all_options, 'server')
    form.ram.choices = _process_category_items(all_options, 'ram')
    form.os.choices = _process_category_items(all_options, 'os')
    form.port_speed.choices = _process_category_items(all_options,
                                                      'port_speed')
    form.disk_controller.choices = _process_category_items(all_options,
                                                           'disk_controller')

    # Setup disk choices
    form.disks.entries[0].choices = _process_category_items(all_options,
                                                            'disk0')

    for category, data in all_options['categories'].items():
        if category.startswith('disk') and category not in ['disk0',
                                                            'disk_controller']:
            if data['is_required']:
                disk_num = category.replace('disk', '')
                field = SelectField('Disks', validators=[Required()])
                form.disks.append_entry(field)
                choices = _process_category_items(all_options,
                                                  'disk' + disk_num)
                form.disks.entries[int(disk_num)].choices = choices

    payload['form'] = form
    payload['title'] = 'Order Monthly Server - Details'
    payload['options'] = all_options
#    payload['domains'] = all_zones(current_username())

    # I want to display these in a different order than the API suggests, so
    # I'm going to exclude them from their normal sections.
    payload['excluded_options'] = ['os', 'ram', 'server', 'disk_controller']

    if form.validate_on_submit():
        fields = _extract_fields_from_form(form)

        (success, message) = manager.place_order(**fields)
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

    return render_template('server_monthly_add.html', **payload)


@login_required
def get_password(object_id, username):
    """ This function is called via AJAX to retrieve the root/admin password
    for the specified machine and account.

    :param int object_id: The server ID to retrieve the password for.
    :param string username: The specific admin account that owns the password.
    """

    server = manager.get_server(object_id, True)

    if not server:
        return 'Invalid account'

    password = 'Password not found'

    for account in lookup(server, 'operatingSystem', 'passwords'):
        if username == account['username']:
            password = account['password']

    return password


@login_required
def hard_reboot_server(server_id):
    """ AJAX call to hard reboot a server.

    :param int vm_id: The ID of the server to reboot
    """
    (success, message) = manager.reboot_server(server_id, False)
    return json.dumps({'success': success, 'message': message})


@login_required
def index():
    """ Displays a list of all servers on the user's account. This includes
    both hourly and monthly servers.
    """

    servers = manager.all_servers()
    payload = {}
    payload['title'] = 'List Servers'
    payload['servers'] = servers

    search = ''

    if request.args.get('dc'):
        search = request.args.get('dc')

    payload['search'] = search

    return render_template("server_index.html", **payload)


@login_required
def price_check(server_type):
    """ AJAX call to perform a price check on a new server order. It takes in
    the entire server creation form, runs it through the validation API call,
    and then returns the results for display.

    :param string server_type: Used to determine if we're ordering an hourly or
                               monthly server so the right form is loaded.
    """

    if 'hourly' == server_type:
        form = forms.CreateHourlyForm()
    else:
        # TODO - Don't I need a package ID here?
        form = forms.CreateMonthlyForm()

    fields = _extract_fields_from_form(form)

    try:
        results = manager.verify_order(**fields)
        return render_template('server_price_quote.html', type=server_type,
                               order_template=results)
    except SoftLayerAPIError as e:
        return render_template('server_price_quote_error.html',
                               error=str(e.message))


@login_required
def server_reload(server_id):
    """ AJAX call to reload a server.

    :param int vm_id: The ID of the server to reload
    """
    (success, message) = manager.reload_server(server_id)
    return json.dumps({'success': success, 'message': message})


@login_required
def soft_reboot_server(server_id):
    """ AJAX call to soft reboot a server.

    :param int vm_id: The ID of the server to reboot
    """
    (success, message) = manager.reboot_server(server_id)
    return json.dumps({'success': success, 'message': message})


@login_required
def status(server_id):
    """ AJAX call to run a status check against a single server. This is used
    with a Javascript timer to update the index for servers that have active
    transactions.

    :param int vm_id: The ID of the server you want the status for
    """
    if not server_id:
        return None

    server = manager.get_server(server_id)
    html = render_template('server_instance_row.html', server=server)

    return json.dumps({
        'active': server['active'],
        'row_html': html,
    })


@login_required
def view(server_id):
    """ Provides a complete view page for a single server.

    :param int vm_id: The ID of the server to view
    """
    server = manager.get_server(server_id)

    payload = {}
    payload['title'] = 'View Server'
    payload['subheader'] = server['fqdn']
    payload['object'] = server
    payload['module'] = 'server_module'

    return render_template('shared/object_view.html', **payload)


def _extract_fields_from_form(form):
    """ Helper method for extracting fields from a form. This was created to
    encapsulate repeated code.

    :param object form: The wtform object being processed
    """
    fields = {}

    for field in form:
        if 'csrf_token' == field.name:
            continue

        if request.form.get(field.name):
            fields[field.name] = request.form[field.name]

    fields['disks'] = []
    for key, value in sorted(request.form.items()):
        if key.startswith('disks-'):
            fields['disks'].append(value)

    if fields.get('bare_metal'):
        fields['hourly'] = True

    return fields


def _process_category_items(options, category):
    """ Helper method for setting up category items for form fields. This was
    done to encapsulate repeated code.

    :param dict options: The dictionary of options
    :param string category: The category to extract from the options dictionary
    """
    results = [('', '-- Select --')]
    for item in options['categories'][category]['items']:
        results.append((str(item['price_id']), item['description']))
    return results
    