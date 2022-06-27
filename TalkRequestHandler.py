from typing import Any
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FlexSendMessage, 
    TemplateSendMessage, ConfirmTemplate, MessageAction, ButtonsTemplate
    )

class TalkRequestHandler:
    """Handle request received from LINE talk message.

    Attributes
    ----------
    requestTemplates @class : dict[str, int]
        dictionary linking request symbol and request type
    
    currentRequester : None or str
        LINE user ID of current requester

    Notes
    -----
    request type : \n
         0. default value (do nothing)
         1. authorize as user
         2. show menu
         3. request Rabbit House Report
         4. turn on home-alone mode
         5. turn off home-alone mode
         6. check Aikotoba
         7. permit authorization
         8. delete my data
         9. set notification temperature
        10. promote to administrator
        11. logout from administrator
        12. [admin] delete particular user data
        13. [admin] get system information
    """
    requestTemplates:'dict[str, int]' = { 
        "ユーザー認証": 1,
        "メニュー": 2, "メニューを開いて": 2, "メニューをひらいて": 2,
        "げんき？": 3, "元気？": 3, "げんき?": 3, "元気?": 3, "げんき": 3, "元気": 3,
        "行ってきます！": 4, "行ってきます!": 4, "いってきます！": 4, "いってきます!": 4, "行ってきます": 4, "いってきます": 4,
        "ただいま。": 5, "ただいま!": 5, "ただいま！": 5, "ただいま": 5,
        "合言葉が何だったか教えて": 6,
        "ユーザー認証機能の設定": 7,
        "私のユーザー認証情報を削除して": 8,
        "通知温度を変更して": 9,
        "login-as-admin": 10,
        "logout-from-admin": 11,
        "for-admin.delete-user": 12,
        "for-admin.get-system_info": 13 }
    replyTemplate = ("##Yes.##", "##No.##", "##DELETE.##", "##CANCEL.##")   # 奇数が肯定形, 偶数が否定形

    def getReplyObject(self, event) -> Any:
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
        pass

    def parseRequest(self, message:str):
        """Parse request message from user.

        Parameters
        ----------
        message : str
            message from user
        """
        pass