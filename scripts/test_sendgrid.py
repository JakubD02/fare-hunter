import sys

from app.core.exceptions import EmailSendError
from app.services.email_service import EmailService


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: uv run python -m scripts.test_sendgrid recipient@example.com")
        raise SystemExit(1)

    to_email = sys.argv[1]
    service = EmailService()

    try:
        service.send_alert_confirmation(
            to_email=to_email,
            route_label="WAW → LHR",
            threshold=500,
            currency="PLN",
            action="created",
        )
    except EmailSendError as e:
        print(f"Send failed: {e}")
        raise SystemExit(1)

    print(f"Test email sent to {to_email}. Check the inbox and the spam folder.")


if __name__ == "__main__":
    main()
