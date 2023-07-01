from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

CHANNEL_ACCESS_TOKEN = "ubkUIO9xTAeNgB93VkoO1usacZSGdVdaACy7uIvPXDFsJK/EaczdFIGpwiVaOvb/crpjS5brDfBWlbKXq8JDpnVvT7FWo24xC5bh0dkHvwVRfogcjHxN7kN4ZclYDaL+acTAL2UUWWoh+Bihj+3rbwdB04t89/1O/w1cDnyilFU="
CHANNEL_SECRET = "307d7a0ee648a43af9804402f5779a28"

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)


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


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event: MessageEvent):
    print(event.message.text)
    line_bot_api.reply_message(event.reply_token,
                               TextSendMessage(text="こんにちは"))
