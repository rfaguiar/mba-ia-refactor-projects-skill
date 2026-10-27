"""Valida um relatório de auditoria contra o template e contra o código ORIGINAL (commit baseline).

  python tests/check_report.py <1|2|3>
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASELINE = "6d1ce62"
PROJECTS = {"1": "code-smells-project", "2": "ecommerce-api-legacy", "3": "task-manager-api"}
ORDER = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
errors = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        errors.append(msg)


def git_files(project):
    return subprocess.run(["git", "ls-tree", "-r", "--name-only", BASELINE, project], cwd=ROOT,
                          capture_output=True, text=True, check=True).stdout.split()


def git_lines(path):
    return len(subprocess.run(["git", "show", f"{BASELINE}:{path}"], cwd=ROOT, capture_output=True, text=True,
                              encoding="utf-8", check=True).stdout.splitlines())


def main(pid):
    project = PROJECTS[pid]
    report = (ROOT / "reports" / f"audit-project-{pid}.md").read_text(encoding="utf-8")
    report = re.sub(r"^`{3,}\w*\n", "", report)
    report = re.sub(r"\n`{3,}\s*$", "\n", report)
    check(report.startswith("================================\nARCHITECTURE AUDIT REPORT"), "cabeçalho do template")
    check(f"Project: {project}" in report, "campo Project")
    check(re.search(r"^Stack:   \S", report, re.M) is not None, "campo Stack")
    check(re.search(r"^Files:   \d+ analyzed \| ~\d+ lines of code", report, re.M) is not None, "campo Files")
    check(report.rstrip().endswith("Proceed with refactoring (Phase 3)? [y/n]"), "termina com pedido de confirmação [y/n]")

    findings = re.split(r"^### ", report, flags=re.M)[1:]
    sev_list, counts = [], dict.fromkeys(ORDER, 0)
    files = git_files(project)
    bad_refs = []
    for f in findings:
        m = re.match(r"\[(CRITICAL|HIGH|MEDIUM|LOW)\] (.+)", f)
        if not m:
            check(False, f"título de finding inválido: {f[:40]}")
            continue
        sev_list.append(m.group(1))
        counts[m.group(1)] += 1
        for field in ("File:", "Description:", "Impact:", "Recommendation:"):
            if f"\n{field}" not in "\n" + f:
                bad_refs.append(f"{m.group(2)[:40]} sem {field}")
        file_line = re.search(r"^File: (.+)$", f, re.M)
        if not file_line:
            continue
        # remove observações entre parênteses ao final da linha File:
        text = re.sub(r"\(.*?\)", "", file_line.group(1))
        refs = re.findall(r"([\w./-]+\.(?:py|js)):([\d,\-\s]+)", text)
        if not refs:
            bad_refs.append(f"{m.group(2)[:40]}: sem arquivo:linha")
        for fname, lines in refs:
            match = [p for p in files if p == f"{project}/{fname}" or p.endswith("/" + fname)]
            if not match:
                bad_refs.append(f"arquivo inexistente {fname}")
                continue
            total = git_lines(match[0])
            for n in re.findall(r"\d+", lines):
                if int(n) < 1 or int(n) > total:
                    bad_refs.append(f"{fname}:{n} fora do arquivo ({total} linhas)")
    check(not bad_refs, f"findings com campos e arquivo:linha válidos {bad_refs}")
    check(len(findings) >= 5, f"mínimo de 5 findings ({len(findings)})")
    check(counts["CRITICAL"] + counts["HIGH"] >= 1, "pelo menos 1 CRITICAL ou HIGH")
    check(sev_list == sorted(sev_list, key=ORDER.index), "findings ordenados CRITICAL → LOW")
    summary = re.search(r"CRITICAL: (\d+) \| HIGH: (\d+) \| MEDIUM: (\d+) \| LOW: (\d+)", report)
    check(bool(summary) and [int(x) for x in summary.groups()] == [counts[s] for s in ORDER],
          f"Summary confere com os findings {counts}")
    total = re.search(r"Total: (\d+) findings", report)
    check(bool(total) and int(total.group(1)) == len(findings), "Total confere")
    check(bool(re.search(r"deprecat|Deprecated APIs: none found", report, re.I)), "detecção de APIs deprecated incluída")
    print("\nRESULT:", "FAIL" if errors else "PASS")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
