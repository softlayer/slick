from flask import g, session

from SoftLayer import TokenAuthentication, Client


def get_client():
    if not hasattr(g, 'client'):
        if session.get('sl_user_id'):
            auth = TokenAuthentication(session['sl_user_id'],
                                       session['sl_user_hash'])
            if auth:
                g.client = Client(auth=auth)
    return g.client
