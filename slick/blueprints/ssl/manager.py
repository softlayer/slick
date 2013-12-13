from SoftLayer import SSLManager, SoftLayerAPIError

from slick.utils.core import get_client
from slick.utils.date import parse_date


def add_cert(certificate):
    """ Creates a new certificate.

    :param dict certificate: A dictionary representing the parts of the
    certificate. See SLDN for more information.

    """
    try:
        get_ssl_manager().add_certificate(certificate)
        success = True
        message = 'SSL certificate added.'
    except SoftLayerAPIError as exception:
        success = False
        message = str(exception.message)

    return (success, message)


def delete_cert(cert_id):
    try:
        get_ssl_manager().remove_certificate(cert_id)
        success = True
        message = 'SSL certificate deleted.'
    except SoftLayerAPIError as exception:
        success = False
        message = str(exception.message)

    return (success, message)


def get_cert(cert_id):
    try:
        cert = get_ssl_manager().get_certificate(cert_id)
        cert['validityBegin'] = parse_date(cert['validityBegin'])
        cert['validityEnd'] = parse_date(cert['validityEnd'])
    except SoftLayerAPIError:
        cert = None

    return cert


def get_ssl_manager():
    return SSLManager(get_client())


def list_certs():
    return get_ssl_manager().list_certs()
