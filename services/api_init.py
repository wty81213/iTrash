import os
import time
from queue import Queue
from flask import Flask
from flask_restx import Api
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookHandler

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



    
