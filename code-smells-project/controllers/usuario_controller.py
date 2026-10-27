from config import constants
from models import usuario_model
from utils.errors import ApiError
from utils.http import json_body
from utils.security import hash_password, is_hashed, verify_password
from utils.validators import validar_login, validar_usuario


def listar_usuarios():
    return {"dados": usuario_model.listar(), "sucesso": True}, 200


def buscar_usuario(usuario_id):
    usuario = usuario_model.buscar_por_id(usuario_id)
    if not usuario:
        raise ApiError("Usuário não encontrado", 404)
    return {"dados": usuario, "sucesso": True}, 200


def criar_usuario():
    nome, email, senha = validar_usuario(json_body())
    usuario_id = usuario_model.criar(nome, email, hash_password(senha), constants.TIPO_USUARIO_PADRAO)
    return {"dados": {"id": usuario_id}, "sucesso": True}, 201


def login():
    email, senha = validar_login(json_body())

    for usuario_id, senha_armazenada, usuario in usuario_model.buscar_credenciais_por_email(email):
        if verify_password(senha_armazenada, senha):
            if not is_hashed(senha_armazenada):
                usuario_model.atualizar_senha(usuario_id, hash_password(senha))
            publico = {chave: usuario[chave] for chave in ("id", "nome", "email", "tipo")}
            return {"dados": publico, "sucesso": True, "mensagem": "Login OK"}, 200

    raise ApiError("Email ou senha inválidos", 401, True)
