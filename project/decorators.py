from functools import wraps, update_wrapper
from project import app
from flask import render_template, abort, make_response
from flask_login import current_user, logout_user
from datetime import datetime


@app.errorhandler(403)
def page_not_found(error):
    return render_template('403.html', title='403'), 403


def is_operator(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.operator is False:
            logout_user()
            abort(403)
        return func(*args, **kwargs)

    return decorated_function


def is_admin(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.admin is False:
            logout_user()
            abort(403)
        return func(*args, **kwargs)

    return decorated_function


def no_http_cache(view):
    @wraps(view)
    def no_cache_view(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers.set('Cache-Control', 'no-store, no-cache, must-revalidate, private, max-age=0')
        return response

    return no_cache_view


def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.now()
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    return update_wrapper(no_cache, view)
