import os
import re
import json
import gspread
import requests
from slackbot.bot import respond_to
from slackbot.bot import listen_to
from oauth2client.service_account import ServiceAccountCredentials
from os.path import join, dirname
from dotenv import load_dotenv

load_dotenv(verbose=True)
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

JSONF = 'credentials.json'
SPREADSHEET_KEY = os.environ.get('SPREADSHEET_KEY')
FORM_URL = os.environ.get('FORM_URL')

def get_spreadsheet(sheet_name):
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(JSONF, scope)
    gc = gspread.authorize(credentials)
    worksheet = gc.open_by_key(SPREADSHEET_KEY).worksheet(sheet_name)
    return worksheet

@listen_to('!show')
def show(message):
    sheet = get_spreadsheet('Summary')
    val = sheet.get('B7')[0][0]
    message.send(val)

@listen_to('!help')
def help(message):
    message.send('!show 支払額確認')
    message.send('!pay [物品名] [金額(数式可)] 支払登録 \n オプション: \n' +
        '-r: コマンド実行者と支払い者が異なる。\n' +
        '-k: くっしー負担分をしゃれんきゅんが立て替えた。\n' +
        '-s: しゃれんきゅん負担分をくっしーが立て替えた。\n' +
        '-tax8: 8%外税\n' +
        '-tax10: 10%外税')

@listen_to('!pay(.+)', re.IGNORECASE)
def pay(message, args):
    args = args.split()
    user = message.channel._client.users[message.body['user']]['real_name']
    
    item = args[0]
    price = int(eval(args[1]))
    payer = user
    kussy_load = 1
    shallen_load = 1
    load_rate = '割り勘'

    if '-r' in args: # コマンド実行者が支払者と異なる
        if user == 'くっしー':
            payer = 'しゃれんきゅん'
        elif user == 'しゃれんきゅん':
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
    message.send('コマンドにより出費登録がされました。\n' + 
        f'支払者: {payer}\n' +
        f'支払額: {price}\n' +
        f'物品名: {item}\n'+
        f'負担割合: {load_rate}\n')

"""    
user    = message.channel._client.users[message.body['user']]
channel = message.channel._client.channels[message.body['channel']]
message.send(f'{user["real_name"]}{channel["name"]}')
"""