from models.database import get_db

def resetar_tabelas():
    db = get_db()
    db.execute("DELETE FROM itens_pedido")
    db.execute("DELETE FROM pedidos")
    db.execute("DELETE FROM produtos")
    db.execute("DELETE FROM usuarios")
    db.commit()


def executar_sql(query):
    """Executa SQL arbitrário (endpoint administrativo protegido por token)."""
    db = get_db()
    cursor = db.execute(query)
    if query.strip().upper().startswith("SELECT"):
        return [dict(row) for row in cursor.fetchall()]
    db.commit()
    return None
