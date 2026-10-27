"""Executa toda a bateria de validação e imprime a matriz dos critérios de aceite.

  python tests/run_all.py
"""
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable
ENV = dict(os.environ, PYTHONIOENCODING="utf-8")
EXPECTED_STACK = {"1": ("Python", "Flask"), "2": ("JavaScript", "Express"), "3": ("Python", "Flask")}
results = {}


def run(*args):
    proc = subprocess.run([PY, *map(str, args)], cwd=ROOT, env=ENV, capture_output=True, text=True, encoding="utf-8")
    return proc.returncode == 0, proc.stdout


def mark(ok):
    return "PASS" if ok else "FAIL"


def main():
    results["manual"], _ = run("tests/check_manual_analysis.py")
    results["skill"], _ = run("tests/check_skill.py")
    results["readme"], _ = run("tests/check_readme.py")
    matrix = {}
    for pid in ("1", "2", "3"):
        evidence = (ROOT / "docs" / "evidencias" / f"project-{pid}.txt").read_text(encoding="utf-8")
        lang, fw = EXPECTED_STACK[pid]
        stack_ok = bool(re.search(rf"Language:\s+{lang}", evidence)) and bool(re.search(rf"Framework:\s+{fw}", evidence))
        report_ok, report_out = run("tests/check_report.py", pid)
        report = (ROOT / "reports" / f"audit-project-{pid}.md").read_text(encoding="utf-8")
        counts = re.search(r"CRITICAL: (\d+) \| HIGH: (\d+) \| MEDIUM: (\d+) \| LOW: (\d+)", report)
        crit_high = int(counts.group(1)) + int(counts.group(2))
        total = sum(int(x) for x in counts.groups())
        smoke_ok, _ = run("tests/smoke.py", pid, "compare")
        mvc_ok, _ = run("tests/check_mvc.py", pid)
        extra_ok = True
        if pid in ("1", "3"):
            extra_ok, _ = run("tests/legacy_data.py", pid)
        matrix[pid] = {
            "Fase 1 detecta stack": stack_ok,
            f"Fase 2 >= 5 findings ({total})": report_ok and total >= 5,
            f"Fase 2 >= 1 CRITICAL/HIGH ({crit_high})": crit_high >= 1,
            "Fase 3 aplicação funciona (boot + endpoints + dados legados)": smoke_ok and extra_ok,
            "Estrutura MVC sem anti-patterns críticos": mvc_ok,
        }

    print("== Skill e análise manual ==")
    print(f"  análise manual: {mark(results['manual'])} | skill: {mark(results['skill'])} | README: {mark(results['readme'])}")
    print("\n== Critérios de aceite ==")
    failed = not (results["manual"] and results["skill"] and results["readme"])
    for pid, crit in matrix.items():
        print(f"\nProjeto {pid}")
        for name, ok in crit.items():
            print(f"  [{mark(ok)}] {name}")
            failed |= not ok
    print("\nRESULT:", "FAIL" if failed else "PASS")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
