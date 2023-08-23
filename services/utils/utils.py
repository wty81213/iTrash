import json
import time
import os

NUM_CLASSES = 20

IS_HUMAN_REPLY_ACTIVE_LIST = ["請稍候，我們將盡速為您服務，不好意思造成您的不便", "真人客服", "真人回覆", "請稍候，將由真人客服為您排除機台異常"]
                                                                                               
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
    return text in IS_HUMAN_REPLY_ACTIVE_LIST
    #  return text == "請稍候，我們將盡速為您服務，不好意思造成您的不便" or "真人客服" in text


def is_skip_predict(last_input_time, current_time, time_interval=30):
    # current_time = time.time()
    
    time_difference = current_time - last_input_time

    # print("current_time: ", current_time)

    # print("last_input_time: ", last_input_time)

    # print("time difference: ", time_difference)

    # print("====================================")
    
    return time_difference < time_interval


def clear_queue(queue):
    while not queue.empty():
        queue.get()



      