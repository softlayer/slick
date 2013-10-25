import json

from flask import redirect, url_for, flash, request, render_template
from flask.ext.login import login_required
from SoftLayer import SoftLayerAPIError
from wtformsparsleyjs import SelectField
from wtforms.validators import Required

from .manager import (all_servers, get_hourly_create_options, get_server,
                      place_order, verify_order, get_monthly_create_options,
                      get_available_monthly_server_packages)
from .forms import CreateHourlyForm, CreateMonthlyForm


@login_required
def create_hourly():
    # Setup the form choices here since we need access to the client object
    # in order to do so.
    form = CreateHourlyForm()
    all_options = get_hourly_create_options('')

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

        (success, message) = place_order(**fields)
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

    return render_template('server_hourly_add.html',
                           title='Order Hourly Server', form=form)


@login_required
def create_monthly(package_id=None):
    if not package_id:
        payload = {}
        payload['title'] = 'Order Monthly Server - Select Chassis'
        payload['options'] = get_available_monthly_server_packages()

        return render_template("server_monthly_add_package.html", **payload)

    payload = {}
    form = CreateMonthlyForm(package_id=package_id)

    all_options = get_monthly_create_options('', package_id)

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

        (success, message) = place_order(**fields)
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

    return render_template('server_monthly_add.html', **payload)


@login_required
def index():
    servers = all_servers()
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
    if 'hourly' == server_type:
        form = CreateHourlyForm()
    else:
        form = CreateMonthlyForm()

    fields = _extract_fields_from_form(form)

    try:
        results = verify_order(**fields)
        return render_template('server_price_quote.html', type=server_type,
                               order_template=results)
    except SoftLayerAPIError as e:
        return render_template('server_price_quote_error.html',
                               error=str(e.message))


@login_required
def status(server_id):
    if not server_id:
        return None

    server = get_server(server_id)
    html = render_template('server_instance_row.html', server=server)

    return json.dumps({
        'active': server['active'],
        'row_html': html,
    })


def _extract_fields_from_form(form):
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
    results = [('', '-- Select --')]
#    previous_sort = None
    for item in options['categories'][category]['items']:
#        if item['sort'] != previous_sort:
#            if previous_sort is not None:
#                results.append(('', '------'))
#            previous_sort = item['sort']
        results.append((str(item['price_id']), item['description']))
    return results
    