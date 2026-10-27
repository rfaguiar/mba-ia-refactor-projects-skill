import logging

from flask import Flask
from flask_cors import CORS

from config import settings
from middlewares.error_handler import register_error_handlers
from models.database import db
from routes.category_routes import category_bp
from routes.health_routes import health_bp
from routes.report_routes import report_bp
from routes.task_routes import task_bp
from routes.user_routes import user_bp


def create_app():
    logging.basicConfig(level=logging.INFO)
    app = Flask(__name__)
    app.config.from_object(settings)

    CORS(app)
    db.init_app(app)

    for blueprint in (health_bp, task_bp, user_bp, category_bp, report_bp):
        app.register_blueprint(blueprint)
    register_error_handlers(app)

    with app.app_context():
        db.create_all()
    return app


if __name__ == '__main__':
    create_app().run(debug=settings.DEBUG, host=settings.HOST, port=settings.PORT)
