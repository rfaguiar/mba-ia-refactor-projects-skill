from flask import jsonify
from itsdangerous import URLSafeTimedSerializer

from config import settings
from config.constants import DEFAULT_ROLE, MIN_PASSWORD_LENGTH, VALID_ROLES
from middlewares.auth import admin_required, check_admin_token
from middlewares.error_handler import (
    ConflictError,
    NotFoundError,
    UnauthorizedError,
    ForbiddenError,
    ValidationError,
)
from models.task import Task
from models.user import User
from utils.validators import is_valid_email, parse_json_body

TOKEN_SALT = 'login-token'


def _generate_token(user):
    return URLSafeTimedSerializer(settings.SECRET_KEY, salt=TOKEN_SALT).dumps({'user_id': user.id})


def _require_user(user_id):
    user = User.get(user_id)
    if not user:
        raise NotFoundError('Usuário não encontrado')
    return user


def _validate_password(password, message):
    if not isinstance(password, str) or len(password) < MIN_PASSWORD_LENGTH:
        raise ValidationError(message)


def _ensure_email_available(email, current_user_id=None):
    existing = User.find_by_email(email)
    if existing and existing.id != current_user_id:
        raise ConflictError('Email já cadastrado')


def list_users():
    task_counts = Task.count_by_user()
    result = []
    for user in User.list_all():
        data = user.to_dict()
        data['task_count'] = task_counts.get(user.id, 0)
        result.append(data)
    return jsonify(result), 200


def get_user(user_id):
    user = _require_user(user_id)
    data = user.to_dict()
    data['tasks'] = [task.to_dict() for task in Task.for_user(user_id)]
    return jsonify(data), 200


def create_user():
    data = parse_json_body()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = DEFAULT_ROLE

    if not name:
        raise ValidationError('Nome é obrigatório')
    if not email:
        raise ValidationError('Email é obrigatório')
    if not password:
        raise ValidationError('Senha é obrigatória')
    if not isinstance(name, str):
        raise ValidationError('Nome inválido')
    if not is_valid_email(email):
        raise ValidationError('Email inválido')
    _validate_password(password, f'Senha deve ter no mínimo {MIN_PASSWORD_LENGTH} caracteres')
    _ensure_email_available(email)
    if role not in VALID_ROLES:
        raise ValidationError('Role inválido')

    user = User(name=name, email=email, role=role)
    user.set_password(password)
    user.save('Erro ao criar usuário')
    return jsonify(user.to_dict()), 201


def update_user(user_id):
    user = _require_user(user_id)
    data = parse_json_body()

    if 'role' in data or 'active' in data:
        check_admin_token()

    if 'name' in data:
        if not isinstance(data['name'], str) or not data['name']:
            raise ValidationError('Nome inválido')
        user.name = data['name']
    if 'email' in data:
        if not is_valid_email(data['email']):
            raise ValidationError('Email inválido')
        _ensure_email_available(data['email'], user_id)
        user.email = data['email']
    if 'password' in data:
        _validate_password(data['password'], 'Senha muito curta')
        user.set_password(data['password'])
    if 'role' in data:
        if data['role'] not in VALID_ROLES:
            raise ValidationError('Role inválido')
        user.role = data['role']
    if 'active' in data:
        if not isinstance(data['active'], bool):
            raise ValidationError('Campo active inválido')
        user.active = data['active']

    user.save('Erro ao atualizar')
    return jsonify(user.to_dict()), 200


@admin_required
def delete_user(user_id):
    user = _require_user(user_id)
    user.delete('Erro ao deletar')
    return jsonify({'message': 'Usuário deletado com sucesso'}), 200


def list_user_tasks(user_id):
    _require_user(user_id)
    result = []
    for task in Task.for_user(user_id):
        data = task.to_summary_dict()
        data['overdue'] = task.is_overdue()
        result.append(data)
    return jsonify(result), 200


def login():
    data = parse_json_body()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        raise ValidationError('Email e senha são obrigatórios')
    if not isinstance(email, str) or not isinstance(password, str):
        raise UnauthorizedError('Credenciais inválidas')

    user = User.find_by_email(email)
    if not user or not user.check_password(password):
        raise UnauthorizedError('Credenciais inválidas')
    if not user.active:
        raise ForbiddenError('Usuário inativo')

    if user.has_legacy_password():
        user.set_password(password)
        user.save('Erro ao atualizar')

    return jsonify({
        'message': 'Login realizado com sucesso',
        'user': user.to_dict(),
        'token': _generate_token(user),
    }), 200
