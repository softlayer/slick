from SoftLayer import SshKeyManager, SoftLayerAPIError

from slick.utils.core import get_client


def add_key(key, label, notes=''):
    try:
        get_sshkey_manager().add_key(key, label, notes)
        success = True
        message = 'SSH key added successfully.'
    except SoftLayerAPIError as exception:
        success = False
        message = str(exception.message)

    return (success, message)


def delete_key(key_id):
    try:
        get_sshkey_manager().delete_key(key_id)
        success = True
        message = 'SSH key deleted.'
    except SoftLayerAPIError as exception:
        success = False
        message = str(exception.message)

    return (success, message)


def get_key(key_id):
    try:
        key = get_sshkey_manager().get_key(key_id)
    except SoftLayerAPIError:
        key = None

    return key


def get_sshkey_manager():
    return SshKeyManager(get_client())


def list_keys():
    return get_sshkey_manager().list_keys()
