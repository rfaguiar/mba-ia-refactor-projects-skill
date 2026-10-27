import os
import sqlite3

from config import settings
from models import admin_model, sistema_model
from services import relatorio_service
from utils.errors import ApiError
from utils.http import json_body


def index():
    return {
        "mensagem": "Bem-vindo à API da Loja",
        "versao": settings.APP_VERSION,
        "endpoints": {
            "produtos": "/produtos",
            "usuarios": "/usuarios",
            "pedidos": "/pedidos",
            "login": "/login",
            "relatorios": "/relatorios/vendas",
            "health": "/health",
        },
    }, 200


def relatorio_vendas():
    return {"dados": relatorio_service.relatorio_vendas(), "sucesso": True}, 200


def health_check():
    return {
        "status": "ok",
        "database": "connected",
        "counts": sistema_model.contagens(),
        "versao": settings.APP_VERSION,
        "ambiente": settings.APP_ENV,
        "db_path": os.path.basename(settings.DB_PATH),
    }, 200


def reset_database():
    admin_model.resetar_tabelas()
    return {"mensagem": "Banco de dados resetado", "sucesso": True}, 200


def executar_query():
    query = (json_body() or {}).get("sql", "")
    if not query or not isinstance(query, str):
        raise ApiError("Query não informada")
    try:
        dados = admin_model.executar_sql(query)
    except sqlite3.Error as erro:
        raise ApiError(str(erro), 500)
    if dados is not None:
        return {"dados": dados, "sucesso": True}, 200
    return {"mensagem": "Query executada", "sucesso": True}, 200
