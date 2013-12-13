import re

from flask import session, url_for

from slick import app
from slick.utils.core import get_client
from SoftLayer import (CCIManager, Client, HardwareManager, NetworkManager,
                       SshKeyManager, SoftLayerAPIError)


def authenticate_with_password(username, password, question_id=None,
                               answer=None):
    client = Client()
    try:
        (user_id, user_hash) = client.authenticate_with_password(username,
                                                                 password,
                                                                 question_id,
                                                                 answer)
        session['sl_user_id'] = user_id
        session['sl_user_hash'] = user_hash
    except SoftLayerAPIError as e:
        c = 'SoftLayer_Exception_User_Customer_InvalidSecurityQuestionAnswer'
        if e.faultCode == c:
            return 'security_question'

        return False

    return True


def get_questions():
    return get_client()['User_Security_Question'].getAllObjects()


def global_search(search):
    client = get_client()
    match_string = '<span class="text-primary">%s</span>' % search

    term = re.compile(search, re.IGNORECASE)

    results = []

    if 'vm' in app.config['installed_blueprints']:
        cci = CCIManager(client)
#        if hostname_regex.match(term):
        for vm in cci.list_instances():
            if term.match(vm['hostname']) or \
               term.match(vm.get('primaryIpAddress', '')):
                text = '%s (%s)' % (vm['fullyQualifiedDomainName'],
                                    vm.get('primaryIpAddress', 'No Public IP'))
                text = term.sub(match_string, text)

                results.append({'label': '<strong>VM:</strong> ' + text,
                                'value': url_for('vm_module.view',
                                                 vm_id=vm['id'])})
    if 'servers' in app.config['installed_blueprints']:
        hw = HardwareManager(client)

        for svr in hw.list_hardware():
            if term.match(svr['hostname']) or \
               term.match(svr.get('primaryIpAddress', '')):
                text = '%s (%s)' % (svr['fullyQualifiedDomainName'],
                                    svr.get('primaryIpAddress',
                                            'No Public IP'))
                text = term.sub(match_string, text)

                results.append({'label': '<strong>Server:</strong> ' + text,
                                'value': url_for('server_module.view',
                                                 server_id=svr['id'])})
    if 'sshkeys' in app.config['installed_blueprints']:
        ssh = SshKeyManager(client)

        for key in ssh.list_keys():
            if term.match(key['label']) or term.match(key['fingerprint']):
                text = '%s (%s)' % (key['label'], key['fingerprint'])
                text = term.sub(match_string, text)

                results.append({'label': '<strong>SSH Key:</strong> ' + text,
                                'value': url_for('ssh_module.view',
                                                 key_id=key['id'])})

    return results
