# Criação de Skills — Refatoração Arquitetural Automatizada

Ao longo do curso você aprendeu o que são Skills e como elas permitem que um agente de IA atue como um especialista em tarefas específicas. Agora imagine o seguinte cenário: você herdou 3 projetos legados com problemas de arquitetura, segurança e qualidade de código. Revisar e corrigir tudo manualmente levaria dias.

Neste desafio, você vai criar uma Skill que automatiza esse processo — analisando, auditando e refatorando qualquer projeto para o padrão MVC, independente da tecnologia.

## Objetivo

Você deve entregar uma Skill capaz de:

- Analisar uma codebase detectando linguagem, framework e arquitetura atual
- Identificar anti-patterns e code smells, classificando por severidade com arquivo e linha exatos
- Gerar um relatório de auditoria estruturado com todos os achados
- Refatorar o projeto para o padrão MVC (Model-View-Controller), eliminando os problemas encontrados
- Validar o resultado garantindo que a aplicação continua funcionando após as mudanças

A skill deve ser agnóstica de tecnologia, funcionando com diferentes linguagens e frameworks.

## Contexto

### Definição de Severidades

Para padronizar a sua auditoria e os relatórios gerados pela IA, utilize a seguinte escala de classificação baseada em problemas de MVC e SOLID:

- **CRITICAL:** Falhas graves de arquitetura ou segurança que impedem o funcionamento correto, expõem dados sensíveis (ex: credenciais hardcoded, SQL Injection) ou violam completamente a separação de responsabilidades (ex: "God Class" contendo banco de dados, lógicas complexas e roteamento no mesmo arquivo).
- **HIGH:** Fortes violações do padrão MVC ou princípios SOLID que dificultam muito a manutenção e testes (ex: lógicas de negócio pesadas presas dentro de Controllers, forte acoplamento sem Injeção de Dependência, ou uso de estado global mutável em toda a aplicação).
- **MEDIUM:** Problemas de padronização, duplicação de código ou gargalos de performance moderada (ex: Queries N+1 no banco de dados, uso inadequado de middlewares, validações ausentes nas rotas).
- **LOW:** Melhorias de legibilidade, nomenclatura de variáveis ruins, ou "magic numbers" soltos pelo código.

### Exemplo de Uso no CLI

```bash
# Executar a skill no projeto com problemas
cd code-smells-project
claude "/refactor-arch"
```

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:      Flask 3.1.1
Dependencies:  flask-cors
Domain:        E-commerce API (produtos, pedidos, usuários)
Architecture:  Monolítica — tudo em 4 arquivos, sem separação de camadas
Source files:  4 files analyzed
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================
```

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~800 lines of code

## Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 2 | LOW: 3

## Findings

### [CRITICAL] God Class / God Method
File: models.py:1-350
Description: Arquivo único contém toda lógica de negócio, queries SQL, validação e formatação para 4 domínios diferentes.
Impact: Impossível testar em isolamento, qualquer mudança afeta tudo.
Recommendation: Separar em models e controllers por domínio.

### [CRITICAL] Hardcoded Credentials
File: app.py:8
Description: SECRET_KEY hardcoded como 'minha-chave-super-secreta-123'
...

================================
Total: 14 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
```

```
[... refatoração executada ...]

================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
src/
├── config/settings.py
├── models/
│   ├── produto_model.py
│   └── usuario_model.py
├── views/
│   └── routes.py
├── controllers/
│   ├── produto_controller.py
│   └── pedido_controller.py
├── middlewares/error_handler.py
└── app.py (composition root)

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

## Tecnologias obrigatórias

- **Ferramenta:** uma das três opções abaixo (não são aceitas outras ferramentas):
  - Claude Code
  - Gemini CLI
  - OpenAI Codex
- **Recurso:** Custom Skills (ou o equivalente na ferramenta escolhida)
- **Formato dos arquivos de referência:** Markdown
- **Projetos-alvo:** Python/Flask (2 projetos) e Node.js/Express (1 projeto) (fornecidos no repositório base)

> **Nota sobre a ferramenta:** Os exemplos deste documento usam o Claude Code (`.claude/skills/`) como referência, pois é a ferramenta utilizada no curso. Se você optar por Gemini CLI ou Codex, adapte o nome da pasta e o comando de invocação conforme a convenção dela — o conceito de skill e a estrutura interna (SKILL.md + arquivos de referência) permanecem os mesmos.

## Requisitos

### 1. Análise Manual dos Projetos

Antes de criar a skill, você deve entender os problemas que ela vai resolver.

**Tarefas:**

- Analisar o projeto `code-smells-project/` (Python/Flask — API de E-commerce)
- Analisar o projeto `ecommerce-api-legacy/` (Node.js/Express — LMS API com fluxo de checkout)
- Analisar o projeto `task-manager-api/` (Python/Flask — API de Task Manager)

Para cada projeto, identificar e documentar no mínimo 5 problemas, incluindo pelo menos:

- 1 de severidade CRITICAL ou HIGH
- 2 de severidade MEDIUM
- 2 de severidade LOW

Documentar os achados na seção "Análise Manual" do seu `README.md`

> **Dica:** Não precisa encontrar todos os problemas — foque nos que têm maior impacto arquitetural. Use os projetos como insumo para entender quais padrões sua skill precisa detectar.

> **Por que 3 projetos?** Dois são Python/Flask (com níveis de organização diferentes) e um é Node.js/Express. Sua skill precisa funcionar nos 3 para provar que é verdadeiramente agnóstica de tecnologia — lidando tanto com código completamente desestruturado quanto com projetos que já possuem alguma separação de camadas.

### 2. Criação da Skill

Agora que você conhece os problemas, crie uma skill que os detecte, gere um relatório de auditoria e corrija automaticamente.

**Tarefas:**

Criar a skill dentro do projeto `code-smells-project/` e implementar o SKILL.md com 3 fases sequenciais:

- **Fase 1 — Análise:** Detectar stack, mapear arquitetura atual, imprimir resumo
- **Fase 2 — Auditoria:** Cruzar código contra catálogo de anti-patterns, gerar relatório, pedir confirmação
- **Fase 3 — Refatoração:** Reestruturar para o padrão MVC, validar que funciona

Criar arquivos de referência em Markdown que forneçam à skill o conhecimento necessário para executar as 3 fases. Os arquivos devem cobrir **obrigatoriamente** as seguintes áreas de conhecimento:

| Área de conhecimento | O que deve conter |
|---|---|
| Análise de projeto | Heurísticas para detecção de linguagem, framework, banco de dados e mapeamento de arquitetura |
| Catálogo de anti-patterns | Anti-patterns com sinais de detecção e classificação de severidade |
| Template de relatório | Formato padronizado do relatório de auditoria (Fase 2) |
| Guidelines de arquitetura | Regras do padrão MVC alvo (camadas Models, Views/Routes e Controllers, responsabilidades de cada uma) |
| Playbook de refatoração | Padrões concretos de transformação para cada anti-pattern (com exemplos de código) |

> **Nota:** Você tem liberdade para organizar os arquivos de referência como preferir — pode usar os nomes e a quantidade de arquivos que fizer sentido para sua skill. O importante é que todas as 5 áreas de conhecimento estejam cobertas. O nome da skill (`refactor-arch`) e o arquivo `SKILL.md` são obrigatórios e não devem ser alterados. O path da skill segue a convenção da ferramenta escolhida (no Claude Code, por exemplo, é `.claude/skills/refactor-arch/`).

**Requisitos da skill:**

- Deve ser agnóstica de tecnologia — deve funcionar corretamente nos 3 projetos fornecidos, independente da stack ou nível de organização
- O catálogo de anti-patterns deve conter no mínimo 8 anti-patterns com severidade distribuída (CRITICAL, HIGH, MEDIUM, LOW)
- O catálogo deve incluir detecção de APIs deprecated — identificar uso de APIs obsoletas e recomendar o equivalente moderno
- O playbook deve ter no mínimo 8 padrões de transformação com exemplos de código antes/depois
- A Fase 2 deve pausar e pedir confirmação antes de modificar qualquer arquivo
- A Fase 3 deve validar o resultado (boot da aplicação + endpoints funcionando)

### 3. Execução da Skill

Execute sua skill nos 3 projetos e valide que ela funciona em todas as stacks.

#### Projeto 1 — code-smells-project (Python/Flask)

Invocar a skill no Claude Code:

```bash
claude "/refactor-arch"
```

> **Nota:** O comando acima é o exemplo com Claude Code. Se você estiver usando Gemini CLI ou Codex, utilize o comando equivalente para invocar uma skill na sua ferramenta.

- Verificar que a Fase 1 detecta corretamente a stack e imprime o resumo
- Verificar que a Fase 2 encontra no mínimo 5 dos problemas documentados na sua análise manual
- Confirmar a execução da Fase 3
- Verificar que a Fase 3:
  - Cria a estrutura de diretórios baseada em MVC
  - A aplicação inicia sem erros
  - Os endpoints originais continuam respondendo
- Salvar o relatório de auditoria (output da Fase 2) em `reports/audit-project-1.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 2 — ecommerce-api-legacy (Node.js/Express)

Prove que sua skill é reutilizável em outro projeto de backend, mas com stack diferente.

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `ecommerce-api-legacy/`
- Invocar a skill:

```bash
cd ../ecommerce-api-legacy
claude "/refactor-arch"
```

- Verificar que as 3 fases executam corretamente neste projeto
- Salvar o relatório em `reports/audit-project-2.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 3 — task-manager-api (Python/Flask)

Agora o teste com um projeto Python/Flask que já possui alguma organização de camadas (models, routes, services, utils).

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `task-manager-api/`
- Invocar a skill:

```bash
cd ../task-manager-api
claude "/refactor-arch"
```

- Verificar que:
  - A Fase 1 detecta corretamente Python/Flask como stack e identifica o domínio de Task Manager
  - A Fase 2 identifica problemas mesmo em um projeto parcialmente organizado
  - A Fase 3 melhora a estrutura sem quebrar a aplicação (todos os endpoints devem continuar respondendo)
- Salvar o relatório em `reports/audit-project-3.md`
- Commitar o código refatorado do projeto no repositório

> **Nota:** Este projeto já possui alguma separação de camadas, mas isso não significa que a arquitetura está adequada. A skill deve identificar tanto problemas de código (segurança, performance, qualidade) quanto oportunidades de melhoria arquitetural. Se houver mudanças estruturais necessárias, a skill deve propô-las e executá-las.

#### Validação

Para cada projeto refatorado, valide o seguinte checklist:

```markdown
## Checklist de Validação

### Fase 1 — Análise
- [x] Linguagem detectada corretamente
- [x] Framework detectado corretamente
- [x] Domínio da aplicação descrito corretamente
- [x] Número de arquivos analisados condiz com a realidade

### Fase 2 — Auditoria
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados
- [x] Detecção de APIs deprecated incluída (se aplicável)
- [x] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [x] Estrutura de diretórios segue padrão MVC
- [x] Configuração extraída para módulo de config (sem hardcoded)
- [x] Models criados para abstrair dados
- [x] Views/Routes separadas para visualização ou roteamento
- [x] Controllers concentram o fluxo da aplicação
- [x] Error handling centralizado
- [x] Entry point claro
- [x] Aplicação inicia sem erros
- [x] Endpoints originais respondem corretamente
```

> **Dica:** Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Entregável

Repositório público no GitHub (fork do repositório base) contendo:

- Skill completa em `.claude/skills/refactor-arch/` (dentro dos 3 projetos)
- Código refatorado dos 3 projetos (resultado da execução da Fase 3, commitado no repositório)
- Relatórios de auditoria em `reports/` (3 arquivos)
- `README.md` atualizado

### Estrutura do repositório

Faça um fork do repositório base contendo os três projetos com code smells.

> **Nota:** A estrutura abaixo usa Claude Code como exemplo (`.claude/skills/`). Se estiver usando outra ferramenta, adapte os caminhos conforme a convenção dela.

```
desafio-skills/
├── README.md                              # Sua documentação
│
├── code-smells-project/                   # Projeto 1 — Python/Flask (API de E-commerce)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← SUA SKILL AQUI
│   │           ├── SKILL.md
│   │           └── (arquivos de referência)
│   ├── app.py
│   ├── controllers.py
│   ├── models.py
│   ├── database.py
│   └── requirements.txt
│
├── ecommerce-api-legacy/                  # Projeto 2 — Node.js/Express (LMS API com checkout)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── src/
│   │   ├── app.js
│   │   ├── AppManager.js
│   │   └── utils.js
│   ├── api.http
│   └── package.json
│
├── task-manager-api/                      # Projeto 3 — Python/Flask (API de Task Manager)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── app.py
│   ├── database.py
│   ├── seed.py
│   ├── requirements.txt
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── utils/
│
└── reports/                               # Relatórios gerados
    ├── audit-project-1.md                 # Saída da Fase 2 no projeto 1
    ├── audit-project-2.md                 # Saída da Fase 2 no projeto 2
    └── audit-project-3.md                 # Saída da Fase 2 no projeto 3
```

**O que você vai criar:**

- `.claude/skills/refactor-arch/` — A skill completa (SKILL.md + arquivos de referência)
- Código refatorado dos 3 projetos — resultado da execução da Fase 3, commitado no repositório
- `reports/audit-project-{1,2,3}.md` — Relatório de auditoria de cada projeto
- `README.md` — Documentação do seu processo

**O que já vem pronto:**

- `code-smells-project/` — API de E-commerce Python/Flask com code smells intencionais
- `ecommerce-api-legacy/` — LMS API Node.js/Express (com fluxo de checkout) e problemas de implementação
- `task-manager-api/` — API de Task Manager Python/Flask com organização parcial e problemas de segurança/qualidade

> **Dica:** Cada projeto contém problemas intencionais de diferentes severidades (CRITICAL, HIGH, MEDIUM, LOW), incluindo falhas de segurança, violações arquiteturais e problemas de qualidade de código. Parte do desafio é identificá-los por conta própria através da análise manual do código.

### README.md deve conter

**A) Seção "Análise Manual":**

- Lista dos problemas identificados manualmente em cada projeto
- Classificação por severidade
- Justificativa de por que cada problema é relevante

**B) Seção "Construção da Skill":**

- Decisões de design: como estruturou o SKILL.md e os arquivos de referência
- Quais anti-patterns incluiu no catálogo e por quê
- Como garantiu que a skill é agnóstica de tecnologia
- Desafios encontrados e como resolveu

**C) Seção "Resultados":**

- Resumo dos relatórios de auditoria dos 3 projetos (quantos findings por severidade em cada)
- Comparação antes/depois da estrutura de cada projeto
- Checklist de validação preenchido para cada projeto
- Screenshots ou logs mostrando as aplicações rodando após refatoração
- Observações sobre como a skill se comportou em stacks diferentes

**D) Seção "Como Executar":**

- Pré-requisitos (a ferramenta escolhida — Claude Code, Gemini CLI ou Codex — instalada e configurada)
- Comandos para executar a skill em cada projeto
- Como validar que a refatoração funcionou

### Ordem de execução sugerida

**1. Analisar os projetos manualmente**

Leia o código dos três projetos e documente os problemas encontrados.

**2. Criar a skill**

Escreva o SKILL.md e os arquivos de referência.

**3. Executar nos 3 projetos**

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch"
```

Salve a saída da Fase 2 de cada projeto em `reports/audit-project-{1,2,3}.md`.

**4. Iterar**

Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Critérios de Aceite

A skill deve atingir os seguintes mínimos em **todos os 3 projetos**:

| Critério | Requisito |
|---|---|
| Fase 1 detecta stack corretamente | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 encontra >= 5 findings | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 inclui pelo menos 1 CRITICAL ou HIGH | OBRIGATÓRIO (3/3 projetos) |
| Fase 3 aplicação funciona após refatoração | OBRIGATÓRIO (3/3 projetos) |

**IMPORTANTE:** Todos os critérios devem ser atingidos nos 3 projetos, não apenas em um!

> **Sobre o projeto 3 (task-manager-api):** Este projeto já possui alguma organização. "aplicação funciona" significa que a API inicia sem erros e todos os endpoints continuam respondendo corretamente.

## Referências

- [Claude Code: Skills](https://docs.anthropic.com/en/docs/claude-code/skills) — Documentação oficial sobre como criar e estruturar Skills
- [Claude Code: Overview](https://docs.anthropic.com/en/docs/claude-code/overview) — Visão geral do Claude Code e suas capacidades
- [The Complete Guide to Building Skills for Claude (PDF)](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) — Guia completo da Anthropic sobre construção de Skills
- [Equipping Agents for the Real World with Agent Skills](https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills) — Blog oficial da Anthropic sobre Agent Skills

---

## Dicas Finais

- **Comece pela análise manual** — entender os problemas profundamente é essencial para criar uma skill que os detecte.
- **O SKILL.md é um prompt** — ele instrui o agente sobre o que fazer, enquanto os arquivos de referência fornecem o conhecimento de domínio.
- **Seja específico nos sinais de detecção** — "código ruim" não ajuda; "query SQL dentro de loop for" é acionável.
- **Teste incrementalmente** — não tente criar a skill perfeita de primeira.
- **A skill deve ser copiável** — se ela só funciona em um projeto específico, está acoplada demais. Teste nos 3 projetos para validar.
- **Projetos diferentes exigem adaptação** — a Fase 3 de um projeto já parcialmente organizado não vai ter as mesmas transformações de um monolito. Sua skill deve se adaptar ao contexto.
- **Pedir confirmação na Fase 2 é obrigatório** — o humano deve revisar o relatório antes de qualquer modificação.
- **Consulte as referências do curso** — revise a documentação oficial da ferramenta escolhida e os materiais das aulas para relembrar a estrutura e anatomia de uma skill.

---

## A) Análise Manual

Análise feita lendo todo o código dos três projetos **antes** de escrever a skill (números de linha referem-se ao commit baseline).

### Projeto 1 — `code-smells-project` (Python/Flask, API de E-commerce)

Mapa: 4 arquivos `.py` (`app.py` 88 linhas, `controllers.py` 292, `models.py` 314, `database.py` 86), SQLite (`loja.db`), tabelas `produtos`, `usuarios`, `pedidos`, `itens_pedido`.

| # | Severidade | Local | Problema | Por que é relevante |
|---|---|---|---|---|
| 1 | CRITICAL | `models.py:28,49,60,110,128,140,174,280,285-297` | **SQL Injection**: todas as queries concatenam strings com entrada do usuário (inclusive o login, `models.py:110`) | Permite burlar o login, ler/alterar/apagar qualquer dado |
| 2 | CRITICAL | `app.py:7-8`, `controllers.py:289` | **Credenciais hardcoded** (`SECRET_KEY`), `DEBUG=True`; a chave ainda é devolvida em `/health` | Vazamento de segredo; debug em produção expõe o console do Werkzeug |
| 3 | CRITICAL | `app.py:47-76` | **Endpoints administrativos sem autenticação**: `/admin/reset-db` apaga o banco e `/admin/query` executa SQL arbitrário | Qualquer cliente destrói ou exfiltra todos os dados |
| 4 | CRITICAL | `models.py:76-83,99,110` / `database.py:76-78` | **Senhas em texto puro** e devolvidas em `GET /usuarios` | Exposição direta de credenciais |
| 5 | HIGH | `models.py` (arquivo inteiro, 1-314) | **God module**: SQL, regras de negócio (desconto, estoque), serialização e 4 domínios no mesmo arquivo | Impossível testar isoladamente; qualquer mudança afeta tudo |
| 6 | HIGH | `controllers.py:24-60,188-220` | **Regra de negócio e validação dentro dos controllers**, mais efeitos colaterais (e-mail/SMS/push simulados com `print`) | Viola a separação de camadas MVC |
| 7 | HIGH | `database.py:4-10` | **Estado global mutável** (`db_connection` singleton com `global`) e acoplamento direto controllers→`get_db` (`controllers.py:3,264`) | Sem injeção de dependência; difícil testar |
| 8 | MEDIUM | `models.py:171-232` | **Queries N+1**: para cada pedido, uma query de itens e, para cada item, outra de produto | Degrada com o volume |
| 9 | MEDIUM | `controllers.py:5-290` | **Tratamento de erro duplicado** (`try/except Exception` em todas as funções vazando `str(e)` ao cliente) | Duplicação; vaza detalhes internos |
| 10 | MEDIUM | `controllers.py:24-45,167-185,237-246` | **Validação ausente/inconsistente** (tipos de `preco`/`estoque`; `login`/`status` quebram com corpo `None`) | 500 em vez de 400 |
| 11 | MEDIUM | `models.py:133-169` | **Pedido sem transação** (sem `rollback` em falha parcial) | Estoque/pedido inconsistentes |
| 12 | LOW | `models.py:257-262` | **Magic numbers** (`10000`, `5000`, `1000`, `0.1`, `0.05`, `0.02`) | Regra de desconto ilegível |
| 13 | LOW | `controllers.py:52,242` | Listas de categorias/status **hardcoded** dentro da função | Duplicação |
| 14 | LOW | `controllers.py:8,11,57,106,161,179,182,208-210,248-250` | **`print` como log** (não há logging) | Sem níveis/formatos |
| 15 | LOW | `models.py:4-21,24-40,72-102,285-314` | Dicionário de serialização **duplicado** 5× | DRY |

### Projeto 2 — `ecommerce-api-legacy` (Node.js/Express, LMS com checkout)

Mapa: 3 arquivos `.js` (`src/app.js` 14, `src/AppManager.js` 141, `src/utils.js` 25), SQLite **em memória**, tabelas `users`, `courses`, `enrollments`, `payments`, `audit_logs`. Endpoints: `POST /api/checkout`, `GET /api/admin/financial-report`, `DELETE /api/users/:id`.

| # | Severidade | Local | Problema | Por que é relevante |
|---|---|---|---|---|
| 1 | CRITICAL | `utils.js:2-6` | **Credenciais hardcoded** (`dbPass`, chave live do gateway `pk_live_...`, SMTP) | Segredos versionados |
| 2 | CRITICAL | `AppManager.js:45` | **Número de cartão completo e chave do gateway logados** com `console.log` | Vazamento de dado de pagamento (PCI) |
| 3 | CRITICAL | `AppManager.js:4-141` | **God class**: `AppManager` cria o banco, o schema/seed, define rotas, regra de checkout, relatório e pagamento | Mistura de todas as camadas |
| 4 | HIGH | `utils.js:17-23` | **`badCrypto`**: "hash" falso (base64 repetido, 10 caracteres, 10.000 iterações inúteis) para senha | Senhas triviais de reverter; bloqueia o event loop |
| 5 | HIGH | `AppManager.js:28-78` | **Lógica de negócio dentro do handler da rota** (callback hell de 5 níveis, pagamento + matrícula + auditoria) | Intestável |
| 6 | HIGH | `utils.js:9-10,25`, `AppManager.js:2` | **Estado global mutável** (`globalCache`, `totalRevenue`) exportado | Acoplamento oculto |
| 7 | HIGH | `AppManager.js:131-137` | `DELETE /api/users/:id` **sem autenticação** e deixa matrículas/pagamentos órfãos | Integridade de dados |
| 8 | MEDIUM | `AppManager.js:80-129` | **N+1** (cursos → matrículas → usuário → pagamento) e relatório montado por contadores manuais | Performance e race conditions |
| 9 | MEDIUM | `AppManager.js:35,51-72` | Validação fraca e respostas de erro em texto puro (`"Erro DB"`), sem middleware de erro; erros do `audit_logs` ignorados (`AppManager.js:58-61`) | Contrato inconsistente |
| 10 | MEDIUM | `AppManager.js:7`, `src/app.js:13` | Config/porta/DB acoplados (banco `:memory:` fixo) | Não configurável por ambiente |
| 11 | LOW | `AppManager.js:29-33` | Nomes pouco descritivos (`u`, `e`, `p`, `cid`, `cc`) | Legibilidade |
| 12 | LOW | `AppManager.js:46`, `utils.js:19-21` | Magic values (`"4"` para aprovar cartão, `10000`, `substring(0,2)`, `"123456"` em `:68`) | Regra escondida |
| 13 | LOW | `AppManager.js:2`, `utils.js:25` | Imports/exports não usados (`totalRevenue`, `globalCache`) | Código morto |

### Projeto 3 — `task-manager-api` (Python/Flask, Task Manager, já com camadas)

Mapa: 15 arquivos `.py` (`app.py`, `database.py`, `seed.py`, `models/{__init__,user,task,category}.py`, `routes/{__init__,task,user,report}_routes.py`, `services/{__init__,notification_service}.py`, `utils/{__init__,helpers}.py`), SQLAlchemy/SQLite (`tasks.db`), tabelas `users`, `tasks`, `categories`.

| # | Severidade | Local | Problema | Por que é relevante |
|---|---|---|---|---|
| 1 | CRITICAL | `models/user.py:29,32` | **MD5 sem salt** para senhas | Quebra trivial por rainbow table |
| 2 | CRITICAL | `models/user.py:21`, `routes/user_routes.py:33,85,129,209` | **`to_dict` devolve o hash da senha** em `/users/<id>`, `POST /users`, `PUT /users/<id>` e `/login` | Exposição de credenciais |
| 3 | CRITICAL | `app.py:13`, `services/notification_service.py:8-10` | **Credenciais hardcoded** (`SECRET_KEY`, senha SMTP) | Segredos versionados |
| 4 | HIGH | `routes/user_routes.py:210` | **Token de login falso** (`'fake-jwt-token-' + id`), nenhuma rota é protegida | Autenticação inexistente |
| 5 | HIGH | `routes/task_routes.py`, `routes/user_routes.py`, `routes/report_routes.py` | **Lógica de negócio e validação dentro das rotas** (não há controllers; `services/` só tem notificação e não é usado) | Camada de controller ausente |
| 6 | HIGH | `routes/report_routes.py:158-221` | Rotas de **`/categories` dentro de `report_routes`** | Responsabilidade errada |
| 7 | MEDIUM | `routes/task_routes.py:42,51`, `report_routes.py:55-60,163`, `user_routes.py:22` | **N+1** (usuário e categoria por task; tasks por usuário; contagem por categoria; `len(u.tasks)`) | Performance |
| 8 | MEDIUM | `routes/task_routes.py:31-39,72-80`, `user_routes.py:172`, `report_routes.py:35,133`, `models/task.py:50-59` | Regra **"overdue" duplicada em 6 lugares** com `if` aninhado, apesar de existir `Task.is_overdue` | DRY |
| 9 | MEDIUM | `task_routes.py:62,137,204,236`, `user_routes.py:130,149`, `report_routes.py:186,207,221` | **`except:` genérico** (engole erro) | Dificulta diagnóstico |
| 10 | MEDIUM | `task_routes.py:113,182,261,264`, `report_routes.py:196` | **Validação ausente**: `priority` sem conversão (`'a' < 1` → 500), `int(...)` sem tratamento, `get_json()` sem checar `None` | 500 em vez de 400 |
| 11 | MEDIUM | `utils/helpers.py` inteiro | **Código morto/duplicado**: `process_task_data`, `validate_email`, constantes `VALID_*` nunca usados; regras repetidas nas rotas | Duas fontes de verdade |
| 12 | LOW | `task_routes.py:31,72`, `user_routes.py:172`, `report_routes.py:35,42,71,133`, `models/task.py:15-16,52`, `models/user.py:14` | **API deprecated**: `datetime.utcnow()` (Python 3.12+) e `Model.query.get()` (SQLAlchemy 2.0, `task_routes.py:42,51,67,117,...`) | Warnings e remoção futura |
| 13 | LOW | `report_routes.py:24-28`, `task_routes.py:113` | **Magic numbers** (prioridades 1-5, limites 3/200/4) | Legibilidade |
| 14 | LOW | `app.py:7`, `task_routes.py:7`, `user_routes.py:6`, `report_routes.py:8`, `helpers.py:1-7` | **Imports não usados** (`os, sys, json, hashlib`, ...) | Ruído |
| 15 | LOW | `app.py:34`, `task_routes.py:149,153,219,234`, `user_routes.py:83,89,147` | `debug=True` + `print` como log | Sem logging |

---

## B) Construção da Skill

### Estrutura

```text
.github/skills/refactor-arch/
├── SKILL.md                         # prompt: 3 fases sequenciais + regras invioláveis
└── references/
    ├── project-analysis.md          # (1) heurísticas de linguagem/framework/banco/arquitetura
    ├── anti-patterns-catalog.md     # (2) 17 anti-patterns + APIs deprecated, com sinais de detecção
    ├── report-template.md           # (3) formato exato do relatório da Fase 2
    ├── mvc-guidelines.md            # (4) responsabilidades de cada camada e estrutura por stack
    └── refactoring-playbook.md      # (5) 14 padrões de transformação com Antes/Depois
```

### Decisões de design

- **`SKILL.md` é o prompt; as referências são o conhecimento.** O `SKILL.md` só define *o que fazer em cada fase*, os formatos de saída e as regras invioláveis; heurísticas, catálogo, template e receitas ficam nas referências (carregadas sob demanda, por fase). Assim, os ajustes entre execuções acontecem nas referências, sem reescrever o prompt.
- **Fase 2 é somente leitura e termina com `[y/n]`.** A única escrita permitida antes da confirmação é salvar o relatório. Nas execuções reais, a skill parou na pergunta e só seguiu para a Fase 3 depois do `y`.
- **Todo finding exige arquivo:linha verificados** e referencia o ID do catálogo (`AP-xx`/`DP-xx`) e o padrão do playbook (`PB-xx`), validado por `tests/check_report.py` contra o código original.
- **Fase 3 começa por uma baseline funcional** e termina com a mesma bateria, mais teste de compatibilidade com dados legados. O resumo final traz obrigatoriamente `Intentional behavior changes` e `Remaining findings`, para que nada fique implícito.
- **Escopo mínimo e contrato preservado.** Regras do `SKILL.md`: nenhum endpoint é removido (endpoints inseguros são protegidos por configuração), não se criam funcionalidades novas (ex.: autenticação em todas as rotas) e a aplicação refatorada deve funcionar com um banco criado pela versão original.
- **Adaptação ao nível de organização:** monolito → cria todas as camadas; projeto parcialmente organizado → mantém o que está adequado e move/cria só o que falta (no projeto 3: introduziu controllers, extraiu categorias, removeu helpers mortos).

### Catálogo de anti-patterns (e por quê)

| Severidade | IDs | Motivo da inclusão |
|---|---|---|
| CRITICAL | AP-01 segredos hardcoded, AP-02 SQL Injection, AP-03 God Class, AP-04 endpoints admin sem auth, AP-05 senhas inseguras, AP-06 dados sensíveis em logs | Cobrem os exemplos de CRITICAL do enunciado e os problemas de segurança vistos nos 3 projetos |
| HIGH | AP-07 lógica em controllers/rotas, AP-08 estado global/sem DI, AP-09 responsabilidade fora do lugar | Violações centrais de MVC/SOLID |
| MEDIUM | AP-10 N+1, AP-11 erros duplicados/genéricos, AP-12 validação, AP-13 duplicação/código morto, AP-14 transações, AP-15 config acoplada | Padronização, duplicação e performance |
| LOW | AP-16 magic numbers, AP-17 nomes/imports/`print` | Legibilidade |
| Deprecated | DP-01 Python, DP-02 Node, DP-03 outras | Exigência do desafio. Só entram **depreciações documentadas** (`datetime.utcnow()`, `Query.get()`, `new Buffer()`...); estilo antigo (callbacks, `var`) e hash fraco ficam nos AP-xx correspondentes |

Cada item traz **sinais de detecção acionáveis** ("query SQL dentro de `for`", "`except:` sem tipo", grep de `utcnow`...).

### Como garanti a neutralidade de tecnologia

1. O `SKILL.md` **não cita** linguagem, framework ou arquivo dos projetos (verificado por `tests/check_skill.py`).
2. Os sinais do catálogo descrevem **conceitos** ("SQL + variável sem placeholder", "variável de módulo mutável"), com exemplos por stack só como ilustração.
3. A detecção de stack é por **evidências** (manifestos, imports, DDL); as guidelines MVC trazem estruturas-alvo para Flask, Express, Spring, Go e Laravel.
4. O playbook mostra cada padrão em **Python e Node**.
5. A **mesma cópia, byte a byte**, da skill foi usada nos 3 projetos (`tests/check_skill.py` compara os diretórios).

### Desafios encontrados e soluções

| Desafio | Solução |
|---|---|
| Provar "endpoints continuam respondendo" de forma objetiva | `tests/smoke.py`: grava a baseline da API **original** (via `git worktree` do commit inicial) e compara status, estrutura e valores. Endpoint removido (404/405/500) **reprova**; só mudanças de segurança explicitamente listadas (ex.: SQL injection no login → 401, rota admin → 403) são aceitas |
| Primeira versão da refatoração quebrava login de bancos existentes (projeto 1) | Detectado por `tests/legacy_data.py` (banco com schema original e senha em texto puro). Regra de "Compatibilidade de dados" adicionada ao `SKILL.md` e ao PB-11; a execução real da skill passou a aceitar o formato legado e regravar o hash |
| Catálogo tratava estilo (callbacks, `var`, `except:`) como API deprecated | Seção de deprecated reescrita: somente depreciações documentadas |
| Rotas admin fazem parte do contrato | PB-10: nunca remover; proteger por token de configuração (403 sem token) e, para SQL arbitrário/reset, desabilitar por padrão |
| Escopo crescendo (autenticação completa) | Regra de escopo mínimo; o que fica de fora aparece em `Remaining findings` |
| ORM com sessão global (Flask-SQLAlchemy) vs. "controller não acessa dados" | PB-05: consultas nomeadas e `save()/remove()` no model; `tests/check_mvc.py` detecta `db.session` em controllers |

### Como a skill foi executada

Ferramenta: **GitHub Copilot CLI 1.0.104** (skill descoberta em `.github/skills/refactor-arch`). Em cada projeto, em uma cópia limpa do código original:

```bash
copilot -p "/refactor-arch Execute as Fases 1 e 2 e PARE aguardando minha confirmacao. Salve o relatorio em ../reports/audit-project-N.md" --allow-all-tools --allow-all-paths
copilot --resume=<id-da-sessao> -p "y" --allow-all-tools --allow-all-paths     # confirmação da Fase 3
```

A skill imprimiu a Fase 1, gerou o relatório, **parou em `Proceed with refactoring (Phase 3)? [y/n]`** e só refatorou após o `y`. Os logs completos (com as chamadas de ferramenta) estão em [docs/evidencias/cli-logs/](docs/evidencias/cli-logs) e os blocos finais de cada fase em `docs/evidencias/project-N.txt`.

Observações honestas: (a) no chat a Fase 2 apareceu resumida (o relatório completo está no arquivo salvo, que segue o template); (b) a sessão do projeto 3 respondeu em inglês, embora a skill esteja em português; (c) durante as iterações a própria sessão do CLI refinou o `SKILL.md` e o PB-10 (regra de endpoints) e os 3 projetos foram executados de novo com a versão final, que é a versão presente nos 3 projetos.

---

## C) Resultados

### Findings por severidade

| Projeto | Stack | CRITICAL | HIGH | MEDIUM | LOW | Total | Relatório |
|---|---|---:|---:|---:|---:|---:|---|
| 1 — code-smells-project | Python + Flask | 5 | 3 | 6 | 2 | 16 | [reports/audit-project-1.md](reports/audit-project-1.md) |
| 2 — ecommerce-api-legacy | Node.js + Express | 5 | 2 | 6 | 2 | 15 | [reports/audit-project-2.md](reports/audit-project-2.md) |
| 3 — task-manager-api | Python + Flask | 3 | 2 | 6 | 4 | 15 | [reports/audit-project-3.md](reports/audit-project-3.md) |

### Reteste do feedback técnico — Projeto 3

Antes da correção, um `POST /users` anônimo com `role: "admin"` retornou `201` e criou um administrador. O cadastro agora ignora o papel enviado e atribui `DEFAULT_ROLE`; o teste de regressão confirma que o usuário criado é `user`. A skill foi executada novamente com foco nesse caso: [relatório da reexecução](reports/audit-project-3-feedback.md). O teste de compatibilidade do Projeto 3 e o smoke test (26/26 endpoints) passaram.

### Antes / Depois (estrutura gerada pela skill)

**Projeto 1** — de 4 arquivos para camadas MVC:

```text
ANTES                         DEPOIS
app.py  (rotas+admin+SQL)     app.py (composition root)
controllers.py                config/{settings,constants}.py
models.py (SQL+regra+JSON)    models/{database,produto,usuario,pedido,sistema,admin}_model.py
database.py (global+seed)     views/{produto,usuario,pedido,sistema}_views.py
                              controllers/{produto,usuario,pedido,sistema}_controller.py
                              services/{pedido,relatorio,notificacao}_service.py
                              middlewares/{error_handler,auth}.py
                              utils/{errors,validators,security,http}.py  ·  .env.example
```

**Projeto 2** — de 3 arquivos (God class `AppManager`) para:

```text
ANTES                         DEPOIS
src/app.js                    src/app.js (composition root)
src/AppManager.js (141 l.)    src/config/{index,constants}.js
src/utils.js (config+global)  src/database/{connection,schema}.js
                              src/models/{user,course,enrollment}Model.js
                              src/services/{checkout,report,password}Service.js
                              src/controllers/{checkout,admin,user}Controller.js
                              src/routes/index.js
                              src/middlewares/{errorHandler,adminAuth}.js  ·  .env.example
```

**Projeto 3** — já tinha `models/routes/services/utils`; ganhou controllers, config e erros centralizados:

```text
ANTES                              DEPOIS
app.py (config inline)             app.py (application factory)
routes/{task,user,report}_routes   routes/{task,user,category,report,health}_routes.py (URL → controller)
  (lógica+validação+SQL)           controllers/{task,user,category,report,health}_controller.py   ← NOVO
models/{task,user,category}.py     models/{database,base,task,user,category}.py
services/notification_service      services/notification_service.py
utils/helpers.py (código morto)    utils/{dates,validators}.py
                                   config/{settings,constants}.py  ·  middlewares/{error_handler,auth}.py
```

### Checklist de validação preenchido

Evidência: [docs/evidencias/](docs/evidencias) (saídas reais das Fases 1–3 e logs dos testes por projeto). O checklist do enunciado está marcado no início deste README.

| Item | P1 | P2 | P3 |
|---|:-:|:-:|:-:|
| **Fase 1** — Linguagem detectada corretamente | ✅ | ✅ | ✅ |
| Framework detectado corretamente | ✅ | ✅ | ✅ |
| Domínio descrito corretamente | ✅ | ✅ | ✅ |
| Nº de arquivos condiz com a realidade (4 / 3 / 15) | ✅ | ✅ | ✅ |
| **Fase 2** — Relatório segue o template | ✅ | ✅ | ✅ |
| Cada finding com arquivo e linhas exatos (validado contra o código original) | ✅ | ✅ | ✅ |
| Ordenado CRITICAL → LOW | ✅ | ✅ | ✅ |
| Mínimo de 5 findings (16 / 15 / 15) | ✅ | ✅ | ✅ |
| Detecção de APIs deprecated incluída | ✅ (nenhuma) | ✅ (nenhuma) | ✅ (`utcnow`, `Query.get`) |
| Skill pausa e pede confirmação antes da Fase 3 | ✅ | ✅ | ✅ |
| **Fase 3** — Estrutura MVC | ✅ | ✅ | ✅ |
| Configuração extraída (sem hardcoded) | ✅ | ✅ | ✅ |
| Models abstraem dados | ✅ | ✅ | ✅ |
| Views/Routes separadas | ✅ | ✅ | ✅ |
| Controllers concentram o fluxo | ✅ | ✅ | ✅ |
| Error handling centralizado | ✅ | ✅ | ✅ |
| Entry point claro | ✅ | ✅ | ✅ |
| Aplicação inicia sem erros | ✅ | ✅ | ✅ |
| Endpoints originais respondem (28/28 · 7/7 · 26/26) | ✅ | ✅ | ✅ |

### Critérios de aceite (`python tests/run_all.py`)

| Critério | P1 | P2 | P3 |
|---|:-:|:-:|:-:|
| Fase 1 detecta stack | PASS | PASS | PASS |
| Fase 2 ≥ 5 findings | PASS (16) | PASS (15) | PASS (15) |
| Fase 2 ≥ 1 CRITICAL/HIGH | PASS (8) | PASS (7) | PASS (5) |
| Fase 3 aplicação funciona (boot + endpoints + dados legados) | PASS | PASS | PASS |

### Logs das aplicações rodando após a refatoração

Trecho de [docs/evidencias/project-1-smoke.txt](docs/evidencias/project-1-smoke.txt) (os arquivos `project-2-smoke.txt` e `project-3-smoke.txt` seguem o mesmo formato):

```text
PASS aplicação iniciou
PASS listar produtos: GET /produtos -> 200
PASS login com SQL injection: POST /login -> 401        # antes: 200 (bypass de login)
PASS admin query (SQL arbitrario): POST /admin/query -> 403   # rota mantida, agora protegida por token
PASS admin reset-db: POST /admin/reset-db -> 403
RESULT project-1: PASS (28/28 endpoints)
```

### Mudanças intencionais de contrato (declaradas pela própria skill na Fase 3)

| Projeto | Mudança | Finding |
|---|---|---|
| 1 | `senha` removida de `/usuarios*`; `secret_key`/`debug` removidos de `/health`; `/admin/reset-db` e `/admin/query` respondem 403 por padrão (habilitam com `ENABLE_ADMIN_ENDPOINTS` + `ADMIN_TOKEN`); login por SQL injection → 401; entradas inválidas que davam 500 agora dão 400 | AP-01, AP-02, AP-04, AP-05, AP-12 |
| 2 | `DELETE /api/users/:id` remove também matrículas e pagamentos; rotas admin/delete exigem `X-Admin-Token` quando `ADMIN_TOKEN` está definido (403 em produção sem token; abertas com aviso em desenvolvimento); senha padrão do checkout passa a ser aleatória; `card` não-string → 400 | AP-04, AP-05, AP-12, AP-14 |
| 3 | `password` removido de `/users*` e `/login`; token de login assinado; `DELETE` e alteração de `role/active` verificam `X-Admin-Token` quando `ADMIN_TOKEN` está definido; debug desligado por padrão; entradas inválidas → 400 em vez de 500 | AP-01, AP-04, AP-05, AP-12 |

### Observações sobre o comportamento da skill em stacks diferentes

- **Projeto 1 (monolito Python):** maior volume de findings críticos (SQL Injection, segredos, endpoints admin, senhas em texto puro). Criou todas as camadas e migra senhas legadas no login.
- **Projeto 2 (Node):** a skill **não** acusou SQL Injection (as queries já eram parametrizadas) nem APIs deprecated: a detecção é por sinal, não por "template". Foco em God class, callbacks aninhados, cartão em log e integridade.
- **Projeto 3 (já em camadas):** a Fase 2 apontou o que a estrutura aparente escondia (ausência de controllers, `services/` não usado, categorias no módulo errado, MD5, hash exposto, `utcnow`/`Query.get`). A Fase 3 **preservou** models/blueprints e adicionou só o que faltava; registrou como falso positivo o finding de integridade de categorias.
- **Fora do escopo declarado nos 3 projetos:** autenticação/autorização completa de todas as rotas (ver `Remaining findings` em `docs/evidencias/project-N.txt`).

---

## D) Como Executar

### Pré-requisitos

- **GitHub Copilot CLI** instalado e autenticado (`copilot`; ex.: `npm install -g @github/copilot`), com suporte a skills em `.github/skills/`. Alternativa: Claude Code com `.claude/skills/` (mesma estrutura).
- Python 3.10+ e Node.js 18+ (testado com Python 3.13 e Node 24).

### Preparação

```bash
git clone <seu-fork>
cd <repo>
# Projetos Python
cd code-smells-project && python -m venv .venv && .venv/Scripts/pip install -r requirements.txt && cd ..
cd task-manager-api    && python -m venv .venv && .venv/Scripts/pip install -r requirements.txt && cd ..
# Projeto Node
cd ecommerce-api-legacy && npm install && cd ..
```

(No Linux/macOS use `.venv/bin/pip`. Os testes esperam o venv em `<projeto>/.venv` no Windows.)

### Executar a skill (ordem sugerida)

> Para repetir a execução, parta dos projetos originais: `git checkout 6d1ce62 -- code-smells-project ecommerce-api-legacy task-manager-api` e restaure a skill em `.github/skills/refactor-arch` de cada projeto.

```bash
# Projeto 1
cd code-smells-project
copilot            # dentro do CLI:  /refactor-arch   (leia a Fase 2 e responda y)
# Projeto 2
cd ../ecommerce-api-legacy
copilot            # /refactor-arch
# Projeto 3
cd ../task-manager-api
copilot            # /refactor-arch
```

Salve a saída da Fase 2 de cada projeto em `reports/audit-project-N.md` na raiz do repositório.

### Como validar que a refatoração funcionou

```bash
python tests/run_all.py              # bateria completa + matriz dos critérios de aceite
python tests/check_skill.py          # estrutura da skill (>=8 anti-patterns, >=8 padrões, agnóstica, cópias idênticas)
python tests/check_report.py 1       # relatório do projeto N (template, ordenação, arquivo:linha reais)
python tests/check_mvc.py 1          # camadas MVC e ausência de anti-patterns CRITICAL detectáveis por busca
python tests/smoke.py 1 compare      # sobe a app e compara todos os endpoints com a baseline original
python tests/legacy_data.py 1        # login com banco criado pela versão original (projetos 1 e 3)
```

`tests/baseline/*.json` guarda as respostas da API **original**. Para regravar: `python tests/smoke.py N record` com o código original (ex.: `git worktree add ../orig 6d1ce62` e `SMOKE_PROJECT_ROOT=../orig`).

Para rodar manualmente cada aplicação refatorada:

```bash
cd code-smells-project  && .venv/Scripts/python app.py      # http://127.0.0.1:5000
cd ecommerce-api-legacy && npm start                        # http://127.0.0.1:3000
cd task-manager-api     && .venv/Scripts/python seed.py && .venv/Scripts/python app.py
```

Configuração por variáveis de ambiente (veja o `.env.example` de cada projeto).
