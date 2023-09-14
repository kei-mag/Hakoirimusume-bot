import os
import sys
from datetime import datetime
from sqlite3 import OperationalError

import yaml
from flask import current_app
from linebot.v3.messaging.models import (ConfirmTemplate, FlexContainer,
                                         FlexMessage, QuickReply, TextMessage)

from hakoirimusume.authorities_manager import AuthoritiesManager
from hakoirimusume.db import get_db
from hakoirimusume.report_creator import ReportCreator


class TalkRequestHandler:
    """Handle request received from LINE talk message."""

    TIME_OUT = 5  # min.

    # User State
    STATE_NORMAL = 0
    STATE_WAIT_FOR_AIKOTOBA = 1
    STATE_CONFIRM_SHUTDOWN = 2
    STATE_WAIT_FOR_TEMPERATURE = 3
    STATE_CONFIRM_DELETE = 4
    STATE_WAIT_FOR_ADMIN_PASS = 5

    def __init__(self) -> None:
        root = current_app.root_path
        # Load menu structure
        with open(f"{root}/resources/menu.json", "r", encoding="UTF-8") as f:
            self.menu_data = FlexContainer.from_json(f.read())
        # Load request map
        with open(f"{root}/resources/acceptable_requests.yml") as f:
            data = yaml.safe_load(f)
            self.request_type = data["request_type"]
            self.request_query = data["request_query"]
        # Initialize other classes
        self.report_creator = ReportCreator()
        self.otp_timeout = current_app.config["AIKOTOBA_EXPIRED_TIME"]
        self.auth_manager = AuthoritiesManager(self.otp_timeout)

    def get_user_state(self, user_id):
        db = get_db()
        cur = db.cursor()
        # TIMEOUT
        cur.execute(
            f"UPDATE user SET request_state={self.STATE_NORMAL} WHERE strftime('%s', datetime(request_time, '+{self.TIME_OUT} seconds'))<strftime('%s', 'now');"
        )
        db.commit()
        try:
            state = cur.execute(f"SELECT request_state FROM user WHERE id='{user_id}'").fetchone()
            if state is None:
                return state
            else:
                return state[0]
        except OperationalError:
            return None

    def set_user_state(self, user_id, state=0):
        db = get_db()
        cur = db.cursor()
        try:
            cur.execute(f"UPDATE user SET request_state={state}, request_time=datetime('now') WHERE id='{user_id}';")
            db.commit()
        except OperationalError:
            pass
        return

    def get_reply(self, event):
        """Provide reply message to server

        Parameters
        ----------
        event : linebot.models.MessageEvent
            object saving properties of request message.

        Returns
        -------
        replyObject : TextSendMessage or FlexSendMessage or TemplateSendMessage
                        or ConfirmTemplate or MessageAction or ButtonsTemplate
            reply message object
        """
        message = event.message.text
        # todo: delete when finish ----------------
        if message == "db":
            print("dbdb")
            db = get_db()
            cur = db.cursor()
            result = db.execute("SELECT datetime('now');").fetchone()[0]
            print("curTime", result)
            print("--------------- user ---------------")
            result = db.execute("SELECT * from user;").fetchall()
            for r in result:
                for v in r:
                    print(v, end="\t")
                print("")
            print("--------------- otp ---------------")
            result = db.execute("SELECT * from otp;").fetchall()
            for r in result:
                for v in r:
                    print(v, end="\t")
                print("")
            return [TextMessage(quickReply=None, text="Check console")]
        # todo: delete -------------------------
        user_id = event.source.user_id
        user_auth = self.auth_manager.is_user(user_id)
        user_state = self.get_user_state(user_id)
        print(user_id, user_auth, user_state, type(user_state))
        if user_state is not None and user_state != self.STATE_NORMAL:
            if user_state == self.STATE_WAIT_FOR_AIKOTOBA:
                result = self.auth_manager.authorize(user_id, message, self.auth_manager.NORMAL_USER)
                self.set_user_state(user_id)
                if result is True:
                    quick_reply = {
                        "items": [
                            {"type": "action", "action": {"type": "message", "label": "メニュー", "text": "メニューをひらいて"}}
                        ]
                    }
                    return [
                        TextMessage(quickReply=None, text="ユーザー認証が完了しました。"),
                        TextMessage(quickReply=QuickReply.from_dict(quick_reply), text="こんにちは！「使い方」と言ってみてください。"),
                    ]
                elif result is False:
                    quick_reply = {
                        "items": [
                            {"type": "action", "action": {"type": "message", "label": "再度認証する", "text": "ユーザー認証"}}
                        ]
                    }
                    return [
                        TextMessage(quickReply=QuickReply.from_dict(quick_reply), text="ユーザー認証に失敗しました。\nもう一度試してみてください。")
                    ]
                else:
                    return [TextMessage(quickReply=None, text="あなたは既にユーザーのようです。")]
            elif user_state == self.STATE_CONFIRM_SHUTDOWN:
                request = self._parse_request(message)
                self.set_user_state(user_id)
                if request is True:
                    # os.system("shutdown -h")
                    return [TextMessage(quickReply=None, text="シャットダウンします")]
            elif user_state == self.STATE_WAIT_FOR_TEMPERATURE:
                self.set_user_state(user_id)
                return [TextMessage(quickReply=None, text="WAIT_FOR_TEMPERATURE→NORMAL")]
            elif user_state == self.STATE_CONFIRM_DELETE:
                self.set_user_state(user_id)
                return [TextMessage(quickReply=None, text="CONFIRM_DELETE→NORMAL")]
            elif user_state == self.STATE_WAIT_FOR_ADMIN_PASS:
                self.set_user_state(user_id)
                return [TextMessage(quickReply=None, text="WAIT_FOR_ADMIN_PASS→NORMAL")]
            else:
                self.set_user_state(user_id)
                print("<ERROR> Undefined User State")
                pass
        request = self._parse_request(message)
        if request is None:  # message is not a request
            return None
        else:
            if request == "authorize":
                self.set_user_state(user_id, self.STATE_WAIT_FOR_AIKOTOBA)
                return [
                    TextMessage(quickReply=None, text="ユーザー認証をします。"),
                    TextMessage(quickReply=None, text="合言葉を入力してください。\n(一字一句正確に！)"),
                ]
            elif request == "invite_user":
                password = self.auth_manager.invite_user(user_id, 0)
                if password is False:
                    text = ["権限がないため、新たなユーザーを招待できません。\n他の方に依頼してください。"]
                else:
                    text = [
                        "新しいユーザーのための合言葉を生成します。\n合言葉は、",
                        password,
                        "です。\nこの合言葉を招待したいユーザーに伝えてください。",
                        f"※合言葉は{self.otp_timeout}秒有効です。\n認証できない場合はもう一度招待をやり直してください。",
                    ]
                return [TextMessage(quickReply=None, text=t) for t in text]
            elif request == "open_menu":
                return [FlexMessage(quickReply=None, altText="メニュー", contents=self.menu_data)]
            elif request == "request_report":
                return [self.report_creator.get_report()]
            elif request == "turn_on_leave_mode":
                return [TextMessage(quickReply=None, text="外出モードオン")]
            elif request == "turn_off_leave_mode":
                return [TextMessage(quickReply=None, text="外出モードオフ")]
            elif request == "delete_user_data":
                return [TextMessage(quickReply=None, text="ユーザー削除")]
            elif request == "open_settings":
                return [TextMessage(quickReply=None, text="設定を開く")]
            elif request == "configure_temperature":
                return [TextMessage(quickReply=None, text="温度設定")]
            elif request == "shutdown_server":
                return [TextMessage(quickReply=None, text="サーバーシャットダウン")]
            else:
                return [TextMessage(quickReply=None, text="[想定外のリクエスト]\nエラーが発生しました。開発者に連絡し、もう一度やり直してください。")]

    def _parse_request(self, message: str):
        """Parse request message from user.

        Parameters
        ----------
        message : str
            message from user

        Returns
        -------
        request_type: str | None
            Type of request from user or None if message is not a request.
        """
        try:
            return self.request_query[message]
        except KeyError:
            return None


class StateManager:
    def set_state(self, s):
        # データベースのユーザーステートを設定
        # ユーザーのリクエストタイムを設定
        ...

    def _check_time_out(self, request_time: datetime) -> None:
        # if <リクエスト時間> - <前回のリクエスト時間> > TIMEOUT:
        #   ユーザーステートをdefaultに
        # else:
        #   なにもしない
        # リクエスト時間を今に
        ...
