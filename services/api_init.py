import os
import time
import pandas as pd
import torch
import configparser
from queue import Queue
from flask import Flask
from flask_restx import Api
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookHandler
from ast import literal_eval
from model.bert_model import BertForSequenceClassifier

load_dotenv()


class ApiInfo(object): 
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
            
    def __init__(self):
        self.name = "iTrash api"
        self.app = Flask(__name__)
        self.api = Api(self.app, title='iTrash Api', description='all the api of iTrash')
        self.ns = self.api.namespace('iTrash', description='iTrash Api')


class LineBotInfo(object): 
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
            
    def __init__(self):
        self.name = "Line Bot"
        self.app = Flask(__name__)

        access_token = os.getenv("ACCESS_TOKEN")
        secret = os.getenv("CHANNEL_SECRET")
        # self.api = Api(self.app, title='Line Bot', description='Line Bot')
        # self.ns = self.api.namespace('iTrash', description='iTrash Api')
        self.user_pool = {}
        # self.first_time_chat = True
        # self.inactive_threshold = 30
        # self.last_input_time = time.time()
        self.line_bot_api = LineBotApi(access_token)
        self.handler = WebhookHandler(secret)
        # self.message_queue = Queue()
        # self.switch_to_human = False

        initial_config = configparser.ConfigParser()
        initial_config.read('./config.ini')

        self.config = self.pre_work_for_intent_recognition(initial_config)
    
    def init_user_info(self, user_id):
        self.user_pool = {
            user_id: {
                'first_time_chat': True, 
                'inactive_threshold': 30,
                'last_input_time': time.time(),
                'message_queue': Queue(),
                'switch_to_human': False
            }  
    }
        
    def pre_work_for_intent_recognition(self, initial_config):
        # setting parameter 
        print('===== setting initial parameter =====')
        PROBLEM_MAPPING_PATH = initial_config['DICTIONARY']['PROBLEM_MAPPING_PATH']
        POSITION_MAPPING_PATH = initial_config['DICTIONARY']['POSITION_MAPPING_PATH']

        MODEL_PATH = initial_config['MODEL']['MODEL_PATH']
        NUM_LABELS = int(initial_config['MODEL']['NUM_LABELS'])
        PREDICTIVE_MAPPING_DICT = literal_eval(initial_config['MODEL']['PREDICTIVE_MAPPING_DICT'])
        
        DEVICE = initial_config['MODEL']['DEVICE']
        device = DEVICE if torch.backends.mps.is_available() else 'cpu'
        # device = DEVICE if torch.cuda.is_available() else 'cpu'


        ##### handling predict_mapping_info 
        print('===== handling predict_mapping_info =====')
        problem_mapping_info = pd.read_csv(os.path.join(os.getcwd(), PROBLEM_MAPPING_PATH))
        position_mapping_info = pd.read_csv(os.path.join(os.getcwd(), POSITION_MAPPING_PATH))

        problem_mapping_info['value'] = problem_mapping_info['problem_id'] + '_' + problem_mapping_info['problem_name']
        problem_mapping_dict = dict(zip(problem_mapping_info['problem_id'],problem_mapping_info['value']))
        predict_mapping_dict = {v: problem_mapping_dict[k] for k, v in PREDICTIVE_MAPPING_DICT.items()}


        print('predict_mapping_dict: ', predict_mapping_dict)
        
        ##### handling postion_mapping_info 
        print('===== handling postion_mapping_info  =====')
        position_mapping_info = pd.read_csv(POSITION_MAPPING_PATH)
        position_mapping_info['station_fuzzyname'] = position_mapping_info['station_fuzzyname'].str.split('@')
        position_mapping_info = position_mapping_info.explode('station_fuzzyname')
        
        value_count_ser = position_mapping_info['station_fuzzyname'].value_counts()
        print('value_count_ser: ', sum(value_count_ser))
        if sum(value_count_ser > 1):
            duplicated_value = value_count_ser[value_count_ser == 1].index.tolist()
            print('Warning: we find some duplicated value {}'.format('|'.join(duplicated_value)))
            position_mapping_info = position_mapping_info.drop_duplicates('station_fuzzyname')
        position_mapping_info['value'] = position_mapping_info['station_id'] + '_' + position_mapping_info['station']
        position_mapping_dict = dict(zip(position_mapping_info['station_fuzzyname'],position_mapping_info['value']))

        #####  load model
        print('===== load model  =====')
        model = BertForSequenceClassifier.from_pretrained(
                pretrained_model_name_or_path = MODEL_PATH,\
                num_labels = NUM_LABELS)

        return {
            'model':model,
            'model_path': MODEL_PATH,
            'device':DEVICE,
            'predict_mapping_dict':predict_mapping_dict,
            'position_mapping_dict':position_mapping_dict
            }



    
