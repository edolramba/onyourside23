from datetime import datetime
from datetime import timedelta
from datetime import date
import sys
sys.path.append("C:\\Dev\\onyourside22\\server")
sys.path.append("C:\\Dev\\onyourside22\\server\\test")
sys.path.append("C:\\Dev\\onyourside22\\server\\util")
from util.MongoDBHandler import MongoDBHandler
import time
import pandas as pd

from config.kiwoomType import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.errorCode import *
from PyQt5.QtTest import *
from config.kiwoomType import *

from common.importConfig import *
from util.telegramutil import TTTelegram
from util.selfTelegram import selfTelegram

from pymongo import MongoClient

class moduleTest:
    
    def __init__(self):
        super().__init__()
        # DB 사용선언
        self.mongodb = MongoDBHandler()
        # Bot 사용선언
        # self.bot = TTTelegram()
        # self.selfBot = selfTelegram()
        # Type 변환 사용선언
        self.realType = RealType()
        
        # n 일 전 장초반 테마 별 1등 종목 추출
        nday = 1
        start = self.afterStrongnDays(nday)[0]
        end = self.afterStrongnDays(nday)[1]
        print("start : %s " % start)
        print("end : %s" % end)
        
        # n 일 전 장종료 1등 테마/종목 추출
        # 점수가 가장 높은 종목 

        thema_list = []
        thema_list_mongo = self.mongodb.find_items({"저장시간": {'$gte': start, '$lt' : end}}, 'TodayStrongThema', 'proMemeCodeList')
        for thema in thema_list_mongo:
            thema_list.append(thema["테마"])
        thema_list = list(set(thema_list))
        print(thema_list)
        
        order_by = {}
        # 대장주 고르기 
        for thema in thema_list:
            # 테마별로 당일 가장 빠르게 검색된 1등 종목
            fastest_item_mongo_dict = []
            fastest_item_mongo = self.mongodb.find_items({"$and":[{"저장시간": {'$gte': start, '$lt' : end}}, {"테마":thema}]}, 'TodayStrongThema', 'proMemeCodeList')
            for i in fastest_item_mongo:
                fastest_item_mongo_dict.append(i)
            print(fastest_item_mongo_dict[1])
            print(fastest_item_mongo_dict[-1])
        
        #     for item in fastest_item_mongo:
        #         if item["테마"] not in order_by.keys():
        #             order_by.update({item["테마"]: {}})
        #         else:
        #             order_by[item["테마"]].update({"저장시간":item["저장시간"]})
        # print(order_by)
                # order_by[item[thema]].update({"저장시간":item["저장시간"]})
            # 테마별로 당일 점수가 가장 높은 종목
            
    # n일 전 테마 날짜 세팅하기
    def afterStrongnDays(self, nday):
        # 오늘날짜
        startDay = datetime.today() - timedelta(days=nday)
        # 검색할 이전 날짜
        endDay = datetime.today() - timedelta(days=nday-1)
        # - timedelta(days=1)
        start = datetime(startDay.year, startDay.month, startDay.day)
        end = datetime(endDay.year, endDay.month, endDay.day)
        return start, end
        
if __name__ == "__main__":
    moduleTest()