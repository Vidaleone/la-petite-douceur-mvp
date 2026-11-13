import os
from flask import Flask
from .db import init_db
from .routes import register_routes


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY",
        "chave-local-apenas-para-desenvolvimento"
    )

    default_database = os.path.join(
        app.instance_path,
        "cafeteria.sqlite3"
    )

    app.config["DATABASE"] = os.environ.get(
        "DATABASE_PATH",
        default_database
    )

    app.config["CURRENCY"] = "BRL"

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(os.path.dirname(app.config["DATABASE"]), exist_ok=True)

    init_db(app)

    app.jinja_env.filters["from_json"] = (
        lambda value: __import__("json").loads(value or "[]")
    )

    register_routes(app)

    return app