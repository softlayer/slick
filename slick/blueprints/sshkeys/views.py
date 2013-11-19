from flask import redirect, url_for, flash, render_template

from SoftLayer import SshKeyManager

from slick.utils.core import get_client
from slick.utils.session import login_required


@login_required
def delete(key_id):
    mgr = SshKeyManager(get_client())

    mgr.delete_key(key_id)

    flash("SSH key deleted.", 'success')

    return redirect(url_for('.index'))


@login_required
def index():
    mgr = SshKeyManager(get_client())

    payload = {
        'title': 'List SSH Keys',
        'keys': mgr.list_keys(),
    }

    return render_template("key_index.html", **payload)


@login_required
def view(key_id):
    mgr = SshKeyManager(get_client())

    key = mgr.get_key(key_id)

    if not key:
        flash('SSH key not found.', 'error')
        return redirect(url_for('.index'))

    payload = {
        'title': 'View SSH Key',
        'subheader': key['label'],
        'key': key,
    }

    return render_template("key_view.html", **payload)
