from uuid import uuid4

from sqlalchemy.orm import DeclarativeBase


def generate_uuid_string() -> str:
    """Generate a UUID string for database IDs."""
    return str(uuid4())


class Base(DeclarativeBase):
    pass
