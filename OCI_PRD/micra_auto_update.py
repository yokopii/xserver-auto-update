from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import re
import logging
from mail_notify import send_notification
from dotenv import load_dotenv
import os
import inspect

#.envファイル読み込み
load_dotenv()

#########
# 定数
#########
SERVER_CONFIG = {
    "chrome_path": "/usr/local/bin/chromedriver" 
}

LOG_CONFIG = {
    "log_file_path": os.getenv("MAIN_LOG_PATH")
}

##########################################
# main処理
##########################################
def main():

    #初期設定
    driver = None

    try:
        #Logging設定
        logging.basicConfig(
            filename=LOG_CONFIG["log_file_path"],
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt='%Y-%m-%d %H:%M:%S',
        )

        #driver初期セットアップ
        driver = setup_driver()

        #XServerログイン
        login_xserver(driver)

        #更新時間取得
        remining_time = get_remaining_time(driver)

        #サーバー残り時間が24時間を切っていれば更新する
        extend_server(driver, remining_time)
        
    except Exception as e:
        msg = f"main処理中に例外が発生しました: {str(e)}"
        output_log(msg, logging.ERROR)
        send_notify_mail("マイクラ自動更新処理失敗", msg)
    finally:
        try:
            if driver:
                driver.close()
                #driver.quit()  #ハングするから禁止(使っちゃダメ)
                return ""
        except Exception as e:
            msg = f"driver shutdown failed: {e}"
            output_log(msg, logging.ERROR)

##########################################
# Driver設定
##########################################
def setup_driver():

    output_log(inspect.currentframe().f_code.co_name + "execute...")

    # オプション設定
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-features=NetworkService")

    try:
        # ChromeDriverのパスを指定（Selenium 3.xでは executable_path を直接渡す）
        driver = webdriver.Chrome(executable_path=SERVER_CONFIG["chrome_path"], options=options)
        return driver
    except Exception as e:
        msg = f"setup_driver 失敗: {str(e)}"
        output_log("| 補足: ChromeDriverの呼び出しで失敗しています。")
        send_notify_mail("ChromeDriverの呼び出し処理失敗", msg)
        driver = None
        raise

    

##########################################
# Xserver ログイン操作
##########################################
def login_xserver(argDriver):

    output_log(inspect.currentframe().f_code.co_name + "execute...")
 
    try:
        # ログインページにアクセス（Xserver）
        argDriver.get(os.getenv("XSERVER_URL"))
        time.sleep(3)

        # ユーザーIDとパスワードを入力
        argDriver.find_element(By.ID, "memberid")     .send_keys(os.getenv("XSERVER_USER"))
        argDriver.find_element(By.ID, "user_password").send_keys(os.getenv("XSERVER_PASS"))

        # ログインボタンをクリック
        argDriver.find_element(By.CLASS_NAME, "btnSubmit").click()
        time.sleep(5)

    except Exception as e:
        msg = f"login_xserver 失敗: {str(e)}"
        output_log(msg, logging.ERROR)
        send_notify_mail("ログイン処理失敗", msg)
        raise  # ここで raise すれば main() 側で止められる
 
##########################################
# Xserver 更新残時間取得
##########################################
def get_remaining_time(argDriver):

    output_log(inspect.currentframe().f_code.co_name + "execute...")

    try:
        # ① 「サービス管理」ナビゲーションメニューをクリックして展開
        service_menu = WebDriverWait(argDriver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "serviceNav__toggle"))
        )
        service_menu.click()

        # ② 「ご利用中のサービス」内の「XServer GAMEs」をクリック
        xserver_games_link = argDriver.find_element(By.ID, "ga-xsa-serviceNav-xmgame")
        xserver_games_link.click()

        time.sleep(5)
        #-- ページ遷移 --

        # 「ゲーム管理」ボタンをクリック（テキスト一致で取得）
        game_manage_button = WebDriverWait(argDriver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[text()='ゲーム管理']"))
        )
        game_manage_button.click()

        time.sleep(5)

        #-- MAINページ遷移 --
        # bodyタグのテキストをすべて取得
        body_text = argDriver.find_element(By.TAG_NAME, "body").text

        # 正規表現で「残り◯時間◯分」を抽出
        match = re.search(r"残り\s*(\d+)\s*時間\s*(\d+)\s*分", body_text)
        if not match:
            output_log("残り時間の形式が取得できませんでした", logging.WARNING)
            return None

        # if match:
        remining_time = {
            "hours"       : int(match.group(1)),
            "minutes"     : int(match.group(2)),
            "total_hours" : int(match.group(1)) + int(match.group(2)) / 60,
        }
        print(f"残り時間（合計）: {remining_time['total_hours']:.2f} 時間")
        output_log(f"残り時間（合計）: {remining_time['total_hours']:.2f} 時間")

        return remining_time

    except Exception as e:
        print(f"更新残時間の取得で失敗しています: {str(e)}", logging.ERROR)
        output_log(f"更新残時間の取得で失敗しています: {str(e)}", logging.ERROR)
        raise

##########################################
# XServer 延長更新
##########################################
def extend_server(argDriver, argRemining_time):

    output_log(inspect.currentframe().f_code.co_name + "execute...")

    try:
        #サーバー残り時間が24時間を切っていれば更新する
        if argRemining_time["hours"] < 24:

            output_log("24時間切っている")

            #「アップグレード・期限延長」ボタンをクリック
            # upgrade_button = argDriver.find_element(By.LINK_TEXT, "アップグレード・期限延長")
            # upgrade_button.click()
            # time.sleep(5)
            # 「アップグレード・期限延長」リンクがクリック可能になるまで待機
            upgrade_button = WebDriverWait(argDriver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "アップグレード・期限延長"))
            )
            # スクロールして中央に表示
            argDriver.execute_script("arguments[0].scrollIntoView({block: 'center'});", upgrade_button)
            # クリック
            upgrade_button.click()

            #-- ページ遷移 --
            
            # 「期限を延長する」ボタンをクリック	
            extend_button = WebDriverWait(argDriver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "期限を延長する")))
            # スクロールして中央に表示
            argDriver.execute_script("arguments[0].scrollIntoView({block: 'center'});", extend_button)
            # クリック
            extend_button.click()

            #-- ページ遷移 --

            # 「延長期間」セレクトボックスを選択（例：72時間）
            select_element = argDriver.find_element(By.NAME, "period")
            select_element.send_keys("+72時間延長")  # または select_element.send_keys("72")

            # 「確認画面に進む」ボタンをクリック
            # confirm_button = argDriver.find_element(By.XPATH, "//button[contains(text(), '確認画面に進む')]")
            # confirm_button.click()
            # time.sleep(5)
            # 「確認画面に進む」ボタンがクリック可能になるまで待機
            confirm_button = WebDriverWait(argDriver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '確認画面に進む')]"))
            )

            # スクロールして中央に表示
            argDriver.execute_script("arguments[0].scrollIntoView({block: 'center'});", confirm_button)

            # クリック
            confirm_button.click()


            #-- ページ遷移 --

            # 「期限を延長する」ボタンをクリック
            # extend_button2 = argDriver.find_element(By.XPATH, "//button[contains(text(), '期限を延長する')]")
            # extend_button2.click()
            # time.sleep(5)
            # 「期限を延長する」ボタンが読み込み完了するまで待機（btn--loadingが消える）
            WebDriverWait(argDriver, 10).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "btn--loading"))
            )

            # 「期限を延長する」ボタンがクリック可能になるまで待機
            extend_button2 = WebDriverWait(argDriver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '期限を延長する')]"))
            )

            # スクロールして中央に表示
            argDriver.execute_script("arguments[0].scrollIntoView({block: 'center'});", extend_button2)

            # クリック
            extend_button2.click()

            # #Indexに移動
            argDriver.get("https://secure.xserver.ne.jp/xmgame/game/index")
            time.sleep(5)

            # bodyタグのテキストをすべて取得
            #body_text = argDriver.find_element(By.TAG_NAME, "body").text
            
            #延長更新後の残時間を取得
            updated_remining_time = get_remaining_time(argDriver)

            #正常終了メール送信
            send_notify_mail(f"更新完了[残:]{updated_remining_time['total_hours']}",f"更新処理が完了して {updated_remining_time['total_hours']} 時間になりました。")
        
        else:
            output_log(f"24時間切っていないので処理を終了します。残:{argRemining_time['total_hours']}")
            send_notify_mail(f"残が24時間以上あるので正常終了  残:{argRemining_time['total_hours']}","正常終了")
            output_log(f"メールとばしたよ")

    except Exception as e:
        output_log(f"extend_server内で例外が発生しました: {str(e)}", logging.ERROR)
        send_notify_mail(
            "更新処理中にエラー発生",
            f"XServer契約延長処理中に例外が発生しました。\n詳細: {str(e)}"
        )

##########################################
# メール送信
##########################################
def send_notify_mail(argSubject, argBody):
    subject="[XServer更新処理] " + argSubject
    send_notification(subject=subject, body=argBody, to=os.getenv("YMAIL_DESTINATION_ACCOUNT"))

##########################################
# ログ出力
##########################################
def output_log(argMsg, argLevel=logging.INFO):
    logging.log(argLevel, f" | 補足: {argMsg}")
    print(argMsg)

##########################################
#スクリプト時のみメイン実行
##########################################
if __name__ == "__main__":
    main()