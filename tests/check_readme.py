"""Valida o README.md (checklist marcado, enunciado preservado) e docs/solucao.md (seções A–D, links e contagens)."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
errors = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        errors.append(msg)


def main():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    check(readme.count("- [x]") == 19 and "- [ ]" not in readme, "README: checklist de validação totalmente marcado (19/19)")
    check("# Criação de Skills" in readme and "## Critérios de Aceite" in readme, "README: enunciado original preservado")

    solucao_path = ROOT / "docs" / "solucao.md"
    readme = solucao_path.read_text(encoding="utf-8")
    for title in ("## A) Análise Manual", "## B) Construção da Skill", "## C) Resultados", "## D) Como Executar"):
        check(title in readme, f"seção '{title}'")

    broken = []
    for target in re.findall(r"\]\((?!https?:)([^)#]+)\)", readme):
        if not (solucao_path.parent / target).exists():
            broken.append(target)
    check(not broken, f"links locais existentes {broken}")

    table = re.findall(r"^\| \d — [\w-]+ \| [^|]+ \| (\d+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \| \[reports/audit-project-(\d)\.md\]",
                       readme, re.M)
    check(len(table) == 3, "tabela de findings com 3 projetos")
    for c, h, m, l, total, pid in table:
        report = (ROOT / "reports" / f"audit-project-{pid}.md").read_text(encoding="utf-8")
        s = re.search(r"CRITICAL: (\d+) \| HIGH: (\d+) \| MEDIUM: (\d+) \| LOW: (\d+)", report)
        check([int(x) for x in (c, h, m, l)] == [int(x) for x in s.groups()] and int(total) == sum(map(int, s.groups())),
              f"contagens do README batem com reports/audit-project-{pid}.md")

    for n in (1, 2, 3):
        check((ROOT / "docs" / "evidencias" / f"project-{n}-smoke.txt").is_file(), f"evidência smoke do projeto {n}")
    print("\nRESULT:", "FAIL" if errors else "PASS")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
