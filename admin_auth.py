import os
from functools import wraps
from flask import request, Response

def check_auth(username, password):
    """Check if the username and password match the environment variables"""
    return username == os.getenv('ADMIN_USERNAME') and password == os.getenv('ADMIN_PASSWORD')

def authenticate():
    """Send a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Admin Access"'}
    )

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated
