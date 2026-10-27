from flask import request


def json_body():
    dados = request.get_json(silent=True)
    return dados if isinstance(dados, dict) else None
