import json

from models.database import get_db

COLUNAS = ("id", "nome", "descricao", "preco", "estoque", "categoria", "ativo", "criado_em")


def _to_dict(row):
    return {coluna: row[coluna] for coluna in COLUNAS}


def listar():
    rows = get_db().execute("SELECT * FROM produtos").fetchall()
    return [_to_dict(row) for row in rows]


def buscar_por_id(produto_id):
    row = get_db().execute("SELECT * FROM produtos WHERE id = ?", (produto_id,)).fetchone()
    return _to_dict(row) if row else None


def buscar_por_ids(ids):
    rows = get_db().execute(
        "SELECT * FROM produtos WHERE id IN (SELECT value FROM json_each(?))",
        (json.dumps(sorted(set(ids))),),
    ).fetchall()
    return {row["id"]: _to_dict(row) for row in rows}


def criar(nome, descricao, preco, estoque, categoria):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
        (nome, descricao, preco, estoque, categoria),
    )
    db.commit()
    return cursor.lastrowid


def atualizar(produto_id, nome, descricao, preco, estoque, categoria):
    db = get_db()
    db.execute(
        "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
        (nome, descricao, preco, estoque, categoria, produto_id),
    )
    db.commit()


def deletar(produto_id):
    db = get_db()
    db.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
    db.commit()


def buscar(termo, categoria=None, preco_min=None, preco_max=None):
    padrao = "%" + termo + "%" if termo else None
    rows = get_db().execute(
        "SELECT * FROM produtos WHERE "
        "(:padrao IS NULL OR nome LIKE :padrao OR descricao LIKE :padrao) "
        "AND (:categoria IS NULL OR categoria = :categoria) "
        "AND (:preco_min IS NULL OR preco >= :preco_min) "
        "AND (:preco_max IS NULL OR preco <= :preco_max)",
        {
            "padrao": padrao,
            "categoria": categoria or None,
            "preco_min": preco_min,
            "preco_max": preco_max,
        },
    ).fetchall()
    return [_to_dict(row) for row in rows]
