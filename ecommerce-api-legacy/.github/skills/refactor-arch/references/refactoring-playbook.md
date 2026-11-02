# Playbook de Refatoração (Fase 3)

Padrões concretos de transformação. Cada padrão tem **Antes / Depois**; os exemplos usam Python/Flask e Node/Express, mas a **ideia** vale para qualquer stack: traduza para a linguagem detectada. Aplique na ordem: PB-01 → PB-02 → PB-11 → PB-03 → PB-04 → PB-05 → PB-06 → PB-08 → PB-09 → PB-12 → PB-07 → PB-10 → PB-13 → PB-14 → PB-15.

---

## PB-01 — Extrair configuração e segredos (AP-01, AP-06, AP-15)

**Antes** (Python)
```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
app.config["DEBUG"] = True
```
**Depois**
```python
# config/settings.py
import os
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"
DB_PATH = os.environ.get("DB_PATH", "loja.db")
PORT = int(os.environ.get("PORT", "5000"))
```
**Antes** (Node)
```js
const config = { dbPass: "senha_super_secreta_prod_123", paymentGatewayKey: "pk_live_123", port: 3000 };
console.log(`Processando cartão ${cc} na chave ${config.paymentGatewayKey}`);
```
**Depois**
```js
// config/index.js
module.exports = {
  port: Number(process.env.PORT) || 3000,
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
  dbFile: process.env.DB_FILE || ':memory:',
};
// no serviço: log sem dados sensíveis
logger.info(`Processando pagamento do curso ${courseId}`);
```
Regras: crie `.env.example`; nunca logue/retorne segredos nem dados de cartão (mascare: `****1234`); remova segredos de respostas como `/health`.

---

## PB-02 — Queries parametrizadas (AP-02)

**Antes**
```python
cursor.execute("SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'")
```
**Depois**
```python
cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
```
Para filtros dinâmicos, monte a lista de condições fixas e uma lista separada de parâmetros:
```python
sql, params = "SELECT * FROM produtos WHERE 1=1", []
if termo:
    sql += " AND (nome LIKE ? OR descricao LIKE ?)"; params += [f"%{termo}%"] * 2
cursor.execute(sql, params)
```
Em ORM: use filtros do ORM (`Model.title.like(...)`, `filter_by`) — nunca `text()` concatenado.

---

## PB-03 — Quebrar God Class/Module em camadas (AP-03, AP-09)

**Antes**
```js
class AppManager {            // banco + schema + rotas + checkout + relatório + hashing
  constructor() { this.db = new sqlite3.Database(':memory:'); }
  initDb() { /* DDL + seed */ }
  setupRoutes(app) { app.post('/api/checkout', ...); app.get('/api/admin/financial-report', ...); }
}
```
**Depois**
```text
src/database/connection.js  src/database/schema.js
src/models/{userModel,courseModel,enrollmentModel,paymentModel}.js
src/services/{checkoutService,reportService}.js
src/controllers/{checkoutController,adminController,userController}.js
src/routes/index.js         src/app.js (composition root)
```
Procedimento: 1) liste as responsabilidades do arquivo; 2) crie um arquivo por responsabilidade/domínio; 3) mova o código sem mudar comportamento; 4) ajuste imports; 5) apague o arquivo original.

---

## PB-04 — Mover lógica de negócio da rota para o controller/service (AP-07)

**Antes** (Python)
```python
@task_bp.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    if len(data.get('title','')) < 3: return jsonify({'error': 'Título muito curto'}), 400
    task = Task(); task.title = data['title']; db.session.add(task); db.session.commit()
    return jsonify(task.to_dict()), 201
```
**Depois**
```python
# views/task_routes.py
task_bp.add_url_rule('/tasks', view_func=task_controller.create_task, methods=['POST'])

# controllers/task_controller.py
def create_task():
    payload = request.get_json(silent=True) or {}
    data = validate_task_payload(payload)          # lança ValidationError
    task = Task.create(**data)                     # model persiste
    return jsonify(task.to_dict()), 201
```
Rota só mapeia; controller orquestra; model persiste. Para callbacks aninhados em Node, extraia um **service** com `async/await`:
```js
async function checkout({ name, email, password, courseId, card }) {
  const course = await courseModel.findActive(courseId);
  if (!course) throw new NotFoundError('Curso não encontrado');
  const user = (await userModel.findByEmail(email)) ?? await userModel.create(...);
  await paymentGateway.charge(card, course.price);
  return enrollmentModel.enroll(user.id, course.id);
}
```

---

## PB-05 — Eliminar estado global e aplicar injeção de dependência (AP-08)

**Antes**
```python
db_connection = None
def get_db():
    global db_connection
    if db_connection is None: db_connection = sqlite3.connect("loja.db")
    return db_connection
```
**Depois**
```python
# models/database.py
class Database:
    def __init__(self, path): self._conn = sqlite3.connect(path, check_same_thread=False); self._conn.row_factory = sqlite3.Row
    def connection(self): return self._conn

# app.py (composition root)
db = Database(settings.DB_PATH)
app.extensions["db"] = db      # ou passar por construtor: ProdutoModel(db)
```
Node: `module.exports = { globalCache, totalRevenue }` → remover; se cache for necessário, uma classe `Cache` instanciada no composition root e injetada no service. Regra: nenhuma dependência é criada dentro de handlers; ela chega por construtor/parâmetro. Em ORMs com sessão global (ex.: Flask-SQLAlchemy), a sessão continua global, mas **controllers não a usam**: exponha `save()`/`remove()`/consultas nomeadas no model (ex.: `Task.list_overdue(now)`, `user.save()`).

---

## PB-06 — Eliminar N+1 com JOIN/eager loading/IN (AP-10)

**Antes**
```python
for pedido in pedidos:
    itens = cursor.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(pedido["id"]))
    for item in itens:
        prod = cursor.execute("SELECT nome FROM produtos WHERE id = " + str(item["produto_id"]))
```
**Depois**
```python
rows = cursor.execute("""
  SELECT p.id, p.usuario_id, p.status, p.total, p.criado_em,
         i.produto_id, i.quantidade, i.preco_unitario, pr.nome AS produto_nome
  FROM pedidos p
  LEFT JOIN itens_pedido i ON i.pedido_id = p.id
  LEFT JOIN produtos pr ON pr.id = i.produto_id""").fetchall()
# agrupar por p.id em um dict -> 1 query
```
ORM: `Task.query.options(joinedload(Task.user), joinedload(Task.category))`; contagens agregadas com `GROUP BY` ou `func.count`; relatórios em Node com uma query `JOIN` em vez de callbacks aninhados.

---

## PB-07 — Error handler centralizado (AP-11)

**Antes**
```python
def listar_produtos():
    try: ...
    except Exception as e: return jsonify({"erro": str(e)}), 500    # repetido em toda função
```
**Depois**
```python
# middlewares/error_handler.py
class AppError(Exception): status = 500
class NotFoundError(AppError): status = 404
class ValidationError(AppError): status = 400

def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(e): return jsonify({"erro": str(e), "sucesso": False}), e.status
    @app.errorhandler(Exception)
    def handle_unexpected(e):
        app.logger.exception("Erro não tratado")
        return jsonify({"erro": "Erro interno do servidor", "sucesso": False}), 500
```
Node:
```js
app.use((err, req, res, next) => {
  logger.error(err);
  res.status(err.status || 500).json({ error: err.status ? err.message : 'Erro interno' });
});
```
Troque `except:` por tipos específicos e mantenha `rollback` onde há transação.

---

## PB-08 — Validação de entrada centralizada (AP-12)

**Antes**
```python
dados = request.get_json()           # None quebra o handler
if dados['priority'] < 1: ...        # string → TypeError → 500
```
**Depois**
```python
def parse_json():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict): raise ValidationError("Dados inválidos")
    return payload

def parse_int(value, field, minimum, maximum):
    try: n = int(value)
    except (TypeError, ValueError): raise ValidationError(f"{field} inválido")
    if not minimum <= n <= maximum: raise ValidationError(f"{field} deve estar entre {minimum} e {maximum}")
    return n
```
Mantenha as **mesmas mensagens e status** das validações originais.

---

## PB-09 — Remover duplicação e reaproveitar o model (AP-13)

**Antes** (regra repetida em 6 rotas)
```python
if t.due_date:
    if t.due_date < datetime.utcnow():
        if t.status != 'done' and t.status != 'cancelled': overdue = True
```
**Depois**
```python
# models/task.py
def is_overdue(self):
    return bool(self.due_date and self.due_date < utcnow() and self.status not in TERMINAL_STATUSES)
# uso: data['overdue'] = task.is_overdue()
```
Idem para serialização duplicada: um único `to_dict()`; apague helpers/constantes/imports sem referência (verifique com busca antes).

---

## PB-10 — Proteger endpoints administrativos/destrutivos sem removê-los (AP-04)

**Antes**
```python
@app.route("/admin/query", methods=["POST"])
def executar_query(): cursor.execute(request.get_json()["sql"])
```
**Depois**
```python
# middlewares/auth.py
def admin_required(fn):
    @wraps(fn)
    def wrapper(*a, **kw):
        configured = settings.ADMIN_TOKEN
        if not configured or not hmac.compare_digest(request.headers.get("X-Admin-Token", ""), configured):
            raise ForbiddenError("Acesso negado")     # 403
        return fn(*a, **kw)
    return wrapper
# views: bp.add_url_rule("/admin/query", view_func=admin_required(controller.run_query), methods=["POST"])
```
Regras (classifique cada endpoint antes de proteger):
- **Perigoso por natureza** (executa SQL/comando arbitrário recebido no body, apaga o banco inteiro): **não remova a rota**; proteja-a com token da config e desabilite por padrão (flag de ambiente). Sem token válido responde 403.
- **Parte do fluxo funcional da API** (listado no README/`api.http`/testes, ex.: relatório administrativo, exclusão de entidade): ela **deve continuar respondendo exatamente como antes na configuração padrão de desenvolvimento**. Aplique um middleware de token (`ADMIN_TOKEN`, comparação em tempo constante) que: (a) valida o token quando ele está configurado; (b) bloqueia (403) em produção (`NODE_ENV/APP_ENV=production`) se o token não estiver configurado; (c) fora de produção, sem token configurado, deixa passar e registra um aviso em log. **Nunca desabilite por padrão uma rota do fluxo funcional** — isso quebraria o contrato.
- **Fora do escopo:** autenticação/autorização completa de todas as rotas (login com sessão, RBAC). Registre como recomendação em `Remaining findings`.

---

## PB-11 — Hash de senha seguro, compatível com dados legados e sem vazamento (AP-05)

**Antes**
```python
self.password = hashlib.md5(pwd.encode()).hexdigest()      # ou senha em texto puro
def to_dict(self): return {..., 'password': self.password}
```
**Depois**
```python
from werkzeug.security import generate_password_hash, check_password_hash
def set_password(self, pwd): self.password = generate_password_hash(pwd)
def check_password(self, pwd):
    if is_legacy(self.password):                  # texto puro ou hash antigo (MD5/SHA1)
        return legacy_matches(self.password, pwd)
    return check_password_hash(self.password, pwd)
# no login bem-sucedido com senha legada: regravar com set_password(pwd)
def to_dict(self): return {'id': self.id, 'name': self.name, 'email': self.email, 'role': self.role}  # sem password
```
Node: `crypto.scrypt` com salt (+ `timingSafeEqual`) em vez de `badCrypto`.

**Compatibilidade obrigatória:** um banco criado pela versão original (senhas em texto puro ou MD5) deve continuar permitindo login; aceite o formato legado e **regrave o hash novo no login**. Seeds novos usam o formato novo.

Campos sensíveis (`password`, `senha`, `secret_key`) saem das respostas — registre isso como mudança intencional. Token de sessão falso (`'fake-jwt-token-' + id`): substitua por token assinado com a `SECRET_KEY` da config (ex.: `itsdangerous`/JWT), mantendo a chave `token` na resposta; não crie novas regras de autorização.

---
## PB-12 — Transações e integridade referencial (AP-14)

**Antes**
```python
cursor.execute("INSERT INTO pedidos ..."); cursor.execute("INSERT INTO itens_pedido ..."); cursor.execute("UPDATE produtos ...")
db.commit()   # sem rollback em falha parcial
```
**Depois**
```python
try:
    cursor.execute("INSERT INTO pedidos ... VALUES (?, ?, ?)", (...))
    ...
    db.commit()
except Exception:
    db.rollback(); raise
```
Node: `DELETE` de usuário → remover/anular também matrículas e pagamentos dentro de uma transação (`BEGIN/COMMIT/ROLLBACK`) ou `ON DELETE CASCADE`.

---

## PB-13 — Constantes nomeadas, nomes claros e logging (AP-16, AP-17)

**Antes**
```python
if faturamento > 10000: desconto = faturamento * 0.1
```
```js
let u = req.body.usr; let cc = req.body.card;
```
**Depois**
```python
DISCOUNT_TIERS = [(10000, 0.10), (5000, 0.05), (1000, 0.02)]   # config/constants.py
desconto = next((faturamento * rate for limit, rate in DISCOUNT_TIERS if faturamento > limit), 0)
```
```js
const { usr: userName, eml: email, pwd: password, c_id: courseId, card: cardNumber } = req.body;
```
Troque `print`/`console.log` por `logging`/logger; remova imports e exports sem uso; mantenha as chaves externas do JSON/payload (só renomeie variáveis internas).

---

## PB-14 — Substituir APIs deprecated (DP-01..DP-03)

**Antes**
```python
datetime.utcnow()
Task.query.get(task_id)
```
```js
const b = new Buffer(str); var x = 1;
```
**Depois**
```python
from datetime import datetime, timezone
datetime.now(timezone.utc)              # se o banco guarda naive UTC, use .replace(tzinfo=None) para manter o formato
db.session.get(Task, task_id)
```
```js
const b = Buffer.from(str); const x = 1;
```
Após substituir, rode a aplicação e confira que os warnings de depreciação desapareceram e que o formato das datas nas respostas **não mudou**.

---

## PB-15 — Ignorar privilégios enviados por rotas anônimas (AP-18)

**Antes**
```python
role = request.get_json().get("role", DEFAULT_ROLE)
user = User(name=name, email=email, role=role)
```
**Depois**
```python
# Cadastro público: o corpo não pode escolher privilégios.
user = User(name=name, email=email, role=DEFAULT_ROLE)
```
Em qualquer rota anônima, descarte campos de privilégio do corpo (`role`, `is_admin`, `permissions` e equivalentes) e atribua o menor privilégio no servidor. Não basta validar se o valor recebido pertence a uma lista de papéis válidos. Se a aplicação tiver um fluxo legítimo de criação privilegiada, exija autorização verificada no servidor antes de aplicar o papel; nunca use o corpo anônimo como fonte de autorização. Adicione um teste sem token que tente solicitar papel elevado e confirme que o recurso criado permanece no papel padrão.

---

## Mapa anti-pattern → padrão

| Anti-pattern | Padrão |
|---|---|
| AP-01, AP-06, AP-15 | PB-01 |
| AP-02 | PB-02 |
| AP-03, AP-09 | PB-03 |
| AP-07 | PB-04 |
| AP-08 | PB-05 |
| AP-10 | PB-06 |
| AP-11 | PB-07 |
| AP-12 | PB-08 |
| AP-13 | PB-09 |
| AP-04 | PB-10 |
| AP-05 | PB-11 |
| AP-14 | PB-12 |
| AP-16, AP-17 | PB-13 |
| DP-01..03 | PB-14 |
| AP-18 | PB-15 |
