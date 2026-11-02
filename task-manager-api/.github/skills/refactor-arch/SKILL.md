---
name: refactor-arch
description: Analisa, audita e refatora qualquer projeto backend (Python/Flask, Node/Express, Java, Go, PHP, etc.) para o padrão MVC. Use quando o usuário pedir "/refactor-arch", auditoria de arquitetura, detecção de anti-patterns/code smells, ou refatoração para MVC. Executa 3 fases sequenciais (Análise → Auditoria com confirmação → Refatoração com validação).
---

# refactor-arch — Refatoração Arquitetural Automatizada para MVC

Você é um arquiteto de software sênior. Execute **as 3 fases abaixo, em ordem**, no projeto que está no diretório de trabalho atual. A skill é **agnóstica de tecnologia**: nunca assuma uma linguagem ou framework; descubra-os na Fase 1 e adapte as regras às convenções da stack detectada.

## Arquivos de referência (leia-os quando indicado)

| Arquivo | Quando usar | Conteúdo |
|---|---|---|
| [project-analysis.md](references/project-analysis.md) | Fase 1 | Heurísticas de detecção de linguagem, framework, banco, domínio e arquitetura |
| [anti-patterns-catalog.md](references/anti-patterns-catalog.md) | Fase 2 | Catálogo de anti-patterns, sinais de detecção, severidades e APIs deprecated |
| [report-template.md](references/report-template.md) | Fase 2 | Formato exato do relatório de auditoria |
| [mvc-guidelines.md](references/mvc-guidelines.md) | Fase 3 | Regras da arquitetura MVC alvo e estrutura por stack |
| [refactoring-playbook.md](references/refactoring-playbook.md) | Fase 3 | Padrões de transformação (antes/depois) por anti-pattern |

## Regras invioláveis

1. **Nenhum arquivo do projeto pode ser criado, alterado ou removido antes da confirmação do usuário ao final da Fase 2.** As Fases 1 e 2 são somente leitura (a única escrita permitida é salvar o relatório de auditoria, ver Fase 2, passo 6).
2. Preserve o **contrato externo**: mesmas rotas, métodos HTTP, formatos de request/response e códigos de status. **Nenhum endpoint existente pode ser removido**: endpoints inseguros devem ser protegidos por configuração, não apagados; **endpoints do fluxo funcional da API devem continuar respondendo como antes na configuração padrão** (só endpoints perigosos por natureza, como execução de SQL arbitrário, podem ficar desabilitados por padrão — ver PB-10) (remoção só se o usuário aprovar explicitamente na confirmação da Fase 2). A refatoração é estrutural; só mude comportamento observável para corrigir um finding de segurança, e liste cada mudança no resumo final.
3. **Escopo mínimo:** corrija o que os findings apontam e estruture em MVC. Não introduza funcionalidades novas (ex.: autenticação/autorização em todas as rotas, novas rotas, novos campos). Melhorias maiores vão como recomendação em Remaining findings no resumo final.
4. **Compatibilidade de dados:** a aplicação refatorada deve funcionar com um banco criado pela versão original (ex.: senhas em texto puro ou hash legado devem continuar permitindo login).
5. Todo finding precisa de **arquivo e linhas exatos**, verificados lendo o arquivo (use busca com número de linha; nunca estime).
6. Nunca invente problemas: cada finding precisa de um sinal de detecção observável no código.
7. Não guarde nem imprima segredos reais encontrados; cite apenas o nome da variável e a linha.
8. **Privilégios em rotas anônimas:** nunca confie em `role`, `is_admin`, `permissions` ou campos equivalentes recebidos no corpo de uma requisição pública. Em cadastros anônimos, ignore esses campos e atribua o papel menos privilegiado no servidor; só aceite atribuição privilegiada após autorização explícita no servidor. Ver AP-18/PB-15.

---

## FASE 1 — Análise do projeto

Leia [project-analysis.md](references/project-analysis.md) e execute:

1. Liste todos os arquivos de código-fonte (ignore `node_modules`, `venv`, `.git`, `__pycache__`, `*.db`, lockfiles, builds). **Conte-os** — o número informado deve ser a contagem real.
2. Detecte **linguagem**, **framework + versão** (manifestos de dependência), **dependências relevantes**, **banco de dados e tabelas/entidades** (DDL, models/ORM, migrations) e **domínio** (o que a aplicação faz, deduzido de rotas e entidades).
3. Mapeie a **arquitetura atual**: quais camadas existem (rotas, controllers, services, models, config, utils), onde estão misturadas responsabilidades, entry point, e liste os **endpoints** existentes (método + caminho) — essa lista será a linha de base para validar a Fase 3.
4. Imprima exatamente neste formato:

```text
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem>
Framework:     <framework + versão>
Dependencies:  <dependências relevantes>
Domain:        <domínio em uma linha>
Architecture:  <descrição da arquitetura atual>
Source files:  <N> files analyzed
DB tables:     <tabelas/entidades>
Endpoints:     <N> (<resumo>)
================================
```

---

## FASE 2 — Auditoria de arquitetura

Leia [anti-patterns-catalog.md](references/anti-patterns-catalog.md) e [report-template.md](references/report-template.md).

1. Leia **todos** os arquivos de código-fonte por inteiro.
2. Cruze o código contra **cada** anti-pattern do catálogo (incluindo a seção de **APIs deprecated**) usando os sinais de detecção. Em projetos já parcialmente organizados (existem `models/`, `routes/`, `services/`...), não presuma que a estrutura está correta: verifique se cada camada cumpre o papel definido em [mvc-guidelines.md](references/mvc-guidelines.md) (ex.: lógica de negócio dentro de rotas, ausência de controllers, serviços não usados).
3. Para cada ocorrência registre: severidade, título do anti-pattern, `arquivo:linha-inicial-linha-final` exatos, descrição concreta do que foi visto, impacto e recomendação (referenciando o padrão do playbook). Agrupe ocorrências repetidas do mesmo anti-pattern em um único finding listando as linhas.
4. Ordene **CRITICAL → HIGH → MEDIUM → LOW**. Deve haver no mínimo 5 findings quando existirem; se achar menos, releia o código e o catálogo antes de concluir.
5. Imprima o relatório seguindo **exatamente** o template.
6. Salve o mesmo relatório no caminho informado pelo usuário; se nenhum for informado, use `reports/audit-<nome-do-projeto>.md` na raiz do repositório (suba diretórios até achar `reports/` ou crie-a ao lado do projeto). Esta é a única escrita permitida antes da confirmação.
7. **PARE e peça confirmação.** Termine a mensagem com:

```text
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

   Aguarde a resposta do usuário. **Não execute nenhuma modificação até receber "y"/"sim".** Se a resposta for "n"/"não", encerre informando que nenhum arquivo do projeto foi alterado.

---

## FASE 3 — Refatoração para MVC

Só execute após a confirmação. Leia [mvc-guidelines.md](references/mvc-guidelines.md) e [refactoring-playbook.md](references/refactoring-playbook.md).

1. **Baseline funcional (antes de mexer):** instale dependências se necessário, suba a aplicação, chame cada endpoint mapeado na Fase 1 e guarde status + estrutura das respostas. Se a aplicação não subir no estado original, registre isso e use a leitura do código como baseline.
2. **Planeje** a estrutura alvo conforme a stack e o nível de organização atual: monolito → criar todas as camadas; projeto parcialmente organizado → manter o que já está adequado, mover/criar apenas o que falta (ex.: introduzir controllers, extrair config, centralizar erros).
3. **Aplique os padrões do playbook** nesta ordem (do maior risco ao menor): configuração/segredos → acesso a dados seguro (queries parametrizadas) → models → controllers (regra de negócio) → views/rotas → error handler centralizado → entry point (composition root) → APIs deprecated, magic numbers e nomes.
4. Estrutura mínima resultante: `config/`, `models/`, `views/` (ou `routes/`), `controllers/`, `middlewares/` (error handler), entry point enxuto que apenas monta a aplicação. Siga as convenções de nomes da stack detectada.
5. Remova o código antigo substituído (arquivos monolíticos, funções duplicadas). Não deixe código morto.
6. **Valide** (obrigatório):
   - Instale dependências e **inicie a aplicação** sem erros;
   - Reexecute **todos** os endpoints da baseline e compare status/estrutura; cada endpoint original deve continuar respondendo (diferenças intencionais, como remoção de campos sensíveis ou endpoint agora protegido, devem ser listadas);
   - Teste a compatibilidade de dados (ex.: login com usuário criado pela versão original do banco);
   - Verifique via busca que os findings CRITICAL corrigidos não existem mais (ex.: nenhum segredo literal, nenhuma query concatenada, nenhum `except` genérico);
   - Se algo falhar, corrija e valide de novo — não declare sucesso sem evidência.
7. Pare o processo da aplicação que você iniciou.
8. Imprima o resumo final neste formato:

```text
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<árvore de diretórios resultante>

## Changes Applied
<lista curta: anti-pattern → padrão aplicado>

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly (<N>/<N>)
  ✓ CRITICAL findings fixed: <n>/<total> (verificado por busca)
  <✗ itens que falharam, se houver>

## Intentional behavior changes
<lista, ou 'none'>

## Remaining findings
<findings não corrigidos por estarem fora do escopo mínimo, ou 'none'>
================================
```
