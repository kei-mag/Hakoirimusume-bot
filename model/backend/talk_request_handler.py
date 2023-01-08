import json
from datetime import datetime
from typing import Any

from linebot.models import (ButtonsTemplate, ConfirmTemplate, FlexSendMessage,
                            MessageAction, MessageEvent, TemplateSendMessage,
                            TextMessage, TextSendMessage)
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

    Notes
    -----
    request type : \n
         0. default value (do nothing)
         1. authorize as user
         2. show menu
         3. request Rabbit's House Report
         4. turn on home-alone mode
         5. turn off home-alone mode
         6. check Aikotoba
         7. permit authorization
         8. delete my data
         9. show system-settings menu
        10. set notification temperature
        11. shutdown system
        12. promote to administrator
        13. logout from administrator
        14. [admin] delete particular user data
        15. [admin] get system information

    status type : \n
         0. default value (not busy)
         1. wait for Aikotoba
         7. wait for reply of permit authorization question
         8. wait for reply of ConfirmTemplate message about user data deletion
         9. wait for choice in system-settings menu
        10. wait for value of notification triger tempeature
        11. wait for reply of ConfirmTemplate message about shutdown
        12. wait for password of administration
        14. wait for choice of user to be delete
    """
    _TIME_OUT = 1  # min
    # request pattern [message, request type]
    _REQUEST_PATTERN: 'dict[str, int]' = {
        "ユーザー認証": 1,
        "メニュー": 2, "メニューを開いて": 2, "メニューをひらいて": 2, "メニュー開いて": 2, "メニューひらいて": 2,
        "げんき？": 3, "元気？": 3, "げんき?": 3, "元気?": 3, "げんき": 3, "元気": 3,
        "行ってきます！": 4, "行ってきます!": 4, "いってきます！": 4, "いってきます!": 4, "行ってきます": 4, "いってきます": 4,
        "ただいま。": 5, "ただいま!": 5, "ただいま！": 5, "ただいま": 5,
        "合言葉が何だったか教えて": 6,
        "ユーザー認証の許可設定": 7,
        "私のユーザー認証情報を削除して": 8,
        "システム設定を開いて": 9,
        "通知温度を変更する": 10,
        "サーバーをシャットダウンして": 11,
        "login-as-admin": 12,
        "logout-from-admin": 13,
        "for-admin.delete-user": 14,
        "for-admin.get-system_info": 15}
    # odd: positive form, even: negative form
    _REPLY_PATTERN: tuple = ("##Yes.##", "##No.##",
                             "##DELETE.##", "##CANCEL.##")

    def __init__(self) -> None:
        with open("backend/assets/menu.json", 'r', encoding='utf-8') as f:
            self.menu_data = json.load(f)
        self.report_creater = ReportCreater()
        self.current_requester = None

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
        print(
            f"talk_request_handler.py @getReplyObject first line: {str(self.current_requester)}")
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
                self.current_requester = {'user_id': event.source.user_id,
                                          'status': 1,
                                          'request_time': int(request_time.timestamp())}
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

    def _parse_request(self, message: str) -> int:
        """Parse request message from user.

        Parameters
        ----------
        message : str
            message from user

        Returns
        -------
        : int
            message type
        """
        try:
            return self._REQUEST_PATTERN[message]
        except KeyError:
            return 0

    def _timeOutCheck(self, request_time: datetime) -> None:
        if (self.current_requester is not None) and ((int(request_time.timestamp()) - self.current_requester['request_time']) > 60*self._TIME_OUT):
            self.current_requester = None
        return
