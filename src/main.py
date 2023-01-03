# https://slack.dev/bolt-python/ja-jp/tutorial/getting-started

import os
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

load_dotenv(verbose=True)
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# ボットトークンとソケットモードハンドラーを使ってアプリを初期化します
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

"""
# SpreadSheet関係
JSONF = 'credentials.json'
SPREADSHEET_KEY = os.environ.get('SPREADSHEET_KEY')
FORM_URL = os.environ.get('FORM_URL')

def get_spreadsheet(sheet_name):
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(JSONF, scope)
    gc = gspread.authorize(credentials)
    worksheet = gc.open_by_key(SPREADSHEET_KEY).worksheet(sheet_name)
    return worksheet
"""

# 「!show」というメッセージをリッスンして、金額をスプレッドシートから取得
@app.message('!show')
def show(message, say):
    say('hey!')
    sheet = get_spreadsheet('Summary')
    val = sheet.get('B7')[0][0]
    say(val)
    print(message)

# アプリを起動します
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()