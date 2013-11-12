from functools import wraps
from flask import redirect, session, url_for, current_app
from flask.ext.login import current_user


def login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_app.login_manager._login_disabled:
            return func(*args, **kwargs)
        elif not current_user.is_authenticated():
            return current_app.login_manager.unauthorized()
        elif session.get('use_two_factor') and not session.get('two_factor_passed'):
            return redirect(url_for('site_module.two_factor_login'))
        return func(*args, **kwargs)
    return decorated_view
