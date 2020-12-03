from functools import wraps
from project import app
from flask import render_template, abort, make_response
from flask_login import current_user, logout_user


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
