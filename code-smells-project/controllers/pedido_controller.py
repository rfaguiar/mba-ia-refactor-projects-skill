from models import pedido_model
from services import notificacao_service, pedido_service
from utils.http import json_body
from utils.validators import validar_pedido, validar_status_pedido


def criar_pedido():
    usuario_id, itens = validar_pedido(json_body())
    resultado = pedido_service.criar_pedido(usuario_id, itens)
    return {"dados": resultado, "sucesso": True, "mensagem": "Pedido criado com sucesso"}, 201


def listar_pedidos_usuario(usuario_id):
    return {"dados": pedido_model.listar_por_usuario(usuario_id), "sucesso": True}, 200


def listar_todos_pedidos():
    return {"dados": pedido_model.listar_todos(), "sucesso": True}, 200


def atualizar_status_pedido(pedido_id):
    novo_status = validar_status_pedido(json_body())
    pedido_model.atualizar_status(pedido_id, novo_status)
    notificacao_service.status_alterado(pedido_id, novo_status)
    return {"sucesso": True, "mensagem": "Status atualizado"}, 200
