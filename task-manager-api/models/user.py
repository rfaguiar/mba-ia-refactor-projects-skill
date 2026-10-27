import hashlib
import hmac

from werkzeug.security import check_password_hash, generate_password_hash

from config.constants import DEFAULT_ROLE
from models.base import CrudMixin
from models.database import db
from utils.dates import utcnow

HASH_PREFIXES = ('scrypt:', 'pbkdf2:')


class User(CrudMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default=DEFAULT_ROLE)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'active': self.active,
            'created_at': str(self.created_at),
        }

    def set_password(self, plain_password):
        self.password = generate_password_hash(plain_password)

    def has_legacy_password(self):
        return not self.password.startswith(HASH_PREFIXES)

    def check_password(self, plain_password):
        if not self.has_legacy_password():
            return check_password_hash(self.password, plain_password)
        legacy_md5 = hashlib.md5(plain_password.encode()).hexdigest()
        return (
            hmac.compare_digest(self.password.encode(), legacy_md5.encode())
            or hmac.compare_digest(self.password.encode(), plain_password.encode())
        )

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def list_all(cls):
        return cls.query.all()
