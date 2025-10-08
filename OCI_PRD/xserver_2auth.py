from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import time
import re

import tempfile


# オプション設定
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--ignore-certificate-errors")
options.add_argument("--disable-features=NetworkService")

# ChromeDriverのパスを指定（Selenium 3.xでは executable_path を直接渡す）
driver = webdriver.Chrome(executable_path="/usr/local/bin/chromedriver", chrome_options=options)

driver = webdriver.Chrome(executable_path="/usr/local/bin/chromedriver", options=options)

# ログインページにアクセス（Xserver）
driver.get("https://secure.xserver.ne.jp/xapanel/login/xserver/")

# 少し待機（ページ読み込み）
time.sleep(2)

# ユーザーIDとパスワードを入力
driver.find_element(By.ID, "memberid").send_keys("yokopii865@yahoo.co.jp")
#driver.find_element(By.ID, "btnNext").click()
#time.sleep(2)
driver.find_element(By.ID, "user_password").send_keys("Asics123#")

# ログインボタンをクリック
driver.find_element(By.CLASS_NAME, "btnSubmit").click()

# 必要に応じて待機や後続処理
time.sleep(5)

# 2段階認証画面を待機
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "auth_mail"))
)

# メール認証ラジオボタンを取得
auth_mail_radio = driver.find_element(By.ID, "auth_mail")

# JavaScriptで強制クリック（CUIでも有効）
driver.execute_script("arguments[0].click();", auth_mail_radio)

# 送信ボタンも同様に強制クリック
submit_btn = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
driver.execute_script("arguments[0].click();", submit_btn)

print("✅ メール認証コードを送信しました（CUI環境でもOK）")


# Fコード入力画面を待機
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.NAME, "auth_code"))
)

# 手動でFコードを入力
f_code = input("📩 メールで届いたFコードを入力してください：")
driver.find_element(By.NAME, "auth_code").send_keys(f_code)
driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
print("✅ Fコードを送信しました")

time.sleep(10)

# ログイン後の要素確認
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "serviceNav__toggle"))
)
print("🎉 ログイン完了、サービスメニューが表示されました")


# 終了
driver.quit()

