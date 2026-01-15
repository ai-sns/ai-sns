"""Base repository with common CRUD operations."""
from typing import TypeVar, Generic, Type, List, Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.config.database import Base, get_db_session

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository providing common CRUD operations."""

    def __init__(self, model: Type[ModelType]):
        """Initialize repository with model class."""
        self.model = model

    def create(self, **kwargs) -> ModelType:
        """Create a new record."""
        session = get_db_session()
        try:
            obj = self.model(**kwargs)
            session.add(obj)
            session.commit()
            session.refresh(obj)
            return obj
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_by_id(self, id: int) -> Optional[ModelType]:
        """Get record by ID."""
        session = get_db_session()
        try:
            return session.query(self.model).filter_by(id=id).first()
        finally:
            session.close()

    def get_all(self, **filters) -> List[ModelType]:
        """Get all records with optional filters."""
        session = get_db_session()
        try:
            query = session.query(self.model)
            if filters:
                query = query.filter_by(**filters)
            return query.all()
        finally:
            session.close()

    def get_one(self, **filters) -> Optional[ModelType]:
        """Get one record with filters."""
        session = get_db_session()
        try:
            return session.query(self.model).filter_by(**filters).first()
        finally:
            session.close()

    def update(self, id: int, **kwargs) -> bool:
        """Update a record by ID."""
        session = get_db_session()
        try:
            obj = session.query(self.model).filter_by(id=id).first()
            if obj:
                for key, value in kwargs.items():
                    setattr(obj, key, value)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def update_by_filter(self, filters: Dict[str, Any], **kwargs) -> bool:
        """Update a record by custom filters."""
        session = get_db_session()
        try:
            obj = session.query(self.model).filter_by(**filters).first()
            if obj:
                for key, value in kwargs.items():
                    setattr(obj, key, value)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def delete(self, id: int) -> bool:
        """Delete a record by ID."""
        session = get_db_session()
        try:
            obj = session.query(self.model).filter_by(id=id).first()
            if obj:
                session.delete(obj)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def delete_by_filter(self, **filters) -> bool:
        """Delete a record by custom filters."""
        session = get_db_session()
        try:
            obj = session.query(self.model).filter_by(**filters).first()
            if obj:
                session.delete(obj)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def count(self, **filters) -> int:
        """Count records with optional filters."""
        session = get_db_session()
        try:
            query = session.query(self.model)
            if filters:
                query = query.filter_by(**filters)
            return query.count()
        finally:
            session.close()

    def exists(self, **filters) -> bool:
        """Check if record exists."""
        session = get_db_session()
        try:
            return session.query(self.model).filter_by(**filters).first() is not None
        finally:
            session.close()
