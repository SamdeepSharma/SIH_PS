from flask import request, abort, session
from functools import wraps

def validate_request(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            abort(400, description="Request is not JSON")
        return func(*args, **kwargs)
    return decorated_function

def csrf_protect(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'DELETE']:
            token = request.headers.get('X-CSRF-TOKEN')
            if not token or token != session.get('_csrf_token'):
                abort(400, description="CSRF token missing or invalid")
        return func(*args, **kwargs)
    return decorated_function