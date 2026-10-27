================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1 (flask-cors 5.0.1, SQLite)
Files:   4 analyzed | ~780 lines of code

## Summary
CRITICAL: 5 | HIGH: 3 | MEDIUM: 6 | LOW: 2

## Findings

### [CRITICAL] SQL Injection (AP-02)
File: models.py:28,47-50,57-61,68,92,109-111,126-129,140,148-151,155,157-166,174,188,192,220,224,280,289-297
Description: Todas as queries de models.py são montadas por concatenação de strings (ex.: `"SELECT * FROM produtos WHERE id = " + str(id)`, login com `email = '" + email + "' AND senha = '" + senha + "'`, busca com `LIKE '%" + termo + "%'`, INSERT/UPDATE de produtos e usuários, `UPDATE pedidos SET status = '" + novo_status + "'`). Nenhum placeholder `?` é usado.
Impact: Bypass de login, leitura/alteração/remoção arbitrária de dados por qualquer cliente.
Recommendation: Usar queries parametrizadas (`cursor.execute(sql, params)`) em todos os models (playbook PB-02)

### [CRITICAL] Endpoints administrativos/destrutivos sem autenticação (AP-04)
File: app.py:47-57, app.py:59-78
Description: `POST /admin/reset-db` apaga itens_pedido, pedidos, produtos e usuários; `POST /admin/query` executa SQL arbitrário recebido em `dados.get("sql")` (também sem checar `dados is None`). Nenhuma verificação de identidade ou papel.
Impact: Qualquer cliente pode destruir ou exfiltrar todo o banco.
Recommendation: Proteger por configuração (flag/token via variável de ambiente, desabilitado por padrão para o SQL arbitrário) sem remover as rotas, e mover para controller/model (playbook PB-10)

### [CRITICAL] Senhas em texto puro e expostas na API (AP-05)
File: database.py:75-79, models.py:83,99,109-111,126-129, controllers.py:176-180
Description: Senhas gravadas em claro (seed "admin123" etc. e `criar_usuario`), comparadas diretamente no SQL (`AND senha = '...'`), e `senha` retornada em `get_todos_usuarios` (GET /usuarios) e `get_usuario_por_id` (GET /usuarios/<id>). Login não emite token, apenas devolve o usuário.
Impact: Exposição direta de credenciais de todos os usuários.
Recommendation: Hash com salt (werkzeug.security) mantendo compatibilidade com senhas legadas em texto puro, e remover `senha` das respostas (playbook PB-11)

### [CRITICAL] Credenciais/segredos hardcoded e debug fixo (AP-01)
File: app.py:7,8,88, controllers.py:286-289
Description: `SECRET_KEY` literal em app.py:7; `DEBUG = True` e `debug=True` com `host="0.0.0.0"` fixos (console interativo do Werkzeug exposto); o endpoint `/health` devolve `secret_key` e `debug` na resposta JSON.
Impact: Vazamento do segredo no código e na API; execução remota de código via debugger em produção.
Recommendation: Ler segredo/debug de variáveis de ambiente em `config/` e remover segredos da resposta de /health (playbook PB-01)

### [CRITICAL] God Module: arquitetura monolítica sem separação de camadas (AP-03)
File: models.py:1-314, app.py:1-88, database.py:1-86
Description: models.py mistura acesso a dados, regra de negócio (estoque e total em `criar_pedido`, desconto escalonado em `relatorio_vendas`), serialização e 4 domínios (produtos, usuários, pedidos, relatórios). database.py mistura conexão, DDL e seed. app.py mistura roteamento, rotas inline e SQL direto (admin).
Impact: Impossível testar isoladamente; qualquer mudança afeta tudo.
Recommendation: Separar em config/, models/ por entidade, controllers/ por domínio, routes/ e middlewares/ (playbook PB-03)

### [HIGH] Lógica de negócio e acesso a dados nos controllers / camada de regra ausente (AP-07)
File: controllers.py:43-54,87-90,208-210,247-250,264-290
Description: Validação de domínio (preço, estoque, nome, lista `categorias_validas`), notificações (email/SMS/push via print) e transição de status ficam nos handlers; `health_check` importa `get_db` e executa SQL diretamente no controller (controllers.py:3,266-274). Regras de pedido/desconto estão no model, não em serviço/controller.
Impact: Viola MVC; regra não reutilizável nem testável.
Recommendation: Mover regra de negócio para controllers/services finos e deixar models apenas com dados (playbook PB-04)

### [HIGH] Estado global mutável e acoplamento sem injeção de dependência (AP-08)
File: database.py:4-5,8-10,86, models.py:1,5,25,44,55,66,73,90,106,123,134,172,204,236,276,286, controllers.py:3,266
Description: `db_connection = None` é global mutável modificado via `global`; cada função de model chama `get_db()` do módulo e uma única conexão `check_same_thread=False` é compartilhada entre requisições; DDL/seed rodam dentro de `get_db()`.
Impact: Acoplamento oculto, efeito entre requisições, testes inviáveis.
Recommendation: Criar conexão por requisição/factory e init de schema separado no composition root (playbook PB-05)

### [HIGH] Responsabilidades fora do lugar (AP-09)
File: app.py:32-78, models.py:12-21,31-40,79-86,235-273, controllers.py:264-290
Description: Rotas admin com SQL dentro do entry point; roteamento em app.py misturado com `index`; models fazem serialização para dict manualmente e cálculo de relatório/desconto; controller faz health check com SQL.
Impact: Código difícil de localizar e manter.
Recommendation: Entry point apenas monta a app; mover cada responsabilidade à camada correta (playbook PB-03/PB-04)

### [MEDIUM] Queries N+1 e consultas em laço (AP-10)
File: models.py:139-141,154-156,187-193,219-225
Description: `criar_pedido` consulta produto dentro de dois laços; `get_pedidos_usuario` e `get_todos_pedidos` executam uma query de itens por pedido e outra de produto por item.
Impact: Número de queries cresce com pedidos e itens.
Recommendation: Usar JOIN/consultas em lote (playbook PB-06)

### [MEDIUM] Tratamento de erros duplicado, genérico e que vaza detalhes (AP-11)
File: controllers.py:10-12,21-22,60-62,95-96,108-109,125-126,133-134,143-144,164-165,185-186,218-220,226-227,234-235,254-255,261-262,291-292, app.py:77-78
Description: Cada handler repete `try/except Exception as e: return jsonify({"erro": str(e)}), 500`, devolvendo mensagem interna ao cliente; não há error handler central.
Impact: Vaza detalhes internos e duplica código.
Recommendation: Error handler central em middlewares/ com resposta JSON padronizada (playbook PB-07)

### [MEDIUM] Validação de entrada ausente ou inconsistente (AP-12)
File: controllers.py:43-46,87-90,119-121,169-171,195-206,239-243, app.py:61-62
Description: `request.get_json()` usado sem checar None em `login`, `atualizar_status_pedido` e `/admin/query`; `preco < 0` / `estoque < 0` sem validar tipo (string causa 500); `float()` sem tratamento; itens do pedido sem validar `produto_id`/`quantidade`; `atualizar_produto` não valida nome/categoria como a criação.
Impact: 500 em vez de 400; dados inválidos persistidos.
Recommendation: Centralizar validação de entrada (playbook PB-08)

### [MEDIUM] Duplicação de regra de negócio e código morto (AP-13)
File: models.py:12-21,31-40,304-313, models.py:178-199,211-232, models.py:79-86,95-102, controllers.py:24-58,64-93, models.py:2
Description: Dicionário de produto repetido 3x, de usuário 2x, de pedido (com itens) 2x; validações de produto duplicadas entre criar/atualizar; `import sqlite3` sem uso em models.py.
Impact: Duas fontes de verdade; correção parcial de bugs.
Recommendation: Extrair serializers/helpers comuns (playbook PB-09)

### [MEDIUM] Operações multi-etapa sem transação e sem integridade referencial (AP-14)
File: models.py:133-169,65-70, database.py:36-53, app.py:51-55
Description: `criar_pedido` faz várias escritas sem try/rollback (validação de estoque antes e baixa depois, sem atomicidade); `deletar_produto` deixa itens_pedido órfãos; tabelas sem FOREIGN KEY; reset-db apaga em passos. Cancelar pedido apenas imprime "Devolver estoque" (controllers.py:250) sem devolver.
Impact: Dados inconsistentes em falhas parciais.
Recommendation: Transação com rollback e FKs (playbook PB-12)

### [MEDIUM] Configuração acoplada ao código (AP-15)
File: database.py:5, app.py:85,88, controllers.py:285-288
Description: Caminho do banco `loja.db`, host `0.0.0.0`, porta 5000, versão e ambiente "producao" fixos no código.
Impact: Não configurável por ambiente.
Recommendation: Módulo config/ lendo variáveis de ambiente (playbook PB-01)

### [LOW] Magic numbers e valores literais soltos (AP-16)
File: models.py:257-262, controllers.py:47-50,52,242, database.py:76-78
Description: Faixas e percentuais de desconto (10000/0.1, 5000/0.05, 1000/0.02), limites de nome (2/200), categorias e status válidos como literais, `'pendente'`/`'aprovado'` repetidos.
Impact: Regra ilegível; mudança propensa a erro.
Recommendation: Constantes nomeadas (playbook PB-13)

### [LOW] Nomenclatura ruim, imports não usados e print como log (AP-17)
File: controllers.py:8,11,57,61,106,161,179,182,208-210,219,248,250, app.py:56,83-86, database.py:2, models.py:2
Description: `print` usado como logging e como "envio" de email/SMS/push; `import os` sem uso em database.py; `import sqlite3` sem uso em models.py; variáveis `id` (shadow de builtin), `db`, `row`.
Impact: Ruído e baixa legibilidade.
Recommendation: Usar `logging`, remover imports mortos e renomear (playbook PB-13)

Deprecated APIs: none found

================================
Total: 16 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
