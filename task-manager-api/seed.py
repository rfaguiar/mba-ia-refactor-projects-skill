"""Script para popular o banco com dados iniciais"""
import logging
from datetime import timedelta

from app import create_app
from models.category import Category
from models.database import db
from models.task import Task
from models.user import User
from utils.dates import utcnow

logger = logging.getLogger(__name__)

USERS = [
    ('João Silva', 'joao@email.com', '1234', 'admin'),
    ('Maria Santos', 'maria@email.com', 'abcd', 'user'),
    ('Pedro Oliveira', 'pedro@email.com', 'pass', 'manager'),
]

CATEGORIES = [
    ('Backend', 'Tarefas de backend', '#3498db'),
    ('Frontend', 'Tarefas de frontend', '#2ecc71'),
    ('DevOps', 'Tarefas de infraestrutura', '#e74c3c'),
    ('Bug', 'Correção de bugs', '#e67e22'),
]

# (title, description, status, priority, user index, category index, due offset in days, tags)
TASKS = [
    ('Implementar autenticação JWT', 'Adicionar autenticação real com JWT', 'pending', 1, 0, 0, -3, None),
    ('Criar tela de login', 'Tela de login responsiva', 'in_progress', 2, 1, 1, 5, None),
    ('Configurar CI/CD', 'Pipeline com GitHub Actions', 'done', 2, 2, 2, None, 'devops,ci,github'),
    ('Corrigir bug no filtro de busca', 'Filtro não funciona com caracteres especiais', 'pending', 1, 0, 3, -1, None),
    ('Adicionar paginação na API', 'Endpoints retornam todos os registros', 'pending', 3, 0, 0, 10, None),
    ('Escrever testes unitários', 'Cobertura mínima de 80%', 'pending', 2, 1, 0, None, None),
    ('Documentar API com Swagger', 'Gerar documentação automática', 'cancelled', 4, 2, 0, None, None),
    ('Refatorar models', 'Melhorar organização dos models', 'in_progress', 3, 1, 0, None, 'refactor,tech-debt'),
    ('Configurar monitoramento', 'Prometheus + Grafana', 'pending', 4, 2, 2, 20, None),
    ('Melhorar validações de input', 'Usar marshmallow ou pydantic', 'pending', 3, 0, 0, None, 'improvement,validation'),
]


def seed_data():
    with create_app().app_context():
        Task.query.delete()
        User.query.delete()
        Category.query.delete()
        db.session.commit()

        users = []
        for name, email, password, role in USERS:
            user = User(name=name, email=email, role=role)
            user.set_password(password)
            db.session.add(user)
            users.append(user)

        categories = [Category(name=n, description=d, color=c) for n, d, c in CATEGORIES]
        db.session.add_all(categories)
        db.session.commit()

        now = utcnow()
        for title, description, status, priority, user_idx, category_idx, due_days, tags in TASKS:
            db.session.add(Task(
                title=title,
                description=description,
                status=status,
                priority=priority,
                user_id=users[user_idx].id,
                category_id=categories[category_idx].id,
                due_date=now + timedelta(days=due_days) if due_days is not None else None,
                tags=tags,
            ))
        db.session.commit()

        logger.info('Seed concluído com sucesso!')
        logger.info('  %s usuários', User.query.count())
        logger.info('  %s categorias', Category.query.count())
        logger.info('  %s tasks', Task.query.count())


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    seed_data()
