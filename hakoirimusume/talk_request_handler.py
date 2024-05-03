import json
from datetime import datetime
from typing import Any

from linebot.models import (
    ButtonsTemplate,
    ConfirmTemplate,
    FlexSendMessage,
    MessageAction,
    MessageEvent,
    TemplateSendMessage,
    TextMessage,
    TextSendMessage,
)
from report_creater import ReportCreater


class TalkRequestHandler:
    """Handle request received from LINE talk message.

    Attributes
    ----------
    _REQUEST_PATTERN @class : dict[str, int]
        dictionary linking request message and request type

    _REPLY_PATTERN @class : tuple
        tuple of reply pattern

    current_requester : None or dict[str, int]
        LINE user ID of current requester, the user's last status, and last request time
        {
            "user_id": <User ID of current requester>,
            "status": <status type of current requester>,
            "request_time": <time to recieve last request message from current requester>
        }
    """

    TIME_OUT = 5  # min

    def __init__(self, request_definition) -> None:
        with open("backend/assets/menu.json", "rb") as f:
            self.menu_data = json.load(f)
        self.report_creater = ReportCreater()
        self.request_type = request_definition["request_type"]
        self.request_query = request_definition["request_query"]
        

    def get_reply_object(self, event) -> Any:
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
        print(f"talk_request_handler.py @getReplyObject first line: {str(self.current_requester)}")
        request_time = datetime.now()
        self._timeOutCheck(request_time)
        message_type = self._parse_request(event.message.text)

        # if server is busy
        if (message_type != 0) and (self.current_requester is not None):
            if event.source.user_id != self.current_requester:
                return TextSendMessage("今、他の人が利用中だよ。\nちょっと待ってから\nもう１回訊いてみて！")
            else:
                # todo: multi-step function
                pass
        else:
            if message_type == 1:
                self.current_requester = {
                    "user_id": event.source.user_id,
                    "status": 1,
                    "request_time": int(request_time.timestamp()),
                }
                return TextSendMessage(">> ユーザー認証をします。 <<\n合言葉を送信してください\n(一字一句正確に!)")

            elif message_type == 2:
                self.current_requester = None
                return FlexSendMessage(alt_text="メニュー", contents=self.menu_data)

            elif message_type == 3:
                self.current_requester = None
                return self.report_creater.get_report()

            elif message_type == 4:
                # todo: 留守番モードに設定
                return TextSendMessage("いってらっしゃい！\n留守番モードで待ってるね♪")

            elif message_type == 5:
                # todo: 留守番モード解除
                return TextSendMessage("おかえり！\n留守番モードを解除するね\n^(>v<)^")

            elif message_type == 6:
                return TextSendMessage("合言葉は、\n<<これから実装>>\nだよ～")

            elif message_type == 7:
                return TextSendMessage("まだ実装されていません！")

            elif message_type == 8:
                pass

            elif message_type == 9:
                pass

            elif message_type == 10:
                pass

            elif message_type == 11:
                pass

            elif message_type == 12:
                pass

            elif message_type == 13:
                pass

            elif message_type == 14:
                pass
            else:
                # not request
                pass

        return TextSendMessage("予期しない動作を確認しました。\nもう一度最初からやり直してください。")

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