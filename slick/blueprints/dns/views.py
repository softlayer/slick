from flask import redirect, url_for, flash, render_template

from SoftLayer import DNSManager, SoftLayerAPIError
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
def record_add(zone_id):
    mgr = DNSManager(get_client())

    zone = mgr.get_zone(zone_id, records=True)

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

        mgr.create_record(**fields)

        flash('Zone record created.', 'success')
        return redirect(url_for('.zone_view', zone_id=zone_id))

    payload = {
        'title': 'Add Zone Record',
        'form': form,
        'zone': zone,
    }

    return render_template('zone_add_record.html', **payload)


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

    payload = {
        'title': 'Edit Zone Record',
        'subheader': '%s.%s' % (record['host'], record['domain']['name']),
        'record': record,
    }

    return render_template('zone_edit_record.html', **payload)


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
