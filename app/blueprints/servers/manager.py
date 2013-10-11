from app.utils.core import get_client
from app.utils.nested_dict import lookup, multikeysort
from SoftLayer import HardwareManager, SoftLayerAPIError


def all_servers(hw_filter=None):
    systems = []

    if not hw_filter:
        hw_filter = {}

    for hw in get_hardware_manager().list_hardware(**hw_filter):
        systems.append(_extract_hw_data(hw))

    return systems


#@memoized
def get_hourly_create_options(username):
    results = get_hardware_manager().get_bare_metal_create_options()

    # Sort locations by their long name
    results['locations'] = sorted(results['locations'],
                                  key=lambda x: x['long_name'])

    # Sort items within each category by the sort key, then the capacity key
    for k, v in results['categories'].iteritems():
        items = multikeysort(v['items'], ['sort', 'capacity'])
        results['categories'][k]['items'] = items

    # Deleting the 'other' category since we don't need it
    if results['categories'].get('other'):
        del(results['categories']['other'])
    return results


def get_hardware_manager():
    return HardwareManager(get_client())


def get_server(server_id, full_data=False):
    try:
        server = get_hardware_manager().get_hardware(server_id)
    except SoftLayerAPIError:
        return None

    if not full_data:
        return _extract_hw_data(server)

    return server


def place_order(**kwargs):
    try:
        get_hardware_manager().place_order(**kwargs)
        success = True
        message = 'Order placed successfully. Check your email for more ' \
                  'information'
    except SoftLayerAPIError as exception:
        success = False
        message = str(exception)

    return (success, message)


def verify_order(**kwargs):
    return get_hardware_manager().verify_order(**kwargs)


def _extract_hw_data(hw):
    return_data = {
        'id': hw.get('id', None),
        'hostname': hw.get('hostname'),
        'domain': hw.get('domain'),
        'fqdn': hw.get('fullyQualifiedDomainName', None),
        'datacenter': hw.get('datacenter', {}).get('name', None),
        'public': hw.get('primaryIpAddress', None),
        'private': hw.get('primaryBackendIpAddress', None),
        'cpu': hw.get('processorCoreAmount', None),
        'memory': hw.get('memoryCapacity', None),
    }

    if hw.get('activeTransaction'):
        active = False
#        print hw['activeTransaction']
        status = lookup(hw, 'activeTransaction', 'transactionStatus',
                        'friendlyName')

        if not status:
            status = 'Unknown status'

    else:
        active = True
        status = 'Running'

    return_data['active'] = active
    return_data['status'] = status
    # status_id = hw.get('hardwareStatusId')

    # if status_id == 5:
    #     return_data['active'] = True
    # else:
    #     return_data['active'] = False

    os_block = lookup(hw, 'operatingSystem', 'softwareLicense',
                      'softwareDescription')

    if os_block:
        return_data['os'] = os_block['name'] + ' ' + os_block['version']

    if lookup(hw, 'operatingSystem', 'passwords'):
        usernames = []
        for username in lookup(hw, 'operatingSystem', 'passwords'):
            usernames.append(username['username'])
        return_data['usernames'] = usernames

    if hw.get('networkComponents'):
        network = []
        for comp in hw.get('networkComponents'):
            net = {'status': comp['status'],
                   'speed': comp['speed'],
                   'maxSpeed': comp['maxSpeed'],
                   'name': comp['name'],
                   'port': comp.get('port'),
                   }

            if comp.get('macAddress'):
                net['mac'] = comp.get('macAddress')
            elif comp.get('ipmiMacAddress'):
                net['mac'] = comp.get('ipmiMacAddress')

            if comp.get('primaryIpAddress'):
                net['ip'] = comp.get('primaryIpAddress')
            elif comp.get('ipmiIpAddress'):
                net['ip'] = comp.get('ipmiIpAddress')

            if comp.get('primarySubnet'):
                subnet = {
                    'netmask': lookup(comp, 'primarySubnet', 'netmask'),
                    'broadcast': lookup(comp, 'primarySubnet',
                                        'broadcastAddress'),
                    'gateway': lookup(comp, 'primarySubnet', 'gateway'),
                    'network_identifier': lookup(comp, 'primarySubnet',
                                                 'networkIdentifier'),
                }
                net['subnet'] = subnet

            network.append(net)

        return_data['network'] = network

    return return_data
