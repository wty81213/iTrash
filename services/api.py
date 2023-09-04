import json, os
from flask import Flask, request
from services.api_init import ApiInfo, LineBotInfo
from flask_restx import  Resource, fields
from flask_restx import abort
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, StickerSendMessage, LocationSendMessage, QuickReply, QuickReplyButton, MessageAction

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from dotenv import load_dotenv

from services.utils.utils import answer_response, read_json_file, main_for_intent_recognition

api_info = ApiInfo()
app = api_info.app
api = api_info.api

line_bot = LineBotInfo()


predict_fields = api.model('Predict', {
    'sentence': fields.String,
})

response_fields = api.model('Response', {
    'predictive_problem': fields.List(fields.String),
    'matching_station': fields.List(fields.String)
})


@api_info.ns.route('/class/all')
@api.doc(params={})
class AllClasses(Resource):
    # @api.marshal_with(cat)
    def get(self):
        content = read_json_file("classes")
        # with open("config/config.json", "r") as f:
        #     classes = json.load(f)["classes"]
        return content


@api_info.ns.route('/class/<string:id>')
@api.doc(params={'id': 'class id'})
class AnswerResponse(Resource):
    def get(self, id):
        res = answer_response(id)
        return res

@api_info.ns.route('/predict/')
class ModelPredict(Resource):
    @api.expect(predict_fields)
    @api.marshal_with(response_fields)
    def post(self):
        data = request.json
        predictive_problem, matching_station = main_for_intent_recognition(data['sentence'], line_bot.config)
        # return predictive_problem, matching_station
        
        return {
            'predictive_problem': predictive_problem,
            'matching_station': matching_station
        }



def run_api():
    app.run()


if __name__ == "__main__": 
    run_api()
    

# app.run(host='0.0.0.0', port=3333)