# https://slack.dev/bolt-python/ja-jp/tutorial/getting-started

import os
import gspread
import requests
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from oauth2client.service_account import ServiceAccountCredentials

load_dotenv(verbose=True)
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# ボットトークンとソケットモードハンドラーを使ってアプリを初期化します
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# SpreadSheet関係
JSONF = 'credentials.json'
SPREADSHEET_KEY = os.environ.get('SPREADSHEET_KEY')
FORM_URL = os.environ.get('FORM_URL')

# USER名
KUSSY = 'U8TFEKDST'
SHALLEN = 'U9389LWTD'

def get_spreadsheet(sheet_name):
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(JSONF, scope)
    gc = gspread.authorize(credentials)
    worksheet = gc.open_by_key(SPREADSHEET_KEY).worksheet(sheet_name)
    return worksheet

# 「!show」というメッセージをリッスンして、金額をスプレッドシートから取得
@app.message('!show')
def show(say):
    sheet = get_spreadsheet('Summary')
    val = sheet.get('B7')[0][0]
    say(val)

@app.message('!pay')
def pay(message, say):
    args = message['text'].split()[1:]
    user = message['user']
    
    item = args[0]
    price = int(eval(args[1]))
    payer = user
    kussy_load = 1
    shallen_load = 1
    load_rate = '割り勘'

    if '-r' in args: # コマンド実行者が支払者と異なる
        if user == KUSSY:
            payer = 'しゃれんきゅん'
        elif user == SHALLEN:
            payer = 'くっしー'
    if '-k' in args: # くっしー負担分をしゃれんきゅんが立て替えた
        payer = 'しゃれんきゅん'
        kussy_load = 1
        shallen_load = 0
        load_rate = 'くっしー負担分をしゃれんきゅんが立て替えた'
    if '-s' in args: # しゃれんきゅん負担分をくっしーが立て替えた
        payer = 'くっしー'
        shallen_load = 1
        kussy_load = 0
        load_rate = 'しゃれんきゅん負担分をしゃれんきゅんが立て替えた'
    if '-tax8' in args: # 外税8%となっている
        price = int(price * 1.08)
    if '-tax10' in args: # 外税10%となっている
        price = int(price * 1.10)
    params = {
        'entry.435833506': payer, # 支払者
        'entry.700152849': price, # 支払額
        'entry.1246589948': item, # 物品名
        'entry.1088414711': shallen_load, #しゃれんきゅんの負担割合
        'entry.901523276': kussy_load, #くっしーの負担割合
    }
    res = requests.post(FORM_URL, params=params)
    if res.status_code == requests.codes.ok:
        message.send('コマンドにより出費登録がされました。\n' + 
            f'支払者: {payer}\n' +
            f'支払額: {price}\n' +
            f'物品名: {item}\n'+
            f'負担割合: {load_rate}\n')
    else:
        message.send('コマンドによる登録はエラーが発生しました。')

# アプリを起動します
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
    