from functools import wraps
from flask import session, redirect, url_for, g

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = session.get("user")
        if not user:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function
