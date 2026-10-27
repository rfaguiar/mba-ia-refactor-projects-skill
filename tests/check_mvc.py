"""Verifica a estrutura MVC e a ausência dos anti-patterns CRITICAL/HIGH detectáveis por busca.

  python tests/check_mvc.py <1|2|3>
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECTS = {
    "1": ("code-smells-project", ".", ".py", "app.py"),
    "2": ("ecommerce-api-legacy", "src", ".js", "src/app.js"),
    "3": ("task-manager-api", ".", ".py", "app.py"),
}
IGNORE = {".venv", "node_modules", "__pycache__", ".github", "instance"}
errors = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        errors.append(msg)


def sources(base, ext):
    return [p for p in base.rglob(f"*{ext}") if not (set(p.relative_to(base).parts) & IGNORE)]


def main(pid):
    name, src, ext, entry = PROJECTS[pid]
    proj = ROOT / name
    base = proj / src
    files = sources(proj, ext)
    rel = lambda p: p.relative_to(proj).as_posix()

    for layer, alts in (("models", ["models"]), ("controllers", ["controllers"]),
                        ("views/routes", ["views", "routes"]), ("config", ["config"]),
                        ("middlewares", ["middlewares", "middleware"])):
        check(any((base / a).is_dir() and sources(base / a, ext) for a in alts), f"camada {layer} existe com código")

    entry_file = proj / entry
    check(entry_file.is_file(), f"entry point {entry}")
    if entry_file.is_file():
        lines = len(entry_file.read_text(encoding="utf-8").splitlines())
        check(lines <= 80, f"entry point enxuto ({lines} linhas)")
        check(not re.search(r"@\w+\.route|\.(get|post|put|delete)\(\s*['\"]/", entry_file.read_text(encoding="utf-8")),
              "entry point sem rotas inline")

    error_handler = [p for p in files if re.search(r"error[_-]?handler", p.name, re.I)]
    check(bool(error_handler), "error handler centralizado")

    secret = re.compile(r"""(?i)(secret[_-]?key|passw(or)?d|pass|api[_-]?key|token|smtp_pass\w*)\s*[:=]\s*['"][^'"\s]{6,}['"]""")
    sql_concat = re.compile(r"""(?i)(select|insert|update|delete)\b[^\n]*['"]\s*\+|f['"][^'"\n]*(select|insert|update|delete)\b[^'"\n]*\{|`[^`\n]*(select|insert|update|delete)\b[^`\n]*\$\{""")
    bare_except = re.compile(r"^\s*except\s*:", re.M)
    for label, rx in (("segredos hardcoded", secret), ("SQL por concatenação/interpolação", sql_concat),
                      ("except genérico (bare)", bare_except)):
        hits = []
        for p in files:
            if label.startswith("segredos") and p.name == "seed.py":
                continue
            for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
                if rx.search(line) and not line.strip().startswith(("#", "//")):
                    hits.append(f"{rel(p)}:{i}")
        check(not hits, f"sem {label} {hits[:5]}")

    sql_outside = []
    for p in files:
        parts = p.relative_to(proj).parts
        if any(x in ("controllers", "routes", "views") for x in parts):
            text = p.read_text(encoding="utf-8")
            if re.search(r"(?i)\b(select\s.+\sfrom|insert\s+into|delete\s+from|update\s+\w+\s+set)\b|\.query\.|db\.session|cursor\(", text):
                sql_outside.append(rel(p))
    check(not sql_outside, f"nenhum acesso a dados em controllers/rotas {sql_outside}")

    print("\nRESULT:", "FAIL" if errors else "PASS")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
