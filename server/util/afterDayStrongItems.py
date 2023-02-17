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
from util.holidayGubn import holidayGubn


# 매수 가능한 종목의 가능기간과 가능 타점을 정하고, 수익률을 계산
class afterDayStrongItems:
    
    def __init__(self):
        super().__init__()
        # DB 사용선언
        self.mongodb = MongoDBHandler()
        # Bot 사용선언
        self.bot = TTTelegram()
        # self.selfBot = selfTelegram()
        # Type 변환 사용선언
        self.realType = RealType()
        
        ten_day_list = self.make_use_data_list(6)
        after_day_count = 0
        after_day_total_list = []
        
        for i in ten_day_list:
            nday = i
            start = self.afterStrongnDays(nday)[0]
            end = self.afterStrongnDays(nday)[1]
            
            # print("start : %s, end : %s" % (start, end))

            # n 일 전 매수타이밍이 왔던(가장 강했던) 테마 리스트 추출
            thema_list = []
            thema_list_mongo = self.mongodb.find_items({"저장시간": {'$gte': start, '$lt' : end}}, 'TodayStrongThema', 'proMemeCodeList')
            for thema in thema_list_mongo:
                thema_list.append(thema["테마"])
            thema_list = list(set(thema_list))

            to_list_df_higher_chongjum = ""
            list_dup_check = []
            # 테마 별 커트라인 이상의 n일전 가장 높은 총점으로 마친 종목들
            for thema in thema_list:
                higher_chongjum_mongo = self.mongodb.find_items({"$and":[{"저장시간": {'$gte': start, '$lt' : end}}, {"테마":thema}]}, 'TodayStrongThema', 'proMemeCodeList')
                df_higher_chongjum = pd.DataFrame(list(higher_chongjum_mongo)).loc[:,["테마","종목명","총점","커트라인"]]
                df_higher_chongjum = df_higher_chongjum.sort_values('총점', ascending=False)
                df_higher_chongjum['rank_min'] = df_higher_chongjum['총점'].rank(method='min', ascending=False, na_option='bottom')
                
                cutline = df_higher_chongjum.iloc[0][4]
                
                condition = (df_higher_chongjum.rank_min <= cutline) # 조건식 작성
                df_higher_chongjum = df_higher_chongjum[condition]
                to_list_df_higher_chongjum = df_higher_chongjum.values.tolist()
                
                if to_list_df_higher_chongjum[0][1] in list_dup_check:
                    pass
                else:
                    list_dup_check.append(to_list_df_higher_chongjum[0][1])
                    after_day_total_list.append("%s 영업일 전 %s / %s / %s" % (after_day_count, to_list_df_higher_chongjum[0][1], to_list_df_higher_chongjum[0][0], to_list_df_higher_chongjum[0][2]))
            after_day_count = after_day_count + 1
        
        temp_count = 0
        total_msg = ""
        for i in after_day_total_list:
            total_msg = total_msg + "\n" + i
            print("%s" % (i))
            temp_count = temp_count + 1
        
        self.bot.send("☆ 장전 대장주 체크 ☆ \n %s" % total_msg)

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
    
    # n 영업일
    def make_use_data_list(self, work_days):
        nday_list = []
        use_date_list = []
        use_date_list_len = 0
        nday = 0
        
        if work_days == 0:
            while use_date_list_len != 1:
                start = self.afterStrongnDays(nday)[0]
                holi_check = holidayGubn(start.strftime('%Y-%m-%d'))
                if holi_check == 1:
                    use_date_list.append(start)
                    nday_list.append(nday)
                else:
                    pass
                use_date_list_len = len(use_date_list)
                nday = nday + 1
        else:
            while use_date_list_len != work_days:
                start = self.afterStrongnDays(nday)[0]
                holi_check = holidayGubn(start.strftime('%Y-%m-%d'))
                if holi_check == 1:
                    use_date_list.append(start)
                    nday_list.append(nday)
                else:
                    pass
                use_date_list_len = len(use_date_list)
                nday = nday + 1
        return nday_list
    
if __name__ == "__main__":
    afterDayStrongItems()