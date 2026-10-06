from datetime import date, datetime

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.airport import Airport
from app.models.base import Base


class Route(Base):
    __tablename__ = "routes"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    origin_id: Mapped[int] = mapped_column(ForeignKey("airports.id"), nullable=False, index=True)
    destination_id: Mapped[int] = mapped_column(ForeignKey("airports.id"), nullable=False, index=True)
    departure_date: Mapped[date] = mapped_column(nullable=False)
    return_date: Mapped[date | None] = mapped_column()
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    origin_airport: Mapped["Airport"] = relationship(foreign_keys=[origin_id])
    destination_airport: Mapped["Airport"] = relationship(foreign_keys=[destination_id])