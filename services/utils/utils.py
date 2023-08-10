import json
import time

NUM_CLASSES = 20

with open("config/config.json", "r") as f:
        classes = json.load(f)["classes"]

def question_options():
      return classes


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

    for subclass in classes:
       
        found_category = find_category_by_id(subclass, id)


        
        if found_category:
            return found_category
        

        

def is_user_inactive(last_input_time, current_time, inactive_threshold):
    # current_time = time.time()
    
    time_difference = current_time - last_input_time
    
    return time_difference > inactive_threshold

def is_skip_predict(last_input_time, current_time, time_interval=5):
    # current_time = time.time()
    
    time_difference = current_time - last_input_time
    
    return time_difference < time_interval



      