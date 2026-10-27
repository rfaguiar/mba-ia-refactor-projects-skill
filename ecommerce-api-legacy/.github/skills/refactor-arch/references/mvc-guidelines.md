# Guidelines de Arquitetura — MVC alvo (Fase 3)

## Responsabilidades por camada

| Camada | Responsabilidade | Pode depender de | **Não pode** |
|---|---|---|---|
| **Config** | Ler configuração de ambiente (porta, banco, segredos, flags) em um único módulo, com defaults seguros | variáveis de ambiente | conter segredos literais de produção |
| **Models** | Representar entidades e **acesso a dados** (queries parametrizadas/ORM), mapeamento linha→objeto/dict, invariantes da entidade | config, driver/ORM | conhecer request/response/HTTP; conter fluxo de aplicação |
| **Views / Routes** | **Roteamento**: mapear método+URL → controller; formatar/serializar a resposta (JSON) | controllers | regra de negócio, SQL, validação de domínio |
| **Controllers** | **Fluxo da aplicação**: ler/validar entrada, chamar models (e services quando a regra é grande), decidir status HTTP, devolver dados para a view | models, services, utils | SQL direto, segredos, estado global |
| **Services** *(opcional)* | Regras de negócio complexas ou efeitos externos (notificação, pagamento) reutilizáveis | models | conhecer HTTP |
| **Middlewares** | Preocupações transversais: **error handler centralizado**, autenticação, logging, CORS | config | regra de negócio |
| **Entry point (composition root)** | Criar a aplicação, **injetar dependências**, registrar rotas/middlewares/erros, iniciar o servidor | todos | conter lógica de negócio ou rotas inline |

Fluxo: `Request → View/Route → Controller → Model → Controller → View/Route → Response`. Erros sobem como exceções de domínio até o middleware de erro.

## Regras

1. **Dependência sempre para dentro**: rotas → controllers → models/services → config. Nunca o inverso.
2. **Uma responsabilidade por arquivo**; um model/controller por domínio (ex.: `produto`, `usuario`, `pedido`).
3. **Sem segredos no código**: tudo via config/variáveis de ambiente, com `.env.example` documentando.
4. **Sem estado global mutável**: conexões/serviços são criados no composition root e injetados (ou obtidos por fábrica com ciclo de vida claro).
5. **Queries parametrizadas** sempre; nenhuma concatenação.
6. **Erros**: controllers lançam exceções de domínio (`NotFound`, `ValidationError`, ...); um único error handler converte em resposta JSON padronizada e loga o detalhe interno sem vazá-lo ao cliente.
7. **Serialização** em um único lugar (método do model ou serializer), nunca duplicada; nunca serialize campos sensíveis (senha/hash).
8. **Entry point enxuto** (≈ < 40 linhas): só montagem.
9. **Preservar o contrato HTTP** (rotas, métodos, status, formato do JSON).
10. Em projetos **parcialmente organizados**: reutilize o que já está bom (ex.: models existentes, blueprints), mova regra de negócio das rotas para controllers/services, corrija responsabilidades fora do lugar e extraia config/erros; não reescreva por reescrever.
11. **Migração de dados legados**: ao trocar o formato de hash de senha, aceite o formato antigo no login e regrave o hash novo (migração transparente); seeds usam o formato novo.
12. **Mudanças intencionais de contrato** (remoção de campos sensíveis, endpoint agora protegido) devem ser listadas no resumo final da Fase 3 e justificadas pelo finding correspondente. **Endpoints existentes nunca são removidos**; autenticação/autorização completa é fora do escopo (vai em Remaining findings).

## Estrutura alvo por stack (adapte nomes às convenções locais)

### Python / Flask
```text
<projeto>/
├── app.py                      # entry point (chama create_app e run)
├── config/settings.py          # config via os.environ
├── models/                     # um arquivo por entidade (+ database.py: conexão/ORM)
├── views/ (ou routes/)         # Blueprints: URL → controller
├── controllers/                # fluxo + validação por domínio
├── services/                   # (opcional) regras/efeitos externos
├── middlewares/error_handler.py
└── utils/                      # helpers puros
```

### Node.js / Express
```text
<projeto>/
├── src/
│   ├── app.js                  # entry point (composition root)
│   ├── config/index.js         # lê process.env
│   ├── database/               # conexão + schema/seed
│   ├── models/                 # acesso a dados por entidade (Promises)
│   ├── routes/ (views)         # express.Router por domínio
│   ├── controllers/            # req/res + fluxo
│   ├── services/               # pagamento, auditoria, hashing
│   └── middlewares/errorHandler.js
├── package.json
└── .env.example
```

### Outras stacks
- **Java/Spring:** `config/`, `model|entity/`, `repository/`, `controller/`, `service/`, `exception/GlobalExceptionHandler`.
- **Go:** `config/`, `models/`, `handlers|controllers/`, `routes/`, `middleware/`, `cmd/main.go`.
- **PHP/Laravel:** `config/`, `app/Models`, `app/Http/Controllers`, `routes/`, `app/Exceptions/Handler`.

## Critérios de "MVC adequado" (usados na validação)

- [ ] Existem camadas separadas de models, views/routes e controllers
- [ ] Nenhuma query SQL fora de models; nenhuma regra de negócio em rotas
- [ ] Config centralizada, sem segredos literais
- [ ] Error handler central registrado
- [ ] Entry point apenas compõe a aplicação
