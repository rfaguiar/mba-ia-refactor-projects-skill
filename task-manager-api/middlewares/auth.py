import hmac
import logging
from functools import wraps

from flask import request

from config import settings
from config.constants import ADMIN_TOKEN_HEADER
from middlewares.error_handler import ForbiddenError

logger = logging.getLogger(__name__)


def check_admin_token():
    configured = settings.ADMIN_TOKEN
    if not configured:
        if settings.IS_PRODUCTION:
            raise ForbiddenError('Acesso negado')
        logger.warning('ADMIN_TOKEN não configurado: endpoint administrativo liberado (ambiente não-produção)')
        return
    provided = request.headers.get(ADMIN_TOKEN_HEADER, '')
    if not hmac.compare_digest(provided.encode(), configured.encode()):
        raise ForbiddenError('Acesso negado')


def admin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        check_admin_token()
        return view(*args, **kwargs)
    return wrapper
