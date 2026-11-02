"""Valida a estrutura da skill refactor-arch e que as cópias nos 3 projetos são idênticas."""
import filecmp
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECTS = ["code-smells-project", "ecommerce-api-legacy", "task-manager-api"]
SKILL_REL = Path(".github/skills/refactor-arch")
REFS = ["project-analysis.md", "anti-patterns-catalog.md", "report-template.md",
        "mvc-guidelines.md", "refactoring-playbook.md"]
PROJECT_SPECIFIC = ["code-smells-project", "ecommerce-api-legacy", "task-manager-api",
                    "AppManager", "loja.db", "produtos", "task_routes", "notification_service"]

errors = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        errors.append(msg)


def main():
    skill = ROOT / "code-smells-project" / SKILL_REL
    md = skill / "SKILL.md"
    check(md.is_file(), "SKILL.md existe em .github/skills/refactor-arch/")
    text = md.read_text(encoding="utf-8")
    fm = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    check(bool(fm) and re.search(r"^name: refactor-arch$", fm.group(1), re.M) is not None,
          "frontmatter com name: refactor-arch")
    check(bool(fm) and re.search(r"^description: .{40,}", fm.group(1), re.M) is not None,
          "frontmatter com description")

    for ref in REFS:
        p = skill / "references" / ref
        check(p.is_file(), f"referência {ref} existe")
        check(f"references/{ref}" in text, f"SKILL.md referencia {ref}")

    for n in (1, 2, 3):
        check(re.search(rf"^## FASE {n} ", text, re.M) is not None, f"SKILL.md define FASE {n}")
    check("[y/n]" in text and "PARE" in text, "Fase 2 pausa e pede confirmação [y/n]")
    check("Nenhum arquivo do projeto pode ser criado" in text, "regra de não modificar antes da confirmação")
    check("PHASE 1: PROJECT ANALYSIS" in text and "PHASE 3: REFACTORING COMPLETE" in text,
          "formatos de saída das fases 1 e 3")
    leaked = [t for t in PROJECT_SPECIFIC if t in text]
    check(not leaked, f"SKILL.md agnóstico (sem termos de projetos específicos) {leaked}")

    cat = (skill / "references" / "anti-patterns-catalog.md").read_text(encoding="utf-8")
    aps = re.findall(r"^### (AP-\d+)", cat, re.M)
    check(len(aps) >= 8, f"catálogo tem >= 8 anti-patterns ({len(aps)})")
    check("AP-18" in aps and "PB-15" in cat,
          "catálogo detecta escalonamento de privilégio em rotas anônimas")
    for sev in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
        check(re.search(rf"\*\*Severidade:\*\* .*{sev}", cat) is not None, f"catálogo cobre severidade {sev}")
    check(len(re.findall(r"^### DP-\d+", cat, re.M)) >= 2 and "deprecated" in cat.lower(),
          "catálogo inclui detecção de APIs deprecated")
    check(all(re.search(rf"AP-{i:02d}.*?\*\*Sinais:\*\*", cat, re.S) for i in range(1, len(aps) + 1)),
          "todo anti-pattern tem sinais de detecção")

    pb = (skill / "references" / "refactoring-playbook.md").read_text(encoding="utf-8")
    pbs = re.findall(r"^## (PB-\d+)", pb, re.M)
    check(len(pbs) >= 8, f"playbook tem >= 8 padrões ({len(pbs)})")
    check("PB-15" in pbs and "role" in pb and "rota anônima" in pb.lower(),
          "playbook impede papel privilegiado enviado por cadastro anônimo")
    check(pb.count("**Antes**") >= 8 and pb.count("**Depois**") >= 8, "playbook tem blocos Antes/Depois (>= 8)")
    check(set(re.findall(r"PB-\d+", " ".join(re.findall(r"→ playbook \*\*([^*]+)\*\*", cat)))) <= set(pbs),
          "todo PB citado no catálogo existe no playbook")

    tpl = (skill / "references" / "report-template.md").read_text(encoding="utf-8")
    for field in ("ARCHITECTURE AUDIT REPORT", "## Summary", "## Findings", "File:", "Description:",
                  "Impact:", "Recommendation:", "Total:", "[y/n]"):
        check(field in tpl, f"template contém {field}")

    mvc = (skill / "references" / "mvc-guidelines.md").read_text(encoding="utf-8")
    check(all(k in mvc for k in ("Models", "Views", "Controllers")), "guidelines cobrem Models/Views/Controllers")
    pa = (skill / "references" / "project-analysis.md").read_text(encoding="utf-8")
    check(all(k in pa for k in ("Linguagem", "Framework", "Banco de dados", "arquitetura")),
          "project-analysis cobre linguagem/framework/banco/arquitetura")

    for proj in PROJECTS[1:]:
        other = ROOT / proj / SKILL_REL
        if not other.exists():
            print(f"SKIP cópia em {proj} (ainda não criada)")
            continue
        cmp = filecmp.dircmp(skill, other)
        same = not (cmp.diff_files or cmp.left_only or cmp.right_only) and not any(
            sub.diff_files or sub.left_only or sub.right_only for sub in cmp.subdirs.values())
        check(same, f"skill em {proj} idêntica à do code-smells-project")

    print("\nRESULT:", "FAIL" if errors else "PASS")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
