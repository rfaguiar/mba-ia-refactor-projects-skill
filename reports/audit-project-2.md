================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript (Node.js) + Express 4.18 + sqlite3
Files:   3 analyzed | ~180 lines of code

## Summary
CRITICAL: 5 | HIGH: 2 | MEDIUM: 6 | LOW: 2

## Findings

### [CRITICAL] Credenciais e segredos hardcoded (AP-01)
File: src/utils.js:1-7
Description: O objeto `config` contém literais para `dbUser`, `dbPass`, `paymentGatewayKey` (chave `pk_live_`) e `smtpUser`, além de `port` fixo.
Impact: Segredos de produção vão para o versionamento e ficam expostos a qualquer pessoa com acesso ao código.
Recommendation: Ler segredos de variáveis de ambiente em um módulo `config/` com defaults seguros e sem valores reais (playbook PB-01)

### [CRITICAL] Dados sensíveis em logs (AP-06)
File: src/AppManager.js:45
Description: `console.log` imprime o número completo do cartão (`cc`) e a chave do gateway (`config.paymentGatewayKey`) a cada checkout.
Impact: Violação PCI/LGPD; vazamento de dados de cartão e de segredo via logs.
Recommendation: Remover o log de dados sensíveis; logar apenas eventos sem PAN/chave (playbook PB-01)

### [CRITICAL] Endpoints administrativos/destrutivos sem autenticação (AP-04)
File: src/AppManager.js:80-129, src/AppManager.js:131-137
Description: `GET /api/admin/financial-report` expõe nomes de alunos e receita sem nenhuma checagem de identidade; `DELETE /api/users/:id` apaga qualquer usuário sem autenticação.
Impact: Qualquer cliente exfiltra dados financeiros ou apaga usuários.
Recommendation: Proteger os endpoints por middleware configurável (ex.: token de admin via variável de ambiente), sem remover as rotas (playbook PB-10)

### [CRITICAL] Senhas armazenadas de forma insegura (AP-05)
File: src/utils.js:17-23, src/AppManager.js:18,68
Description: `badCrypto` é um "hash" caseiro (base64 repetido e truncado em 10 caracteres, 10000 iterações inúteis), usado em AppManager.js:68 com senha padrão `"123456"` quando `pwd` não é enviada; o seed (linha 18) grava a senha em texto puro.
Impact: Credenciais facilmente reversíveis/adivinháveis; autenticação burlável.
Recommendation: Usar hash com salt (scrypt/bcrypt) mantendo compatibilidade com valores legados e remover a senha padrão (playbook PB-11)

### [CRITICAL] God Class / God Module (AP-03)
File: src/AppManager.js:4-139
Description: `AppManager` mistura criação de conexão e DDL/seed (`initDb`), roteamento (`setupRoutes`), regra de checkout/pagamento, relatório financeiro e exclusão de usuário, cobrindo vários domínios (users, courses, enrollments, payments, audit).
Impact: Impossível testar isoladamente; qualquer mudança afeta tudo.
Recommendation: Separar em config, models, controllers, routes e middlewares (playbook PB-03)

### [HIGH] Lógica de negócio e acesso a dados nas rotas (AP-07)
File: src/AppManager.js:28-78, src/AppManager.js:80-129, src/AppManager.js:131-137
Description: Os handlers de rota contêm SQL direto, validação, decisão de pagamento (`cc.startsWith("4")`), criação de usuário, matrícula, pagamento, auditoria e callbacks aninhados em até 7 níveis; não existem controllers/services.
Impact: Viola MVC; regra não reutilizável nem testável.
Recommendation: Extrair controllers (e services) e models com acesso a dados (playbook PB-04)

### [HIGH] Estado global mutável e acoplamento sem DI (AP-08)
File: src/utils.js:9-10,25, src/AppManager.js:7,59, src/app.js:8
Description: `globalCache` é um objeto global mutável alterado por `logAndCache`; `AppManager` cria a conexão SQLite no construtor (`new sqlite3.Database(':memory:')`) e `app.js` instancia o manager diretamente.
Impact: Acoplamento oculto, estado compartilhado entre requisições, testes inviáveis.
Recommendation: Injetar a conexão/dependências a partir de um composition root e remover o cache global (playbook PB-05)

### [MEDIUM] Query N+1 e consultas em laço (AP-10)
File: src/AppManager.js:83-127
Description: No relatório financeiro, para cada curso (`courses.forEach`) há uma query de matrículas e, para cada matrícula, queries de usuário e pagamento.
Impact: Número de queries cresce com os dados; relatório lento.
Recommendation: Substituir por consulta com JOIN e agrupar em memória (playbook PB-06)

### [MEDIUM] Tratamento de erros genérico, inconsistente ou engolido (AP-11)
File: src/AppManager.js:38,41,51,55,70,84, src/AppManager.js:57,92,104,106,133-135
Description: Erros são devolvidos como texto puro ("Erro DB", "Erro Matrícula") em cada handler; `err` é ignorado nos callbacks das linhas 57, 92, 104, 106 e 133 (a exclusão responde sucesso mesmo com falha; `enrollments.length` na linha 93 quebra se `err`); não há error handler central.
Impact: Respostas inconsistentes, falhas silenciosas, possível crash por `undefined`.
Recommendation: Propagar erros e centralizar em middleware de erro, preservando o contrato de status/mensagens (playbook PB-07)

### [MEDIUM] Validação de entrada ausente ou inconsistente (AP-12)
File: src/AppManager.js:29-35,132
Description: `req.body.*` é lido sem checar o corpo; `cc.startsWith` assume string (`card` numérico gera exceção/500); `cid` e `req.params.id` não são validados; `pwd` é opcional por design.
Impact: Erros 500 em vez de 400; dados inválidos persistidos.
Recommendation: Validar entrada no controller antes do uso (playbook PB-08)

### [MEDIUM] Operação multi-etapa sem transação / integridade referencial (AP-14)
File: src/AppManager.js:50-62, src/AppManager.js:131-137
Description: Usuário, matrícula, pagamento e auditoria são gravados em INSERTs independentes sem transação; `DELETE FROM users` deixa matrículas e pagamentos órfãos (a própria mensagem na linha 135 admite).
Impact: Dados inconsistentes em falhas parciais e registros órfãos.
Recommendation: Envolver o checkout em transação e tratar a exclusão em cascata/limpeza dos dependentes (playbook PB-12)

### [MEDIUM] Configuração acoplada ao código (AP-15)
File: src/AppManager.js:7, src/utils.js:6
Description: Tipo/caminho do banco (`':memory:'`) e porta (`3000`) estão fixos no código, sem variável de ambiente.
Impact: Não configurável por ambiente.
Recommendation: Centralizar em `config/` lendo de `process.env` com defaults equivalentes (playbook PB-01)

### [MEDIUM] Código morto e exports não usados (AP-13)
File: src/utils.js:10,25, src/AppManager.js:2
Description: `totalRevenue` é declarado, exportado e importado em AppManager.js sem nunca ser usado; `globalCache` é só escrito e nunca lido; `config.dbUser`, `dbPass` e `smtpUser` não são usados.
Impact: Ruído e falsa impressão de funcionalidade.
Recommendation: Remover itens sem referência (playbook PB-09)

### [LOW] Magic numbers e valores literais soltos (AP-16)
File: src/AppManager.js:46,48,68,60, src/utils.js:19,22
Description: `"4"` como prefixo de cartão aprovado, status `"PAID"`/`"DENIED"` repetidos, senha padrão `"123456"`, e `10000`, `2` e `10` no `badCrypto`.
Impact: Regra de negócio ilegível e propensa a erro.
Recommendation: Extrair constantes nomeadas (playbook PB-13)

### [LOW] Nomenclatura ruim e `console.log` como log (AP-17)
File: src/AppManager.js:29-33,26,45, src/utils.js:13, src/app.js:13
Description: Variáveis `u`, `e`, `p`, `cid`, `cc`, `c`, `enr` pouco descritivas; `const self = this` (linha 26); uso de `console.log` como logging; nome do projeto "Frankenstein LMS" na mensagem.
Impact: Legibilidade reduzida.
Recommendation: Renomear para nomes descritivos mantendo as chaves do contrato do body e usar logger simples (playbook PB-13)

Deprecated APIs: none found

================================
Total: 15 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
