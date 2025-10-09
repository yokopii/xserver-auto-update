##############################################################################################
# Gmailのアプリパスワードを使用して,yahooメールへメール送信（タイムアウト・TLS・ログ安定化済）
##############################################################################################
import smtplib
from email.message import EmailMessage
import logging
from dotenv import load_dotenv
import os

# .envファイル読み込み
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

# 設定値の存在チェック
assert all(GMAIL_CONFIG.values()), "GMAIL_CONFIG に未設定の項目があります"
assert LOG_CONFIG["mail_log_path"], "MAIL_LOG_PATH が未設定です"

# Logging
try:
    logging.basicConfig(
        filename=LOG_CONFIG["mail_log_path"],
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
except Exception as log_err:
    print(f"[WARN] ログ初期化失敗: {log_err}")

def send_notification(subject, body, to):
    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = GMAIL_CONFIG["account"]
        msg['To'] = ", ".join(to) if isinstance(to, list) else to  # 複数の宛先も可能

        output_log("メール送信処理開始")
        with smtplib.SMTP(GMAIL_CONFIG["smtp_domain"], GMAIL_CONFIG["smtp_port"], timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(GMAIL_CONFIG["account"], GMAIL_CONFIG["app_pass"])
            code, response = server.noop()
            server.send_message(msg)

        try:
            output_log(f"メールOK: {subject} → {to} | 内容: {body[:50]}...")
        except Exception as log_err:
            print(f"[WARN] ログ出力失敗: {log_err}")

    except Exception as e:
        try:
            output_log(f"[ERROR] メールNG: {subject} → {to} | {e}", argLevel=logging.ERROR)
        except:
            print(f"[ERROR] ログ出力失敗: {log_err}")

##########################################
# ログ出力
##########################################
def output_log(argMsg, argLevel=logging.INFO):
    logging.log(argLevel, f" | 補足: {argMsg}")
    print(argMsg)
