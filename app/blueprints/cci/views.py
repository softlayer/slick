from __future__ import division
import json
import math

from flask import redirect, url_for, flash, request, render_template
from flask.ext.login import login_required

from app import app
from app.utils.core import get_client
from app.blueprints.cci import cci_module
from app.blueprints.cci.forms import CreateCCIForm
from app.blueprints.cci.manager import (all_instances, all_instance_options,
                                        get_instance, reload_instance,
                                        launch_instance, validate_instance)


@cci_module.route('/add', methods=['GET', 'POST'])
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

            return redirect(url_for("cci_module.index"))
        else:
            flash(message, 'error')

    if form.errors:
        flash('There are validation errors with your submission.', 'error')

    return render_template('cci_add.html', title='Create Instance', form=form)


@cci_module.route('/', defaults={'page': 1})
@cci_module.route('/index', defaults={'page': 1})
@cci_module.route('/index/page/<int:page>')
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


@cci_module.route('/priceCheck', methods=['GET', 'POST'])
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


@cci_module.route('/reload/<int:cci_id>')
@login_required
def reload_cci(cci_id):
    (success, message) = reload_instance(cci_id)
    return json.dumps({'success': success, 'message': message})


@cci_module.route('/status')
@cci_module.route('/status/<int:cci_id>')
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
