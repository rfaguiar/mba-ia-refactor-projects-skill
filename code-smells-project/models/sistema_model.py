from config import constants
from models.database import get_db


def totais_pedidos():
    row = get_db().execute(
        "SELECT COUNT(*) AS total_pedidos, "
        "COALESCE(SUM(total), 0) AS faturamento, "
        "COALESCE(SUM(status = ?), 0) AS pendentes, "
        "COALESCE(SUM(status = ?), 0) AS aprovados, "
        "COALESCE(SUM(status = ?), 0) AS cancelados "
        "FROM pedidos",
        (constants.STATUS_PENDENTE, constants.STATUS_APROVADO, constants.STATUS_CANCELADO),
    ).fetchone()
    return dict(row)


def contagens():
    db = get_db()
    db.execute("SELECT 1")
    return {
        "produtos": db.execute("SELECT COUNT(*) FROM produtos").fetchone()[0],
        "usuarios": db.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0],
        "pedidos": db.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0],
    }
