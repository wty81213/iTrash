import json, os
from services.api_init import ApiInfo
from flask_restx import  Resource, fields
from flask_restx import abort
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, StickerSendMessage, LocationSendMessage, QuickReply, QuickReplyButton, MessageAction

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from dotenv import load_dotenv

from services.utils.utils import answer_response, read_json_file

api_info = ApiInfo()
app = api_info.app
api = api_info.api


# resource_fields = api.model('Resource', {
#     'name': fields.String,
# })


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


def run_api():
    app.run()


if __name__ == "__main__": 
    run_api()
    

# app.run(host='0.0.0.0', port=3333)