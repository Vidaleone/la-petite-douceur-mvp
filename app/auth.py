from functools import wraps
from flask import session, redirect, url_for, flash, g
from .db import get_db

def current_user():
    uid = session.get("user_id")
    if not uid: return None
    if not hasattr(g, "_current_user"):
        g._current_user = get_db().execute("SELECT id,name,email,role FROM users WHERE id=?", (uid,)).fetchone()
    return g._current_user

def login_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if not current_user():
            flash("Entre na sua conta para continuar.", "warning")
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapped

def roles_required(*roles):
    def deco(fn):
        @wraps(fn)
        @login_required
        def wrapped(*args, **kwargs):
            user = current_user()
            if user["role"] not in roles:
                flash("Você não tem permissão para acessar esta área.", "danger")
                return redirect(url_for("home"))
            return fn(*args, **kwargs)
        return wrapped
    return deco
