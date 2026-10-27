import hmac
import logging
from functools import wraps

from flask import request

from config import settings
from utils.errors import ApiError

logger = logging.getLogger(__name__)


def admin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        token = request.headers.get("X-Admin-Token", "")
        if (
            not settings.ENABLE_ADMIN_ENDPOINTS
            or not settings.ADMIN_TOKEN
            or not hmac.compare_digest(token.encode(), settings.ADMIN_TOKEN.encode())
        ):
            logger.warning("Acesso administrativo negado em %s", request.path)
            raise ApiError("Acesso negado", 403)
        return view(*args, **kwargs)

    return wrapper
