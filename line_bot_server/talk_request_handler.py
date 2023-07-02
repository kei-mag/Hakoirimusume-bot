from __future__ import annotations

import json
from datetime import datetime
from logging import getLogger
from pathlib import Path

from linebot.models import (ButtonsTemplate, ConfirmTemplate, FlexSendMessage,
                            MessageAction, MessageEvent, TemplateSendMessage,
                            TextMessage, TextSendMessage)

from line_bot_server.models import User
from line_bot_server.user_manager import UserManager

logger = getLogger(__name__)


class TalkRequestHandler:
    _REQUEST_PATTERN = {
        "ユーザー認証": 1,
        "メニュー": 2, "メニューを開いて": 2, "メニューをひらいて": 2, "メニュー開いて": 2, "メニューひらいて": 2,
        "げんき？": 3, "元気？": 3, "げんき": 3, "元気": 3,
        "行ってきます！": 4, "いってきます！": 4, "行ってきます": 4, "いってきます": 4,
        "ただいま。": 5, "ただいま！": 5, "ただいま": 5,
        "合言葉が何だったか教えて": 6,
        "ユーザー認証の許可設定": 7,
        "私のユーザー認証情報を削除して": 8,
        "システム設定を開いて": 9,
        "通知温度を変更する": 10,
        "サーバーをシャットダウンして": 11,
        "login-as-admin": 12,
        "logout-from-admin": 13,
        "for-admin.delete-user": 14,
        "for-admin.get-system_info": 15,
        }
    _REPLY_PATTERN = {
        "##Yes.##": "positive",
        "##No.##": "negative",
        "##DELETE.##": "positive",
        "##CANCEL.##": "negative"
    }
    
    def __init__(self, assets_dir: Path | str = "assets") -> None:
        if isinstance(assets_dir, str):
            assets_dir = Path(assets_dir)
        with open(assets_dir.joinpath("menu.json"), mode="r", encoding="utf-8") as fp:
            self.menu_data = json.load(fp)
        self.user_manager = UserManager()

    def get_reply_object(self, event: MessageEvent):
        request_time = datetime.now()
        requester_id = event.source.user_id
        message = event.message.text
        request_type = self._parse_request(message)
        if request_type == 1:
            print(self.user_manager.generate_aikotoba())
            self.user_manager.add_user(requester_id, 'user')
        try:
            requester = User.objects.get(user_id=event.source.user_id)
        except User.DoesNotExist:
            return TextSendMessage("You are not user.")
        return TextSendMessage(f"{request_time}\n{message}\nrequest={request_type}")
    
    def _parse_request(self, msg: str):
        if msg in self._REQUEST_PATTERN:
            return self._REQUEST_PATTERN[msg]
        else:
            return -1