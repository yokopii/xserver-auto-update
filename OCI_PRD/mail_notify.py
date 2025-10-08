##############################################################################################
# Gmailのアプリパスワードを使用して,yahooメールへメール送信
##############################################################################################
import smtplib
from email.message import EmailMessage
import logging
from dotenv import load_dotenv
import os

#.envファイル読み込み
load_dotenv()

GMAIL_CONFIG = {
    "account"    : os.getenv("GMAIL_ACCOUNT"),
    "app_pass"   : os.getenv("GMAIL_APP_PASS"),
    "smtp_domain": os.getenv("GMAIL_SMTP_DOMAIN"),
    "smtp_port"  : int(os.getenv("GMAIL_SMTP_PORT")),
}

LOG_CONFIG = {
    "mail_log_path": os.getenv("MAIL_LOG_PATH")
}

#Logging
logging.basicConfig(
    filename=LOG_CONFIG["mail_log_path"],
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def send_notification(subject, body, to):
    try:

        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = GMAIL_CONFIG["account"]
        msg['To'] = ", ".join(to) if isinstance(to, list) else to  #複数の宛先も可能

        with smtplib.SMTP(GMAIL_CONFIG["smtp_domain"], GMAIL_CONFIG["smtp_port"]) as server:
            server.starttls()
            server.login(GMAIL_CONFIG["account"], GMAIL_CONFIG["app_pass"])
            server.send_message(msg)

        logging.info(f"メールOK: {subject} → {to} | 内容: {body[:50]}...")
    except Exception as e:
        logging.error(f"メールNG: {subject} → {to} | {e}")

