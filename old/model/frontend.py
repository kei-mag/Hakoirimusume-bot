"""
LINE BOT "Hakoirimusume" server program

Please run this program after running "install.py"

(c) 2022 Keisuke Magara
"""

import os

from backend.talk_request_handler import TalkRequestHandler
from flask import Flask, abort, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage

try:
    YOUR_CHANNEL_ACCESS_TOKEN = os.environ["CHANNEL_ACCESS_TOKEN"]
    YOUR_CHANNEL_SECRET = os.environ["CHANNEL_SECRET"]
except KeyError:
    print("[ERROR] Environment variants is not defined correctly.\nPlease run \"install.sh\".\n")
    exit(1)


request_handler = TalkRequestHandler()

app = Flask(__name__)

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Reqest body:" + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token, request_handler.get_reply_object(event))


if __name__ == "__main__":
    app.run(port=21212)
