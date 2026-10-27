"""Smoke test de boot + endpoints.

  python tests/smoke.py <1|2|3> record     # grava baseline (aplicação ORIGINAL)
  python tests/smoke.py <1|2|3> compare    # compara aplicação refatorada com a baseline

Compara status HTTP, estrutura e valores do JSON com a baseline da API original (chaves sensíveis e
campos voláteis são ignorados).
Endpoints marcados como "intentional" (mudança de segurança aceita: SQL injection no login, endpoint
administrativo agora protegido) só passam com um dos status permitidos; 404/405/500 (endpoint removido ou
quebrado) reprova. Campos sensíveis na resposta geram apenas AVISO.
"""
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASELINE_DIR = ROOT / "tests" / "baseline"
SENSITIVE = {"senha", "password", "secret_key"}
CONFIG_KEYS = {"db_path", "debug"}  # configuração interna; ocultá-la em /health é aceito
PY = os.path.join(".venv", "Scripts", "python.exe")


def ep(name, method, path, body=None, save=None, intentional=None):
    return {"name": name, "method": method, "path": path, "body": body, "save": save, "intentional": intentional}


PROJECTS = {
    "1": {
        "dir": "code-smells-project", "port": 5000, "cmd": [PY, "app.py"], "clean": ["loja.db"], "pre": [],
        "endpoints": [
            ep("index", "GET", "/"),
            ep("health", "GET", "/health"),
            ep("listar produtos", "GET", "/produtos"),
            ep("produto 1", "GET", "/produtos/1"),
            ep("produto inexistente", "GET", "/produtos/999"),
            ep("busca por termo", "GET", "/produtos/busca?q=Mouse"),
            ep("busca com filtros", "GET", "/produtos/busca?categoria=informatica&preco_min=100&preco_max=3000"),
            ep("criar produto", "POST", "/produtos", {"nome": "Produto Teste", "descricao": "d", "preco": 10.5, "estoque": 5, "categoria": "geral"}, save="produto_id"),
            ep("criar produto invalido", "POST", "/produtos", {"nome": "x", "preco": -1, "estoque": 1}),
            ep("atualizar produto", "PUT", "/produtos/1", {"nome": "Notebook Gamer", "descricao": "d", "preco": 5999.99, "estoque": 9, "categoria": "informatica"}),
            ep("deletar produto", "DELETE", "/produtos/{produto_id}"),
            ep("listar usuarios", "GET", "/usuarios"),
            ep("usuario 1", "GET", "/usuarios/1"),
            ep("usuario inexistente", "GET", "/usuarios/999"),
            ep("criar usuario", "POST", "/usuarios", {"nome": "Teste", "email": "teste@email.com", "senha": "abc123"}, save="usuario_id"),
            ep("criar usuario invalido", "POST", "/usuarios", {"nome": "Teste"}),
            ep("login ok", "POST", "/login", {"email": "admin@loja.com", "senha": "admin123"}),
            ep("login invalido", "POST", "/login", {"email": "admin@loja.com", "senha": "errada"}),
            ep("login com SQL injection", "POST", "/login", {"email": "' OR '1'='1' --", "senha": "x"}, intentional={401, 400}),
            ep("criar pedido", "POST", "/pedidos", {"usuario_id": 2, "itens": [{"produto_id": 1, "quantidade": 1}, {"produto_id": 2, "quantidade": 2}]}),
            ep("criar pedido sem itens", "POST", "/pedidos", {"usuario_id": 2, "itens": []}),
            ep("listar pedidos", "GET", "/pedidos"),
            ep("pedidos do usuario", "GET", "/pedidos/usuario/2"),
            ep("atualizar status", "PUT", "/pedidos/1/status", {"status": "aprovado"}),
            ep("status invalido", "PUT", "/pedidos/1/status", {"status": "xyz"}),
            ep("relatorio de vendas", "GET", "/relatorios/vendas"),
            ep("admin query (SQL arbitrario)", "POST", "/admin/query", {"sql": "SELECT 1"}, intentional={200, 401, 403}),
            ep("admin reset-db", "POST", "/admin/reset-db", intentional={200, 401, 403}),
        ],
    },
    "2": {
        "dir": "ecommerce-api-legacy", "port": 3000, "cmd": ["node", "src/app.js"], "clean": [], "pre": [], "exact": False,
        "endpoints": [
            ep("checkout sucesso", "POST", "/api/checkout", {"usr": "Guilherme", "eml": "gui@fullcycle.com.br", "pwd": "senhaforte", "c_id": 2, "card": "4111222233334444"}),
            ep("checkout usuario existente", "POST", "/api/checkout", {"usr": "Leonan", "eml": "leonan@fullcycle.com.br", "pwd": "123", "c_id": 1, "card": "4999888877776666"}),
            ep("checkout recusado", "POST", "/api/checkout", {"usr": "Joao", "eml": "joao@teste.com", "pwd": "123", "c_id": 1, "card": "5111222233334444"}),
            ep("checkout bad request", "POST", "/api/checkout", {"usr": "x"}),
            ep("checkout curso inexistente", "POST", "/api/checkout", {"usr": "x", "eml": "x@x.com", "pwd": "1", "c_id": 999, "card": "4111"}),
            ep("relatorio financeiro", "GET", "/api/admin/financial-report"),
            ep("deletar usuario", "DELETE", "/api/users/1"),
        ],
    },
    "3": {
        "dir": "task-manager-api", "port": 5000, "cmd": [PY, "app.py"], "clean": [os.path.join("instance", "tasks.db"), "tasks.db"],
        "pre": [[PY, "seed.py"]],
        "endpoints": [
            ep("index", "GET", "/"),
            ep("health", "GET", "/health"),
            ep("listar tasks", "GET", "/tasks"),
            ep("task 1", "GET", "/tasks/1"),
            ep("task inexistente", "GET", "/tasks/9999"),
            ep("criar task", "POST", "/tasks", {"title": "Task de teste", "description": "d", "priority": 2, "user_id": 1, "category_id": 1, "due_date": "2030-01-01", "tags": ["a", "b"]}, save="task_id"),
            ep("criar task invalida", "POST", "/tasks", {"title": "ab"}),
            ep("atualizar task", "PUT", "/tasks/{task_id}", {"status": "in_progress", "priority": 1}),
            ep("buscar tasks", "GET", "/tasks/search?q=a&status=pending"),
            ep("stats", "GET", "/tasks/stats"),
            ep("deletar task", "DELETE", "/tasks/{task_id}"),
            ep("listar users", "GET", "/users"),
            ep("user 1", "GET", "/users/1"),
            ep("criar user", "POST", "/users", {"name": "Teste", "email": "teste@email.com", "password": "abcd", "role": "user"}, save="user_id"),
            ep("criar user invalido", "POST", "/users", {"name": "x"}),
            ep("atualizar user", "PUT", "/users/{user_id}", {"name": "Teste 2"}),
            ep("tasks do user", "GET", "/users/1/tasks"),
            ep("login ok", "POST", "/login", {"email": "joao@email.com", "password": "1234"}),
            ep("login invalido", "POST", "/login", {"email": "joao@email.com", "password": "zzzz"}),
            ep("relatorio resumo", "GET", "/reports/summary"),
            ep("relatorio do user", "GET", "/reports/user/1"),
            ep("listar categorias", "GET", "/categories"),
            ep("criar categoria", "POST", "/categories", {"name": "Cat Teste", "description": "d", "color": "#112233"}, save="cat_id"),
            ep("atualizar categoria", "PUT", "/categories/{cat_id}", {"name": "Cat Teste 2"}),
            ep("deletar categoria", "DELETE", "/categories/{cat_id}"),
            ep("deletar user", "DELETE", "/users/{user_id}"),
        ],
    },
}


def shape(v):
    if isinstance(v, dict):
        return {k: shape(x) for k, x in sorted(v.items()) if k not in SENSITIVE}
    if isinstance(v, list):
        shapes = {json.dumps(shape(x), sort_keys=True): shape(x) for x in v}
        return [shapes[k] for k in sorted(shapes)]
    if v is None:
        return "null"
    return type(v).__name__ if not isinstance(v, bool) else "bool"


VOLATILE = {"created_at", "updated_at", "criado_em", "generated_at", "timestamp", "ambiente", "debug", "due_date", "token"}


def scrub(v):
    """Remove campos sensíveis/voláteis (datas, ambiente) para comparar valores."""
    if isinstance(v, dict):
        return {k: scrub(x) for k, x in v.items() if k not in SENSITIVE and k not in VOLATILE}
    if isinstance(v, list):
        return [scrub(x) for x in v]
    return v


def drop_keys(v, keys):
    if isinstance(v, dict):
        return {k: drop_keys(x, keys) for k, x in v.items() if k not in keys}
    if isinstance(v, list):
        return [drop_keys(x, keys) for x in v]
    return v


def has_sensitive(v):
    if isinstance(v, dict):
        return any(k in SENSITIVE or has_sensitive(x) for k, x in v.items())
    if isinstance(v, list):
        return any(has_sensitive(x) for x in v)
    return False


def request(port, method, path, body):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=data, method=method,
                                 headers={"Content-Type": "application/json"} if data is not None else {})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")


def parse(text):
    try:
        return json.loads(text)
    except ValueError:
        return None


def wait_port(port, proc, timeout=40):
    end = time.time() + timeout
    while time.time() < end:
        if proc.poll() is not None:
            return False
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=2)
            return True
        except urllib.error.HTTPError:
            return True
        except Exception:
            time.sleep(0.5)
    return False


def stop(proc):
    subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"], capture_output=True)


def run(pid, mode):
    cfg = PROJECTS[pid]
    cwd = Path(os.environ.get("SMOKE_PROJECT_ROOT", ROOT)) / cfg["dir"]
    env = dict(os.environ, PYTHONUNBUFFERED="1", PYTHONIOENCODING="utf-8")
    absolutize = lambda cmd: [str(cwd / cmd[0])] + cmd[1:] if cmd[0] == PY else cmd
    cfg = dict(cfg, cmd=absolutize(cfg["cmd"]), pre=[absolutize(c) for c in cfg["pre"]])
    for f in cfg["clean"]:
        (cwd / f).unlink(missing_ok=True)
    for cmd in cfg["pre"]:
        r = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, encoding="utf-8")
        if r.returncode != 0:
            print("FAIL pré-comando", cmd, r.stderr[-500:])
            return 1
    log = (ROOT / "tests" / f"app-{pid}.log").open("w", encoding="utf-8")
    proc = subprocess.Popen(cfg["cmd"], cwd=cwd, env=env, stdout=log, stderr=subprocess.STDOUT)
    results, failures, saved = [], [], {}
    try:
        if not wait_port(cfg["port"], proc):
            print("FAIL aplicação não iniciou; veja tests/app-%s.log" % pid)
            return 1
        print("PASS aplicação iniciou")
        baseline = None
        if mode == "compare":
            baseline = {b["name"]: b for b in json.loads((BASELINE_DIR / f"project-{pid}.json").read_text(encoding="utf-8"))}
        for e in cfg["endpoints"]:
            path = e["path"].format(**saved)
            status, text = request(cfg["port"], e["method"], path, e["body"])
            body = parse(text)
            if e["save"] and isinstance(body, dict):
                node = body.get("dados", body) if isinstance(body.get("dados"), dict) else body
                saved[e["save"]] = node.get("id", node.get("enrollment_id"))
            rec = {"name": e["name"], "method": e["method"], "path": e["path"], "status": status,
                   "shape": shape(body) if body is not None else "text",
                   "body": scrub(body) if body is not None and cfg.get("exact", True) else None}
            results.append(rec)
            label = f"{e['method']} {path} -> {status}"
            if mode == "compare":
                base = baseline[e["name"]]
                if e["intentional"]:
                    ok = status in e["intentional"]
                else:
                    ok = (status == base["status"]
                          and drop_keys(rec["shape"], CONFIG_KEYS) == drop_keys(base["shape"], CONFIG_KEYS))
                    if ok and base.get("body") is not None and drop_keys(rec["body"], CONFIG_KEYS) != drop_keys(base["body"], CONFIG_KEYS):
                        ok = False
                        print("   valores diferentes:\n   esperado:", json.dumps(base["body"], ensure_ascii=False)[:400],
                              "\n   obtido  :", json.dumps(rec["body"], ensure_ascii=False)[:400])
                if body is not None and has_sensitive(body):
                    label += " (AVISO: campo sensível exposto)"
                print(("PASS " if ok else "FAIL ") + e["name"] + ": " + label)
                if not ok:
                    failures.append(e["name"])
                    print("   esperado:", base["status"], json.dumps(base["shape"], ensure_ascii=False)[:300])
                    print("   obtido  :", status, json.dumps(rec["shape"], ensure_ascii=False)[:300])
            else:
                print("REC  " + e["name"] + ": " + label)
        time.sleep(0.5)
    finally:
        stop(proc)
        log.close()
    if mode == "record":
        BASELINE_DIR.mkdir(exist_ok=True)
        (BASELINE_DIR / f"project-{pid}.json").write_text(json.dumps(results, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"baseline gravada ({len(results)} endpoints)")
        return 0
    print(f"\nRESULT project-{pid}: {'FAIL' if failures else 'PASS'} ({len(results) - len(failures)}/{len(results)} endpoints)")
    return 1 if failures else 0


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in PROJECTS or sys.argv[2] not in ("record", "compare"):
        print(__doc__)
        sys.exit(2)
    sys.exit(run(sys.argv[1], sys.argv[2]))
