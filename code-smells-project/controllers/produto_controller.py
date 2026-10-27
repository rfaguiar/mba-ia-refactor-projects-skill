from models import produto_model
from utils.errors import ApiError
from utils.http import json_body
from utils.validators import parse_preco, validar_produto
from flask import request


def listar_produtos():
    return {"dados": produto_model.listar(), "sucesso": True}, 200


def buscar_produto(produto_id):
    produto = produto_model.buscar_por_id(produto_id)
    if not produto:
        raise ApiError("Produto não encontrado", 404, True)
    return {"dados": produto, "sucesso": True}, 200


def criar_produto():
    dados = validar_produto(json_body())
    produto_id = produto_model.criar(**dados)
    return {"dados": {"id": produto_id}, "sucesso": True, "mensagem": "Produto criado"}, 201


def atualizar_produto(produto_id):
    dados = json_body()
    if not produto_model.buscar_por_id(produto_id):
        raise ApiError("Produto não encontrado", 404)
    produto_model.atualizar(produto_id, **validar_produto(dados))
    return {"sucesso": True, "mensagem": "Produto atualizado"}, 200


def deletar_produto(produto_id):
    if not produto_model.buscar_por_id(produto_id):
        raise ApiError("Produto não encontrado", 404)
    produto_model.deletar(produto_id)
    return {"sucesso": True, "mensagem": "Produto deletado"}, 200


def buscar_produtos():
    termo = request.args.get("q", "")
    categoria = request.args.get("categoria")
    preco_min = parse_preco(request.args.get("preco_min"), "preco_min")
    preco_max = parse_preco(request.args.get("preco_max"), "preco_max")
    resultados = produto_model.buscar(termo, categoria, preco_min, preco_max)
    return {"dados": resultados, "total": len(resultados), "sucesso": True}, 200
