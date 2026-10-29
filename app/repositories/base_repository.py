from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.base import IdModel


class BaseRepository[ModelT: IdModel]:
    """Common CRUD operations for a single SQLAlchemy model."""

    model: type[ModelT]

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, entity_id: str) -> ModelT | None:
        return self._db.get(self.model, entity_id)

    def list_all(self, limit: int, offset: int) -> list[ModelT]:
        stmt = select(self.model).limit(limit).offset(offset)
        return list(self._db.scalars(stmt))

    def add(self, entity: ModelT) -> ModelT:
        self._db.add(entity)
        self._db.commit()
        self._db.refresh(entity)
        return entity

    def save(self, entity: ModelT) -> ModelT:
        self._db.commit()
        self._db.refresh(entity)
        return entity

    def delete(self, entity: ModelT) -> None:
        self._db.delete(entity)
        self._db.commit()
