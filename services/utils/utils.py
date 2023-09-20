import json
import re 
import time
import os
import torch
from tqdm import tqdm
from queue import Queue
from ..intention_dataset import IntentionDataset
from torch.utils.data import DataLoader
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, AudioSendMessage, QuickReply, QuickReplyButton, MessageAction, PostbackAction, TemplateSendMessage, ConfirmTemplate, MessageTemplateAction, FlexSendMessage

NUM_CLASSES = 20

IS_HUMAN_REPLY_ACTIVE_LIST = ["請稍候，我們將盡速為您服務", "真人客服", "真人回覆", "請稍候，將由真人客服為您排除機台異常", "我們將盡速為您服務"]
                                                                                               
# /Users/wty81213/Documents/project/ML/iTrash/services/utils/utils.py
with open(os.getcwd() + "/config/config.json", "r") as f:
        content = json.load(f)

def question_options():
      return content["classes"]


def find_category_by_id(subclass, target_id):
    if  "id" in subclass and subclass["id"] == target_id:
        return subclass
    
    if "subclasses" in subclass:
        for subclass_data in subclass["subclasses"]:
            found_category = find_category_by_id(subclass_data, target_id)
            if found_category:
                return found_category

    return None

def answer_response(id):
   
    found_category = {}

    for subclass in content["classes"]:
       
        found_category = find_category_by_id(subclass, id)


        
        if found_category:
            return found_category
        

        

def is_user_inactive(last_input_time, current_time, inactive_threshold):
    # current_time = time.time()
    
    time_difference = current_time - last_input_time
    
    return time_difference > inactive_threshold



def read_json_file(key):
    return content[key]
        # no_id_list = content["key"]
        # human_customer_service = content["human_customer_service"]
        
def is_change_to_human_customer_service(text):
    for str in IS_HUMAN_REPLY_ACTIVE_LIST:
        if str in text:
            return True
    
    return False
    #  return text == "請稍候，我們將盡速為您服務，不好意思造成您的不便" or "真人客服" in text


def is_skip_predict(last_input_time, current_time, time_interval=10):
    # current_time = time.time()
    
    time_difference = current_time - last_input_time

    # print("current_time: ", current_time)

    # print("last_input_time: ", last_input_time)
  
    return time_difference < time_interval


def clear_queue(queue):

    # print("queue empty: ", queue.empty())
    while not queue.empty():
        print("clear the queue............................")
        queue.get()


# def init_user_info(line_bot, user_id):
#     line_bot.user_info = {
#         user_id: {
#             'first_time_chat': True, 
#             'inactive_threshold': 30,
#             'last_input_time': time.time(),
#             'message_queue': Queue(),
#             'switch_to_human': False
#         },
        
#     }

def problem_prediction(sentence, model, device, model_path, predict_mapping_dict):

    # checking format of sentences
    if isinstance(sentence,str):
        sentence = [sentence]
    else :
        assert isinstance(sentence,list)

    # convert cpu to specific device
    model = model.to(device)
    
    # data preparation
    senti_data  = (sentence,[0]*len(sentence),[0]*len(sentence))
    input_dataset = IntentionDataset(senti_data, token_path = model_path)
    dataloader = DataLoader(input_dataset, batch_size=1, collate_fn=input_dataset.collate_fn)

    # model prediction
    total_logits = []
    total_target = []
    batchs_iterator = tqdm(dataloader, unit = 'batch', position = 0)  
    for batch_idx, (_, data, target) in enumerate(batchs_iterator):
        data = {k:v.to(device) for k,v in data.items()}
        target = target.to(device)
        with torch.no_grad():
            output = model(**data, return_dict = True)  
        total_logits.append(output.logits)
        total_target.append(target)

        batchs_iterator.set_description('Prediction')

    # convert idx to problem_id
    total_logits = torch.cat(total_logits, dim = 0).to('cpu')
    pred_labels = torch.argmax(total_logits, dim=1).to('cpu').numpy()
    pred_labels = [predict_mapping_dict[i] for i in pred_labels]

    return pred_labels

def matching_stations(sentence, position_mapping_dict):
    # setting parameter 
    fuzzyname = list(position_mapping_dict.keys())
    fuzzyname = sorted(fuzzyname, key = lambda x : len(x))[::-1]

    # checking format of sentences
    if isinstance(sentence,str):
        sentence = [sentence]
    else :
        assert isinstance(sentence,list)    

    stations_list = []
    for s in sentence:
        extract_fuzzyname = re.findall('|'.join(fuzzyname), s)
        extract_station = [position_mapping_dict[i] for i in extract_fuzzyname]
        extract_station = list(set(extract_station))
        stations_list.append(extract_station)
    
    return stations_list


def main_for_intent_recognition(sentence, config):
    print('===== predicting problem =====')
    prediction_result = problem_prediction(sentence, 
                                           model = config['model'],
                                           device = config['device'],
                                           model_path = config['model_path'],
                                           predict_mapping_dict = config['predict_mapping_dict'])
    
    print('===== matching_station =====')
    matching_result = matching_stations(sentence,
                                        position_mapping_dict = config['position_mapping_dict'])

    return prediction_result, matching_result
    

def chat_bot_reply_content(line_bot_api, line_bot, user_id):
    line_bot_api.push_message(
        user_id,
        TextSendMessage(text="請稍等，我將為您換成機器人回覆。")
    )
    # line_bot.switch_to_human = False
    line_bot.user_pool[user_id]["switch_to_human"] = False
    clear_queue(line_bot.user_pool[user_id]["message_queue"])

    line_bot.user_pool[user_id]["no_reply"] = False

    line_bot.user_pool[user_id]["last_time"] = time.time()

def human_reply_content(line_bot_api, line_bot, user_id):
    line_bot_api.push_message(user_id, TextSendMessage(text="請稍等，我將為您轉接至客服人員。"))

    line_bot.user_pool[user_id]["switch_to_human"] = True
    clear_queue(line_bot.user_pool[user_id]["message_queue"])

def error_reply_content(line_bot_api, line_bot, user_id):
    line_bot_api.push_message(user_id, TextSendMessage(text = "發生錯誤!!"))
    clear_queue(line_bot.user_pool[user_id]["message_queue"])

      