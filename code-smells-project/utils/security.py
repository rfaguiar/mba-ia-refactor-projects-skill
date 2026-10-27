import hmac

from werkzeug.security import check_password_hash, generate_password_hash

HASH_PREFIXES = ("pbkdf2:", "scrypt:")


def hash_password(senha):
    return generate_password_hash(senha, method="pbkdf2:sha256")


def is_hashed(armazenada):
    return bool(armazenada) and armazenada.startswith(HASH_PREFIXES)


def verify_password(armazenada, informada):
    if not armazenada:
        return False
    if is_hashed(armazenada):
        return check_password_hash(armazenada, informada)
    # Formato legado: senha em texto puro de bancos criados pela versão original
    return hmac.compare_digest(armazenada.encode(), informada.encode())
