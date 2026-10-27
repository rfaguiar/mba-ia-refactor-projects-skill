# Skill `refactor-arch` — Refatoração Arquitetural Automatizada para MVC

Solução do desafio de criação de **Skills**: uma skill agnóstica de tecnologia que **analisa**, **audita** e **refatora** projetos backend para o padrão **MVC**, validada em 3 projetos legados (2× Python/Flask e 1× Node.js/Express).

> Este documento (`docs/solucao.md`) concentra as seções A–D pedidas no enunciado; o `README.md` do repositório foi mantido como no original, apenas com o checklist de validação marcado. O enunciado do desafio está no `readme.md` da pasta pai (fora do versionamento).

## Estrutura do repositório

```text
.
├── README.md                   # enunciado original + checklist de validação marcado
├── code-smells-project/        # Projeto 1 — Python/Flask (E-commerce)  → refatorado
│   └── .github/skills/refactor-arch/
├── ecommerce-api-legacy/       # Projeto 2 — Node.js/Express (LMS)       → refatorado
│   └── .github/skills/refactor-arch/
├── task-manager-api/           # Projeto 3 — Python/Flask (Task Manager) → refatorado
│   └── .github/skills/refactor-arch/
├── reports/                    # audit-project-{1,2,3}.md (saída da Fase 2)
├── tests/                      # scripts de validação (smoke, legacy_data, relatório, MVC, skill, run_all)
│   └── baseline/               # respostas da API ORIGINAL usadas como referência
└── docs/                       # solucao.md (seções A–D) e evidencias/ (saídas das Fases 1–3 e logs dos testes)
```

**Ferramenta:** GitHub Copilot CLI (skills em `.github/skills/<nome>/SKILL.md`; invocação `/refactor-arch`). O nome `refactor-arch` e o arquivo `SKILL.md` seguem o enunciado.

> **Execução:** as 3 fases foram executadas pelo **GitHub Copilot CLI** invocando a skill `refactor-arch` (detalhes e logs na seção B, "Como a skill foi executada").

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

A skill imprimiu a Fase 1, gerou o relatório, **parou em `Proceed with refactoring (Phase 3)? [y/n]`** e só refatorou após o `y`. Os logs completos (com as chamadas de ferramenta) estão em [docs/evidencias/cli-logs/](evidencias/cli-logs) e os blocos finais de cada fase em `docs/evidencias/project-N.txt`.

Observações honestas: (a) no chat a Fase 2 apareceu resumida (o relatório completo está no arquivo salvo, que segue o template); (b) a sessão do projeto 3 respondeu em inglês, embora a skill esteja em português; (c) durante as iterações a própria sessão do CLI refinou o `SKILL.md` e o PB-10 (regra de endpoints) e os 3 projetos foram executados de novo com a versão final, que é a versão presente nos 3 projetos.

---

## C) Resultados

### Findings por severidade

| Projeto | Stack | CRITICAL | HIGH | MEDIUM | LOW | Total | Relatório |
|---|---|---:|---:|---:|---:|---:|---|
| 1 — code-smells-project | Python + Flask | 5 | 3 | 6 | 2 | 16 | [reports/audit-project-1.md](../reports/audit-project-1.md) |
| 2 — ecommerce-api-legacy | Node.js + Express | 5 | 2 | 6 | 2 | 15 | [reports/audit-project-2.md](../reports/audit-project-2.md) |
| 3 — task-manager-api | Python + Flask | 3 | 2 | 6 | 4 | 15 | [reports/audit-project-3.md](../reports/audit-project-3.md) |

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

Evidência: [docs/evidencias/](evidencias) (saídas reais das Fases 1–3 e logs dos testes por projeto). O checklist marcado também está no `README.md`.

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

Trecho de [docs/evidencias/project-1-smoke.txt](evidencias/project-1-smoke.txt) (os arquivos `project-2-smoke.txt` e `project-3-smoke.txt` seguem o mesmo formato):

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
