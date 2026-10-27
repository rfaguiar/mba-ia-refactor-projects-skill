# task-manager-api

API de Task Manager em Python/Flask usada como entrada do desafio `refactor-arch`. Diferente dos outros projetos, este já possui alguma separação de camadas (`models/`, `routes/`, `services/`, `utils/`), mas ainda contém problemas arquiteturais e de qualidade.

## Como rodar

```bash
pip install -r requirements.txt
python seed.py
python app.py
```

A aplicação sobe em `http://localhost:5000`. O `seed.py` popula o banco SQLite (`tasks.db`) com usuários, categorias e tasks de exemplo — **rode-o antes do primeiro boot**, caso contrário os endpoints vão retornar listas vazias.

## Configuração

Variáveis de ambiente (veja `.env.example`): `SECRET_KEY`, `ADMIN_TOKEN` (header `X-Admin-Token` nos DELETEs e em alterações de `role`/`active`; obrigatório quando `APP_ENV=production`), `FLASK_DEBUG`, `HOST`, `PORT`, `DATABASE_URL`, `SMTP_*`.

## Estrutura

`config/` · `models/` · `routes/` (URL → controller) · `controllers/` · `middlewares/` (erros, admin token) · `services/` · `utils/`
