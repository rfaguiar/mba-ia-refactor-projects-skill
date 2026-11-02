# Catálogo de Anti-Patterns (Fase 2)

Use este catálogo como checklist: percorra **todos** os itens contra **todo** o código. Cada item traz: severidade, sinais de detecção (acionáveis, buscáveis), impacto e o padrão do [playbook](refactoring-playbook.md) que o corrige.

## Escala de severidade

| Severidade | Critério | Exemplos |
|---|---|---|
| **CRITICAL** | Falha grave de arquitetura ou segurança: expõe dados, permite ataque ou viola completamente a separação de responsabilidades | Credenciais hardcoded, SQL Injection, God Class, endpoint admin aberto |
| **HIGH** | Forte violação de MVC/SOLID que dificulta manutenção e testes | Regra de negócio em controller/rota, estado global mutável, acoplamento sem DI, auth falsa |
| **MEDIUM** | Padronização, duplicação, performance moderada | N+1, error handling duplicado/genérico, validação ausente, regra duplicada |
| **LOW** | Legibilidade | Magic numbers, nomes ruins, imports/código morto, `print` como log |

---

## Anti-patterns de segurança e arquitetura

### AP-01 — Credenciais e segredos hardcoded
- **Severidade:** CRITICAL → playbook **PB-01**
- **Sinais:** literais atribuídos a nomes como `SECRET`, `KEY`, `PASSWORD`, `PASS`, `TOKEN`, `API_KEY`, `pk_live_`, `sk_`; usuário/senha de SMTP ou banco no código; `DEBUG = True`/`debug=True` fixo; segredos devolvidos em respostas (`/health`) ou logs.
- **Impacto:** vazamento de segredo no versionamento; debug em produção expõe console interativo.

### AP-02 — SQL Injection (queries montadas por concatenação/interpolação)
- **Severidade:** CRITICAL → playbook **PB-02**
- **Sinais:** `execute("... " + var)`, `f"SELECT ... {var}"`, `` `SELECT ... ${var}` ``, `.format(` ou `%` dentro de string SQL; `LIKE '%" + termo + "%'`; ORM `text()`/`raw()` com concatenação. Em qualquer stack, SQL + variável sem placeholder (`?`, `%s`, `:nome`, `$1`).
- **Impacto:** bypass de login, leitura/alteração/remoção arbitrária de dados.

### AP-03 — God Class / God Module (tudo no mesmo arquivo)
- **Severidade:** CRITICAL → playbook **PB-03**
- **Sinais:** um arquivo/classe que mistura acesso a dados (SQL/DDL/seed), regra de negócio, roteamento e/ou serialização para vários domínios; classe "Manager"/"Service" com banco + rotas + cálculo; arquivo com > ~250 linhas e > 3 domínios; funções sem coesão.
- **Impacto:** impossível testar isoladamente; toda mudança afeta tudo.

### AP-04 — Endpoints administrativos/destrutivos sem autenticação
- **Severidade:** CRITICAL → playbook **PB-10**
- **Sinais:** rotas `/admin/*`, `reset`, `drop`, `query`/`sql`, `DELETE` de entidades sem checagem de identidade/papel; execução de SQL recebido no body; autenticação ausente em recursos sensíveis.
- **Impacto:** qualquer cliente destrói ou exfiltra todos os dados.

### AP-05 — Senhas armazenadas ou transmitidas de forma insegura
- **Severidade:** CRITICAL (texto puro / retorno do hash na API) ou HIGH (hash fraco) → playbook **PB-11**
- **Sinais:** comparação `senha = '...'` direta no SQL; coluna de senha preenchida com valor em claro; `md5`/`sha1` sem salt; "hash" caseiro (base64, truncado); `password` presente em `to_dict`/serializers/respostas JSON; token de sessão falso (`'fake-jwt-token-'+id`).
- **Impacto:** exposição direta de credenciais; autenticação burlável.

### AP-06 — Dados sensíveis em logs
- **Severidade:** CRITICAL → playbook **PB-01**
- **Sinais:** `console.log`/`print`/`logger` contendo número de cartão, senha, token, chave de gateway.
- **Impacto:** violação de conformidade (PCI/LGPD), vazamento por logs.

### AP-07 — Lógica de negócio em Controllers/Rotas (camada ausente ou anêmica)
- **Severidade:** HIGH → playbook **PB-04**
- **Sinais:** handler de rota com validação de domínio, cálculo, orquestração de múltiplas entidades, acesso a dados e efeitos colaterais (e-mail/SMS/pagamento); controllers/`services` inexistentes ou não usados; callbacks aninhados > 3 níveis dentro da rota; `Model.query`/SQL dentro da rota.
- **Impacto:** viola a separação MVC; regra não reutilizável nem testável.

### AP-08 — Estado global mutável e acoplamento sem injeção de dependência
- **Severidade:** HIGH → playbook **PB-05**
- **Sinais:** `global x` / variável de módulo mutável (`db_connection = None`, `globalCache = {}`, contadores exportados); singleton criado dentro do próprio módulo e importado por controllers; `new Dependency()` dentro do construtor/handler; serviços instanciados em lugar fixo.
- **Impacto:** acoplamento oculto, efeitos entre requisições, testes impossíveis.

### AP-09 — Responsabilidade fora do lugar (camadas misturadas)
- **Severidade:** HIGH → playbook **PB-03/PB-04**
- **Sinais:** rotas de um domínio dentro do arquivo de outro (ex.: `/categories` em `report_routes`); models com lógica de apresentação/serialização duplicada; validação de entrada dentro do model e da rota ao mesmo tempo; utils com regras de negócio.
- **Impacto:** difícil localizar código; manutenção propensa a erros.

## Anti-patterns de qualidade e performance

### AP-10 — Queries N+1 e consultas em laço
- **Severidade:** MEDIUM → playbook **PB-06**
- **Sinais:** query (`execute`, `.get(`, `Model.query`, `db.get`/`db.all`) dentro de `for`/`forEach`/`.map`; acessar relação lazy dentro de laço (`len(u.tasks)`); contagem por item (`count()` por categoria).
- **Impacto:** número de queries cresce com os dados.

### AP-11 — Tratamento de erros duplicado, genérico ou engolido
- **Severidade:** MEDIUM → playbook **PB-07**
- **Sinais:** `try/except Exception as e: return ... str(e)` repetido em cada handler; `except:` sem tipo; callback ignorando `err`; respostas de erro em formatos diferentes (texto vs JSON); ausência de error handler/middleware central; stack/mensagem interna devolvida ao cliente.
- **Impacto:** vaza detalhes internos, dificulta diagnóstico, duplicação.

### AP-12 — Validação de entrada ausente ou inconsistente
- **Severidade:** MEDIUM → playbook **PB-08**
- **Sinais:** `request.get_json()`/`req.body` usado sem checar `None`; conversão `int()`/`float()` sem tratamento; comparação de tipos não validados (`priority < 1` com string); validação repetida em várias rotas; listas de valores válidos recriadas dentro de funções.
- **Impacto:** erros 500 em vez de 400; dados inválidos persistidos.

### AP-13 — Duplicação de regra de negócio e código morto
- **Severidade:** MEDIUM → playbook **PB-09**
- **Sinais:** mesmo bloco `if` repetido em ≥ 3 lugares (ex.: cálculo de "atrasado"); dicionário de serialização copiado; helper existente mas não usado (funções/constantes/imports sem referência); método de model definido e ignorado pelas rotas.
- **Impacto:** duas fontes de verdade; correção parcial de bugs.

### AP-14 — Operações multi-etapa sem transação / integridade referencial
- **Severidade:** MEDIUM → playbook **PB-12**
- **Sinais:** várias escritas dependentes sem `try/rollback`/transação; `DELETE` de entidade pai que deixa filhos órfãos; `commit` por etapa.
- **Impacto:** dados inconsistentes em falhas parciais.

### AP-15 — Configuração acoplada ao código/ambiente
- **Severidade:** MEDIUM → playbook **PB-01**
- **Sinais:** porta, host, caminho/tipo do banco (`:memory:`, `loja.db`), URLs e limites fixos no código sem variável de ambiente; `app.run(host="0.0.0.0", debug=True)`.
- **Impacto:** não configurável por ambiente.

### AP-16 — Magic numbers e valores literais soltos
- **Severidade:** LOW → playbook **PB-13**
- **Sinais:** números/strings com regra de negócio embutida (`> 10000`, `0.05`, `cc.startsWith("4")`, `priority 1..5`, `len(x) < 3`, `'pending'` repetido, `"123456"` como senha padrão).
- **Impacto:** regra ilegível; mudança propensa a erro.

### AP-17 — Nomenclatura ruim, imports não usados e `print` como log
- **Severidade:** LOW → playbook **PB-13**
- **Sinais:** variáveis de 1–2 letras (`u`, `e`, `p`, `cc`, `cid`); imports/exports sem uso (`import os, sys, json`); `print`/`console.log` como logging; comentários obsoletos.
- **Impacto:** legibilidade, ruído.

### AP-18 — Escalonamento de privilégio por campos enviados em rotas anônimas
- **Severidade:** CRITICAL → playbook **PB-15**
- **Sinais:** cadastro público ou outra rota sem autorização lê `role`, `is_admin`, `permissions` ou campos equivalentes do corpo e os persiste/aplica diretamente ou via atribuição em massa.
- **Impacto:** qualquer cliente pode criar usuário administrador ou obter permissões elevadas.

---

## APIs deprecated / obsoletas (detecção obrigatória)

Reporte **somente APIs com depreciação documentada** pelo fornecedor da linguagem/framework/biblioteca, na versão em uso no projeto. Reporte como finding **LOW** (ou **MEDIUM** se houver risco de segurança/quebra iminente), recomendando o equivalente moderno (→ playbook **PB-14**).

> **Não são APIs deprecated** (não reporte como `DP-xx`): estilo antigo (`var`, callbacks, `type(x) == list`, `except:`), hash fraco (`md5`/`sha1` → é **AP-05**), `body-parser` (continua suportado), `debug=True` (é **AP-01/AP-15**). Esses casos entram nos anti-patterns correspondentes.

### DP-01 — Python
| API deprecated | Sinal | Substituta |
|---|---|---|
| `datetime.utcnow()` / `utcfromtimestamp()` (deprecated desde o Python 3.12) | grep `utcnow` | `datetime.now(timezone.utc)` |
| `Query.get()` / `Model.query.get(id)` (legado no SQLAlchemy 2.0) | grep `\.query\.get\(` | `db.session.get(Model, id)` |
| `flask.json.JSONEncoder`, `@app.before_first_request`, `flask.Markup`, `flask.escape` (removidos/deprecated no Flask 2.3+) | grep | APIs atuais do Flask 3.x |
| `imp`, `distutils`, `asyncio.get_event_loop()` sem loop em execução | grep | `importlib`, `setuptools`, `asyncio.run` |

### DP-02 — JavaScript / Node
| API deprecated | Sinal | Substituta |
|---|---|---|
| `new Buffer()` / `Buffer()` | grep | `Buffer.from()` / `Buffer.alloc()` |
| `crypto.createCipher` / `createDecipher` | grep | `crypto.createCipheriv` / `createDecipheriv` |
| `url.parse()`, `fs.exists`, `req.param()`, `res.send(status)`, `res.json(status, obj)` | grep | `new URL()`, `fs.access`, `req.params/query/body`, `res.sendStatus`, `res.status().json()` |
| `request` (lib), `node-uuid` | `package.json` | `fetch`/`axios`, `uuid` |

### DP-03 — Outras stacks (exemplos)
- Java: `Thread.stop`, `javax.*` em Jakarta EE 9+ → `jakarta.*`.
- PHP: `mysql_*`, `ereg`, `create_function` → PDO/`mysqli`, `preg_*`, closures.
- Go: `ioutil.*` → `io`/`os`. Ruby/Rails: `before_filter` → `before_action`.

Para stacks não listadas, consulte a documentação oficial de depreciação do framework detectado. Se nada for encontrado, registre `Deprecated APIs: none found` no relatório.