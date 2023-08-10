
import threading
from flask import Flask
from services.api_init import ApiInfo
from services import api, line_bot
from flask_restx import Resource, fields, Api



# def init():
#     MyResource()


def main():
    t1 = threading.Thread(target=line_bot.run_line_bot)
    t2 = threading.Thread(target=api.run_api)
    t1.start()
    t2.start()
    
    

if __name__ == "__main__":
    main()
    