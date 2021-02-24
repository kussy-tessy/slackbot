from slackbot.bot import respond_to
from slackbot.bot import listen_to
import re
from datetime import datetime, timedelta

@listen_to('あと(\d+)クレ', re.IGNORECASE)
def calc_time(message, credit):
    TIME_PER_CREDIT = timedelta(minutes=13)
    finish_at = datetime.now() + TIME_PER_CREDIT * int(credit)
    formatted = finish_at.strftime('%H:%M')
    message.send(f'終了予想 {formatted}')