# code-smells-project

API de E-commerce em Python/Flask usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
pip install -r requirements.txt
python app.py
```

A aplicação sobe em `http://localhost:5000`. O banco SQLite (`loja.db`) é criado automaticamente no primeiro boot, já com produtos e usuários de exemplo.

## Estrutura (MVC)

`app.py` (composition root) · `config/` · `models/` · `views/` (rotas) · `controllers/` · `services/` · `middlewares/` · `utils/`

## Configuração

Variáveis de ambiente (ver `.env.example`): `SECRET_KEY`, `FLASK_DEBUG`, `HOST`, `PORT`, `DB_PATH`, `APP_ENV`.
Os endpoints `/admin/reset-db` e `/admin/query` ficam desabilitados (403) por padrão; para habilitá-los defina `ENABLE_ADMIN_ENDPOINTS=1` e `ADMIN_TOKEN`, enviando o token no header `X-Admin-Token`.
