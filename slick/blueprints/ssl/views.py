from flask import redirect, url_for, flash, render_template

from slick.utils.session import login_required
from . import manager


@login_required
def add():
    pass


@login_required
def delete(cert_id):
    (success, message) = manager.delete_cert(cert_id)

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('.index'))


@login_required
def index():
    payload = {
        'title': 'List SSL Certificates',
        'certs': manager.list_certs(),
    }

    return render_template("cert_index.html", **payload)


@login_required
def view(cert_id):
    cert = manager.get_cert(cert_id)

    if not cert:
        flash('SSL certificate not found.', 'error')
        return redirect(url_for('.index'))

    payload = {
        'title': 'View SSL Certificate',
        'cert': cert,
    }

    return render_template("cert_view.html", **payload)
