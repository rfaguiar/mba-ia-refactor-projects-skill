"""Compatibilidade com bancos criados pela versão ORIGINAL (dados legados).

  python tests/legacy_data.py <1|3>

Projeto 1: banco SQLite com o schema original e senhas em texto puro -> login deve continuar funcionando.
Projeto 3: banco com hash MD5 (formato original do seed) -> login deve continuar funcionando.
"""
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from smoke import PY, ROOT, stop, wait_port  # noqa: E402

ORIGINAL_SCHEMA_P1 = [
    """CREATE TABLE produtos (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, descricao TEXT, preco REAL,
       estoque INTEGER, categoria TEXT, ativo INTEGER DEFAULT 1, criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""",
    """CREATE TABLE usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, email TEXT, senha TEXT,
       tipo TEXT DEFAULT 'cliente', criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""",
    """CREATE TABLE pedidos (id INTEGER PRIMARY KEY AUTOINCREMENT, usuario_id INTEGER, status TEXT DEFAULT 'pendente',
       total REAL, criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""",
    """CREATE TABLE itens_pedido (id INTEGER PRIMARY KEY AUTOINCREMENT, pedido_id INTEGER, produto_id INTEGER,
       quantidade INTEGER, preco_unitario REAL)""",
]
errors = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        errors.append(msg)


def post(path, body):
    req = urllib.request.Request(f"http://127.0.0.1:5000{path}", method="POST", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code


def run_app(project, prepare):
    cwd = Path(os.environ.get("SMOKE_PROJECT_ROOT", ROOT)) / project
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUNBUFFERED="1")
    prepare(cwd, env)
    proc = subprocess.Popen([str(cwd / PY), "app.py"], cwd=cwd, env=env, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)
    if not wait_port(5000, proc):
        stop(proc)
        raise SystemExit("FAIL aplicação não iniciou com o banco legado")
    return proc


def project1():
    def prepare(cwd, env):
        (cwd / "loja.db").unlink(missing_ok=True)
        conn = sqlite3.connect(cwd / "loja.db")
        for ddl in ORIGINAL_SCHEMA_P1:
            conn.execute(ddl)
        conn.execute("INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES ('P', 'd', 10, 5, 'geral')")
        conn.execute("INSERT INTO usuarios (nome, email, senha, tipo) VALUES ('Admin', 'admin@loja.com', 'admin123', 'admin')")
        conn.commit()
        conn.close()

    proc = run_app("code-smells-project", prepare)
    try:
        check(post("/login", {"email": "admin@loja.com", "senha": "admin123"}) == 200,
              "P1: login com senha em texto puro de banco legado")
        check(post("/login", {"email": "admin@loja.com", "senha": "admin123"}) == 200,
              "P1: login repetido (após possível migração do hash)")
        check(post("/login", {"email": "admin@loja.com", "senha": "errada"}) == 401, "P1: senha errada -> 401")
    finally:
        stop(proc)


def project3():
    def prepare(cwd, env):
        for f in ("instance/tasks.db", "tasks.db"):
            (cwd / f).unlink(missing_ok=True)
        subprocess.run([str(cwd / PY), "seed.py"], cwd=cwd, env=env, capture_output=True, check=True)
        db_file = next(p for p in (cwd / "instance" / "tasks.db", cwd / "tasks.db") if p.exists())
        conn = sqlite3.connect(db_file)
        conn.execute("UPDATE users SET password = ? WHERE email = 'maria@email.com'", (hashlib.md5(b"abcd").hexdigest(),))
        conn.commit()
        conn.close()

    proc = run_app("task-manager-api", prepare)
    try:
        check(post("/login", {"email": "maria@email.com", "password": "abcd"}) == 200,
              "P3: login com hash MD5 de banco legado")
        check(post("/login", {"email": "maria@email.com", "password": "abcd"}) == 200,
              "P3: login repetido (após possível migração do hash)")
        check(post("/login", {"email": "maria@email.com", "password": "errada"}) == 401, "P3: senha errada -> 401")
    finally:
        stop(proc)


if __name__ == "__main__":
    {"1": project1, "3": project3}[sys.argv[1]]()
    print("\nRESULT:", "FAIL" if errors else "PASS")
    sys.exit(1 if errors else 0)
