from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import UUID, Boolean, Column, Date, DateTime, ForeignKey, Integer, String, func

from app.models.base import Base


class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    origin_id = Column(Integer, ForeignKey("airports.id"), nullable=False, index=True)
    destination_id = Column(Integer, ForeignKey("airports.id"), nullable=False, index=True)
    departure_date = Column(Date, nullable=True)
    return_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())