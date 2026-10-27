# Template do Relatório de Auditoria (Fase 2)

Imprima o relatório **exatamente** neste formato (e salve o mesmo conteúdo em `reports/audit-<projeto>.md`). Não omita campos; não altere os rótulos em inglês.

````text
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome-da-pasta-do-projeto>
Stack:   <Linguagem> + <Framework>
Files:   <N> analyzed | ~<L> lines of code

## Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>

## Findings

### [CRITICAL] <Nome do anti-pattern> (<ID do catálogo, ex.: AP-02>)
File: <arquivo>:<linha-inicial>-<linha-final>[, <arquivo2>:<linhas>]
Description: <o que foi observado, concreto, citando nomes de funções/variáveis>
Impact: <consequência para segurança/manutenção/teste>
Recommendation: <ação objetiva> (playbook <PB-xx>)

### [HIGH] ...
...

### [MEDIUM] ...
...

### [LOW] ...
...

================================
Total: <N> findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
````

## Regras de preenchimento

1. **Ordem:** todos os CRITICAL, depois HIGH, MEDIUM e LOW (dentro da mesma severidade, do mais impactante ao menos).
2. **`File:`** sempre `arquivo:linha` ou `arquivo:inicio-fim`, caminho relativo à raiz do projeto, números **verificados** no arquivo. Para ocorrências repetidas, liste os trechos separados por vírgula (`models.py:28,49,60-62`).
3. **Summary** deve bater exatamente com a quantidade de findings por severidade; **Total** = soma.
4. Cada finding referencia o ID do catálogo (`AP-xx`/`DP-xx`) e o padrão do playbook (`PB-xx`).
5. **APIs deprecated** (`DP-xx`) aparecem como findings normais, com o equivalente moderno na Recommendation. Se a stack não tiver nenhuma, escreva ao final, antes do `Total`, a linha: `Deprecated APIs: none found`.
6. `Files:` = número de arquivos de código-fonte da Fase 1; `~L lines` = soma aproximada das linhas.
7. Nunca inclua segredos reais no texto (cite somente o nome da variável).
8. A última linha do relatório impresso é o prompt de confirmação `[y/n]`; ao salvar o arquivo, inclua-o também.
