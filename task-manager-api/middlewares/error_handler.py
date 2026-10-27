import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

from models.base import PersistenceError
from models.database import db

logger = logging.getLogger(__name__)


class AppError(Exception):
    status = 500

    def __init__(self, message):
        super().__init__(message)
        self.message = message


class ValidationError(AppError):
    status = 400


class UnauthorizedError(AppError):
    status = 401


class ForbiddenError(AppError):
    status = 403


class NotFoundError(AppError):
    status = 404


class ConflictError(AppError):
    status = 409


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(error):
        return jsonify({'error': error.message}), error.status

    @app.errorhandler(PersistenceError)
    def handle_persistence_error(error):
        logger.error('Erro de persistência: %s (%s)', error.message, error.__cause__)
        return jsonify({'error': error.message}), 500

    @app.errorhandler(Exception)
    def handle_unexpected(error):
        if isinstance(error, HTTPException):
            return error
        db.session.rollback()
        logger.exception('Erro não tratado')
        return jsonify({'error': 'Erro interno'}), 500
