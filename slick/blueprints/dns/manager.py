from SoftLayer import DNSManager, SoftLayerAPIError

from slick.utils.core import get_client
from slick.utils.date import parse_date


def all_zones():
    """ This method returns a dictionary of all available DNS zones.

    Note that this method is memoized for performance reasons!

    :param string username: The username of the current user. This is used
    to ensure memoization uniqueness.
    """
    zones = []

    for zone in get_dns_manager().list_zones():
        zones.append({'id': zone.get('id'),
                      'name': zone.get('name'),
                      'updated': parse_date(zone.get('updateDate'))})

    return zones


def delete_record(record_id):
    """ Deletes the specified record.

    :param int record_id: The ID of the record being deleted.
    """
    try:
        get_dns_manager().delete_record(record_id)
        success = True
        message = 'Record has been removed.'
    except SoftLayerAPIError as exception:
        success = False
        message = str(exception)

    return (success, message)


def get_dns_manager():
    return DNSManager(get_client())


def get_record(record_id):
    api = get_client()['Dns_Domain_ResourceRecord']

    try:
        record = api.getObject(id=record_id, mask='domain')
    except SoftLayerAPIError:
        record = None

    return record


def get_zone(zone_id):
    mgr = get_dns_manager()

    try:
        zone = mgr.get_zone(zone_id, records=True)
    except SoftLayerAPIError:
        zone = None

    return zone


def update_record(record):
    """ Updates the specified record.

    :param dict record: The full set of information about the record being
    updated. Must contain an 'id' parameter, which will be updated.
    """
    try:
        get_dns_manager().edit_record(record)
        success = True
        message = 'Record updated successfully.'
    except SoftLayerAPIError as exception:
        success = False
        message = str(exception)

    return (success, message)
