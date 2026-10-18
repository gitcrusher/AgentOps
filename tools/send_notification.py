import os
import smtplib
import time
from email.mime.text import MIMEText

SMTP_TIMEOUT_SECONDS = 10
RETRY_BACKOFF_SECONDS = 2


def _send_once(sender: str, pwd: str, msg: MIMEText) -> None:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=SMTP_TIMEOUT_SECONDS) as server:
        server.login(sender, pwd)
        server.send_message(msg)


def execute_send_notification(params: dict) -> dict:
    # Credentials come only from env (.env / Streamlit Secrets), never logged.
    sender = os.getenv("GMAIL_ADDRESS")
    pwd = os.getenv("GMAIL_APP_PASSWORD")
    if not sender or not pwd:
        return {"status": "failed", "reason": "missing_credentials"}

    msg = MIMEText(params.get("message", ""))
    msg["Subject"] = params.get("subject", "")
    msg["From"] = sender
    msg["To"] = params.get("to", "")

    # AGENTS.md Section 3: one retry after 2s on connection failure; no retry on
    # auth errors (retrying won't fix bad credentials). Only the error *type* is
    # returned, so nothing credential-related can leak into the trace.
    for attempt in range(2):
        try:
            _send_once(sender, pwd, msg)
            return {"status": "sent"}
        except smtplib.SMTPAuthenticationError:
            return {"status": "failed", "reason": "SMTPAuthenticationError"}
        except (OSError, smtplib.SMTPException) as e:  # timeouts, refused, disconnects
            if attempt == 0:
                time.sleep(RETRY_BACKOFF_SECONDS)
                continue
            return {"status": "failed", "reason": type(e).__name__}
