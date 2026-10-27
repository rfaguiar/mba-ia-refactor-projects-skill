from flask import jsonify, request

from config.constants import (
    DEFAULT_PRIORITY,
    MAX_PRIORITY,
    MAX_TITLE_LENGTH,
    MIN_PRIORITY,
    MIN_TITLE_LENGTH,
    STATUS_CANCELLED,
    STATUS_DONE,
    STATUS_IN_PROGRESS,
    STATUS_PENDING,
    VALID_STATUSES,
)
from middlewares.auth import admin_required
from middlewares.error_handler import NotFoundError, ValidationError
from models.category import Category
from models.task import Task
from models.user import User
from utils.dates import utcnow
from utils.validators import (
    normalize_tags,
    parse_date,
    parse_int,
    parse_json_body,
    parse_query_int,
)

CREATE_DATE_ERROR = 'Formato de data inválido. Use YYYY-MM-DD'
UPDATE_DATE_ERROR = 'Formato de data inválido'


def _validate_title(title):
    if not isinstance(title, str):
        raise ValidationError('Título inválido')
    if len(title) < MIN_TITLE_LENGTH:
        raise ValidationError('Título muito curto')
    if len(title) > MAX_TITLE_LENGTH:
        raise ValidationError('Título muito longo')
    return title


def _validate_references(data, fields):
    if 'user_id' in data:
        user_id = data['user_id']
        if user_id:
            parse_int(user_id, 'user_id inválido')
            if not User.get(user_id):
                raise NotFoundError('Usuário não encontrado')
        fields['user_id'] = user_id
    if 'category_id' in data:
        category_id = data['category_id']
        if category_id:
            parse_int(category_id, 'category_id inválido')
            if not Category.get(category_id):
                raise NotFoundError('Categoria não encontrada')
        fields['category_id'] = category_id


def _clean_fields(data, date_error):
    fields = {}
    if 'title' in data:
        fields['title'] = _validate_title(data['title'])
    if 'description' in data:
        fields['description'] = data['description']
    if 'status' in data:
        if data['status'] not in VALID_STATUSES:
            raise ValidationError('Status inválido')
        fields['status'] = data['status']
    if 'priority' in data:
        priority = parse_int(data['priority'], 'Prioridade inválida')
        if priority < MIN_PRIORITY or priority > MAX_PRIORITY:
            raise ValidationError('Prioridade deve ser entre 1 e 5')
        fields['priority'] = priority
    _validate_references(data, fields)
    if 'due_date' in data:
        fields['due_date'] = parse_date(data['due_date'], date_error) if data['due_date'] else None
    if 'tags' in data:
        fields['tags'] = normalize_tags(data['tags'])
    return fields


def _with_overdue(task):
    data = task.to_dict()
    data['overdue'] = task.is_overdue()
    return data


def list_tasks():
    result = []
    for task in Task.list_with_relations():
        data = _with_overdue(task)
        data['user_name'] = task.user.name if task.user else None
        data['category_name'] = task.category.name if task.category else None
        result.append(data)
    return jsonify(result), 200


def get_task(task_id):
    task = Task.get(task_id)
    if not task:
        raise NotFoundError('Task não encontrada')
    return jsonify(_with_overdue(task)), 200


def create_task():
    data = parse_json_body()
    if not data.get('title'):
        raise ValidationError('Título é obrigatório')

    fields = _clean_fields(data, CREATE_DATE_ERROR)
    fields.setdefault('description', '')
    fields.setdefault('status', STATUS_PENDING)
    fields.setdefault('priority', DEFAULT_PRIORITY)
    if not fields.get('tags'):
        fields.pop('tags', None)

    task = Task(**fields)
    task.save('Erro ao criar task')
    return jsonify(task.to_dict()), 201


def update_task(task_id):
    task = Task.get(task_id)
    if not task:
        raise NotFoundError('Task não encontrada')

    fields = _clean_fields(parse_json_body(), UPDATE_DATE_ERROR)
    for name, value in fields.items():
        setattr(task, name, value)
    task.updated_at = utcnow()
    task.save('Erro ao atualizar')
    return jsonify(task.to_dict()), 200


@admin_required
def delete_task(task_id):
    task = Task.get(task_id)
    if not task:
        raise NotFoundError('Task não encontrada')
    task.delete('Erro ao deletar')
    return jsonify({'message': 'Task deletada com sucesso'}), 200


def search_tasks():
    priority = request.args.get('priority', '')
    user_id = request.args.get('user_id', '')
    tasks = Task.search(
        text=request.args.get('q', ''),
        status=request.args.get('status', ''),
        priority=parse_query_int(priority, 'Prioridade inválida') if priority else None,
        user_id=parse_query_int(user_id, 'user_id inválido') if user_id else None,
    )
    return jsonify([task.to_dict() for task in tasks]), 200


def task_stats():
    total = Task.count_all()
    by_status = Task.count_by_status()
    done = by_status.get(STATUS_DONE, 0)
    stats = {
        'total': total,
        'pending': by_status.get(STATUS_PENDING, 0),
        'in_progress': by_status.get(STATUS_IN_PROGRESS, 0),
        'done': done,
        'cancelled': by_status.get(STATUS_CANCELLED, 0),
        'overdue': Task.count_overdue(),
        'completion_rate': round((done / total) * 100, 2) if total > 0 else 0,
    }
    return jsonify(stats), 200
