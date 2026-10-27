````text
================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask 3.0.0 (Flask-SQLAlchemy 3.1.1, SQLite)
Files:   15 analyzed | ~1160 lines of code

## Summary
CRITICAL: 3 | HIGH: 2 | MEDIUM: 6 | LOW: 4

## Findings

### [CRITICAL] Credenciais e segredos hardcoded (AP-01)
File: app.py:13,34, services/notification_service.py:9-10
Description: SECRET_KEY esta literal em app.py:13; email_user/email_password (SMTP) estao literais no __init__ de NotificationService (linhas 9-10); app.run(debug=True, host='0.0.0.0') fixo em app.py:34 expoe o console do debugger Werkzeug em todas as interfaces.
Impact: Vazamento de segredos no versionamento; debug ativo permite execucao remota de codigo.
Recommendation: Mover para config/settings lendo variaveis de ambiente, com debug desligado por padrao (playbook PB-01)

### [CRITICAL] Endpoints destrutivos/sensiveis sem autenticacao (AP-04)
File: routes/user_routes.py:119-122,124-125,134-151, routes/task_routes.py:225-238, routes/report_routes.py:211-223
Description: DELETE /users/<id> (apaga usuario e todas as tasks), DELETE /tasks/<id> e DELETE /categories/<id> nao checam identidade ou papel; PUT /users/<id> permite que qualquer cliente altere 'role' (promover a admin) e 'active'. Nao ha nenhum middleware de autenticacao.
Impact: Qualquer cliente anonimo destroi dados e escala privilegios.
Recommendation: Proteger por configuracao (flag/token de admin) preservando as rotas, sem remove-las (playbook PB-10)

### [CRITICAL] Senhas inseguras e token falso (AP-05)
File: models/user.py:21,29,32, routes/user_routes.py:85-86,129,207-210, routes/user_routes.py:33,40
Description: Senha armazenada com md5 sem salt (set_password/check_password). User.to_dict() inclui 'password' (hash), devolvido em POST /users, GET /users/<id>, PUT /users/<id> e /login. O login devolve token 'fake-jwt-token-' + id, que nao autentica nada e e previsivel.
Impact: Exposicao de hashes quebraveis trivialmente; autenticacao burlavel.
Recommendation: Remover 'password' das respostas; hash forte (werkzeug) com fallback para hash md5/legado no login; token assinado (itsdangerous) mantendo o campo 'token' (playbook PB-11)

### [HIGH] Logica de negocio nas rotas / sem camada de controllers (AP-07)
File: routes/task_routes.py:11-299, routes/user_routes.py:10-211, routes/report_routes.py:12-223, services/notification_service.py:4-48
Description: Todos os handlers fazem validacao, calculo (overdue, estatisticas, taxa de conclusao), acesso a dados (Model.query, db.session) e serializacao. Nao existem controllers; NotificationService nunca e importado/usado (codigo morto); models/task.py:38-60 define validate_status/validate_priority/is_overdue ignorados pelas rotas.
Impact: Regra nao reutilizavel nem testavel; viola MVC.
Recommendation: Criar controllers/ com a regra de negocio e deixar routes finas (playbook PB-04)

### [HIGH] Responsabilidade fora do lugar (AP-09)
File: routes/report_routes.py:157-223, routes/task_routes.py:17-28, routes/user_routes.py:15-23,162-169, utils/helpers.py:57-108
Description: CRUD de /categories vive em report_routes (blueprint 'reports'); serializacao de Task replicada manualmente nas rotas em vez de Task.to_dict(); validacao de entrada duplicada entre rotas, models e helpers.process_task_data (nao usado); utils contem regras de negocio de task.
Impact: Dificil localizar codigo; correcoes parciais.
Recommendation: Rotas/controller proprios para categories; serializacao unica no model; validacao centralizada (playbook PB-03/PB-04)

### [MEDIUM] Queries N+1 (AP-10)
File: routes/task_routes.py:41-57, routes/user_routes.py:22, routes/report_routes.py:55-56,163, routes/task_routes.py:281-287
Description: GET /tasks faz User.query.get e Category.query.get por task; GET /users usa len(u.tasks) por usuario; summary_report consulta tasks por usuario; GET /categories faz count() por categoria; task_stats carrega todas as tasks para contar atrasadas.
Impact: Numero de queries cresce com os dados.
Recommendation: Joins/eager loading (joinedload) e agregacoes GROUP BY/COUNT (playbook PB-06)

### [MEDIUM] Tratamento de erros duplicado, generico ou engolido (AP-11)
File: routes/task_routes.py:62,137,151-154,204,221-223,236, routes/user_routes.py:87-90,130,149, routes/report_routes.py:186,207,221, utils/helpers.py:46,49,88
Description: `except:` sem tipo e try/rollback repetido em cada handler; erros apenas via print; sem error handler central; handlers sem try (ex.: task_routes.py:85-154 antes do commit) retornam 500 HTML do Flask.
Impact: Formatos de erro inconsistentes, diagnostico dificil, captura indevida de KeyboardInterrupt.
Recommendation: Error handler centralizado e excecoes especificas (playbook PB-07)

### [MEDIUM] Validacao de entrada ausente ou inconsistente (AP-12)
File: routes/task_routes.py:96,113,167,182,203,261,264, routes/report_routes.py:196-202,180, routes/user_routes.py:103,125
Description: priority comparado direto (`priority < 1`) sem checar tipo -> 500 com string; int(priority)/int(user_id) em /tasks/search sem tratamento -> 500; len(title) sem checar string; request.get_json() sem checar None em update_category; color de categoria nao validado (is_valid_color existe e nao e usado); 'active' e 'name' sem validacao.
Impact: Erros 500 no lugar de 400; dados invalidos persistidos.
Recommendation: Camada de validacao unica retornando 400 (playbook PB-08)

### [MEDIUM] Duplicacao de regra de negocio e codigo morto (AP-13)
File: routes/task_routes.py:30-39,71-80,283-287, routes/user_routes.py:171-180, routes/report_routes.py:34-43,132-135, models/task.py:50-60, utils/helpers.py:9-55,57-108
Description: Regra de "atrasada" copiada em 6 locais apesar de Task.is_overdue existir; lista de status validos repetida (models/task.py:39, helpers.py:75,110, task_routes.py:110,177); helpers format_date, calculate_percentage (importado mas nao usado), validate_email (regex repetida em user_routes.py:61,106), generate_id, sanitize_string e constantes VALID_*/MIN_*/MAX_* sem uso.
Impact: Multiplas fontes de verdade.
Recommendation: Usar Task.is_overdue e constantes centralizadas; remover codigo morto (playbook PB-09)

### [MEDIUM] Operacoes sem transacao/integridade referencial (AP-14)
File: routes/user_routes.py:140-151, routes/report_routes.py:217-220
Description: delete_user apaga tasks em laco e depois o usuario (so funciona pelo commit unico, sem cascade declarado); delete_category remove a categoria deixando tasks com category_id orfao (SQLite nao aplica FK por padrao).
Impact: Dados orfaos/inconsistentes.
Recommendation: Cascade no relationship ou limpar category_id na mesma transacao (playbook PB-12)

### [MEDIUM] Configuracao acoplada ao codigo (AP-15)
File: app.py:11-13,34
Description: URI do banco 'sqlite:///tasks.db', host 0.0.0.0 e porta 5000 fixos; python-dotenv esta no requirements mas nao e usado.
Impact: Nao configuravel por ambiente.
Recommendation: config/ com variaveis de ambiente e defaults (playbook PB-01)

### [LOW] Magic numbers e literais soltos (AP-16)
File: routes/task_routes.py:96,99,110,113,177,182, routes/user_routes.py:64,71,115,120, routes/report_routes.py:24-28,45,129,180, models/task.py:12,39,46, seed.py:19,26,33
Description: limites de titulo (3/200), prioridade (1..5), senha minima (4), dias (7), prioridade alta (<=2), cor padrao '#000000', status e roles como strings repetidas; constantes existem em utils/helpers.py:110-116 mas nao sao usadas.
Impact: Regras ilegiveis e propensas a erro.
Recommendation: Constantes nomeadas centralizadas (playbook PB-13)

### [LOW] Nomes ruins, imports nao usados e print como log (AP-17)
File: app.py:7, routes/task_routes.py:1,7,149,153,219,234, routes/user_routes.py:6,83,89,147, routes/report_routes.py:1,7,8, models/task.py:3, utils/helpers.py:3-7,39-41, services/notification_service.py:21,24
Description: imports sem uso (os, sys, json, time, hashlib, math, request, format_date etc.); print() usado como log; variaveis de 1 letra (t, u, c, p, p1..p5, cat).
Impact: Ruido e legibilidade.
Recommendation: Usar logging, remover imports e renomear (playbook PB-13)

### [LOW] API deprecated: datetime.utcnow() (DP-01)
File: models/category.py:11, models/task.py:15,16,52, models/user.py:14, services/notification_service.py:35, utils/helpers.py:38, routes/task_routes.py:31,72,215,285, routes/user_routes.py:172, routes/report_routes.py:35,42,45,71,133, seed.py:66,67,69,70,74
Description: datetime.utcnow() e deprecated desde o Python 3.12.
Impact: DeprecationWarning e quebra futura.
Recommendation: datetime.now(timezone.utc) (naive para manter compatibilidade com o banco existente) (playbook PB-14)

### [LOW] API deprecated: Model.query.get() (DP-01)
File: routes/task_routes.py:42,51,67,117,122,158,188,195,227, routes/user_routes.py:29,94,136,155, routes/report_routes.py:105,192,213
Description: Query.get() e legado no SQLAlchemy 2.0 (Flask-SQLAlchemy 3.1).
Impact: LegacyAPIWarning; remocao futura.
Recommendation: db.session.get(Model, id) (playbook PB-14)

================================
Total: 15 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
````
