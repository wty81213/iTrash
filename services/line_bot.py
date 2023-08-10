import os, json
import time
import datetime
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, AudioSendMessage, QuickReply, QuickReplyButton, MessageAction, PostbackAction, TemplateSendMessage, ConfirmTemplate, MessageTemplateAction, FollowEvent
from flask import Flask
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models.send_messages import VideoSendMessage
from services.api_init import ApiInfo, LineBotInfo
from dotenv import load_dotenv
from flask import request, abort

from services.utils.utils import answer_response, question_options, is_user_inactive, is_skip_predict


line_bot = LineBotInfo()
app = line_bot.app
line_bot_api = line_bot.line_bot_api
last_input_time = line_bot.last_input_time
inactive_threshold = line_bot.inactive_threshold
message_queue = line_bot.message_queue
last_id = ""
input_message = ""


line_bot_api_new = LineBotApi('znGqCb0IVXqlwW/3a4ZLfO9IQVvSvcN8MV5RjzG9Rs4dmqL+qLt8eEn1W2oIXQr3UnT+Q0QQ+i2KR+bnGbPO0T3SqGuIz6dZ1n5TJyZEgsuLPZYYGe60ZyKXTqhFGYUqsh7KVcW06VOYk6lnjm7gwQdB04t89/1O/w1cDnyilFU=')
handler_new = WebhookHandler('94d708d169f17c9cca0cfc4d8c22b668')

with open("config/config.json", "r") as f:
        no_id_list = json.load(f)["no_id_list"]

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        line_bot.handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

def yes_no_message(response):
    message = TemplateSendMessage(
        alt_text="yes and no",
        template=ConfirmTemplate(
            text=response["content"],
            actions=[
                MessageTemplateAction(
                    label= subclass["name"],
                    text=subclass["name"]
                ) for subclass in response["subclasses"]
            ]
        )
    )

    return message




def people_handle_message(event):
    
    user_input = event.message.text

    print("user_input: ", user_input)

    if user_input == "請稍候，我們將盡速為您服務，不好意思造成您的不便":
        # Use the reply token to reply to the user's message
        response_text = "請稍等，我將為您轉接至客服人員。"
        line_bot_api_new.reply_message(
            event.reply_token,
            TextSendMessage(text=response_text)
        )
        
        # Push a message to the user indicating that they are being connected to a live agent
        line_bot_api_new.push_message(
            event.source.user_id,
            TextSendMessage(text="您即將轉接至客服人員。請稍等片刻。")
        )
    else:
        response_text = "您好，這是一個機器人回覆。"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response_text)
        )

# @line_bot_api_new.add(MessageEvent, message=TextMessage):
# def handle_message_new(event):
#     people_handle_message(event)

@line_bot.handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    global last_input_time
    global last_id
    global input_message

    print('event: ', event)


    
    # get user message
    mtext = event.message.text

    # body = request.get_data(as_text=True)

    current_time = event.timestamp / 1000 # time.time()

   

    # # print("event: ", event)
    # print("first_time_chat: ", line_bot.first_time_chat)
    # print("is_user_inactive: ", is_user_inactive(last_input_time, current_time, inactive_threshold))

   # chek if the user chat with line bot first time
    if line_bot.first_time_chat or is_user_inactive(last_input_time, current_time, inactive_threshold):
        text = "你可能遇到下列問題"

        # return default options to user
        options = question_options()
        line_bot.first_time_chat = False
    else:
        match (mtext):
            case ("iTrash基本資訊"):
                id = "TQ001"
            case ("收費制度"):
                id = "SQ001"
            case ("如何使用機台"):
                id = "SQ002"
            case ("企業合作洽談"):
                id = "SQ003"
            case ("客服電話"):
                id = "SQ004"
            case ("詢問瓶子相關"):
                id = "TQ002"
            case ("瓶罐建立條碼"):
                id = "SQ005"
            case ("機台卡瓶子"):
                id = "SQ006"
            case ("瓶罐無法投入"):
                id = "SQ007"
            case ("詢問卡片相關"):
                id = "TQ003"
            case ("插卡被吃卡"):
                id = "SQ008"
            case ("卡片無法使用"):
                id = "SQ009"
            case ("撿到他人卡片"):
                id = "SQ010"
            case ("查詢機台狀況"):
                id = "TQ004"
            case ("詢問站點資訊"):
                id = "SQ011"
            case ("機台垃圾已滿載"):
                id = "SQ012"
            case ("是"):
                id = "SQ012-yes"
            case ("否"):
                id = "SQ012-no"
            case ("機台異常通知"):
                id = "SQ013"
            case ("確認機台回收狀況"):
                id = "SQ014"
            case ("詢問清運時間與頻率"):
                id = "SQ015"
            case _ if mtext in no_id_list:
                id = ""
            case _:
                # check time interval and model predict
                if is_skip_predict(last_input_time, current_time):
                    print("skip!!!!!!!!!!")
                    message_queue.put(mtext)
                    return 
                else:
                    message_queue.put(mtext)
                    while not message_queue.empty():
                        input_message += message_queue.get()

                    # id, class_content = model.predict(input_message)


                    
                
                    id = "TQ005"
                
                print("input_message: ", input_message)
        # resp = answer_response(id) 
        print("last_id: ", last_id)
        print("id: ", id)

        # if the user click the answer which has no id in the config.json, ex: subclasses: [{"name": "瑞陽站", type": "單一式回覆","content": "您好，請先確認是否為PET1寶特瓶或鐵鋁罐。無誤的話條碼今日會建檔，待系統凌晨更新，明天可回收。請留意，瓶罐請不要擠壓，以免影響條碼辨識，謝謝" }]
        if id == "" and last_id != "":
            resp = answer_response(last_id)
            subclasses = resp["subclasses"]
            match_subclasses = list(filter(lambda x: x["name"] == mtext, subclasses))[0]
            text = match_subclasses["content"]
            print("filter list: ", list(filter(lambda x: x["name"] == mtext, subclasses)))
            options = list(filter(lambda x: x["name"] == mtext, subclasses))[0]["subclasses"] if "subclasses" in match_subclasses else []
                
        else:
            # if last_id == "SQ012":
            text = answer_response(id)["content"]
            options = answer_response(id)["subclasses"] 


        
        # last_id = answer_response(id)["id"] if id != "" else last_id
        last_id = id if id != "" else last_id
    
    last_input_time = current_time
    print("options: ", options)
    print("text: ", text)
 
    print("============")
    try:
        if mtext == "機台垃圾已滿載": 
            message = yes_no_message(answer_response(id))
            
        else: 
            message = TextSendMessage(
                text = text,
                quick_reply = QuickReply(
                    items = [ QuickReplyButton(action=MessageAction(label=option["name"], text=option["name"])) for option in options],
                ) if len(options) else None
            
            )
        
        if text:
            

            if text == "請稍候，我們將盡速為您服務，不好意思造成您的不便":


                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="請稍等，我將為您轉接至客服人員。")
                )

                
                line_bot_api_new.push_message(
                    'Uc3106920b7dc21372e3efd7d02b43d7a',
                    TextSendMessage(text="您好，請問有什麼可以幫助您的？"),
                    # as_user=True  # 以客服人員身份發送訊息
                )
            else:
                line_bot_api.reply_message(event.reply_token, message)



    except  Exception as e:
        print("error: ", e)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "發生錯誤!!"))
    

def run_line_bot():
    app.run(host='0.0.0.0', port=3333)

if __name__ == "__main__":
   run_line_bot()