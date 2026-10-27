import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

from utils.errors import ApiError

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(ApiError)
    def handle_api_error(erro):
        corpo = {"erro": erro.message}
        if erro.include_success:
            corpo["sucesso"] = False
        return jsonify(corpo), erro.status

    @app.errorhandler(Exception)
    def handle_unexpected(erro):
        if isinstance(erro, HTTPException):
            return erro
        logger.exception("Erro não tratado")
        return jsonify({"erro": "Erro interno do servidor"}), 500
