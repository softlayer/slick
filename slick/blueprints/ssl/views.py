from flask import redirect, url_for, flash, render_template

from SoftLayer import SSLManager

from slick.utils.core import get_client
from slick.utils.session import login_required


@login_required
def delete(cert_id):
    mgr = SSLManager(get_client())

    mgr.remove_certificate(cert_id)

    flash("SSL certificate deleted.", 'success')

    return redirect(url_for('.index'))


@login_required
def index():
    mgr = SSLManager(get_client())

    payload = {
        'title': 'List SSL Certificates',
        'certs': mgr.list_certs(),
    }

    return render_template("cert_index.html", **payload)


@login_required
def view(cert_id):
    mgr = SSLManager(get_client())

    cert = mgr.get_certificate(cert_id)

    if not cert:
        flash('SSL certificate not found.', 'error')
        return redirect(url_for('.index'))

    payload = {
        'title': 'View SSL Certificate',
        'cert': cert,
    }

    return render_template("cert_view.html", **payload)
