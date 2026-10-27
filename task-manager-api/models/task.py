from sqlalchemy import and_, func
from sqlalchemy.orm import joinedload

from config.constants import DEFAULT_PRIORITY, STATUS_PENDING, TERMINAL_STATUSES
from models.base import CrudMixin
from models.database import db
from utils.dates import utcnow


class Task(CrudMixin, db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default=STATUS_PENDING)
    priority = db.Column(db.Integer, default=DEFAULT_PRIORITY)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    tags = db.Column(db.String(500), nullable=True)

    user = db.relationship('User', backref=db.backref('tasks', cascade='all'))
    category = db.relationship('Category', backref='tasks')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'created_at': str(self.created_at),
            'updated_at': str(self.updated_at),
            'due_date': str(self.due_date) if self.due_date else None,
            'tags': self.tags.split(',') if self.tags else [],
        }

    def to_summary_dict(self):
        full = self.to_dict()
        keys = ('id', 'title', 'description', 'status', 'priority', 'created_at', 'due_date')
        return {key: full[key] for key in keys}

    def is_overdue(self):
        return bool(
            self.due_date
            and self.due_date < utcnow()
            and self.status not in TERMINAL_STATUSES
        )

    @classmethod
    def list_with_relations(cls):
        return cls.query.options(joinedload(cls.user), joinedload(cls.category)).all()

    @classmethod
    def search(cls, text=None, status=None, priority=None, user_id=None):
        query = cls.query
        if text:
            query = query.filter(db.or_(cls.title.like(f'%{text}%'), cls.description.like(f'%{text}%')))
        if status:
            query = query.filter(cls.status == status)
        if priority is not None:
            query = query.filter(cls.priority == priority)
        if user_id is not None:
            query = query.filter(cls.user_id == user_id)
        return query.all()

    @classmethod
    def for_user(cls, user_id):
        return cls.query.filter_by(user_id=user_id).all()

    @classmethod
    def _overdue_filter(cls):
        return and_(cls.due_date.isnot(None), cls.due_date < utcnow(), cls.status.notin_(TERMINAL_STATUSES))

    @classmethod
    def overdue(cls, user_id=None):
        query = cls.query.filter(cls._overdue_filter())
        if user_id is not None:
            query = query.filter(cls.user_id == user_id)
        return query.all()

    @classmethod
    def count_overdue(cls, user_id=None):
        query = cls.query.filter(cls._overdue_filter())
        if user_id is not None:
            query = query.filter(cls.user_id == user_id)
        return query.count()

    @classmethod
    def count_all(cls, user_id=None):
        query = db.session.query(func.count(cls.id))
        if user_id is not None:
            query = query.filter(cls.user_id == user_id)
        return query.scalar()

    @classmethod
    def count_by_status(cls, user_id=None):
        query = db.session.query(cls.status, func.count(cls.id))
        if user_id is not None:
            query = query.filter(cls.user_id == user_id)
        return dict(query.group_by(cls.status).all())

    @classmethod
    def count_by_priority(cls):
        return dict(db.session.query(cls.priority, func.count(cls.id)).group_by(cls.priority).all())

    @classmethod
    def count_high_priority(cls, user_id, threshold):
        return cls.query.filter(cls.user_id == user_id, cls.priority <= threshold).count()

    @classmethod
    def count_created_since(cls, since):
        return cls.query.filter(cls.created_at >= since).count()

    @classmethod
    def count_with_status_updated_since(cls, status, since):
        return cls.query.filter(cls.status == status, cls.updated_at >= since).count()

    @classmethod
    def count_by_user(cls, status=None):
        query = db.session.query(cls.user_id, func.count(cls.id))
        if status:
            query = query.filter(cls.status == status)
        return dict(query.group_by(cls.user_id).all())

    @classmethod
    def count_by_category(cls):
        return dict(db.session.query(cls.category_id, func.count(cls.id)).group_by(cls.category_id).all())
