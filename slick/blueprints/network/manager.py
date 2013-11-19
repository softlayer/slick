from slick.utils.core import get_client
from SoftLayer import NetworkManager, SoftLayerAPIError


def cancel_subnet(subnet_id):
    """ Wrapper for the NetworkManager's cancel_subnet() call.

    :param int subnet_id: The ID of the subnet to cancel.
    """

    try:
        get_network_manager().cancel_subnet(subnet_id)
        success = True
        message = 'Cancel subnet successful. Please check your email for ' \
                  'more information.'
    except SoftLayerAPIError as exception:
        success = False
        message = str(exception)

    return (success, message)


def create_subnet(**kwargs):
    try:
        get_network_manager().add_subnet(**kwargs)
        success = True
        message = 'Order placed successfully. Check your email for more ' \
                  'information'
    except SoftLayerAPIError as exception:
        success = False
        message = str(exception)

    return (success, message)


def get_network_manager():
    return NetworkManager(get_client())
