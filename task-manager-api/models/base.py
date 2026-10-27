from models.database import db


class PersistenceError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class CrudMixin:
    @classmethod
    def get(cls, entity_id):
        return db.session.get(cls, entity_id)

    def save(self, error_message):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            raise PersistenceError(error_message) from error

    def delete(self, error_message):
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            raise PersistenceError(error_message) from error
