import os, json
import time
import threading
import sched
import requests
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, AudioSendMessage, QuickReply, QuickReplyButton, MessageAction, PostbackAction, TemplateSendMessage, ConfirmTemplate, MessageTemplateAction, FlexSendMessage
from flask import Flask
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models.send_messages import VideoSendMessage
from services.api_init import ApiInfo, LineBotInfo
from dotenv import load_dotenv
from flask import request, abort

from services.utils.utils import answer_response, question_options, is_user_inactive, is_skip_predict, read_json_file, is_change_to_human_customer_service, clear_queue, main_for_intent_recognition, chat_bot_reply_content, human_reply_content, error_reply_content


line_bot = LineBotInfo()


app = line_bot.app
line_bot_api = line_bot.line_bot_api
# last_input_time = line_bot.last_input_time
# inactive_threshold = line_bot.inactive_threshold
# message_queue = line_bot.message_queue
last_id = ""
# input_message = ""

last_message_time = {}


line_bot_api_new = LineBotApi('znGqCb0IVXqlwW/3a4ZLfO9IQVvSvcN8MV5RjzG9Rs4dmqL+qLt8eEn1W2oIXQr3UnT+Q0QQ+i2KR+bnGbPO0T3SqGuIz6dZ1n5TJyZEgsuLPZYYGe60ZyKXTqhFGYUqsh7KVcW06VOYk6lnjm7gwQdB04t89/1O/w1cDnyilFU=')
handler_new = WebhookHandler('94d708d169f17c9cca0cfc4d8c22b668')



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
    
    line_bot_api_new.push_message(
        'Uc3106920b7dc21372e3efd7d02b43d7a',
        TextSendMessage(text="您好，請問有什麼可以幫助您的？"),
    )



@line_bot.handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    # current_user_time = time.time()

    input_message = ""
    matching_station = [[]]

    user_id = event.source.user_id 

    # print("user_id: ", user_id)

    current_time = event.timestamp / 1000 # time.time()
    
    
    if user_id not in line_bot.user_pool:
        line_bot.init_user_info(user_id)
        # line_bot.user_pool[user_id]["timer"].start()
        line_bot.user_pool[user_id]["current_time"] = current_time
        line_bot.user_pool[user_id]["last_time"] = current_time

    else:

        if line_bot.user_pool[user_id]["is_new_conversation"]: 
            line_bot.user_pool[user_id]["current_time"] = current_time
            line_bot.user_pool[user_id]["last_time"] = current_time
        
        else:
            # last_time = line_bot.user_pool[user_id]["current_time"]
            line_bot.user_pool[user_id]["last_time"] = line_bot.user_pool[user_id]["current_time"]
            line_bot.user_pool[user_id]["current_time"] = current_time


    # if not line_bot.switch_to_human:
    if not line_bot.user_pool[user_id]["switch_to_human"]:

        last_id = line_bot.user_pool[user_id]["last_id"]

        # get user message
        mtext = event.message.text
        if mtext == "機器人回覆":
            chat_bot_reply_content(line_bot_api, line_bot, user_id)
        else:
            # check if the user want to change to human customer service
            if is_change_to_human_customer_service(mtext):
                human_reply_content(line_bot_api, line_bot, user_id)
            
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
                    case ("詢問瓶罐機相關"):
                        id = "TQ002"
                    case ("瓶罐建立條碼"):
                        id = "SQ005"
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
                    case _ if mtext in read_json_file("no_id_list"):
                        id = ""
                    case _:
                        # check time interval and model predict
                        print("last_time: ", line_bot.user_pool[user_id]["last_time"])
                        print("is_skip_predict: ", is_skip_predict(line_bot.user_pool[user_id]["last_time"], line_bot.user_pool[user_id]["current_time"]))
                       
                        if is_skip_predict(line_bot.user_pool[user_id]["last_time"], line_bot.user_pool[user_id]["current_time"]) and not is_change_to_human_customer_service(mtext):
                            print("skip!!!!!!!!!!!")
                            print("====================================")
                            line_bot.user_pool[user_id]["message_queue"].put(mtext)
                            line_bot.user_pool[user_id]["is_new_conversation"] = False
                            return 
                        else:

                            # line_bot.user_pool[user_id]["message_queue"].put(mtext)
                            # while not message_queue.empty():
                            while not line_bot.user_pool[user_id]["message_queue"].empty():
                                input_message += line_bot.user_pool[user_id]["message_queue"].get()
                                input_message += ','
                            input_message += mtext

                            # model predict
                            predictive_problem, matching_station = main_for_intent_recognition(input_message, line_bot.config)
                            id = predictive_problem[0].split('_')[0]




                        
                # print("input_message: ", input_message)
                # print("id: ", id)
                # print("last_id: ", last_id)
                # print("matching_station: ", matching_station)

                # os._exit(0)

            
                # check if the matching_station is empty
                if not len(matching_station[0]):
                # if the user click the answer which has no id in the config.json, ex: subclasses: [{"name": "瑞陽站", type": "單一式回覆","content": "您好，請先確認是否為PET1寶特瓶或鐵鋁罐。無誤的話條碼今日會建檔，待系統凌晨更新，明天可回收。請留意，瓶罐請不要擠壓，以免影響條碼辨識，謝謝" }]
                    if id == "" and  last_id != "":
                        resp = answer_response(last_id)
                        subclasses = resp["subclasses"]
                        match_subclasses = list(filter(lambda x: x["name"] == mtext, subclasses))[0]
                        text = match_subclasses["content"]
                        # print("match_subclasses: ", match_subclasses)
                        options = list(filter(lambda x: x["name"] == mtext, subclasses))[0]["subclasses"] if "subclasses" in match_subclasses else []

                        # print('options: ', options)

                            
                    else:
                        # if last_id == "SQ012":
                        text = answer_response(id)["content"]
                        options = answer_response(id)["subclasses"] 


                    # last_id = id if id != "" else last_id 
                    line_bot.user_pool[user_id]["last_id"] = id if id != "" else last_id

                
                else: 
                    options = []
                    
                    # resp = answer_response(id)
                    # print("resp: ", resp)
                    # os._exit(0)
                    if id == "SQ012": 
                        text = answer_response("SQ012-no")["content"]
                    else:
                        if len(answer_response(id)["subclasses"]) == 0:
                            text = answer_response(id)["content"]
                        else:
                            text = answer_response(id)["subclasses"][0]['content']
                    # print('id: ', id)
                    # print('text: ', text)

                    # os._exit(0)


                try:
                    
                    if id == "SQ012" and not len(matching_station[0]): 
                        message = yes_no_message(answer_response(id))

                    else: 
                        message = TextSendMessage(
                            text = text,
                            quick_reply = QuickReply(
                                items = [QuickReplyButton(action=MessageAction(label=option["name"], text=option["name"])) for option in options],
                            ) if len(options) else None
                        
                        )
                
                    
                    # if the text is empty, reply nothing
                    if text:
                        if is_change_to_human_customer_service(text):
                            # line_bot.switch_to_human = True
                            line_bot.user_pool[user_id]["switch_to_human"] = True
                            # clear_queue(line_bot.user_pool[user_id]["message_queue"])
                            

                        # line_bot_api.reply_message(event.reply_token, message)
                        line_bot_api.push_message(user_id, message)

                    # print('clear message queue...')
                    clear_queue(line_bot.user_pool[user_id]["message_queue"])

                except  Exception as e:
                    error_reply_content(line_bot_api, line_bot, user_id)
        

    else:
        if event.message.text == "機器人回覆":
            # line_bot_api.push_message(
            #     user_id,
            #     TextSendMessage(text="請稍等，我將為您換成機器人回覆。")
            # )
            # # line_bot.switch_to_human = False
            # line_bot.user_pool[user_id]["switch_to_human"] = False
            # clear_queue(line_bot.user_pool[user_id]["message_queue"])

            # line_bot.user_pool[user_id]["no_reply"] = False

            # line_bot.user_pool[user_id]["last_time"] = time.time()

            chat_bot_reply_content(line_bot_api, line_bot, user_id)




def run_line_bot():
    app.run(host='0.0.0.0', port=3333)

def process(user_id, period):
        
        t = time.time()
        
        input_message = ""
        last_id = line_bot.user_pool[user_id]["last_id"]
        # user_id, value = user
        # print("user_id: ", user_id)
        # print("last_time: ", line_bot.user_pool[user_id]["last_time"])
        # print("user_id: ", user_id)
        # print("diff: ", t - line_bot.user_pool[user_id]["current_time"])

        if (t - line_bot.user_pool[user_id]["current_time"]) > period:
            # line_bot.user_pool[user_id]["no_reply"] = True

            while not line_bot.user_pool[user_id]["message_queue"].empty():
                    input_message += line_bot.user_pool[user_id]["message_queue"].get()
                    input_message += ','
            if input_message != "":
                predictive_problem, matching_station = main_for_intent_recognition(input_message[:-1], line_bot.config)
                id = predictive_problem[0].split('_')[0]

                # print("input_message in proecess: ", input_message)
                # print("t: ", t)
                # print("diff: ", t - line_bot.user_pool[user_id]["current_time"])
                # print("last time in process: ", line_bot.user_pool[user_id]["last_time"])
                # print("id in proecess: ", id)
                # print("last_id in proecess: ", last_id)
                
                # check if the matching_station is empty
                if not len(matching_station[0]): 

                    text = answer_response(id)["content"]
                    options = answer_response(id)["subclasses"]


                    # last_id = id if id != "" else last_id 
                    line_bot.user_pool[user_id]["last_id"] = id if id != "" else last_id
                
                else:
                    options = []

                    if id == "SQ012": 
                        text = answer_response("SQ012-no")["content"]
                    else:
                        if len(answer_response(id)["subclasses"]) == 0:
                            text = answer_response(id)["content"]
                        else:
                            text = answer_response(id)["subclasses"][0]['content']
                    # print('id: ', id)
                    # print('text: ', text)

                try:
                
                    if id == "SQ012" and not len(matching_station[0]): 
                        message = yes_no_message(answer_response(id))

                    else: 
                        message = TextSendMessage(
                            text = text,
                            quick_reply = QuickReply(
                                items = [QuickReplyButton(action=MessageAction(label=option["name"], text=option["name"])) for option in options],
                            ) if len(options) else None
                        
                        )
            
                
                    # if the text is empty, reply nothing
                    if text:
                        if is_change_to_human_customer_service(text):
                            # line_bot.switch_to_human = True
                            line_bot.user_pool[user_id]["switch_to_human"] = True
                            # clear_queue(line_bot.user_pool[user_id]["message_queue"])
                            

                        # line_bot_api.reply_message(event.reply_token, message)
                        line_bot_api.push_message(user_id, message)

                    # print('clear message queue...')
                    clear_queue(line_bot.user_pool[user_id]["message_queue"])

                except  Exception as e:
                    error_reply_content(line_bot_api, line_bot, user_id)

                
                # line_bot.user_pool[user_id]["last_time"] = t
                line_bot.user_pool[user_id]["is_new_conversation"] = True
                # os._exit(0)
        # else:
        #     line_bot.user_pool[user_id]["no_reply"] = False


    
def timer(period=5):
    # t = time.time()
    while True:
        threads = []   
        for user_id in line_bot.user_pool.copy():
            threads.append(threading.Thread(target=process, args=(user_id, period)))
            threads[-1].start()


        for t in threads:                                                           
            t.join()  

  
    
    
    
    
if __name__ == "__main__":
   run_line_bot()