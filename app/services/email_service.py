import logging
from decimal import Decimal
from typing import Literal

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from app.core.config import settings
from app.core.exceptions import EmailSendError

logger = logging.getLogger(__name__)

AlertAction = Literal["created", "updated"]


class EmailService:
    def __init__(self, api_key: str | None = None, from_email: str | None = None) -> None:
        self._api_key = api_key or settings.SENDGRID_API_KEY
        self._from_email = from_email or settings.FROM_EMAIL

    def send(self, to_email: str, subject: str, body: str) -> None:
        message = Mail(
            from_email=self._from_email,
            to_emails=to_email,
            subject=subject,
            plain_text_content=body,
        )
        try:
            response = SendGridAPIClient(self._api_key).send(message)
        except Exception as e:
            logger.error("SendGrid request failed to=%s error=%s", to_email, e)
            raise EmailSendError(f"Failed to send email to {to_email}") from e

        if not 200 <= response.status_code < 300:
            logger.error("SendGrid rejected email to=%s status=%s", to_email, response.status_code)
            raise EmailSendError(f"SendGrid returned {response.status_code} for {to_email}")

    def send_alert_confirmation(
        self,
        to_email: str,
        route_label: str,
        threshold: Decimal,
        currency: str,
        action: AlertAction,
    ) -> None:
        subject = f"Price alert {action}: {route_label}"
        body = (
            f"Your alert for route {route_label} has been {action}.\n"
            f"We will notify you when the price drops below {threshold:.2f} {currency}."
        )
        self.send(to_email, subject, body)

    def send_price_drop_notification(
        self,
        to_email: str,
        route_label: str,
        price: Decimal,
        threshold: Decimal,
        currency: str,
    ) -> None:
        subject = f"Price drop: {route_label} for {price:.2f} {currency}"
        body = f"On route {route_label}, the price dropped to {price:.2f} {currency}.\nYour threshold is {threshold:.2f} {currency}."
        self.send(to_email, subject, body)
