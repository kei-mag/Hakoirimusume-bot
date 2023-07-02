from logging import getLogger
from pathlib import Path

from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseForbidden)
from django.views.decorators.csrf import csrf_exempt
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage

from line_bot_server.talk_request_handler import TalkRequestHandler

CHANNEL_ACCESS_TOKEN = "ubkUIO9xTAeNgB93VkoO1usacZSGdVdaACy7uIvPXDFsJK/EaczdFIGpwiVaOvb/crpjS5brDfBWlbKXq8JDpnVvT7FWo24xC5bh0dkHvwVRfogcjHxN7kN4ZclYDaL+acTAL2UUWWoh+Bihj+3rbwdB04t89/1O/w1cDnyilFU="
CHANNEL_SECRET = "307d7a0ee648a43af9804402f5779a28"

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

logger = getLogger(__name__)
request_handler = TalkRequestHandler(assets_dir=Path(__file__).parent.joinpath("assets"))


@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.headers['X-Line-Signature']
        body = request.body.decode('utf-8')
        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        else:
            return HttpResponse(status=200)
    else:
        return HttpResponseBadRequest


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event: MessageEvent):
    print(f"name={line_bot_api.get_profile(event.source.user_id).display_name}")
    logger.info(f"from: {event.source.user_id}, msg: {event.message.text}")
    line_bot_api.reply_message(event.reply_token,
                               request_handler.get_reply_object(event))
