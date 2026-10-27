# Análise de Projeto — Heurísticas de Detecção (Fase 1)

Objetivo: descobrir **linguagem, framework, banco, domínio e arquitetura** sem assumir nada previamente. Use sempre evidência (arquivo + trecho), nunca suposição.

## 1. Linguagem

| Evidência | Linguagem |
|---|---|
| `*.py`, `requirements.txt`, `pyproject.toml`, `Pipfile` | Python |
| `*.js`/`*.mjs`/`*.cjs`, `package.json` | JavaScript / Node.js |
| `*.ts`, `tsconfig.json` | TypeScript |
| `*.java`, `pom.xml`, `build.gradle` | Java |
| `*.cs`, `*.csproj` | C# / .NET |
| `*.go`, `go.mod` | Go |
| `*.php`, `composer.json` | PHP |
| `*.rb`, `Gemfile` | Ruby |
| `*.rs`, `Cargo.toml` | Rust |

Quando há mais de uma, a linguagem da aplicação é a do **entry point** e das rotas; as demais são tooling.

## 2. Framework e versão

Leia o manifesto de dependências (a versão pode vir de `==`, `^`, `~` ou do lockfile) e **confirme pelos imports** no código.

| Manifesto/Import | Framework |
|---|---|
| `flask` / `from flask import Flask` | Flask |
| `fastapi` / `FastAPI(` | FastAPI |
| `django` / `manage.py`, `settings.py` | Django |
| `express` / `require('express')` | Express |
| `@nestjs/core` | NestJS |
| `koa`, `fastify`, `hapi` | respectivo |
| `spring-boot-starter-web` / `@RestController` | Spring Boot |
| `gin-gonic/gin`, `net/http` | Gin / stdlib Go |
| `laravel/framework` | Laravel |
| `rails` | Rails |

Dependências de interesse: ORM/driver (`flask-sqlalchemy`, `sqlalchemy`, `sqlite3`, `sequelize`, `prisma`, `typeorm`, `psycopg2`, `mysql`), CORS, auth (`jwt`, `bcrypt`), validação (`marshmallow`, `pydantic`, `joi`), HTTP clients.

## 3. Banco de dados

1. Driver/ORM nos imports (`sqlite3`, `sqlalchemy`, `pg`, `mysql2`, `mongoose`...).
2. String de conexão: arquivo `*.db` / `sqlite:///` / `:memory:` / `postgres://` (em **config** ou **hardcoded**).
3. Tabelas/entidades: `CREATE TABLE ...` (DDL), classes que herdam de `db.Model` / `Model` / `@Entity`, schemas, migrations.
4. Seed de dados: `INSERT` iniciais, `seed.*`.
5. Liste nomes de tabelas e relações principais (FK).

## 4. Domínio da aplicação

Deduza de: nomes de tabelas/entidades, nomes de rotas, README e mensagens de resposta. Descreva em uma linha objetiva (ex.: "API de e-commerce: produtos, pedidos e usuários").

## 5. Mapeamento de arquitetura

Para cada arquivo de código registre a(s) **responsabilidade(s) real(is)** e classifique:

| Papel | Sinais |
|---|---|
| Entry point | `app.run`, `app.listen`, `main()`, `createApp`, WSGI app |
| Rotas/Views | `@app.route`, `Blueprint`, `router.get`, `app.post`, `add_url_rule`, `@GetMapping` |
| Controllers | funções/classes que recebem request e orquestram o fluxo |
| Services/regra de negócio | cálculo, validação de domínio, orquestração entre entidades |
| Models/acesso a dados | SQL, ORM, `cursor.execute`, `db.run`, `Model.query` |
| Config | variáveis, constantes de ambiente, chaves, portas |
| Utils/helpers | funções utilitárias sem estado |
| Middlewares/erros | `errorhandler`, `app.use((err,...))`, interceptors |

Classifique a arquitetura atual em uma destas categorias (e descreva o que existe):

- **Monolítica / sem camadas**: poucos arquivos, SQL + regra + rota misturados; ou um único arquivo/classe "Deus".
- **Parcialmente em camadas**: existem pastas `models/routes/services/utils`, mas há lógica de negócio nas rotas, services ausentes/não usados, regras duplicadas, sem controllers.
- **MVC adequado**: camadas com responsabilidades corretas (só nesse caso a Fase 3 se limita aos problemas de código).

Também levante: **endpoints** (método + caminho + arquivo:linha), pontos de entrada de dados externos, uso de estado global, onde ficam os segredos.

## 6. Contagem de arquivos

Conte apenas código-fonte da aplicação (exclua dependências, lockfiles, bancos, caches, `__init__.py` vazios podem ser contados ou não — **seja consistente e informe**). Informe `N files analyzed`.
