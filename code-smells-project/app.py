import logging

from flask import Flask
from flask_cors import CORS

from config import settings
from middlewares.error_handler import register_error_handlers
from models.database import close_db, init_db
from views import register_routes


def create_app():
    logging.basicConfig(level=logging.INFO)
    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    CORS(app)

    init_db()
    app.teardown_appcontext(close_db)
    register_error_handlers(app)
    register_routes(app)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
