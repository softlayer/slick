from flask import g, redirect, url_for, flash, request, render_template
from flask.ext.login import login_required

from app.blueprints.cci import cci_module
from app.blueprints.cci.forms import CreateCCIForm
from app.blueprints.cci.manager import (all_instances, all_instance_options,
                                        launch_instance, validate_instance)


@cci_module.route('/')
@cci_module.route('/index')
@login_required
def index():
    instance_filter = {}

    instances = all_instances(instance_filter)
    payload = {}
    payload['title'] = 'List Instances'
    payload['instances'] = instances
    return render_template("cci_index.html", **payload)


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
        print "Taco snacks"
        for f in form:
            print f.name,f.data

    if form.errors:
        flash('There are validation errors with your submission.', 'error')

    return render_template('cci_add.html', title='Create Instance', form=form)


@cci_module.route('/priceCheck', methods=['GET', 'POST'])
@login_required
def price_check():
    fields = _extract_cci_fields(request.form)
    results = validate_instance(**fields)
    return render_template('cci_price_quote.html', order_template=results)


def _extract_cci_fields(source):
    form = CreateCCIForm()

    results = {}

    for field in form:
        if 'csrf_token' == field.name:
            continue

        if source.get(field.name):
            results[field.name] = source[field.name]

    return results
