from linebot import LineBotApi
from linebot.models import FlexSendMessage
import json
import os

YOUR_CHANNEL_ACCESS_TOKEN = "<CHANNEL ACCESS TOKEN VALUE>"

line_bot_api = LineBotApi (YOUR_CHANNEL_ACCESS_TOKEN)

def main():
    os.system("python3 ./makeflex.py")
    f = open("./flexmessage.json", "r")
    json_data = json.load(f)
    container_obj = FlexSendMessage(alt_text='Rabbit House Report', contents=json_data)
    f = open ("./go_away", "r")
    send_list = f.read().splitlines()
    for i in range(len(send_list)):
        send_id = send_list[i]
        line_bot_api.push_message(send_id, messages=container_obj)

if __name__ == "__main__":
    main()
