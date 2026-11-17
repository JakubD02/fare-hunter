import logging
import secrets
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.enums.currency import Currency
from app.models.airport import Airport
from app.models.route import Route
from app.models.user import User

logger = logging.getLogger(__name__)

FEATURED_ROUTES = [
    {
        "origin": "WAW",
        "destination": "LHR",
        "departure_date": date(2026, 12, 20),
        "return_date": date(2026, 12, 27),
        "currency": Currency.PLN,
    },
]


def get_or_create_system_user(db: Session) -> User:
    owner = db.scalar(select(User).where(User.email == settings.SYSTEM_USER_EMAIL))
    if owner is None:
        owner = User(
            email=settings.SYSTEM_USER_EMAIL,
            first_name="System",
            password_hash=hash_password(secrets.token_urlsafe(32)),
        )
        db.add(owner)
        db.flush()
        logger.info("created system user id=%s", owner.id)
    return owner


def load_airport_ids(db: Session, codes: set[str]) -> dict[str, str]:
    airports = {a.iata_code: a.id for a in db.scalars(select(Airport).where(Airport.iata_code.in_(codes)))}
    missing = codes - airports.keys()
    if missing:
        raise RuntimeError(f"Airports missing, run seed_data first: {sorted(missing)}")
    return airports


def seed_featured(db: Session) -> None:
    owner = get_or_create_system_user(db)

    codes = {code for spec in FEATURED_ROUTES for code in (spec["origin"], spec["destination"])}
    airports = load_airport_ids(db, codes)

    for spec in FEATURED_ROUTES:
        origin_id = airports[spec["origin"]]
        destination_id = airports[spec["destination"]]

        exists = db.scalar(
            select(Route).where(
                Route.user_id == owner.id,
                Route.is_featured.is_(True),
                Route.origin_id == origin_id,
                Route.destination_id == destination_id,
                Route.departure_date == spec["departure_date"],
            )
        )
        if exists:
            logger.info("featured route already exists: %s->%s", spec["origin"], spec["destination"])
            continue

        db.add(
            Route(
                user_id=owner.id,
                origin_id=origin_id,
                destination_id=destination_id,
                departure_date=spec["departure_date"],
                return_date=spec["return_date"],
                currency=spec["currency"],
                is_active=True,
                is_featured=True,
            )
        )
        logger.info("featured route added: %s->%s", spec["origin"], spec["destination"])

    db.commit()


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    with SessionLocal() as db:
        seed_featured(db)


if __name__ == "__main__":
    main()
