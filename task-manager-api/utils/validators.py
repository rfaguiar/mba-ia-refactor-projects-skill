import re
from datetime import datetime

from flask import request

from config.constants import DATE_FORMAT, EMAIL_PATTERN
from middlewares.error_handler import ValidationError


def parse_json_body():
    payload = request.get_json(silent=True)
    if not payload or not isinstance(payload, dict):
        raise ValidationError('Dados inválidos')
    return payload


def is_valid_email(email):
    return isinstance(email, str) and re.match(EMAIL_PATTERN, email) is not None


def parse_int(value, error_message):
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValidationError(error_message)
    return value


def parse_query_int(value, error_message):
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValidationError(error_message)


def parse_date(value, error_message):
    try:
        return datetime.strptime(value, DATE_FORMAT)
    except (TypeError, ValueError):
        raise ValidationError(error_message)


def normalize_tags(tags):
    if isinstance(tags, list):
        return ','.join(str(tag) for tag in tags)
    if tags is None or isinstance(tags, str):
        return tags
    raise ValidationError('Tags inválidas')
