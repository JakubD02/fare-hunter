

from sqlalchemy import Column, Integer, String

from app.models.base import Base


class Airline(Base):
    __tablename__ = "airlines"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(3), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)