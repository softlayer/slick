""" This module provides a wrapper for API calls related to CloudCompute.

"""
#from slick.client.dns import all_zones
#from slick.utils.memoized import memoized
from slick.utils.core import get_client
from slick.utils.nested_dict import lookup
from SoftLayer import CCIManager, SoftLayerAPIError


#@memoized
def all_instance_options(username):
    """ Retrieves all of the available instance options and caches them.

    Note that this function takes a username as an argument for the express
    purpose of guaranteeing things are memoized on a per-user basis. Otherwise,
    the wrong instance options may be cached in the event that multiple users
    hit the tool simultaneously.
    """

    all_options = get_vm_manager().get_create_options()

    # Prime our results dictionary.
    results = {
        'cpus': _extract_processor_options(all_options),
        'domains': _extract_domain_options(username),
        'datacenter': _extract_datacenter_options(all_options),
        'memory': _extract_memory_options(all_options),
        'os': _extract_os_options(all_options),
    }

    return results


def all_instances(instance_filter=None):
    """ This method will retrieve all CloudCompute instances and return
    them as a list.
    """
    instances = []

    if not instance_filter:
        instance_filter = {}

    for instance in get_vm_manager().list_instances(**instance_filter):
        instances.append(_extract_instance_data(instance))

    return instances


def change_port_speed(instance_id, nic, speed):
    public = True
    if 'eth0' == nic:
        public = False

    try:
        get_vm_manager().change_port_speed(instance_id, public, speed)
        success = True
        message = "Port speed changed. It may take up to a minute for this " \
                  "to take effect"
    except SoftLayerAPIError as exception:
        success = False
        message = str(exception.message)

    return (success, message)


def cancel_instance(instance_id):
    """ Wrapper for the CCIManager's cancel_instance() call.

    :param int instance_id: The ID of the CloudCompute instance to cancel.
    """

    try:
        get_vm_manager().cancel_instance(instance_id)
        success = True
        message = 'Cancel instance successful. Please check your email for ' \
                  'more information.'
    except SoftLayerAPIError as exception:
        success = False
        message = str(exception.message)

    return (success, message)


def edit_instance(vm_id, hostname='', domain='', notes='', userdata=''):
    """ This method wraps the CCIManager's edit() call.

    :param string hostname: The new hostname for the VM.
    :param string domain: The new domain for the VM.
    :param string notes: Notes to set on the instance.
    :param string userdata: User data to set on the VM.
    """
    instance = {
        'id': vm_id,
        'hostname': hostname,
        'domain': domain,
        'notes': notes,
        'userdata': userdata,
    }

    try:
        get_vm_manager().edit(**instance)
        success = True
        message = 'Edit instance successful. Please check your email ' \
                  'for more information.'
    except SoftLayerAPIError as exception:
        success = False
        message = str(exception.message)

    return (success, message)


def get_vm_manager():
    return CCIManager(get_client())


def get_instance(instance_id, full_data=False):
    """ Wrapper for the CCIManager's get_instance() call.

    :param int instance_id: The ID of the CloudCompute instance to cancel.
    """
    try:
        instance = get_vm_manager().get_instance(instance_id)
    except SoftLayerAPIError:
        return None

    if not full_data:
        return _extract_instance_data(instance)

    return instance


def launch_instance(hostname, domain, os, cpus, memory, network, tags='', datacenter=''):
    """ This method wraps the CCIManager's create_instance() call.

    :param string datacenter: The datacenter in which to spin up the new VM.
    :param string hostname: The hostname for the new VM.
    :param string domain: The domain for the new VM.
    :param string os: The code for the operating system to load onto the VM.
    :param int cpus: The number of CPUs needed for the new VM.
    :param int memory: The amount of memory (in MB) for the new VM.
    :param int network: The speed (in Mbps) for the new VM.
    :param string tags: The tags associated with the new VM.
    """
    instance = {
        'datacenter': datacenter,
        'hostname': hostname,
        'domain': domain,
        'os_code': os,
        'cpus': cpus,
        'memory': memory,
        'nic_speed': network,
        'tags': tags
    }

    try:
        get_vm_manager().create_instance(**instance)
        success = True
        message = 'Create instance successful. Please check your email ' \
                  'for more information.'
    except SoftLayerAPIError as exception:
        success = False
        message = str(exception.message)

    return (success, message)


def reboot_instance(instance_id, soft=True):
    """ Provides a single interface function for rebooting a VM.

    :param int instance_id: The ID of the CloudCompute instance to reboot.
    :param bool soft: Flag to determine if this should be a soft or hard
                      reboot. [Default: true (soft)]
    """
    try:
        vg = get_client()['Virtual_Guest']
        if soft:
            vg.rebootSoft(id=instance_id)
        else:
            vg.rebootHard(id=instance_id)
        success = True
        message = 'Reboot request sent to instance.'
    except SoftLayerAPIError as exception:
        success = False
        message = str(exception.message)

    return (success, message)


def reload_instance(instance_id):
    """ Wrapper for the CCIManager's reload_instance() call.

    :param int instance_id: The ID of the CloudCompute instance to reload.
    """

    try:
        get_vm_manager().reload_instance(instance_id)
        success = True
        message = 'Reload request issued. You will receive an email when ' \
                  'the reload is complete.'
    except SoftLayerAPIError as exception:
        success = False
        message = str(exception.message)

    return (success, message)


def start_vm(instance_id):
    """ Starts a halted virtual machine.

    :param int instance_id: The ID of the virtual machine to start.
    """
    vg_client = get_client()['Virtual_Guest']

    try:
        vg_client.powerOn(id=instance_id)
        success = True
        message = 'Instance is being started.'
    except SoftLayerAPIError as exception:
        success = False
        message = str(exception.message)

    return (success, message)


def stop_vm(instance_id):
    """ Stops a running virtual machine.

    :param int instance_id: The ID of the virtual machine to stop.
    """
    vg_client = get_client()['Virtual_Guest']

    try:
        vg_client.powerOff(id=instance_id)
        success = True
        message = 'Instance is being stopped.'
    except SoftLayerAPIError as exception:
        success = False
        message = str(exception.message)

    return (success, message)


def validate_instance(hostname, domain, os, cpus, memory, network, datacenter=''):
    """ This method wraps the CCIManager's verify_create_instance() call.

    Useful if you want to get a price quote or just check the parameters before
    actually placing an order.

    :param string datacenter: The datacenter in which to spin up the new VM.
    :param string hostname: The hostname for the new VM.
    :param string domain: The domain for the new VM.
    :param string os: The code for the operating system to load onto the VM.
    :param int cpus: The number of CPUs needed for the new VM.
    :param int memory: The amount of memory (in MB) for the new VM.
    :param int network: The speed (in Mbps) for the new VM.
    :returns: Returns a dict containing the order template for a valid order
    """
    instance = {
        'datacenter': datacenter,
        'hostname': hostname,
        'domain': domain,
        'os_code': os,
        'cpus': cpus,
        'memory': memory,
        'nic_speed': network
    }

    return get_vm_manager().verify_create_instance(**instance)


#########################
# Begin private methods #
#########################
def _extract_domain_options(username):
    """ This method creates the list of available zones using the DNS client.

    :param string username: The name of the current user. Used for memoization.
    """
    results = []

#    for zone in all_zones(username):
#        results.append((zone['name'], zone['name']))

    return results


def _extract_datacenter_options(all_options):
    """ This method extracts all available datacenters from the
    all_options dict.

    :param dict all_options: The all_options dictionary produced by
    the get_create_options() API call.

    """
    # Reference for data center codes to give them a prettier name.
    datacenters = {
        'ams01': 'Amsterdam',
        'dal01': 'Dallas (1)',
        'dal05': 'Dallas (5)',
        'sea01': 'Seattle',
        'sjc01': 'San Jose',
        'sng01': 'Singapore',
        'wdc01': 'Washington, D.C.'
    }

    results = []
    # Load and sort all data centers
    for option in all_options['datacenters']:
        name = lookup(option, 'template', 'datacenter', 'name')

        if name and name in datacenters:
            name = datacenters[name]
        results.append((lookup(option, 'template', 'datacenter', 'name'),
                        name))
    results = sorted(results)

    return results


def _extract_instance_data(instance):
    """ This option takes an instance record from the API and extracts
    its useful data into a flattened dictionary.

    :param dict instance: The instance dictionary from the API.
    """
    if instance.get('activeTransaction'):
        active = False
        status = lookup(instance, 'activeTransaction', 'transactionStatus',
                        'friendlyName')

        if not status:
            status = 'Unknown status'
    elif instance['powerState'].get('keyName') == 'HALTED':
        active = False
        status = 'Stopped'
    else:
        active = True
        status = 'Running'

    tagReferencesList = instance.get('tagReferences', None)
    if not tagReferencesList:
        tag = 'None'
    else:
        tagsReference = tagReferencesList[0]
        tags = tagsReference.get('tag')
        tag = tags.get('name')
        x = 1
        while (x < len(tagReferencesList)):
            tagsReference = tagReferencesList[x]
            tags = tagsReference.get('tag')
            tag = tag + ', ' + tags.get('name')
            x = x + 1
        
    return_data = {
        'id': instance.get('id', None),
        'hostname': instance.get('hostname'),
        'domain': instance.get('domain'),
        'fqdn': instance.get('fullyQualifiedDomainName', None),
        'datacenter': instance.get('datacenter', {}).get('name', None),
        'public': instance.get('primaryIpAddress', None),
        'private': instance.get('primaryBackendIpAddress', None),
        'cpu': instance.get('maxCpu', None),
        'memory': instance.get('maxMemory', None),
        'active': active,
        'status': status,
        'notes': instance.get('notes'),
        'userdata': instance.get('userdata'),
        'tags': tag
    }

    os_block = lookup(instance, 'operatingSystem', 'softwareLicense',
                      'softwareDescription')

    if os_block:
        return_data['os'] = os_block['name'] + ' ' + os_block['version']
        return_data['os_code'] = os_block['referenceCode']

    if lookup(instance, 'operatingSystem', 'passwords'):
        usernames = []
        for username in lookup(instance, 'operatingSystem', 'passwords'):
            usernames.append(username['username'])
        return_data['usernames'] = usernames

    if instance.get('networkComponents'):
        network = []
        for comp in instance.get('networkComponents'):
            net = {'status': comp['status'],
                   'speed': comp['speed'],
                   'maxSpeed': comp['maxSpeed'],
                   'name': comp['name'],
                   'port': comp.get('port'),
                   'id': comp['id'],
                   }

            if comp.get('macAddress'):
                net['mac'] = comp.get('macAddress')

            if comp.get('primaryIpAddress'):
                net['ip'] = comp.get('primaryIpAddress')

            if comp.get('primarySubnet'):
                subnet = {'netmask': lookup(comp, 'primarySubnet', 'netmask'),
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


def _extract_memory_options(all_options):
    """ This method extracts all memory options from the all_options dict.

    :param dict all_options: The all_options dictionary produced by
    the get_create_options() API call.

    """
    results = []

    # Load and sort memory options
    for option in all_options['memory']:
        results.append((str(lookup(option, 'template', 'maxMemory')),
                        lookup(option, 'itemPrice', 'item', 'description')))

    return results


def _extract_os_options(all_options):
    """ This method extracts all O/S options from the all_options dict.

    :param dict all_options: The all_options dictionary produced by
    the get_create_options() API call.

    """
    results = []

    # Load and sort available operating systems
    # TODO - Turn this into relational fields
    for option in all_options['operatingSystems']:
        # Remove premium operating systems from the list
        recurring_fee = int(lookup(option, 'itemPrice', 'recurringFee'))
        if not recurring_fee:
            results.append((lookup(option, 'template',
                                   'operatingSystemReferenceCode'),
                            lookup(option, 'itemPrice', 'item',
                                   'description')))

    return sorted(results)


def _extract_processor_options(all_options):
    """ This method extracts all processor options from the all_options dict.

    :param dict all_options: The all_options dictionary produced by
    the get_create_options() API call.

    """
    results = []

    # Load all processor options except for those tied to
    # dedicated account hosts
    for option in all_options['processors']:
        if 'dedicatedAccountHostOnlyFlag' not in option['template'] \
           or not lookup(option, 'template', 'dedicatedAccountHostOnlyFlag'):
            results.append((str(lookup(option, 'template', 'startCpus')),
                            lookup(option, 'itemPrice', 'item', 'description')
                            ))

    return results
