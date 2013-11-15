from flask import redirect, url_for, flash, render_template

from SoftLayer import SshKeyManager

from app.utils.core import get_client
#from app.utils.nested_dict import lookup
from app.utils.session import login_required
#from app.blueprints.vm.forms import CreateVMForm
#from app.blueprints.vm.manager import (all_instances, all_instance_options,
#                                       cancel_instance, change_port_speed,
#                                       get_instance, launch_instance,
#                                       reboot_instance, reload_instance,
#                                       validate_instance)


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
