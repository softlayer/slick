from SoftLayer import DNSManager, SoftLayerAPIError

from slick.utils.core import get_client
from slick.utils.date import parse_date


def add_record(zone_id, host, rec_type, data, ttl=60):
    """ Creates a new record based upon the passed information.

    :param int zone_id: The ID of the zone in which this record should be
                        created.
    :param string host: Host entry for the new record
    :param string rec_type: The DNS type of the new record
    :param string data: The data value of the new record
    :param int ttl: The TTL for the new record. Defaults to 60.
    """

    record = {
        'zone_id': zone_id,
        'record': host,
        'type': rec_type,
        'data': data,
        'ttl': ttl,
    }
    try:
        get_dns_manager().create_record(**record)
        success = True
        message = 'Record created successfully.'
    except SoftLayerAPIError as exception:
        success = False
        message = str(exception)

    return (success, message)


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


def get_zone_id_by_name(zone):
    return get_dns_manager()._get_zone_id_from_name(zone)[0]


def search_record(zone, record):
    mgr = get_dns_manager()
    zone_id = mgr._get_zone_id_from_name(zone)[0]
    return mgr.get_records(zone_id, host=record)


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
