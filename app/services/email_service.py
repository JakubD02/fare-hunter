import logging

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Content, Mail, To

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        self.from_email = settings.FROM_EMAIL

    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: str | None = None,
    ) -> bool:
        try:
            message = Mail(
                from_email=self.from_email,
                to_emails=To(to_email),
                subject=subject,
                plain_text_content=Content("text/plain", body),
            )

            if html_body:
                message.add_content(Content("text/html", html_body))

            response = self.sg.send(message)
            logger.info(f"Email sent to {to_email}: {response.status_code}")
            return response.status_code in [200, 201]
        except (ConnectionError, TimeoutError, ValueError) as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    def send_price_alert_email(
        self, to_email: str, route: str, old_price: float, new_price: float
    ) -> bool:
        """Send price drop notification"""
        subject = f"✈️ Price Drop Alert: {route}"

        body = f"""
Hello,

Great news! The price for your flight {route} has dropped!

Old price: ${old_price:.2f}
New price: ${new_price:.2f}
Savings: ${old_price - new_price:.2f}

Check it out in your Fare Hunter dashboard!

Best regards,
Fare Hunter Team
"""

        html_body = f"""
<html>
  <body>
    <h2>✈️ Price Drop Alert</h2>
    <p>Great news! The price for your flight <strong>{route}</strong> has dropped!</p>
    <p>
      <strong>Old price:</strong> ${old_price:.2f}<br>
      <strong>New price:</strong> ${new_price:.2f}<br>
      <strong>Savings:</strong> ${old_price - new_price:.2f}
    </p>
    <p>Check it out in your <a href="{settings.APP_URL}">Fare Hunter dashboard</a>!</p>
    <p>Best regards,<br>Fare Hunter Team</p>
  </body>
</html>
"""

        return self.send_email(
            to_email=to_email,
            subject=subject,
            body=body,
            html_body=html_body,
        )

    def send_alert_confirmation_email(
        self, to_email: str, route: str, threshold: float
    ) -> bool:
        """Send confirmation when alert is created"""
        subject = f"Alert Created: {route}"

        body = f"""
Hi,

Your price alert has been created!

Route: {route}
Alert threshold: ${threshold:.2f}

We'll notify you as soon as the price drops below this threshold.

Best regards,
Fare Hunter Team
"""

        return self.send_email(to_email=to_email, subject=subject, body=body)


email_service = EmailService()
