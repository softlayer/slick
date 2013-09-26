import json

from flask import redirect, url_for, flash, request, render_template
from flask.ext.login import login_required
from SoftLayer import SoftLayerAPIError

from app import app
from .manager import (all_servers, get_bmc_create_options, get_server,
                      place_order, verify_order)
from .forms import CreateBMCForm


@login_required
def create_bmc():
    # Setup the form choices here since we need access to the client object
    # in order to do so.
    form = CreateBMCForm()
    all_options = get_bmc_create_options('')

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
        fields = {}
        for field in form:
            if 'csrf_token' == field.name:
                continue

            fields[field.name] = field.data

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

    return render_template('server_bmc_add.html', title='Order BMC', form=form)


@login_required
def create_dedicated():
    pass


@login_required
def index():
    servers = all_servers()
    payload = {}
    payload['title'] = 'List Servers'
    payload['servers'] = servers

    return render_template("server_index.html", **payload)


@login_required
def price_check():
    form = CreateBMCForm()

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

    try:
        results = verify_order(**fields)
        return render_template('server_bmc_price_quote.html',
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


def _process_category_items(options, category):
    results = [('', '-- Select --')]
#    previous_sort = None
    for item in options['categories'][category]['items']:
#        if item['sort'] != previous_sort:
#            if previous_sort is not None:
#                results.append(('', '------'))
#            previous_sort = item['sort']
        results.append((item['price_id'], item['description']))
    return results
    