"""
Base repository with common database operations.
Implements the Repository pattern for data access abstraction.
"""
from app import db


class BaseRepository:
    model = None

    def get_by_id(self, pk):
        return db.session.get(self.model, pk)

    def get_all(self, limit=100, offset=0):
        return self.model.query.limit(limit).offset(offset).all()

    def create(self, **kwargs):
        instance = self.model(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance

    def update(self, pk, **kwargs):
        instance = self.get_by_id(pk)
        if instance is None:
            return None
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        db.session.commit()
        return instance

    def delete(self, pk):
        instance = self.get_by_id(pk)
        if instance is None:
            return False
        db.session.delete(instance)
        db.session.commit()
        return True

    def count(self):
        return self.model.query.count()
