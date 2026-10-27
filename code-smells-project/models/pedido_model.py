import sqlite3

from config import constants
from models.database import get_db


def criar(usuario_id, total, linhas):
    """Grava pedido, itens e baixa de estoque em uma única transação."""
    db = get_db()
    try:
        cursor = db.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, ?, ?)",
            (usuario_id, constants.STATUS_PENDENTE, total),
        )
        pedido_id = cursor.lastrowid
        for linha in linhas:
            db.execute(
                "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
                (pedido_id, linha["produto_id"], linha["quantidade"], linha["preco_unitario"]),
            )
            db.execute(
                "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
                (linha["quantidade"], linha["produto_id"]),
            )
        db.commit()
    except sqlite3.Error:
        db.rollback()
        raise
    return pedido_id


def _listar(usuario_id=None):
    db = get_db()
    pedidos = db.execute(
        "SELECT * FROM pedidos WHERE (:usuario_id IS NULL OR usuario_id = :usuario_id) ORDER BY id",
        {"usuario_id": usuario_id},
    ).fetchall()
    itens = db.execute(
        "SELECT ip.pedido_id, ip.produto_id, ip.quantidade, ip.preco_unitario, pr.nome AS produto_nome "
        "FROM itens_pedido ip "
        "JOIN pedidos pe ON pe.id = ip.pedido_id "
        "LEFT JOIN produtos pr ON pr.id = ip.produto_id "
        "WHERE (:usuario_id IS NULL OR pe.usuario_id = :usuario_id) ORDER BY ip.id",
        {"usuario_id": usuario_id},
    ).fetchall()

    itens_por_pedido = {}
    for item in itens:
        itens_por_pedido.setdefault(item["pedido_id"], []).append({
            "produto_id": item["produto_id"],
            "produto_nome": item["produto_nome"] if item["produto_nome"] is not None else "Desconhecido",
            "quantidade": item["quantidade"],
            "preco_unitario": item["preco_unitario"],
        })

    return [
        {
            "id": pedido["id"],
            "usuario_id": pedido["usuario_id"],
            "status": pedido["status"],
            "total": pedido["total"],
            "criado_em": pedido["criado_em"],
            "itens": itens_por_pedido.get(pedido["id"], []),
        }
        for pedido in pedidos
    ]


def listar_todos():
    return _listar()


def listar_por_usuario(usuario_id):
    return _listar(usuario_id)


def atualizar_status(pedido_id, novo_status):
    db = get_db()
    db.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))
    db.commit()
