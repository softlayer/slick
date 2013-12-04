from flask import redirect, url_for, flash, render_template

from SoftLayer import DNSManager, SoftLayerAPIError
from slick.utils.core import get_client
from slick.utils.session import login_required

from .manager import all_zones


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
        'zones': all_zones(),
    }

    return render_template("zone_index.html", **payload)


@login_required
def view(zone_id):
    mgr = DNSManager(get_client())

    zone = mgr.get_zone(zone_id, records=True)

    if not zone:
        flash('DNS zone not found.', 'error')
        return redirect(url_for('.index'))

    payload = {
        'title': 'View Zone',
        'subheader': zone['name'],
        'zone': zone,
    }

    return render_template("zone_view.html", **payload)


@login_required
def edit_record(record_id):
    api = get_client()['Dns_Domain_ResourceRecord']

    try:
        record = api.getObject(id=record_id, mask='domain[name]')
    except SoftLayerAPIError:
        flash('DNS record not found.', 'error')
        return redirect(url_for('.index'))

    payload = {
        'title': 'Edit Zone Record',
        'subheader': '%s.%s' % (record['host'], record['domain']['name']),
        'record': record,
    }

    return render_template('zone_edit_record.html', **payload)
