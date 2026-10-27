"""Valida a seção "Análise Manual" do README.md: >=5 achados por projeto, distribuição mínima de
severidades e referências arquivo:linha existentes nos projetos originais (baseline git)."""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "solucao.md"
PROJECTS = ["code-smells-project", "ecommerce-api-legacy", "task-manager-api"]
BASELINE = "6d1ce62"


def baseline_files(project):
    out = subprocess.run(["git", "ls-tree", "-r", "--name-only", BASELINE, project],
                         cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
    return out


def baseline_lines(path):
    out = subprocess.run(["git", "show", f"{BASELINE}:{path}"], cwd=ROOT,
                         capture_output=True, text=True, encoding="utf-8", check=True).stdout
    return len(out.splitlines())


def main():
    text = DOC.read_text(encoding="utf-8")
    text = re.search(r"^## A\) Análise Manual(.*?)^## B\)", text, re.S | re.M).group(1)
    sections = re.split(r"^### Projeto \d", text, flags=re.M)[1:]
    failures = []
    for project, section in zip(PROJECTS, sections):
        files = baseline_files(project)
        rows = re.findall(r"^\| \d+ \| (CRITICAL|HIGH|MEDIUM|LOW) \| (.+?) \|", section, flags=re.M)
        sev = {s: 0 for s in ("CRITICAL", "HIGH", "MEDIUM", "LOW")}
        for s, _ in rows:
            sev[s] += 1
        ok = (len(rows) >= 5 and sev["CRITICAL"] + sev["HIGH"] >= 1
              and sev["MEDIUM"] >= 2 and sev["LOW"] >= 2)
        print(f"{project}: {len(rows)} findings {sev} -> {'OK' if ok else 'FAIL'}")
        if not ok:
            failures.append(f"{project}: distribuição insuficiente")
        for _, local in rows:
            for fname, lines in re.findall(r"`([\w./\\*-]+\.(?:py|js)):?([\d,\-]*)`", local):
                matches = [f for f in files if f.endswith("/" + fname.replace("\\", "/")) or f.endswith(fname)]
                if not matches:
                    failures.append(f"{project}: arquivo inexistente {fname}")
                    continue
                total = baseline_lines(matches[0])
                for n in re.findall(r"\d+", lines):
                    if int(n) > total:
                        failures.append(f"{project}: {fname}:{n} > {total} linhas")
    if failures:
        print("\n".join("FAIL " + f for f in failures))
        return 1
    print("PASS check_manual_analysis")
    return 0


if __name__ == "__main__":
    sys.exit(main())
