import logging
from uuid import UUID

from app.celery_app import celery_app
from app.core.exceptions import EmailSendError
from app.database import SessionLocal
from app.models.price_alert import PriceAlert
from app.models.route import Route
from app.services.auth_service import get_user_by_id
from app.services.email_service import email_service

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def send_alert_confirmation_email_task(self, user_id: str, alert_id: int):
    db = SessionLocal()
    try:
        user_id_uuid = UUID(user_id)
        user = get_user_by_id(db, user_id_uuid)

        if not user:
            logger.warning(f"User {user_id} not found")
            return

        alert = db.query(PriceAlert).filter(PriceAlert.id == alert_id).first()
        if not alert:
            logger.warning(f"Alert {alert_id} not found")
            return

        route = alert.route
        success = email_service.send_alert_confirmation_email(
            to_email=user.email,
            route=f"{route.origin} -> {route.destination}",
            threshold=alert.price_threshold,
        )

        if not success:
            raise EmailSendError(f"Failed to send email to {user.email}")

    except EmailSendError as e:
        logger.error(f"Error sending alert confirmation email: {e}")
    except (ValueError, LookupError) as e:
        logger.error(f"Invalid data in alert confirmation email task: {e}")

    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3)
def send_price_drop_email_task(
    self, user_id: str, route_id: int, old_price: float, new_price: float
):
    db = SessionLocal()
    try:
        user_id_uuid = UUID(user_id)
        user = get_user_by_id(db, user_id_uuid)

        if not user:
            logger.warning(f"User {user_id} not found")
            return

        route = db.query(Route).filter(Route.id == route_id).first()
        if not route:
            logger.warning(f"Route {route_id} not found")
            return

        success = email_service.send_price_alert_email(
            to_email=user.email,
            route=f"{route.origin} → {route.destination}",
            old_price=old_price,
            new_price=new_price,
        )

        if not success:
            raise EmailSendError(f"Failed to send email {user.email}")

    except EmailSendError as e:
        logger.error(f"Error sending price drop email: {e}")
        raise self.retry(exc=e, countdown=300)
    finally:
        db.close()
