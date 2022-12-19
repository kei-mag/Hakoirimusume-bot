from linebot import (
    LineBotApi, WebhookHandler
    )
from linebot.exceptions import (
    InvalidSignatureError
    )
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FlexSendMessage, TemplateSendMessage, ConfirmTemplate, MessageAction, ButtonsTemplate
    )

YOUR_CHANNEL_ACCESS_TOKEN = "<CHANNEL ACCESS TOKEN VALUE>"
user_id = "<USER ID VALUE>"
rich_menu_id = "<RICH MENU ID VALUE>"

line_bot_api = LineBotApi (YOUR_CHANNEL_ACCESS_TOKEN)
line_bot_api.unlink_rich_menu_from_user(user_id)
line_bot_api.link_rich_menu_to_user(user_id, rich_menu_id)
