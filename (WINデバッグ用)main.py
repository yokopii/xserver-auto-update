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



# Chromeブラウザを起動
#driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
'''
# Chromeブラウザを起動(セキュリティエラー無視版)
options = Options()
options.add_argument("--ignore-certificate-errors")
options.add_argument("--disable-features=NetworkService")

temp_profile = tempfile.mkdtemp()
options.add_argument(f"--user-data-dir={temp_profile}")
options.add_argument("--disable-gpu")
print(f"Using temp profile: {temp_profile}")
'''

###
# 一時プロファイル作成
temp_profile = tempfile.mkdtemp()
print(f"Using temp profile: {temp_profile}")

# オプション設定
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--ignore-certificate-errors")
options.add_argument("--disable-features=NetworkService")
#options.add_argument(f"--user-data-dir={temp_profile}")

# ChromeDriverのパスを指定（Selenium 3.xでは executable_path を直接渡す）
driver = webdriver.Chrome(executable_path="/usr/local/bin/chromedriver", chrome_options=options)

###

#driver = webdriver.Chrome(options=options)
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

#ログイン後の動き
#-- ページ遷移 --

# ① 「サービス管理」ナビゲーションメニューをクリックして展開
service_menu = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CLASS_NAME, "serviceNav__toggle"))
)
service_menu.click()

# ② 「ご利用中のサービス」内の「XServer GAMEs」をクリック
xserver_games_link = driver.find_element(By.ID, "ga-xsa-serviceNav-xmgame")
xserver_games_link.click()

time.sleep(5)
#-- ページ遷移 --

# 「ゲーム管理」ボタンをクリック（テキスト一致で取得）
game_manage_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//a[text()='ゲーム管理']"))
)
game_manage_button.click()

time.sleep(5)




#-- MAINページ遷移 --
# bodyタグのテキストをすべて取得
body_text = driver.find_element(By.TAG_NAME, "body").text

# 正規表現で「残り◯時間◯分」を抽出
match = re.search(r"残り\s*(\d+)\s*時間\s*(\d+)\s*分", body_text)
if match:
    hours = int(match.group(1))
    minutes = int(match.group(2))
    total_hours = hours + minutes / 60
    print(f"残り時間（合計）: {total_hours:.2f} 時間")
else:
    print("残り時間の形式が見つかりませんでした")

#サーバー残り時間が24時間を切っていれば更新する

if hours < 24: #もし残り時間を24時間切った場合
    print("24時間きってるよ")

    #「アップグレード・期限延長」ボタンをクリック
    upgrade_button = driver.find_element(By.LINK_TEXT, "アップグレード・期限延長")
    upgrade_button.click()
    time.sleep(5)
    #-- ページ遷移 --
    
    # 「期限を延長する」ボタンをクリック	
    extend_button = driver.find_element(By.LINK_TEXT, "期限を延長する")
    extend_button.click()
    time.sleep(5)
    #-- ページ遷移 --

    # 「延長期間」セレクトボックスを選択（例：72時間）
    select_element = driver.find_element(By.NAME, "period")
    select_element.send_keys("+72時間延長")  # または select_element.send_keys("72")

    # 「確認画面に進む」ボタンをクリック
    confirm_button = driver.find_element(By.XPATH, "//button[contains(text(), '確認画面に進む')]")
    confirm_button.click()
    time.sleep(5)
    #-- ページ遷移 --

    # 「期限を延長する」ボタンをクリック
    extend_button2 = driver.find_element(By.XPATH, "//button[contains(text(), '期限を延長する')]")
    extend_button2.click()
    time.sleep(5)
    
    #Indexに移動
    driver.get("https://secure.xserver.ne.jp/xmgame/game/index")
    time.sleep(5)

    # bodyタグのテキストをすべて取得
    body_text = driver.find_element(By.TAG_NAME, "body").text

    # 正規表現で「残り◯時間◯分」を抽出
    match = re.search(r"残り\s*(\d+)\s*時間\s*(\d+)\s*分", body_text)
    if match:
        hours = int(match.group(1))
        minutes = int(match.group(2))
        total_hours = hours + minutes / 60
        print(f"更新後：残り時間（合計）: {total_hours:.2f} 時間")

        # #メール送信
        # to_address = "yokopii865@yahoo.co.jp"
        # subject = "更新完了"
        # body = f"更新して {total_hours} 時間になりました。"

        # # Yahooメールの送信設定
        # from_address = "yokopii865@yahoo.co.jp"
        # password = "tukimiya865$"  # 通常のログインパスワードではなく、Yahooの「アプリ用パスワード」

        # # メール構築
        # msg = MIMEMultipart()
        # msg["From"] = from_address
        # msg["To"] = to_address
        # msg["Subject"] = subject
        # msg.attach(MIMEText(body, "plain"))

        # # SMTPサーバーに接続して送信
        # try:
        #     with smtplib.SMTP_SSL("smtp.mail.yahoo.co.jp", 465) as server:
        #         server.login(from_address, password)
        #         server.send_message(msg)
        #     print("メール送信完了")
        # except Exception as e:
        #     print("送信失敗:", e)

    else:
        print("更新後の時間が取れなかった")

else:
    print("24時間きってないから終了")
#    driver.quit()

# 終了（必要なら driver.quit()）



#テスト
#メール送信
# msg = MIMEText(f"更新して {total_hours} 時間になりました。")
# msg["Subject"] = "更新完了"
# msg["From"] = "your_verified_sender@example.com"
# msg["To"] = "yokopii865@yahoo.co.jp"

# server = smtplib.SMTP("smtp.sendgrid.net", 587)
# server.starttls()
# server.login("apikey", "YOUR_SENDGRID_API_KEY")
# server.send_message(msg)
# server.quit()
