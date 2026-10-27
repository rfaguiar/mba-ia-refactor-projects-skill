from models.database import get_db

COLUNAS_PUBLICAS = ("id", "nome", "email", "tipo", "criado_em")


def _to_dict(row):
    return {coluna: row[coluna] for coluna in COLUNAS_PUBLICAS}


def listar():
    rows = get_db().execute("SELECT * FROM usuarios").fetchall()
    return [_to_dict(row) for row in rows]


def buscar_por_id(usuario_id):
    row = get_db().execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()
    return _to_dict(row) if row else None


def buscar_credenciais_por_email(email):
    rows = get_db().execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchall()
    return [(row["id"], row["senha"], _to_dict(row)) for row in rows]


def criar(nome, email, senha_hash, tipo):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, senha_hash, tipo),
    )
    db.commit()
    return cursor.lastrowid


def atualizar_senha(usuario_id, senha_hash):
    db = get_db()
    db.execute("UPDATE usuarios SET senha = ? WHERE id = ?", (senha_hash, usuario_id))
    db.commit()
