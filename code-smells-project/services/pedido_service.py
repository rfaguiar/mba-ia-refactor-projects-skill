from models import pedido_model, produto_model
from services import notificacao_service
from utils.errors import ApiError


def criar_pedido(usuario_id, itens):
    produtos = produto_model.buscar_por_ids([item["produto_id"] for item in itens])

    total = 0
    linhas = []
    for item in itens:
        produto = produtos.get(item["produto_id"])
        if produto is None:
            raise ApiError("Produto " + str(item["produto_id"]) + " não encontrado", 400, True)
        if produto["estoque"] < item["quantidade"]:
            raise ApiError("Estoque insuficiente para " + produto["nome"], 400, True)
        total = total + produto["preco"] * item["quantidade"]
        linhas.append({
            "produto_id": item["produto_id"],
            "quantidade": item["quantidade"],
            "preco_unitario": produto["preco"],
        })

    pedido_id = pedido_model.criar(usuario_id, total, linhas)
    notificacao_service.pedido_criado(pedido_id, usuario_id)
    return {"pedido_id": pedido_id, "total": total}
