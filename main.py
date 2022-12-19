from flask import Flask, request, abort
import subprocess
from subprocess import PIPE
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FlexSendMessage, TemplateSendMessage, ConfirmTemplate, MessageAction, ButtonsTemplate
)
import os
import json

app = Flask(__name__)

YOUR_CHANNEL_ACCESS_TOKEN = "<CHANNEL ACCESS TOKEN VALUE>"
YOUR_CHANNEL_SECRET = '<CHANNEL SECRET VALUE>'

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
    password = '<PLEASE SET PASSWORD HERE>'
    adminpass = '<PLEASE SET ADMIN PASSWORD HERE>'
    rich_menu_id = "<RICH MENU ID VALUE>"
    noauth = "認証済みユーザーでないと利用できません。\n\"ユーザー認証\" と言うと、ユーザー認証を開始できます。"
    reply_message = ""
    print(search('user_list', event.source.user_id))
    if (get_flag('auth') == event.source.user_id and event.message.text != password):
        reply_message = ""
        set_flag('auth', -2)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(
            text=">> 合言葉が違います <<\n最初からやり直してください。"))
    if (search('user_list', event.source.user_id) == True):
        if (get_flag('auth') == '-'+str(event.source.user_id)):
            user = -1
        else:
            user = 1
    else:
        user = 0
    if (event.message.text == '合言葉が何だったか教えて' and user == 1):
        reply_message = "合言葉は\n\" " + password + " \"\nです。"
    elif (event.message.text == 'ユーザー認証機能の設定' and user == 1):
        reply_message = ""
        AltText = ""
        Text = ""
        if (get_flag('auth') == '0'):
            AltText = "ユーザー認証機能をロックしますか？"
            Text = "現在、新規ユーザー認証は許可されています。\nユーザー認証機能を無効にしますか？"
        else:
            AltText = "ユーザー認証機能を有効化しますか？"
            Text = "現在、新規ユーザー認証は許可されていません。\nユーザー認証機能を有効にしますか？"
        confirm_template_message = TemplateSendMessage(
            alt_text=AltText,
            template=ConfirmTemplate(
                text=Text,
                actions=[
                    MessageAction(
                        label='はい',
                        text='##Yes.##'
                    ),
                    MessageAction(
                        label='いいえ',
                        text='##No.##'
                    )
                ]
            )
        )
        line_bot_api.reply_message(
            event.reply_token, messages=confirm_template_message)
    elif (event.message.text == "##Yes.##" and user == 1):
        if (get_flag('auth') == '0'):
            reply_message = "> ユーザー認証機能をロック <\n解除するまで新規のユーザー認証はできません。"
            set_flag('auth', '-1')
        else:
            reply_message = "> 新規ユーザー認証を許可 <\nセキュリティリスクの観点から、新規の認証が終わったらもう一度認証機能をロックしてください。"
            set_flag('auth', 0)
    elif (event.message.text == "##No.##"):
        reply_message = "何も変更されませんでした。"
        if (user == -1):
            set_flag('./auth', '0')
# ここに追加（インデント注意！）
    elif (event.message.text == 'ユーザー認証'):
        if (user == 1):
            reply_message = "あなたは既にユーザー認証済みです。"
        else:
            flag = get_flag('auth')
            print("flag="+flag)
            if (flag == '0'):
                set_flag('auth', event.source.user_id)
                reply_message = ">> ユーザー認証をします。 <<\n合言葉を送信してください\n(一字一句正確に!)"
            elif (flag == '-1'):
                reply_message = "現在、新規のユーザー認証はロックされています。"
            elif (flag == '-2'):
                pass
            else:
                reply_message = "現在、他の誰かがユーザー認証操作中です。\n時間をおいてお試しください。"

    elif (event.message.text == password and get_flag('auth') == event.source.user_id):
        if (search("user_list", event.source.user_id) == True):
            reply_message = "あなたは既にユーザー認証済みです。"
        else:
            reply_message = "ユーザー認証成功。ようこそ！"
            f = open("./user_list", "a")
            f.write(event.source.user_id+"\n")
            f.close()
            line_bot_api.link_rich_menu_to_user(
                event.source.user_id, rich_menu_id)
        set_flag('auth', 0)
    elif (event.message.text == 'げんき？' or event.message.text == 'げんき?' or event.message.text == '元気？' or event.message.text == '元気?' or event.message.text == 'げんき'):
        if (user == 1):
            reply_message = ""
            ##########
            os.system("python3 ./makeflex.py")
            f = open("./flexmessage.json", "r")
            json_data = json.load(f)
            json_data["footer"]["contents"][0]["text"] = ">> 手動呼び出し"
            container_obj = FlexSendMessage(
                alt_text='Rabbit House Report', contents=json_data)
            line_bot_api.reply_message(
                event.reply_token, messages=container_obj)
        else:
            reply_message = noauth
    elif (event.message.text == '行ってきます！' or event.message.text == '行ってきます!' or event.message.text == 'いってきます！' or event.message.text == 'いってきます!' or event.message.text == '行ってきます' or event.message.text == 'いってきます'):
        if (user == 1):
            reply_message = "いってらっしゃい！\n留守番モードで待ってるね♪"
            target = "0"
            try:
                target = event.source.group_id
            except AttributeError:
                target = event.source.user_id
            if (search('go_away', target) == False):
                f = open("./go_away", "a")
                f.write(target+"\n")
                f.close()
        else:
            reply_message = noauth
    elif (event.message.text == 'ただいま。' or event.message.text == 'ただいま!' or event.message.text == 'ただいま！' or event.message.text == 'ただいま'):
        if (user == 1):
            try:
                file_del('go_away', event.source.group_id)
            except AttributeError:
                file_del('go_away', event.source.user_id)
            finally:
                reply_message = "おかえり！\n留守番モードを解除するね\n^(・v・)^"
        else:
            reply_message = noauth
    elif (event.message.text == 'メニュー' or event.message.text == 'めにゅー'):
        if (user == 1 or user == 2):
            reply_message = ""
            f = open("./menu.json", "r")
            json_data = json.load(f)
            container_obj = FlexSendMessage(
                alt_text='MENU', contents=json_data)
            line_bot_api.reply_message(
                event.reply_token, messages=container_obj)
        else:
            reply_message = noauth
    elif (event.message.text == '私のユーザー認証情報を削除して' and user == 1):
        if (search('user_list', event.source.user_id) == True):
            set_flag('./auth', '-'+str(event.source.user_id))
            profile = line_bot_api.get_profile(event.source.user_id)
            reply_message = "あなたの情報であるか確認してください。\n名前: "+profile.display_name+"\nステータスメッセージ: "+profile.status_message+"\nユーザーID: " + \
                profile.user_id[:7] + \
                "...\n\n上記が自分の情報であり、認証情報の削除を望む場合は、\n\" ##DELETE## \"\nを、キャンセルする場合は\n\" ##No.## \"\nを送信してください。"
        else:
            reply_message = "あなたの情報がユーザーリストから見つかりませんでした。\nデータ不整合が起きている可能性がありますので、管理者にお伝えください。"
    elif (event.message.text == '##DELETE##' and user == -1):
        reply_message = "あなたの情報を削除しました。\nサービスを再び利用したい場合には、ユーザー認証からやり直してください。"
        file_del('./user_list', event.source.user_id)
        line_bot_api.unlink_rich_menu_from_user(event.source.user_id)
        set_flag('./auth', '0')
    elif (event.message.text == 'for-admin.get-system_info' and user == 1):
        if (search('./admin-user_list', event.source.user_id) == True):
            hostname = subprocess.run(
                "hostname", shell=True, stdout=PIPE, stderr=PIPE, text=True)
            localip = subprocess.run(
                "hostname -I", shell=True, stdout=PIPE, stderr=PIPE, text=True)
            reply_message = "> システム情報 <\nhostname: " + \
                str(hostname.stdout)+"\nlocal IP: "+str(localip.stdout)
        else:
            reply_message = "この機能は管理者以外は利用できません。"
    elif (event.message.text == 'for-admin.set-system_config' and user == 1):
        # まだ開発途中===================================================
        reply_message = "この機能はまだ開発中です。\n乞うご期待！！"
        # if (search('./admin-user_list', event.source.user_id) == True):
        # None
        # ^^この上に追加（インデントに注意！）^^ <<=======================
    else:
        pass
    if (get_flag('auth') == '-2'):
        set_flag('auth', 0)
    if (reply_message != ''):
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_message))
    print("UserID:"+event.source.user_id)


def set_flag(name, number):
    f = open("./"+name, "w")
    f.write(str(number))
    f.close()


def get_flag(name):
    f = open("./"+name, "r")
    r = f.readline()
    f.close()
    return r


def search(file, target):
    flag = 0
    f = open("./"+file, "r")
    scan = f.read().splitlines()
    r = target in scan
    return r


def file_del(filename, target):
    f = open("./"+filename, "r+")
    scan = f.read().splitlines()
    f.close()
    f = open("./"+filename, "w")
    l = target in scan
    try:
        scan.remove(target)
    except ValueError:
        pass
    for i in range(len(scan)):
        scan[i] = scan[i] + "\n"
        f.writelines(scan)
    l = target in scan
    f.close()
    return l


if __name__ == "__main__":
    app.run(port=21212)
