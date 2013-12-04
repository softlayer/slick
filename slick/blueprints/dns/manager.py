from SoftLayer import DNSManager

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


def get_dns_manager():
    return DNSManager(get_client())
