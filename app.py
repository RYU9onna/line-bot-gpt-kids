import os
import openai
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage,
)

# LINE のチャンネルシークレット
LINE_CHANNEL_SECRET = os.environ['LINE_CHANNEL_SECRET']
# LINE のチャンネルアクセストークン
LINE_ACCESS_TOKEN = os.environ['LINE_ACCESS_TOKEN']
# OpenAI APIのAPIキーの設定
openai.api_key = os.environ['OPENAI_API_KEY']

app = Flask(__name__)

line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/test")
def test():
    return "TEST OK"

@app.route("/", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
  try:

    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo-0301",
#      model="text-davinci-003",

      # 猫の部分はいじっても大丈夫
      messages=[
        {"role": "user", "content":event.message.text}
      ]
    )

    # AIからの応答を取得する
    print(response['choices'][0]['message']['content'])

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text = response['choices'][0]['message']['content']),
    )

  except InvalidRequestError as e:
    print(e)
    print(type(e))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
