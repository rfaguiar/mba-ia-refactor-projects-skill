from datetime import timedelta

from flask import jsonify

from config.constants import (
    HIGH_PRIORITY_THRESHOLD,
    PRIORITY_LABELS,
    RECENT_DAYS,
    STATUS_CANCELLED,
    STATUS_DONE,
    STATUS_IN_PROGRESS,
    STATUS_PENDING,
)
from middlewares.error_handler import NotFoundError
from models.category import Category
from models.task import Task
from models.user import User
from utils.dates import utcnow


def _completion_rate(done, total):
    return round((done / total) * 100, 2) if total > 0 else 0


def summary_report():
    now = utcnow()
    since = now - timedelta(days=RECENT_DAYS)
    by_status = Task.count_by_status()
    by_priority = Task.count_by_priority()
    total_by_user = Task.count_by_user()
    done_by_user = Task.count_by_user(status=STATUS_DONE)
    users = User.list_all()

    overdue_tasks = Task.overdue()
    user_stats = []
    for user in users:
        total = total_by_user.get(user.id, 0)
        completed = done_by_user.get(user.id, 0)
        user_stats.append({
            'user_id': user.id,
            'user_name': user.name,
            'total_tasks': total,
            'completed_tasks': completed,
            'completion_rate': _completion_rate(completed, total),
        })

    report = {
        'generated_at': str(now),
        'overview': {
            'total_tasks': Task.count_all(),
            'total_users': len(users),
            'total_categories': len(Category.list_all()),
        },
        'tasks_by_status': {
            STATUS_PENDING: by_status.get(STATUS_PENDING, 0),
            STATUS_IN_PROGRESS: by_status.get(STATUS_IN_PROGRESS, 0),
            STATUS_DONE: by_status.get(STATUS_DONE, 0),
            STATUS_CANCELLED: by_status.get(STATUS_CANCELLED, 0),
        },
        'tasks_by_priority': {label: by_priority.get(level, 0) for level, label in PRIORITY_LABELS.items()},
        'overdue': {
            'count': len(overdue_tasks),
            'tasks': [
                {
                    'id': task.id,
                    'title': task.title,
                    'due_date': str(task.due_date),
                    'days_overdue': (now - task.due_date).days,
                }
                for task in overdue_tasks
            ],
        },
        'recent_activity': {
            'tasks_created_last_7_days': Task.count_created_since(since),
            'tasks_completed_last_7_days': Task.count_with_status_updated_since(STATUS_DONE, since),
        },
        'user_productivity': user_stats,
    }
    return jsonify(report), 200


def user_report(user_id):
    user = User.get(user_id)
    if not user:
        raise NotFoundError('Usuário não encontrado')

    by_status = Task.count_by_status(user_id)
    total = Task.count_all(user_id)
    done = by_status.get(STATUS_DONE, 0)
    report = {
        'user': {'id': user.id, 'name': user.name, 'email': user.email},
        'statistics': {
            'total_tasks': total,
            'done': done,
            'pending': by_status.get(STATUS_PENDING, 0),
            'in_progress': by_status.get(STATUS_IN_PROGRESS, 0),
            'cancelled': by_status.get(STATUS_CANCELLED, 0),
            'overdue': Task.count_overdue(user_id),
            'high_priority': Task.count_high_priority(user_id, HIGH_PRIORITY_THRESHOLD),
            'completion_rate': _completion_rate(done, total),
        },
    }
    return jsonify(report), 200
