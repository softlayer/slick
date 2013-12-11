from flask import redirect, url_for, flash, render_template

from slick.utils.session import login_required

from . import manager, forms


@login_required
def add():
    form = forms.AddSshKeyForm()

    if form.validate_on_submit():
        fields = {}
        for field in form:
            if 'csrf_token' == field.name:
                continue

            fields[field.name] = field.data

        (success, message) = manager.add_key(**fields)
        if success:
            flash(message, 'success')
            return redirect(url_for(".index"))
        else:
            flash(message, 'error')

    payload = {
        'title': 'Add SSH Key',
        'form': form,
    }

    return render_template('key_add.html', **payload)


@login_required
def delete(key_id):
    (success, message) = manager.delete_key(key_id)

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('.index'))


@login_required
def index():
    payload = {
        'title': 'List SSH Keys',
        'keys': manager.list_keys(),
        'submenu': [(url_for('.add'), 'Add SSH Key')],
    }

    return render_template("key_index.html", **payload)


@login_required
def view(key_id):
    key = manager.get_key(key_id)

    if not key:
        flash('SSH key not found.', 'error')
        return redirect(url_for('.index'))

    payload = {
        'title': 'View SSH Key',
        'subheader': key['label'],
        'key': key,
    }

    return render_template("key_view.html", **payload)
