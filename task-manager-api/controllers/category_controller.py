from flask import jsonify

from config.constants import DEFAULT_COLOR
from middlewares.auth import admin_required
from middlewares.error_handler import NotFoundError, ValidationError
from models.category import Category
from models.task import Task
from utils.validators import parse_json_body


def _require_category(category_id):
    category = Category.get(category_id)
    if not category:
        raise NotFoundError('Categoria não encontrada')
    return category


def list_categories():
    task_counts = Task.count_by_category()
    result = []
    for category in Category.list_all():
        data = category.to_dict()
        data['task_count'] = task_counts.get(category.id, 0)
        result.append(data)
    return jsonify(result), 200


def create_category():
    data = parse_json_body()
    name = data.get('name')
    if not name:
        raise ValidationError('Nome é obrigatório')

    category = Category(
        name=name,
        description=data.get('description', ''),
        color=data.get('color', DEFAULT_COLOR),
    )
    category.save('Erro ao criar categoria')
    return jsonify(category.to_dict()), 201


def update_category(category_id):
    category = _require_category(category_id)
    data = parse_json_body()
    for field in ('name', 'description', 'color'):
        if field in data:
            setattr(category, field, data[field])
    category.save('Erro ao atualizar')
    return jsonify(category.to_dict()), 200


@admin_required
def delete_category(category_id):
    category = _require_category(category_id)
    category.delete('Erro ao deletar')
    return jsonify({'message': 'Categoria deletada'}), 200
