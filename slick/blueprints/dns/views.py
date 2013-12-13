import json

from flask import redirect, url_for, flash, render_template
from slick.utils.core import get_client
from slick.utils.session import login_required

from .forms import ZoneRecordForm
import manager


# @login_required
# def delete(key_id):
#     mgr = SshKeyManager(get_client())

#     mgr.delete_key(key_id)

#     flash("SSH key deleted.", 'success')

#     return redirect(url_for('.index'))


@login_required
def index():
    payload = {
        'title': 'List DNS Zones',
        'zones': manager.all_zones(),
    }

    return render_template("zone_index.html", **payload)


@login_required
def quick_register(domain, hostname, ip):
    """ This method attempts to immediately register the specified hostname in
    the specified zone as an A record with a TTL of 3600.

    :param string domain: The domain in which the record should be registered.
    :param string hostname: The hostname for the new record.
    :param string ip: The IP address to associate with the new record.
    """
    existing_record = manager.search_record(domain, hostname)

    already_exists = False
    success = True

    # Check to see if the record already exists. This is a quick, slight weak
    # attempt to avoid registering duplicate or conflicting records. If we want
    # to support round robin A records, this code should be removed.
    if existing_record:
        if existing_record[0].get('data') == ip:
            already_exists = 'Record already registered in DNS.'
        elif existing_record[0].get('type') == 'a':
            success = False
            already_exists = 'Record registered with a different IP. Aborting.'
        else:
            success = False
            already_exists = 'A non-A record already exists for this name.' \
                             'Aborting.'

    if already_exists:
        return json.dumps({
            'success': success,
            'message': already_exists
        })

    domain_id = manager.get_zone_id_by_name(domain)
    if not domain_id:
        return json.dumps({
            'success': False,
            'message': 'Invalid domain specified.',
        })

    # Create the dictionary that will be used to create the new record.
    # This method hardcodes some values to make the process a single click.
    fields = {
        'zone_id': domain_id,
        'rec_type': 'A',
        'host': hostname,
        'data': ip,
        'ttl': 3600,
    }

    (success, message) = manager.add_record(**fields)

    return json.dumps({
        'success': success,
        'message': message,
    })


@login_required
def record_add(zone_id):
    zone = manager.get_zone(zone_id)

    if not zone:
        flash('DNS zone not found.', 'error')
        return redirect(url_for('.index'))

    form = ZoneRecordForm(zone_id=zone_id)

    if form.validate_on_submit():
        fields = {}
        for field in form:
            if 'csrf_token' == field.name:
                continue

            fields[field.name] = field.data

        fields['rec_type'] = fields['type']
        del(fields['type'])

        manager.add_record(**fields)

        flash('Zone record created.', 'success')
        return redirect(url_for('.zone_view', zone_id=zone_id))

    payload = {
        'title': 'Add Zone Record',
        'form': form,
        'zone': zone,
        'action': url_for('.record_add', zone_id=zone_id),
        'action_name': 'Add',
    }

    return render_template('zone_update_record.html', **payload)


@login_required
def record_delete(record_id):
    """ This function will remove the record ID from the specified zone.

    :param int id: The ID of the record to remove

    """

    record = manager.get_record(record_id)

    if not record:
        flash('DNS record not found.', 'error')
        return redirect(url_for('.index'))

    (success, message) = manager.delete_record(record_id)

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('.zone_view', zone_id=record['domain']['id']))


@login_required
def record_edit(record_id):
    record = manager.get_record(record_id)

    if not record:
        flash('DNS record not found.', 'error')
        return redirect(url_for('.index'))

    defaults = record
    defaults['zone_id'] = record['domain']['id']

    form = ZoneRecordForm(**defaults)

    if form.validate_on_submit():
        fields = {'id': record_id}

        for field in form:
            if 'csrf_token' == field.name:
                continue

            fields[field.name] = field.data

        (success, message) = manager.update_record(fields)

        if success:
            flash(message, 'success')
        else:
            flash(message, 'error')

        return redirect(url_for('.zone_view', zone_id=record['domain']['id']))

    payload = {
        'title': 'Edit Zone Record',
        'subheader': '%s.%s' % (record['host'], record['domain']['name']),
        'record': record,
        'form': form,
        'action': url_for('.record_edit', record_id=record_id),
        'action_name': 'Edit',
        'zone': record['domain'],
    }

    return render_template('zone_update_record.html', **payload)


@login_required
def zone_view(zone_id):
    zone = manager.get_zone(zone_id)

    if not zone:
        flash('DNS zone not found.', 'error')
        return redirect(url_for('.index'))

    payload = {
        'title': 'View Zone',
        'subheader': zone['name'],
        'submenu': [(url_for('.record_add', zone_id=zone_id), 'Add Record')],
        'zone': zone,
    }

    return render_template("zone_view.html", **payload)
