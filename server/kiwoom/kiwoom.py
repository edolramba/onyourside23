import os
import sys
from tkinter import E
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.errorCode import *
from PyQt5.QtTest import *
from config.kiwoomType import *
from config.log_class import *
from common.importConfig import *
from datetime import datetime
from datetime import timedelta
import threading
from util.telegramutil import TTTelegram
from util.telegramutil2 import TTTelegram2
from util.telegramutil3 import TTTelegram3
from util.selfTelegram import selfTelegram
from util.MongoDBHandler import MongoDBHandler
import pandas as pd
import time
from util.newsNLP import *


# 텔레그램 테스트
from util.themaUpdate import themaUpdate

class Kiwoom(QAxWidget):

    def __init__(self):
        super().__init__()
        # DB 사용선언
        self.mongodb = MongoDBHandler()
        
        if "00:00:00" <= datetime.today().strftime("%H:%M:%S") <= "07:30:00":
            # Bot 사용선언
            self.bot = selfTelegram()
            self.bot2 = selfTelegram()
            self.bot3 = selfTelegram()
        elif "18:01:00" <= datetime.today().strftime("%H:%M:%S") <= "23:59:00":
            # Bot 사용선언
            self.bot = selfTelegram()
            self.bot2 = selfTelegram()
            self.bot3 = selfTelegram()
        else:
            # Bot 사용선언
            self.bot = TTTelegram()
            self.bot2 = TTTelegram2()
            self.bot3 = TTTelegram3()
        self.selfBot = selfTelegram()
        self.themaUpdate = themaUpdate()
        # Log 사용선업
        self.logging = Logging()
        # Type 변환 사용선언
        self.realType = RealType()
        
        ########### 텔레그램 Flood 방지용 
        self.telFloodCnt = 1
        self.telStart = time.time()
        self.telType = 1
        ##########################################
        
        ########### 재시작 / 작동 코드
        # self.restart_bot = self.mongodb.find_item({},"TodayStrongThema", "restartCode")
        # print("restart_bot Code : %s" % self.restart_bot["restartCode"])
        self.thema_make_check_oper_num = 1
        ##########################################
        
        # if self.restart_bot["restartCode"] == 0:
        ####### [시작] 초기 메세지 발송
        self.logging.logger.debug("☆☆☆ Raorkebot start ☆☆☆")
        self.startMsgesFilePath = "C:\\Dev\\onyourside22\\server\\kiwoom\\files\\startMsg.txt"
        self.startMsg = ""

        startMsgesFile = open(self.startMsgesFilePath, 'rt', encoding='utf-8')
        
        startMsg = startMsgesFile.readlines()
        for line in startMsg:
            self.startMsg = self.startMsg + line
            
        startMsgesFile.close()
        
        self.bot_send_in_cnt(self.startMsg)
        ####### [종료] 초기 메세지 발송 
        # elif self.restart_bot["restartCode"] == 1:
        #     self.logging.logger.debug("☆☆☆ Raorkebot restart ☆☆☆")
        #     self.bot_send_in_cnt("☆☆☆ Calculating score...☆☆☆")
        # else:
        #     self.logging.logger.debug("☆☆☆ Raorkebot restart error ☆☆☆")
        
        ########## 종목 점수 변수 관리 
        self.PerRate = 16  # 등락률 점수 (1%당)
        self.PerUpperHolding = 1.3  # 상한가 유지 점수 (1분당)
        self.PerPower = 28  # 시장장악률 점수 (1%당)
        self.outTimeUpDownJumsu = -300 # 시간외단일가 점수
        ##########################################

        ####### event loop를 실행하기 위한 변수 모음
        self.operation_time_status_value =''; # 시작시간 체크를 위한 변수
        self.login_event_loop = QEventLoop() # 로그인 요청용 이벤트 루프
        self.detail_account_info_event_loop = QEventLoop() # 예수금 요청용 이벤트 루프
        self.calculator_event_loop = QEventLoop() # 계산용 이벤트 루프
        #########################################

        ########### 전체 종목 관리
        self.all_stock_dict = {}
        ###########################

        ####### 계좌 관련된 변수
        self.account_stock_dict = {}
        self.not_account_stock_dict = {}
        self.account_num = None #계좌번호 담아줄 변수
        self.deposit = 0 #예수금
        self.use_money = 0 #실제 투자에 사용할 금액
        self.use_money_percent = 0.5 #예수금에서 실제 사용할 비율
        self.output_deposit = 0 #출력가능 금액
        self.total_profit_loss_money = 0 #총평가손익금액
        self.total_profit_loss_rate = 0.0 #총수익률(%)
        ########################################

        ######## 종목 정보 가져오기
        self.portfolio_stock_dict = {}
        self.portfolio_stock_list = []
        self.jogun1_dict = {} # 자동_대장주확인
        self.jogun2_dict = {} # 자동_장초반_상승률상위
        self.jogun3_dict = {} # 자동_장중세력봉
        self.jogun4_dict = {} # 자동_장중매횡
        self.jogun5_dict = {} # 자동_당일강세테마
        self.jango_dict = {}
        self.upjong_dict = {}
        self.upjong_list = []
        self.kospi_code_list = []
        self.kosdaq_code_list = []
        
        # 테마 변경여부 체크용
        self.buy_first_condition_dup_check = []
        self.buy_second_condition_dup_check = []
        self.buy_third_condition_dup_check = []
        self.buy_atleast_condition_dup_check = []
        self.two_buy_first_condition_dup_check = []
        self.two_buy_second_condition_dup_check = []
        self.two_buy_third_condition_dup_check = []
        self.two_buy_atleast_condition_dup_check = []
        
        ### 점수 계산을 위한 변수
        self.rawMemeList = {}
        self.outTimeUpDownRate = {}
        self.codePlusCnt = 0
        self.codePlus = ""
        self.one_min_data = []
        self.TempOutTimeUpDownRate = 0
        ########################

        ########### 종목 분석 용
        self.calcul_data = []
        ##########################################

        ####### 요청 스크린 번호
        self.screen_num_cnt = 0
        self.screen_start_stop_real = "1000" #장 시작/종료 실시간 스크린 번호
        self.screen_my_info = "2000" #계좌 관련한 스크린 번호
        self.screen_calculation_stock = "4000" #계산용 스크린 번호
        self.screen_real_stock = "5000" #종목별 할당할 스크린 번호
        self.screen_meme_stock = "6000" #종목별 할당할 주문용 스크린 번호
        self.upjong_sisae_stock = "7000" # 코스피/코스닥 시세 스크린 번호 
        ########################################

        ######### 초기 셋팅 함수들 바로 실행
        self.get_ocx_instance() # OCX 방식을 파이썬에 사용할 수 있게 반환해 주는 함수 실행
        self.event_slots() # 키움과 연결하기 위한 시그널 / 슬롯 모음
        self.real_event_slot()  # 실시간 이벤트 시그널 / 슬롯 연결
        self.signal_login_commConnect() # 로그인 요청 함수 포함
        self.get_account_info() #계좌번호 가져오기
        self.get_upjong_list()
        # self.detail_account_info() # 예수금 요청 시그널 포함
        # self.detail_account_mystock() #계좌평가잔고내역 가져오기
        # QTimer.singleShot(5000, not_concluded_account(self)) #5초 뒤에 미체결 종목들 가져오기 실행

        
        # 스크린번호 1000
        self.dynamicCall("SetRealReg(QString, QString, QString, QString)", self.screen_start_stop_real, '', self.realType.REALTYPE['장시작시간']['장운영구분'], "1")
        # KOSPI / KOSDAQ 실시간 시세요청
        self.dynamicCall("SetRealReg(QString, QString, QString, QString)", "7000", "001", "10", "1")
        self.dynamicCall("SetRealReg(QString, QString, QString, QString)", "7000", "101", "10", "1")
        #########################################
        
        ######### 나중에 한 번에 풀어주면 되는 함수들
        self.realdata_slot_start_point = 0
        self.condition_tr_slot_send_msg_check = 0
        self.thema_notyet_input_list = []

        self.condition_event_slot() # 조건검색식 Event Slot
        self.condition_signal() # 조건검색식 로딩 Signal
        self.screen_number_setting()
        QTest.qWait(4000)
        
        self.thema_make_check()
        # 당일 매매 추천 종목 복기
        # 장 종료후에 일괄 복기
        # self.mongodb.insert_item(save_item, "TodayStrongThema", "proMemeCodeList")

    def cal_total_score(self):
        
        self.logging.logger.debug("실시간 점수계산 로직 시작")
        mongoToday = str(datetime.today().strftime("%Y%m%d"))
        cal_total_score_start_gubn = self.mongodb.find_item({"$and":[{"날짜": mongoToday},{"순위": "N"}]}, "TodayStrongThema", "rawMemeCodeList")
        if cal_total_score_start_gubn != None:

            self.rawMemeList = self.mongodb.find_items({"$and":[{"날짜": mongoToday},{"순위": "N"}]},"TodayStrongThema", "rawMemeCodeList")
            
            # 오늘 날짜의 순위가 매겨지지 않은 매매리스트 추출
            sum_save_item =[]
            for raw in self.rawMemeList:
                code = raw["종목코드"]
                code_nm = raw["종목명"]
                bokHapKey = raw["복합키"]
                chongJum = raw["총점"]
                thema = raw["테마"]
                themaJumsu = raw["테마점수"]
                save_time = raw["저장시간"]
                upDownJumsu = raw["등락률점수"]
                holdPowerJumsu = raw["장악률점수"]
                cutLine = raw["커트라인"]
                
                self.codePlus = bokHapKey
                
                if bokHapKey not in self.outTimeUpDownRate.keys():
                    self.outTimeUpDownRate.update({bokHapKey: {}})
                
                self.outTimeUpDownRate[bokHapKey].update({"종목명": code_nm})
                self.outTimeUpDownRate[bokHapKey].update({"종목코드": code})
                
                tempOutTimeData = self.mongodb.find_item({"$and":[{"수집날짜": mongoToday},{"종목코드": code}]}, "TodayStrongThema", "outTimeUpDownRate")
                if tempOutTimeData != None:
                    self.outTimeUpDownRate[bokHapKey].update({"시간외단일가": tempOutTimeData["시간외단일가"]})
                else:
                    self.outTimeUpDownRate[bokHapKey].update({"시간외단일가": 0})

                if self.outTimeUpDownRate[bokHapKey]["시간외단일가"] >= 2 or self.outTimeUpDownRate[bokHapKey]["시간외단일가"] <= -2:
                    self.outTimeUpDownRate[bokHapKey].update({"시간외단일가점수": self.outTimeUpDownJumsu})
                    self.logging.logger.debug("시간외 단일가가 +-2 에 걸리는 경우 : %s " % self.outTimeUpDownJumsu)
                else:
                    self.outTimeUpDownJumsu = 0
                    self.outTimeUpDownRate[bokHapKey].update({"시간외단일가점수": self.outTimeUpDownJumsu})
                    self.logging.logger.debug("시간외 단일가가 +-2 에 안 걸리는 경우 : %s " % self.outTimeUpDownJumsu)
                self.outTimeUpDownRate[bokHapKey].update({"종목코드": code})
                
                self.logging.logger.debug("시간외단일가 요청 완료")
                
                
                # 주식기본 정보 요청 (상한가 가격요청)
                
                upper_price = self.portfolio_stock_dict[code]["상한가"]
                self.outTimeUpDownRate[bokHapKey].update({"상한가": upper_price})
                
                # 상한가 유지 분봉 갯수 요청
                upperMainTainCnt = self.upper_price_maintain_score(code)
                
                self.outTimeUpDownRate[bokHapKey].update({"상한가유지시간": upperMainTainCnt})
                self.outTimeUpDownRate[bokHapKey].update({"상한가유지점수": upperMainTainCnt * self.PerUpperHolding})
                
                upperMaintainJumsu = round(self.outTimeUpDownRate[bokHapKey]["상한가유지점수"])
                
                self.outTimeUpDownRate[bokHapKey].update({"총점": int(chongJum) + float(upperMaintainJumsu) + int(self.outTimeUpDownJumsu)})
                
                chongjum = round(self.outTimeUpDownRate[bokHapKey]["총점"])
                
                self.outTimeUpDownRate[bokHapKey]
                
                if cutLine <= 3:
                    cutLine = 1
                elif 6 > cutLine >= 4:
                    cutLine = 2
                elif cutLine >= 6:
                    cutLine = 3
                else:
                    pass
                
                save_item = {
                    "복합키": bokHapKey,
                    "테마": thema,
                    "저장시간": save_time,
                    "상한가": int(str(self.outTimeUpDownRate[bokHapKey]["상한가"])),
                    "종목명": code_nm,
                    "종목코드": code,
                    "테마점수": round(themaJumsu),
                    "등락률점수": upDownJumsu,
                    "장악률점수": holdPowerJumsu,
                    "시간외단일가점수": self.outTimeUpDownRate[bokHapKey]["시간외단일가점수"],
                    "상한가유지점수": upperMaintainJumsu, 
                    "커트라인" : cutLine,
                    "총점": chongjum
                }
                
                sum_save_item.append((cutLine, thema, code_nm, chongjum, ))

                self.mongodb.insert_item(save_item, "TodayStrongThema", "proMemeCodeList")
                self.mongodb.update_item({"$and": [{"복합키": bokHapKey},{"순위":"N"}]},{"$set": {"순위": "Y"}},"TodayStrongThema", "rawMemeCodeList")
                
            sum_save_item = pd.DataFrame(sum_save_item,columns=['커트라인', '테마', '종목명', '총점'])
            sum_save_item = sum_save_item.sort_values('총점', ascending=False)
            sum_save_item.insert(0,'순위',sum_save_item['총점'].rank(method='min', ascending=False, na_option='bottom'),allow_duplicates=False)
            
            # 순위가 커트라인보다 높거나 같은 라인까지만 추출

            condition = (sum_save_item.순위 <= sum_save_item.커트라인) # 조건식 작성
            sum_save_item = sum_save_item[condition]
            sum_save_item.set_index(keys='순위',inplace=True, drop=True)
            
            self.bot_send_in_cnt("매수 가능 종목\n%s" % sum_save_item)
            # db.collection.insert_many(df.to_dict('records'))
        
        self.logging.logger.debug("실시간 점수계산 로직 종료")
        #################################################
    
    # 상한가 계산하는 함수
    def calUpperPrice(self, price, market):
        # price = 전일종가
        price = price * 1.3
        
        if market == 'KOSDAQ':
            
            if price < 1000:
                # 1
                quote = int(price)
                
            elif price >= 1000 and price < 5000:
                # 5
                quote = int(price / 10) * 10 + 5
                if price < quote:
                    quote -= 5

            elif price >= 5000 and price < 10000:
                # 10
                quote = int(price / 10) * 10

            elif price >= 10000 and price < 50000:
                # 50
                quote = int(price / 100) * 100 + 50
                if price < quote:
                    quote -= 50

            elif price >= 50000:
                # 100
                quote = int(price / 100) * 100
                
            else:
                self.logging.logger.debug("calUpperPrice KOSDAQ price Error")
            
        elif market == 'KOSPI':
            
            if price < 1000:
                # 1
                quote = int(price)
            
            elif price >= 1000 and price < 5000:
                # 5
                quote = int(price / 10) * 10 + 5
                if price < quote:
                    quote -= 5
            
            elif price >= 5000 and price < 10000:
                # 10
                quote = int(price / 10) * 10

            elif price >= 10000 and price < 50000:
                # 50
                quote = int(price / 100) * 100 + 50
                if price < quote:
                    quote -= 50

            elif price >= 50000 and price < 100000:
                # 100
                quote = int(price / 100) * 100

            elif price >= 100000 and price < 500000:
                # 500
                quote = int(price / 1000) * 1000 + 500
                if price < quote:
                    quote -= 500

            elif price >= 500000:
                # 1000
                quote = int(price / 1000) * 1000
                
            else:
                self.logging.logger.debug("calUpperPrice KOSPI price Error")
                
        else:
            self.logging.logger.debug("calUpperPrice KOSPI/KOSDAQ gubn Error")
        
        return quote
    
            
    # 상한가 유지 점수를 계산하기 위한 식
    def upper_price_maintain_score(self, code):
        
        today = datetime.today()
        tomorrow = datetime.today() + timedelta(days=1)
        start = datetime(today.year, today.month, today.day) + timedelta(hours=8)
        end = datetime(tomorrow.year, tomorrow.month, tomorrow.day)

        aa = []
        aa_mongo = self.mongodb.find_items({"$and": [{"종목코드": code}, {"저장시간": {'$gte': start, '$lt' : end}}]}, "TodayStrongThema", "upperCodeOneMinData")

        if aa_mongo is not None:
            print("Not None")
            for item in aa_mongo:
                aa.append(item)
        else:
            print("None")
            pass
        
        return len(aa)
    # def out_time_up_down_rate_info(self, code, sPrevNext="0"):
    #     # 요청가능한 시간제한 걸어주기 (오전9시~오후3시30분)
    #     # self.logging.logger.debug("시간외단일가요청")
    #     try:
    #         self.dynamicCall("SetInputValue(QString, QString)","종목코드", code)
    #         # CommRqData : 조회함수
    #         self.dynamicCall("CommRqData(QString, QString, int, QString)", "시간외단일가요청", "opt10087", sPrevNext, self.screen_calculation_stock)
    #         self.calculator_event_loop.exec_()
    #     except KeyError:
    #         self.logging.logger.debug("시간외단일가요청 시 Error 발생")

    def detail_account_info(self, sPrevNext="0"):
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "0000")
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "1")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "예수금상세현황요청", "opw00001", sPrevNext, self.screen_my_info)

        self.detail_account_info_event_loop.exec_()
  
    def set_real_reg_stock_dict(self, code):
        try:
            screen_num = self.portfolio_stock_dict[code]['스크린번호']
            # self.logging.logger.debug("%s 의 스크린번호 %s 정상요청" % (code, screen_num))
        except KeyError:
            self.logging.logger.debug("%s 의 스크린번호 없음" % code)
            screen_num = '9000'
            self.logging.logger.debug("set_real_reg_stock_dict 의 screen_num KeyError")
        fids = self.realType.REALTYPE['주식체결']['체결시간']
        # 속도와 screen_num 의 수가 의심된다.
        self.dynamicCall("SetRealReg(QString, QString, QString, QString)", screen_num, code, fids, "1")
        
    ######### 초기 셋팅 함수들 바로 실행 Start ################

    def thema_make_check(self):
        self.logging.logger.debug("Ing thema make check function...")
        ##### 1. 포트폴리오에 담긴 종목을 기준으로 테마를 검색한다. #####
        thema_list = []  # 포트폴리오에 포함된 전체 테마
        set_list = []  # 테마의 중복을 제거하기 위한 리스트 변수
        portfolio_code_list = []  #포트폴리오에 포함된 종목
        for code in self.portfolio_stock_dict.keys():  # 포트폴리오에 담긴 종목코드 리스트를 추출
            portfolio_code_list.append(code)
            thema_none_check = self.mongodb.find_items({"종목코드": code}, "TodayStrongThema", "themaUpdate")  # 포트폴리오 리스트의 테마를 DB 에서 모두 뽑아서 중복을 제거하고 List 에 넣는다.
            for item in thema_none_check:
                if item["테마"] != "패스":
                    set_list.append(item["테마"])
                else:
                    pass
        thema_list = list(set(set_list))  # 중복이 제거된 테마리스트
        
        ##### 2. 테마를 기준으로 포트폴리오에 있는 종목을 분류하고 테마정보와 각 종목의 정보를 입력한다. #####
        thema_dict = {}  # 테마의 정보변수 (테마(Key) 10프로이상 등락률 거래대금 장악률 코드리스트)
        thema_dict_dict = {}  # 테마안에 포함된 개별 종목에 대한 정보변수 (종목코드(Key), 종목몇, 등락률, 거래대금, 장악률, 테마)
        for thema in thema_list:  # 중복이 제거된 테마리스트에 대해서
            QTest.qWait(400)
            thema_code_list = []  # 각 테마에 종목코드를 할당하는 딕셔너리를 만든다.
            thema_dict.update({thema:{}})  # 테마를 키로 dict 를 생성한다.
            rst1 = self.mongodb.find_items_distinct({"테마": thema}, "TodayStrongThema", "themaUpdate", "종목코드")  # 각 테마에 해당하는 종목코드(중복제거)를 추출한다.
            thema_code_list = list(rst1)  # 테마에 해당하는 종목코드를 리스트에 담는다 (포트폴리오를 넘어갈 수 있다.)
            # print("thema_code_list : %s" % thema_code_list)
            # print("thema_code_list_len : %s" % len(thema_code_list))

            sum_rate = 0  # 등락률의 합
            sum_rate_cnt = 0  # 등락률 합 의 수
            ten_more_cnt = 0  # 10프로이상 상승종목 수
            fifteen_more_cnt = 0 # 15프로이상 상승종목 수 
            total_don = 0  # 거래대금의 합
            holdPower = 0  # 장악률의 합
            
            # 각 종목의 정보를 입력한다
            for item in thema_code_list:  # 테마의 코드리스트에 있는 종목들을
                QTest.qWait(400)
                # 여기에서 포트폴리오에 없으면 넣고 실시간 데이터 추가하도록 수정필요
                if item in self.portfolio_stock_dict.keys():  # 포트폴리오에 있는 종목으로 필터링
                    try:
                        # 테마 dict 에 해당하는 각키에 해당하는 value (종목명, 등락률, 거래대금, 시장악악률, 테마) 를 추출 후 dict 에 넣는다.
                        # 장 시작전에는 데이터를 못 받아오기 때문에 에러가 발생한다.
                        a = item
                        b = self.portfolio_stock_dict[item]["종목명"]
                        c = self.portfolio_stock_dict[item]["등락률"]
                        d = self.portfolio_stock_dict[item]["누적거래대금"]
                        e = self.portfolio_stock_dict[item]["장악률"]
                        f = thema
                        
                        thema_dict_dict.update({item:{}})
                        thema_dict_dict[item].update({"종목코드":a})
                        thema_dict_dict[item].update({"종목명":b})
                        thema_dict_dict[item].update({"등락률":c})
                        thema_dict_dict[item].update({"거래대금":d})
                        thema_dict_dict[item].update({"장악률":e})
                        thema_dict_dict[item].update({"테마":f})
                        # print("종목코드 %s 종목명 %s 등락률 %s 거래대금 %s 장악률 %s 테마 %s" % (a,b,c,d,e,f))
                        sum_rate = sum_rate + c
                        sum_rate_cnt = sum_rate_cnt + 1
                        total_don = total_don + d
                        if c > 10:
                            ten_more_cnt = ten_more_cnt + 1  # 10프로 이상 상승종목 수
                        if c > 15:
                            fifteen_more_cnt = fifteen_more_cnt + 1  # 15프로 이상 상승종목 수 
                        holdPower = holdPower + e
                        # self.logging.logger.debug("등락률의 합 %s 등락률합한 수 %s 거래대금의 합 %s 10프로 이상 상승종목 수 %s 장악률의 합 %s"% (sum_rate,sum_rate_cnt,total_don,ten_more_cnt,holdPower))
                    except KeyError:
                        # self.logging.logger.debug("테마 코드리스트의 포트폴리오에 있는 종목인데Key Error ")
                        pass
                else:
                    pass
            # self.logging.logger.debug("테마 코드정보 입력 완료")
            # 테마 평균 등락률 계산
            if sum_rate_cnt != 0:
                rate_avg = round((sum_rate / sum_rate_cnt), 1)
            else:
                rate_avg = 0
            try:
                thema_dict[thema].update({"10프로이상": ten_more_cnt})
                thema_dict[thema].update({"15프로이상": fifteen_more_cnt})
                thema_dict[thema].update({"등락률": rate_avg})
                thema_dict[thema].update({"거래대금": round(total_don/1000000,2)})
                thema_dict[thema].update({"장악률": holdPower})
                thema_dict[thema].update({"코드리스트": thema_code_list})
            except KeyError:
                self.logging.logger.debug("thema 리스트 만들다 에러남")

        ##### 3. 테마의 정보를 기준으로 여러 조건을 만들기 위한 기초 테마 정보를 DataFrame 으로 구성한다.  #####
        don_order_dict = {}
        ten_order_dict = {}
        ten_power_order_dict = {}
        fifteen_order_dict = {}
        # 테마 리스트를 추출하기 위해 기존 데이터를 재구성한다.
        for key, value in thema_dict.items():
            new_key = key
            new_value = value
            ten_order_dict.update({new_key:new_value["10프로이상"]})
            fifteen_order_dict.update({new_key:new_value["15프로이상"]})
            don_order_dict.update({new_key:new_value["거래대금"]})
            ten_power_order_dict.update({new_key:new_value["장악률"]})

        # 테마의 15% 이상 2개이상 조건 + 종목수 순위를 판단하기 위한 데이터 생성
        df_fifteen_order_list = pd.DataFrame(list(fifteen_order_dict.items()),columns=['테마', '15프로이상'])
        df_fifteen_order_list = df_fifteen_order_list.sort_values('15프로이상', ascending=False)
        df_fifteen_order_list['rank_min'] = df_fifteen_order_list['15프로이상'].rank(method='first', ascending=False, na_option='bottom')
        
        self.logging.logger.debug("15%% 2개이상 테마: %s " % df_fifteen_order_list)
        
        # 테마의 10% 이상 3개이상 조건 + 종목수 순위를 판단하기 위한 데이터 생성
        df_ten_order_list = pd.DataFrame(list(ten_order_dict.items()),columns=['테마', '10프로이상'])
        df_ten_order_list = df_ten_order_list.sort_values('10프로이상', ascending=False)
        df_ten_order_list['rank_min'] = df_ten_order_list['10프로이상'].rank(method='first', ascending=False, na_option='bottom')
        
        self.logging.logger.debug("10%% 3개이상 테마: %s " % df_ten_order_list)
            
        # 테마 내 종목들의 거래대금 순위를 판단하기위한 데이터 생성
        df_don_order_list = pd.DataFrame(list(don_order_dict.items()),columns=['테마', '거래대금'])
        df_don_order_list = df_don_order_list.sort_values('거래대금', ascending=False)
        df_don_order_list['rank_min'] = df_don_order_list['거래대금'].rank(method='first', ascending=False, na_option='bottom')
        
        self.logging.logger.debug("거래대금상위테마: %s " % df_don_order_list)
        
        # 테마 내 종목들의 시장장악을 판단하기위한 데이터 생성
        df_power_order_list = pd.DataFrame(list(ten_power_order_dict.items()),columns=['테마', '장악률'])
        df_power_order_list = df_power_order_list.sort_values('장악률', ascending=False)
        
        self.logging.logger.debug("장악률 기준 테마 분류: %s " % df_power_order_list)
        
        ##### 4. 기초 테마정보를 바탕으로 원하는 조건을 만든다. (거래대금상위, 10프로이상 종목수 상위) #####
        two_fifteen_order_list = []
        two_fifteen_top_order_list = []
        three_ten_order_list = []
        three_ten_top_order_list = []
        three_ten_power_order_list = [] 
        top_don_order_list = []

        # 15%↑ 2↑ 테마 리스트 추출
        for i in range(len(df_fifteen_order_list['테마'][df_fifteen_order_list['15프로이상'] >= 2])):
            two_fifteen_order_list.append(df_fifteen_order_list['테마'][df_fifteen_order_list['15프로이상'] >= 2].iloc[i])
        self.logging.logger.debug("15%%↑ 2↑ 테마 : %s " % two_fifteen_order_list)

        # 15%↑ 테마 리스트 중 순위가 가장 높은 테마 추출
        for i in range(len(df_fifteen_order_list['테마'][df_fifteen_order_list['rank_min'] < 2])):
            two_fifteen_top_order_list.append(df_fifteen_order_list['테마'][df_fifteen_order_list['rank_min'] < 2].iloc[i])        
        self.logging.logger.debug("15%%↑ 중 상승률 베스트 테마 : %s " % two_fifteen_top_order_list)
        
        # 10%↑ 3↑ 테마 리스트 추출
        for i in range(len(df_ten_order_list['테마'][df_ten_order_list['10프로이상'] >= 3])):
            three_ten_order_list.append(df_ten_order_list['테마'][df_ten_order_list['10프로이상'] >= 3].iloc[i])
        self.logging.logger.debug("10%%↑ 3↑ 테마 : %s " % three_ten_order_list)
        
        # 10%↑ 테마 리스트 중 순위가 가장 높은 테마 추출
        for i in range(len(df_ten_order_list['테마'][df_ten_order_list['rank_min'] < 2])):
            three_ten_top_order_list.append(df_ten_order_list['테마'][df_ten_order_list['rank_min'] < 2].iloc[i])
        self.logging.logger.debug("10%%↑ 중 상승률 베스트 테마 : %s " % three_ten_top_order_list)

        # 장악률 5%↑ 테마 리스트 추출
        for i in range(len(df_power_order_list['테마'][df_power_order_list['장악률'] >= 5])):
            three_ten_power_order_list.append(df_power_order_list['테마'][df_power_order_list['장악률'] >= 5].iloc[i])
        self.logging.logger.debug("장악률 5%% 이상 테마 : %s " % three_ten_power_order_list)
        
        # 거래대금1위 테마 리스트 추출
        for i in range(len(df_don_order_list['테마'][df_don_order_list['rank_min'] < 2])):
            top_don_order_list.append(df_don_order_list['테마'][df_don_order_list['rank_min'] < 2].iloc[i])    
        self.logging.logger.debug("거래대금1위 테마 : %s " % top_don_order_list)

        ##### 5. 원하는 조건을 더 디테일화한다. #####
        buy_first_condition_thema_list = []  # 매수 1순위 테마 리스트
        buy_second_condition_thema_list = []  # 매수 2순위 테마 리스트
        buy_third_condition_thema_list = []  # 매수 3순위 테마리스트akdntm zuwudlTdma
        buy_atleast_condition_list = [] # 매수 4 순위
        
        two_buy_first_condition_thema_list = []  # 매수 1순위 테마 리스트
        two_buy_second_condition_thema_list = []  # 매수 2순위 테마 리스트
        two_buy_third_condition_thema_list = []  # 매수 3순위 테마리스트
        two_buy_atleast_condition_list = []  # 매수 4순위 테마 리스트
        
        # 15%↑ 2↑
        for thema in two_fifteen_order_list:
            # 장악률 5% 이상 테마 (최소매매조건 필터)
            if thema in three_ten_power_order_list:
                # 15%↑ 2↑ 1순위 + 거래대금1위 (매매1순위) - 한 개
                if (thema in two_fifteen_top_order_list) and (thema in top_don_order_list):
                    two_buy_first_condition_thema_list.append(thema)
                # 15%↑ 2↑ + 거래대금1위 테마 (매매2순위) - 여러개
                elif thema in top_don_order_list:
                    two_buy_second_condition_thema_list.append(thema)
                # 15%↑ 2↑ 1순위 (매매3순위)
                elif thema in two_fifteen_top_order_list:
                    two_buy_third_condition_thema_list.append(thema)
                # 최소매매 조건
                else:
                    two_buy_atleast_condition_list.append(thema)
            else:
                pass
                self.logging.logger.debug("15프로이상 상승종목이 2종목 이상이면서 장악률 5%이상의 테마가 없음")
                
        # 10%↑ 3↑
        for thema in three_ten_order_list:
            # 장악률 5% 이상 테마 (최소매매조건 필터)
            if thema in three_ten_power_order_list:
                # 10%↑ 3↑ 1순위 + 거래대금1위 (매매1순위)
                if (thema in top_don_order_list) and (thema in three_ten_top_order_list):
                    buy_first_condition_thema_list.append(thema)
                # 거래대금1위 테마 (매매2순위)
                elif (thema in top_don_order_list) and (thema not in three_ten_top_order_list):
                    buy_second_condition_thema_list.append(thema)
                # 10%↑ 3↑ 1순위 (매매3순위)
                elif (thema not in top_don_order_list) and (thema in three_ten_top_order_list):
                    buy_third_condition_thema_list.append(thema)
                # 최소매매 조건
                else:
                    buy_atleast_condition_list.append(thema)
            else:
                pass
                self.logging.logger.debug("10프로이상 상승종목이 3종목 이상이면서 장악률 5%이상의 테마가 없음")

        # print("모두 만족하는 테마 %s " % sam_top_don_thema_list)

        kospi_don = 0
        kosdaq_don = 0
        try:
            kospi_don = self.upjong_dict["001"]["누적거래대금"]
        except KeyError:
            kospi_don = 0
        try:
            kosdaq_don = self.upjong_dict["101"]["누적거래대금"]
        except KeyError:
            kospi_don = 0

        # print("kospi 거래대금: %s kosdaq 거래대금: %s" % (kospi_don, kosdaq_don))
        
        if kospi_don == 0 or kosdaq_don == 0:
            kospi_kosdaq_don = "KOSPI KOSDAQ 지수 업데이트 전"
        else:
            kospi_kosdaq_don = "KOSPI: %s(조) KOSDAQ: %s(조)" % (round(kospi_don/1000000,1), round(kosdaq_don/1000000,1))
        
        ##### 6. 각 테마의 종목 정보를 구체화 시킨다. #####
        
        buy_first_condition_code_list = []  # 10% 매수 1순위 테마의 종목 리스트
        buy_second_condition_code_list = []  # 10% 매수 2순위 테마의 종목 리스트
        buy_third_condition_code_list = []  # 10% 매수 3순위 테마의 종목 리스트
        buy_atleast_condition_code_list = []  # 10% 매수 4순위 테마의 종목 리스트
        
        buy_first_condition_mgs = []  # 10% 매수 1순위 봇 메시지 담는 변수
        buy_second_condition_mgs = []  # 10% 매수 2순위 봇 메시지 담는 변수
        buy_third_condition_mgs = []  # 10% 매수 3순위 봇 메시지 담는 변수
        buy_atleast_condition_mgs = []  # 10% 매수 4순위 봇 메시지 담는 변수
        
        two_buy_first_condition_code_list = []  # 15% 매수 1순위 테마의 종목 리스트
        two_buy_second_condition_code_list = []  # 15% 매수 2순위 테마의 종목 리스트
        two_buy_third_condition_code_list = []  # 15% 매수 3순위 테마의 종목 리스트
        two_buy_atleast_condition_code_list = []  # 15% 매수 4순위 테마의 종목 리스트
        
        two_buy_first_condition_mgs = []  # 15% 매수 1순위 봇 메시지 담는 변수
        two_buy_second_condition_mgs = []  # 15% 매수 2순위 봇 메시지 담는 변수
        two_buy_third_condition_mgs = []  # 15% 매수 3순위 봇 메시지 담는 변수
        two_buy_atleast_condition_mgs = []  # 15% 매수 4순위 봇 메시지 담는 변수
        
        sum_save_item = []
        # 10%↑ 3↑ 1위, 거래대금 1위 로 매수 1순위 테마의 종목들 (종목명 등락률 거래대금 장악률 종목순위)
        for thema in buy_first_condition_thema_list:
            save_time = datetime.today()
            thema_contents = []
            a = thema
            b = thema_dict[thema]["10프로이상"]
            c = thema_dict[thema]["등락률"]
            d = thema_dict[thema]["거래대금"]
            e = round(thema_dict[thema]["장악률"],2)
            thema_jumsu = round(thema_dict[thema]["등락률"] * self.PerRate + ( round(thema_dict[thema]["장악률"],2) * self.PerPower / thema_dict[thema]["10프로이상"] ))
            # 헤더의 출력 값 양식
            df_header = ("%s 점수: %s점 10%%↑: %s개 등락률: %s%% 거래대금: %s조 장악률: %s%%" % (a, thema_jumsu, b, c, d, e))
            self.logging.logger.debug(df_header)
            
            code_rst1 = thema_dict[thema]["코드리스트"]
            code_rst2 = []
            dup_check_only_rate = []
            # 테마에 있는 종목들의 실시간 정보 업데이트
            for code in code_rst1:
                
                if code in self.portfolio_stock_dict.keys():
                    try:
                        a = self.portfolio_stock_dict[code]["종목명"]
                        b = self.portfolio_stock_dict[code]["등락률"]
                        c = round(self.portfolio_stock_dict[code]["누적거래대금"]/100)
                        d = self.portfolio_stock_dict[code]["장악률"]
                        thema_contents.append((a, b, c, d))
                        dup_check_only_rate.append(b)
                        # 종목 점수 계산에 필요한 변수
                        if b > 10:
                            e = round(b * self.PerRate,0)  # 등락률 점수
                            f = round(d * self.PerPower,0)  # 장악률 점수
                            
                            save_item = {
                                "저장시간": save_time,
                                "복합키": str(thema)+str(code)+str(save_time),
                                "날짜": save_time.strftime("%Y%m%d"),
                                "테마": thema,
                                "테마점수": thema_jumsu,
                                "커트라인": thema_dict[thema]["10프로이상"],
                                "종목코드": code,
                                "종목명": a,
                                "등락률": b,
                                "등락률베이스점수": self.PerRate,
                                "등락률점수": e,
                                "장악률": d,
                                "장악률베이스점수": self.PerPower,
                                "장악률점수": f, 
                                "순위": "N",
                                "총점": e + f
                            }
                            sum_save_item.append(save_item)
                            code_rst2.append(code)
                        else:
                            pass
                    except KeyError:
                        self.logging.logger.debug("Code Score Error")
                else:
                    pass
                    # self.logging.logger.debug("테마에 있는 종목이 포트폴리오 안에 없음")

            # 현재 선택된 테마의 가장 높은 등락률 max(dup_check_only_rate)
            if len(dup_check_only_rate) == 0:
                dup_check_only_rate.append(0)
                self.logging.logger.debug("기존 중복 테마가 없어서 가장 높은 등락률 0으로 설정")
            else:
                pass
            
            tempCodeRateDupCheck = []
            tempCodeListDupCheck = []
            mongoRateList = self.mongodb.find_items({"$and":[{"테마":thema},{"날짜":save_time.strftime("%Y%m%d")}]},"TodayStrongThema","rawMemeCodeList")
            
            for i in mongoRateList:
                tempCodeRateDupCheck.append(i["등락률"])
                tempCodeListDupCheck.append(i["종목코드"])
            
            if len(tempCodeRateDupCheck) == 0:
                tempCodeRateDupCheck.append(0)
            
            # tempCodeListDupCheck 리스트의 중복제거
            tempCodeListDupCheck = list(set(tempCodeListDupCheck))
            
            self.logging.logger.debug("최고등락률 비교 : %s vs %s " % (max(tempCodeRateDupCheck), max(dup_check_only_rate)))
            self.logging.logger.debug("최고등락률 비교 : %s " % (max(tempCodeRateDupCheck) <= max(dup_check_only_rate)))
            self.logging.logger.debug("중복선정비교 DB 에 있는 종목 : %s " % tempCodeListDupCheck)
            self.logging.logger.debug("지금 추출된 종목 : %s " % code_rst2)
            self.logging.logger.debug("종목비교 : %s " % (len(set(code_rst2)-set(tempCodeListDupCheck)) > 0))
            
            if (max(tempCodeRateDupCheck) <= max(dup_check_only_rate)) and (len(set(code_rst2)-set(tempCodeListDupCheck)) > 0):
                # Contents DataFrame 만들기
                df_contents = pd.DataFrame(thema_contents, columns = ['종목명','등락률','거래대금','장악률'])
                df_contents = df_contents.sort_values("등락률", ascending=False)
                df_contents.insert(0,'순위',df_contents['등락률'].rank(method='min', ascending=False, na_option='bottom'),allow_duplicates=False)
                df_contents.set_index(keys='순위',inplace=True, drop=True)
                
                buy_first_condition_mgs.append("☆☆  당일주도주  ☆☆\n%s\n%s\n\n%s" % (kospi_kosdaq_don,df_header,df_contents))
                buy_first_condition_code_list.append(code_rst2)
            else:
                self.logging.logger.debug("종목선정 1번식 중복으로 발송안함")
            
            if (len(buy_first_condition_code_list) != 0):
                for i in range(len(buy_first_condition_mgs)):
                    self.bot_send_in_cnt(buy_first_condition_mgs[i])

                self.logging.logger.debug("☆☆  당일주도주(종목선정 1번식)  ☆☆\n%s\n%s\n\n%s" % (kospi_kosdaq_don,df_header,df_contents))
                for save_item in sum_save_item:
                    self.mongodb.upsert_item({"복합키": save_item["복합키"]}, {"$set": save_item}, "TodayStrongThema", "rawMemeCodeList")
                self.cal_total_score()
            else:
                pass
                # print("중복이거나 걸리는 조건 없음")
        
        sum_save_item = []
        # 10% 3개이상 + 거래대금 1위 로 매수 2순위 테마의 종목들 (종목명 등락률 거래대금 장악률 종목순위)
        for thema in buy_second_condition_thema_list:
            save_time = datetime.today()
            thema_contents = []
            a = thema
            b = thema_dict[thema]["10프로이상"]
            c = thema_dict[thema]["등락률"]
            d = thema_dict[thema]["거래대금"]
            e = round(thema_dict[thema]["장악률"],2)
            thema_jumsu = round(thema_dict[thema]["등락률"] * self.PerRate + ( round(thema_dict[thema]["장악률"],2) * self.PerPower / thema_dict[thema]["10프로이상"] ))
            # 헤더의 출력 값 양식
            df_header = ("%s 점수: %s점 10%%↑: %s개 등락률: %s%% 거래대금: %s조 장악률: %s%%" % (a, thema_jumsu, b, c, d, e))
            self.logging.logger.debug(df_header)
            
            code_rst1 = thema_dict[thema]["코드리스트"]
            code_rst2 = []
            dup_check_only_rate = []
            # 테마에 있는 종목들의 실시간 정보 업데이트
            for code in code_rst1:
                
                if code in self.portfolio_stock_dict.keys():
                    try:
                        a = self.portfolio_stock_dict[code]["종목명"]
                        b = self.portfolio_stock_dict[code]["등락률"]
                        c = round(self.portfolio_stock_dict[code]["누적거래대금"]/100)
                        d = self.portfolio_stock_dict[code]["장악률"]
                        thema_contents.append((a, b, c, d))
                        dup_check_only_rate.append(b)
                        # 종목 점수 계산에 필요한 변수
                        if b > 10:
                            e = round(b * self.PerRate,0)  # 등락률 점수
                            f = round(d * self.PerPower,0)  # 장악률 점수

                            save_item = {
                                "저장시간": save_time,
                                "복합키": str(thema)+str(code)+str(save_time),
                                "날짜": save_time.strftime("%Y%m%d"),
                                "테마": thema,
                                "테마점수": thema_jumsu,
                                "커트라인": thema_dict[thema]["10프로이상"],
                                "종목코드": code,
                                "종목명": a,
                                "등락률": b,
                                "등락률베이스점수": self.PerRate,
                                "등락률점수": e,
                                "장악률": d,
                                "장악률베이스점수": self.PerPower,
                                "장악률점수": f,
                                "순위": "N",
                                "총점": e + f
                            }
                            sum_save_item.append(save_item)
                            code_rst2.append(code)
                        else:
                            pass
                    except KeyError:
                        self.logging.logger.debug("Code Score Error")
                else:
                    pass
                    # self.logging.logger.debug("테마에 있는 종목이 포트폴리오 안에 없음")

            # 현재 선택된 테마의 가장 높은 등락률 max(dup_check_only_rate)
            if len(dup_check_only_rate) == 0:
                dup_check_only_rate.append(0)
                self.logging.logger.debug("기존 중복 테마가 없어서 가장 높은 등락률 0으로 설정")
            else:
                pass
            
            tempCodeRateDupCheck = []
            tempCodeListDupCheck = []
            mongoRateList = self.mongodb.find_items({"$and":[{"테마":thema},{"날짜":save_time.strftime("%Y%m%d")}]},"TodayStrongThema","rawMemeCodeList")
            
            for i in mongoRateList:
                tempCodeRateDupCheck.append(i["등락률"])
                tempCodeListDupCheck.append(i["종목코드"])
                
            if len(tempCodeRateDupCheck) == 0:
                tempCodeRateDupCheck.append(0)
            
            # tempCodeListDupCheck 리스트의 중복제거
            tempCodeListDupCheck = list(set(tempCodeListDupCheck))
            
            self.logging.logger.debug("최고등락률 비교 : %s vs %s " % (max(tempCodeRateDupCheck), max(dup_check_only_rate)))
            self.logging.logger.debug("최고등락률 비교 : %s " % (max(tempCodeRateDupCheck) <= max(dup_check_only_rate)))
            self.logging.logger.debug("중복선정비교 DB 에 있는 종목 : %s " % tempCodeListDupCheck)
            self.logging.logger.debug("지금 추출된 종목 : %s " % code_rst2)
            self.logging.logger.debug("종목비교 : %s " % (len(set(code_rst2)-set(tempCodeListDupCheck)) > 0))
            
            if (max(tempCodeRateDupCheck) <= max(dup_check_only_rate)) and (len(set(code_rst2)-set(tempCodeListDupCheck)) > 0):
                # Contents DataFrame 만들기
                df_contents = pd.DataFrame(thema_contents, columns = ['종목명','등락률','거래대금','장악률'])
                df_contents = df_contents.sort_values("등락률", ascending=False)
                df_contents.insert(0,'순위',df_contents['등락률'].rank(method='min', ascending=False, na_option='bottom'),allow_duplicates=False)
                df_contents.set_index(keys='순위',inplace=True, drop=True)
                
                buy_second_condition_mgs.append("☆☆ 당일주도주  ☆☆\n%s\n%s\n\n%s" % (kospi_kosdaq_don,df_header,df_contents))
                buy_second_condition_code_list.append(code_rst2) # 밖에 있는 변수와 통신이 필요
            else:
                self.logging.logger.debug("종목선정 2번식 중복으로 발송안함")

            if (len(buy_second_condition_code_list) != 0):
                for i in range(len(buy_second_condition_mgs)):
                    self.bot_send_in_cnt(buy_second_condition_mgs[i])

                self.logging.logger.debug("☆☆  당일주도주(종목선정 2번식)  ☆☆\n%s\n%s\n\n%s" % (kospi_kosdaq_don,df_header,df_contents))
                for save_item in sum_save_item:
                    self.mongodb.upsert_item({"복합키": save_item["복합키"]}, {"$set": save_item}, "TodayStrongThema", "rawMemeCodeList")
                self.cal_total_score()
            else:
                pass
                # print("중복이거나 걸리는 조건 없음")
        
        sum_save_item = []    
        # 10%↑ 3↑ 1위로 매수 3순위 테마의 종목들 (종목명 등락률 거래대금 장악률 종목순위)
        for thema in buy_third_condition_thema_list:
            save_time = datetime.today()
            thema_contents = []
            a = thema
            b = thema_dict[thema]["10프로이상"]
            c = thema_dict[thema]["등락률"]
            d = thema_dict[thema]["거래대금"]
            e = round(thema_dict[thema]["장악률"],2)
            thema_jumsu = round(thema_dict[thema]["등락률"] * self.PerRate + ( round(thema_dict[thema]["장악률"],2) * self.PerPower / thema_dict[thema]["10프로이상"] ))
            # 헤더의 출력 값 양식
            df_header = ("%s 점수: %s점 10%%↑: %s개 등락률: %s%% 거래대금: %s조 장악률: %s%%" % (a, thema_jumsu, b, c, d, e))
            self.logging.logger.debug(df_header)
            
            code_rst1 = thema_dict[thema]["코드리스트"]
            code_rst2 = []
            dup_check_only_rate = []
            # 테마에 있는 종목들의 실시간 정보 업데이트
            for code in code_rst1:

                if code in self.portfolio_stock_dict.keys():
                    try:
                        a = self.portfolio_stock_dict[code]["종목명"]
                        b = self.portfolio_stock_dict[code]["등락률"]
                        c = round(self.portfolio_stock_dict[code]["누적거래대금"]/100)
                        d = self.portfolio_stock_dict[code]["장악률"]
                        thema_contents.append((a, b, c, d))
                        dup_check_only_rate.append(b)
                        # 종목 점수 계산에 필요한 변수
                        if b > 10:
                            e = round(b * self.PerRate,0)  # 등락률 점수
                            f = round(d * self.PerPower,0)  # 장악률 점수
                            
                            save_item = {
                                "저장시간": save_time,
                                "복합키": str(thema)+str(code)+str(save_time),
                                "날짜": save_time.strftime("%Y%m%d"),
                                "테마": thema,
                                "테마점수": thema_jumsu,
                                "커트라인": thema_dict[thema]["10프로이상"],
                                "종목코드": code,
                                "종목명": a,
                                "등락률": b,
                                "등락률베이스점수": self.PerRate,
                                "등락률점수": e,
                                "장악률": d,
                                "장악률베이스점수": self.PerPower,
                                "장악률점수": f,
                                "순위": "N",
                                "총점": e + f
                            }
                            sum_save_item.append(save_item)
                            code_rst2.append(code)
                        else:
                            pass
                    except KeyError:
                        self.logging.logger.debug("Code Score Error")
                else:
                    pass 
                    # self.logging.logger.debug("테마에 있는 종목이 포트폴리오 안에 없음")
                    
            # 현재 선택된 테마의 가장 높은 등락률
            if len(dup_check_only_rate) == 0:
                dup_check_only_rate.append(0)
                self.logging.logger.debug("기존 중복 테마가 없어서 가장 높은 등락률 0으로 설정")
            else:
                pass
            
            tempCodeRateDupCheck = []
            tempCodeListDupCheck = []
            mongoRateList = self.mongodb.find_items({"$and":[{"테마":thema},{"날짜":save_time.strftime("%Y%m%d")}]},"TodayStrongThema","rawMemeCodeList")
            
            for i in mongoRateList:
                tempCodeRateDupCheck.append(i["등락률"])
                tempCodeListDupCheck.append(i["종목코드"])
            
            if len(tempCodeRateDupCheck) == 0:
                tempCodeRateDupCheck.append(0)
            
            # tempCodeListDupCheck 리스트의 중복제거
            tempCodeListDupCheck = list(set(tempCodeListDupCheck))
            
            self.logging.logger.debug("최고등락률 비교 : %s vs %s " % (max(tempCodeRateDupCheck), max(dup_check_only_rate)))
            self.logging.logger.debug("최고등락률 비교 : %s " % (max(tempCodeRateDupCheck) <= max(dup_check_only_rate)))
            self.logging.logger.debug("중복선정비교 DB 에 있는 종목 : %s " % tempCodeListDupCheck)
            self.logging.logger.debug("지금 추출된 종목 : %s " % code_rst2)
            self.logging.logger.debug("종목비교 : %s " % (len(set(code_rst2)-set(tempCodeListDupCheck)) > 0))
            
            if (max(tempCodeRateDupCheck) <= max(dup_check_only_rate)) and (len(set(code_rst2)-set(tempCodeListDupCheck)) > 0):
                # Contents DataFrame 만들기
                df_contents = pd.DataFrame(thema_contents, columns = ['종목명','등락률','거래대금','장악률'])
                df_contents = df_contents.sort_values("등락률", ascending=False)
                df_contents.insert(0,'순위',df_contents['등락률'].rank(method='min', ascending=False, na_option='bottom'),allow_duplicates=False)
                df_contents.set_index(keys='순위',inplace=True, drop=True)
                
                buy_third_condition_mgs.append("☆☆  당일주도주  ☆☆\n%s\n%s\n\n%s" % (kospi_kosdaq_don,df_header,df_contents))
                buy_third_condition_code_list.append(code_rst2) # 밖에 있는 변수와 통신이 필요
            else:
                buy_third_condition_code_list = []
                self.logging.logger.debug("종목선정 3번식 중복으로 발송안함")

            if (len(buy_third_condition_code_list) != 0):
                for i in range(len(buy_third_condition_mgs)):
                    self.bot_send_in_cnt(buy_third_condition_mgs[i])

                self.logging.logger.debug("☆☆  당일주도주(종목선정 3번식)  ☆☆\n%s\n%s\n\n%s" % (kospi_kosdaq_don,df_header,df_contents))
                for save_item in sum_save_item:
                    self.mongodb.upsert_item({"복합키": save_item["복합키"]}, {"$set": save_item}, "TodayStrongThema", "rawMemeCodeList")
                self.cal_total_score()
            else:
                pass
                # print("매수 3순위 조건에 걸리는 종목 없음")
        
        sum_save_item = []       
        # 10%↑ 3↑ 이고 장악률 10% 이상의 매수 커트라인(4순위) 종목 (종목명 등락률 거래대금 장악률 종목순위)
        for thema in buy_atleast_condition_list:
            save_time = datetime.today()
            thema_contents = []
            a = thema
            b = thema_dict[thema]["10프로이상"]
            c = thema_dict[thema]["등락률"]
            d = thema_dict[thema]["거래대금"]
            e = round(thema_dict[thema]["장악률"],2)
            thema_jumsu = round(thema_dict[thema]["등락률"] * self.PerRate + ( round(thema_dict[thema]["장악률"],2) * self.PerPower / thema_dict[thema]["10프로이상"] ))
            # 헤더의 출력 값 양식
            df_header = ("%s 점수: %s점 10%%↑: %s개 등락률: %s%% 거래대금: %s조 장악률: %s%%" % (a, thema_jumsu, b, c, d, e))
            self.logging.logger.debug(df_header)
            
            code_rst1 = thema_dict[thema]["코드리스트"]
            code_rst2 = []
            dup_check_only_rate = []

            # 테마에 있는 종목들의 실시간 정보 업데이트
            for code in code_rst1:
                
                if code in self.portfolio_stock_dict.keys():
                    try:
                        a = self.portfolio_stock_dict[code]["종목명"]
                        b = self.portfolio_stock_dict[code]["등락률"]
                        c = round(self.portfolio_stock_dict[code]["누적거래대금"]/100)
                        d = self.portfolio_stock_dict[code]["장악률"]
                        thema_contents.append((a, b, c, d))
                        dup_check_only_rate.append(b)
                        # 종목 점수 계산에 필요한 변수
                        if b > 10:
                            e = round(b * self.PerRate,0)  # 등락률 점수
                            f = round(d * self.PerPower,0)  # 장악률 점수
                            
                            save_item = {
                                "저장시간": save_time,
                                "복합키": str(thema)+str(code)+str(save_time),
                                "날짜": save_time.strftime("%Y%m%d"),
                                "테마": thema,
                                "테마점수": thema_jumsu,
                                "커트라인": thema_dict[thema]["10프로이상"],
                                "종목코드": code,
                                "종목명": a,
                                "등락률": b,
                                "등락률베이스점수": self.PerRate,
                                "등락률점수": e,
                                "장악률": d,
                                "장악률베이스점수": self.PerPower,
                                "장악률점수": f,
                                "순위": "N",
                                "총점": e + f
                            }
                            sum_save_item.append(save_item)
                            code_rst2.append(code)
                        else:
                            pass
                    except KeyError:
                        self.logging.logger.debug("Code Score Error")
                else:
                    pass
                    # self.logging.logger.debug("테마에 있는 종목이 포트폴리오 안에 없음")

            # 현재 선택된 테마의 가장 높은 등락률 max(dup_check_only_rate)
            if len(dup_check_only_rate) == 0:
                dup_check_only_rate.append(0)
                self.logging.logger.debug("기존 중복 테마가 없어서 가장 높은 등락률 0으로 설정")
            else:
                pass
            
            tempCodeRateDupCheck = []
            tempCodeListDupCheck = []
            mongoRateList = self.mongodb.find_items({"$and":[{"테마":thema},{"날짜":save_time.strftime("%Y%m%d")}]},"TodayStrongThema","rawMemeCodeList")
            
            for i in mongoRateList:
                tempCodeRateDupCheck.append(i["등락률"])
                tempCodeListDupCheck.append(i["종목코드"])
            
            if len(tempCodeRateDupCheck) == 0:
                tempCodeRateDupCheck.append(0)
                
            # tempCodeListDupCheck 리스트의 중복제거
            tempCodeListDupCheck = list(set(tempCodeListDupCheck))
            
            self.logging.logger.debug("최고등락률 비교 : %s vs %s " % (max(tempCodeRateDupCheck), max(dup_check_only_rate)))
            self.logging.logger.debug("최고등락률 비교 : %s " % (max(tempCodeRateDupCheck) <= max(dup_check_only_rate)))
            self.logging.logger.debug("중복선정비교 DB 에 있는 종목 : %s " % tempCodeListDupCheck)
            self.logging.logger.debug("지금 추출된 종목 : %s " % code_rst2)
            self.logging.logger.debug("종목비교 : %s " % (len(set(code_rst2)-set(tempCodeListDupCheck)) > 0))
            # 이전보다 상승률이 높거나 같고 중복된 코드리스트가 아닌 경우
            if (max(tempCodeRateDupCheck) <= max(dup_check_only_rate)) and (len(set(code_rst2)-set(tempCodeListDupCheck)) > 0):
                # Contents DataFrame 만들기
                df_contents = pd.DataFrame(thema_contents, columns = ['종목명','등락률','거래대금','장악률'])
                df_contents = df_contents.sort_values("등락률", ascending=False)
                df_contents.insert(0,'순위',df_contents['등락률'].rank(method='min', ascending=False, na_option='bottom'),allow_duplicates=False)
                df_contents.set_index(keys='순위',inplace=True, drop=True)
                
                buy_atleast_condition_mgs.append("☆☆  당일주도주  ☆☆\n%s\n%s\n\n%s" % (kospi_kosdaq_don,df_header,df_contents))
                buy_atleast_condition_code_list.append(code_rst2) # 밖에 있는 변수와 통신이 필요
            else:
                buy_atleast_condition_code_list = []
                self.logging.logger.debug("종목선정 4번식 중복으로 발송안함")
            
            if (len(buy_atleast_condition_code_list) != 0):
                for i in range(len(buy_atleast_condition_mgs)):
                    self.bot_send_in_cnt(buy_atleast_condition_mgs[i])

                self.logging.logger.debug("☆☆  당일주도주(종목선정 4번식)  ☆☆\n%s\n%s\n\n%s" % (kospi_kosdaq_don,df_header,df_contents))
                for save_item in sum_save_item:
                    self.mongodb.upsert_item({"복합키": save_item["복합키"]}, {"$set": save_item}, "TodayStrongThema", "rawMemeCodeList")
                self.cal_total_score()
            else:
                pass
                # print("중복이거나 걸리는 조건 없음")

        sum_save_item = []
        # 15%↑ 2↑ 1위, 거래대금 1위 로 매수 1순위 테마의 종목들 (종목명 등락률 거래대금 장악률 종목순위)
        for thema in two_buy_first_condition_thema_list:
            save_time = datetime.today()
            thema_contents = []
            a = thema
            b = thema_dict[thema]["15프로이상"]
            c = thema_dict[thema]["등락률"]
            d = thema_dict[thema]["거래대금"]
            e = round(thema_dict[thema]["장악률"],2)
            thema_jumsu = round(thema_dict[thema]["등락률"] * self.PerRate + ( round(thema_dict[thema]["장악률"],2) * self.PerPower / thema_dict[thema]["10프로이상"] ))
            # 헤더의 출력 값 양식
            df_header = ("%s 점수: %s점 10%%↑: %s개 등락률: %s%% 거래대금: %s조 장악률: %s%%" % (a, thema_jumsu, b, c, d, e))
            self.logging.logger.debug(df_header)
            
            code_rst1 = thema_dict[thema]["코드리스트"]
            code_rst2 = []
            dup_check_only_rate = []

            # 테마에 있는 종목들의 실시간 정보 업데이트
            for code in code_rst1:

                if code in self.portfolio_stock_dict.keys():
                    try:
                        a = self.portfolio_stock_dict[code]["종목명"]
                        b = self.portfolio_stock_dict[code]["등락률"]
                        c = round(self.portfolio_stock_dict[code]["누적거래대금"]/100)
                        d = self.portfolio_stock_dict[code]["장악률"]
                        thema_contents.append((a, b, c, d))
                        dup_check_only_rate.append(b)
                        # 종목 점수 계산에 필요한 변수
                        if b > 10:
                            e = round(b * self.PerRate,0)  # 등락률 점수
                            f = round(d * self.PerPower,0)  # 장악률 점수
                            
                            save_item = {
                                "저장시간": save_time,
                                "복합키": str(thema)+str(code)+str(save_time),
                                "날짜": save_time.strftime("%Y%m%d"),
                                "테마": thema,
                                "테마점수": thema_jumsu,
                                "커트라인": thema_dict[thema]["10프로이상"],
                                "종목코드": code,
                                "종목명": a,
                                "등락률": b,
                                "등락률베이스점수": self.PerRate,
                                "등락률점수": e,
                                "장악률": d,
                                "장악률베이스점수": self.PerPower,
                                "장악률점수": f,
                                "순위": "N",
                                "총점": e + f
                            }
                            sum_save_item.append(save_item)
                            code_rst2.append(code)
                        else:
                            pass
                    except KeyError:
                        self.logging.logger.debug("Code Score Error")
                else:
                    pass
                    # self.logging.logger.debug("테마에 있는 종목이 포트폴리오 안에 없음")

            # 현재 선택된 테마의 가장 높은 등락률
            if len(dup_check_only_rate) == 0:
                dup_check_only_rate.append(0)
                self.logging.logger.debug("기존 중복 테마가 없어서 가장 높은 등락률 0으로 설정")
            else:
                pass
            
            tempCodeRateDupCheck = []
            tempCodeListDupCheck = []
            mongoRateList = self.mongodb.find_items({"$and":[{"테마":thema},{"날짜":save_time.strftime("%Y%m%d")}]},"TodayStrongThema","rawMemeCodeList")
            
            for i in mongoRateList:
                tempCodeRateDupCheck.append(i["등락률"])
                tempCodeListDupCheck.append(i["종목코드"])
            
            if len(tempCodeRateDupCheck) == 0:
                tempCodeRateDupCheck.append(0)
            
            # tempCodeListDupCheck 리스트의 중복제거
            tempCodeListDupCheck = list(set(tempCodeListDupCheck))
            
            self.logging.logger.debug("최고등락률 비교 : %s vs %s " % (max(tempCodeRateDupCheck), max(dup_check_only_rate)))
            self.logging.logger.debug("최고등락률 비교 : %s " % (max(tempCodeRateDupCheck) <= max(dup_check_only_rate)))
            self.logging.logger.debug("중복선정비교 DB 에 있는 종목 : %s " % tempCodeListDupCheck)
            self.logging.logger.debug("지금 추출된 종목 : %s " % code_rst2)
            self.logging.logger.debug("종목비교 : %s " % (len(set(code_rst2)-set(tempCodeListDupCheck)) > 0))
            
            if (max(tempCodeRateDupCheck) <= max(dup_check_only_rate)) and (len(set(code_rst2)-set(tempCodeListDupCheck)) > 0):
                # Contents DataFrame 만들기
                df_contents = pd.DataFrame(thema_contents, columns = ['종목명','등락률','거래대금','장악률'])
                df_contents = df_contents.sort_values("등락률", ascending=False)
                df_contents.insert(0,'순위',df_contents['등락률'].rank(method='min', ascending=False, na_option='bottom'),allow_duplicates=False)
                df_contents.set_index(keys='순위',inplace=True, drop=True)
                
                two_buy_first_condition_mgs.append("☆☆  당일주도주  ☆☆\n%s\n%s\n\n%s" % (kospi_kosdaq_don,df_header,df_contents))
                two_buy_first_condition_code_list.append(code_rst2) # 밖에 있는 변수와 통신이 필요
            else:
                two_buy_first_condition_code_list = []
                self.logging.logger.debug("종목선정 5번식 중복으로 발송안함")
            
            if (len(two_buy_first_condition_code_list) != 0):
                for i in range(len(two_buy_first_condition_mgs)):
                    self.bot_send_in_cnt(two_buy_first_condition_mgs[i])

                self.logging.logger.debug("☆☆  당일주도주(종목선정 5번식)  ☆☆\n%s\n%s\n\n%s" % (kospi_kosdaq_don,df_header,df_contents))
                for save_item in sum_save_item:
                    self.mongodb.upsert_item({"복합키": save_item["복합키"]}, {"$set": save_item}, "TodayStrongThema", "rawMemeCodeList")
                self.cal_total_score()
            else:
                pass
                # print("중복이거나 걸리는 조건 없음")
        
        sum_save_item = []        
        # 15% 2개이상 거래대금 1위 로 매수 2순위 테마의 종목들 (종목명 등락률 거래대금 장악률 종목순위)
        for thema in two_buy_second_condition_thema_list:
            save_time = datetime.today()
            thema_contents = []
            a = thema
            b = thema_dict[thema]["10프로이상"]
            c = thema_dict[thema]["등락률"]
            d = thema_dict[thema]["거래대금"]
            e = round(thema_dict[thema]["장악률"],2)
            thema_jumsu = round(thema_dict[thema]["등락률"] * self.PerRate + ( round(thema_dict[thema]["장악률"],2) * self.PerPower / thema_dict[thema]["10프로이상"] ))
            # 헤더의 출력 값 양식
            df_header = ("%s 점수: %s점 10%%↑: %s개 등락률: %s%% 거래대금: %s조 장악률: %s%%" % (a, thema_jumsu, b, c, d, e))
            self.logging.logger.debug(df_header)
            
            code_rst1 = thema_dict[thema]["코드리스트"]
            code_rst2 = []
            dup_check_only_rate = []
            # 테마에 있는 종목들의 실시간 정보 업데이트
            for code in code_rst1:
                    
                if code in self.portfolio_stock_dict.keys():
                    try:
                        a = self.portfolio_stock_dict[code]["종목명"]
                        b = self.portfolio_stock_dict[code]["등락률"]
                        c = round(self.portfolio_stock_dict[code]["누적거래대금"]/100)
                        d = self.portfolio_stock_dict[code]["장악률"]
                        thema_contents.append((a, b, c, d))
                        dup_check_only_rate.append(b)
                        # 종목 점수 계산에 필요한 변수
                        if b > 10:
                            e = round(b * self.PerRate,0)  # 등락률 점수
                            f = round(d * self.PerPower,0)  # 장악률 점수
                            
                            save_item = {
                                "저장시간": save_time,
                                "복합키": str(thema)+str(code)+str(save_time),
                                "날짜": save_time.strftime("%Y%m%d"),
                                "테마": thema,
                                "테마점수": thema_jumsu,
                                "커트라인": thema_dict[thema]["10프로이상"],
                                "종목코드": code,
                                "종목명": a,
                                "등락률": b,
                                "등락률베이스점수": self.PerRate,
                                "등락률점수": e,
                                "장악률": d,
                                "장악률베이스점수": self.PerPower,
                                "장악률점수": f,
                                "순위": "N",
                                "총점": e + f
                            }
                            sum_save_item.append(save_item)
                            code_rst2.append(code)
                        else:
                            pass
                    except KeyError:
                        self.logging.logger.debug("Code Score Error")
                else:
                    pass
                    # self.logging.logger.debug("테마에 있는 종목이 포트폴리오 안에 없음")

            # 현재 선택된 테마의 가장 높은 등락률 max(dup_check_only_rate)
            if len(dup_check_only_rate) == 0:
                dup_check_only_rate.append(0)
                self.logging.logger.debug("기존 중복 테마가 없어서 가장 높은 등락률 0으로 설정")
            else:
                pass
            
            tempCodeRateDupCheck = []
            tempCodeListDupCheck = []
            mongoRateList = self.mongodb.find_items({"$and":[{"테마":thema},{"날짜":save_time.strftime("%Y%m%d")}]},"TodayStrongThema","rawMemeCodeList")
            
            for i in mongoRateList:
                tempCodeRateDupCheck.append(i["등락률"])
                tempCodeListDupCheck.append(i["종목코드"])
            
            if len(tempCodeRateDupCheck) == 0:
                tempCodeRateDupCheck.append(0)
            
            # tempCodeListDupCheck 리스트의 중복제거
            tempCodeListDupCheck = list(set(tempCodeListDupCheck))
            
            self.logging.logger.debug("최고등락률 비교 : %s vs %s " % (max(tempCodeRateDupCheck), max(dup_check_only_rate)))
            self.logging.logger.debug("최고등락률 비교 : %s " % (max(tempCodeRateDupCheck) <= max(dup_check_only_rate)))
            self.logging.logger.debug("중복선정비교 DB 에 있는 종목 : %s " % tempCodeListDupCheck)
            self.logging.logger.debug("지금 추출된 종목 : %s " % code_rst2)
            self.logging.logger.debug("종목비교 : %s " % (len(set(code_rst2)-set(tempCodeListDupCheck)) > 0))
            
            if (max(tempCodeRateDupCheck) <= max(dup_check_only_rate)) and (len(set(code_rst2)-set(tempCodeListDupCheck)) > 0):
                # Contents DataFrame 만들기
                df_contents = pd.DataFrame(thema_contents, columns = ['종목명','등락률','거래대금','장악률'])
                df_contents = df_contents.sort_values("등락률", ascending=False)
                df_contents.insert(0,'순위',df_contents['등락률'].rank(method='min', ascending=False, na_option='bottom'),allow_duplicates=False)
                df_contents.set_index(keys='순위',inplace=True, drop=True)
                
                two_buy_second_condition_mgs.append("☆☆  당일주도주  ☆☆\n%s\n%s\n\n%s" % (kospi_kosdaq_don,df_header,df_contents))
                two_buy_second_condition_code_list.append(code_rst2) # 밖에 있는 변수와 통신이 필요
            else:
                two_buy_second_condition_code_list = []
                self.logging.logger.debug("종목선정 6번식 중복으로 발송안함")
            
            if (len(two_buy_second_condition_code_list) != 0):
                for i in range(len(two_buy_second_condition_mgs)):
                    self.bot_send_in_cnt(two_buy_second_condition_mgs[i])

                self.logging.logger.debug("☆☆ 당일주도주(종목선정 6번식  ☆☆\n%s\n%s\n\n%s" % (kospi_kosdaq_don,df_header,df_contents))
                for save_item in sum_save_item:
                    self.mongodb.upsert_item({"복합키": save_item["복합키"]}, {"$set": save_item}, "TodayStrongThema", "rawMemeCodeList") 
                self.cal_total_score()                        
            else:
                pass
                # print("중복이거나 걸리는 조건 없음")
        
        sum_save_item = []        
        # 15%↑ 1위로 매수 3순위 테마의 종목들 (종목명 등락률 거래대금 장악률 종목순위)
        for thema in two_buy_third_condition_thema_list:
            save_time = datetime.today()
            thema_contents = []
            a = thema
            b = thema_dict[thema]["15프로이상"]
            c = thema_dict[thema]["등락률"]
            d = thema_dict[thema]["거래대금"]
            e = round(thema_dict[thema]["장악률"],2)
            thema_jumsu = round(thema_dict[thema]["등락률"] * self.PerRate + ( round(thema_dict[thema]["장악률"],2) * self.PerPower / thema_dict[thema]["10프로이상"] ))
            # 헤더의 출력 값 양식
            df_header = ("%s 점수: %s점 10%%↑: %s개 등락률: %s%% 거래대금: %s조 장악률: %s%%" % (a, thema_jumsu, b, c, d, e))
            self.logging.logger.debug(df_header)
            
            code_rst1 = thema_dict[thema]["코드리스트"]
            code_rst2 = []
            dup_check_only_rate = []
            # 테마에 있는 종목들의 실시간 정보 업데이트
            for code in code_rst1:
                    
                if code in self.portfolio_stock_dict.keys():
                    try:
                        a = self.portfolio_stock_dict[code]["종목명"]
                        b = self.portfolio_stock_dict[code]["등락률"]
                        c = round(self.portfolio_stock_dict[code]["누적거래대금"]/100)
                        d = self.portfolio_stock_dict[code]["장악률"]
                        thema_contents.append((a, b, c, d))
                        dup_check_only_rate.append(b)
                        # 종목 점수 계산에 필요한 변수
                        if b > 10:
                            e = round(b * self.PerRate,0)  # 등락률 점수
                            f = round(d * self.PerPower,0)  # 장악률 점수
                            
                            save_item = {
                                "저장시간": save_time,
                                "복합키": str(thema)+str(code)+str(save_time),
                                "날짜": save_time.strftime("%Y%m%d"),
                                "테마": thema,
                                "테마점수": thema_jumsu,
                                "커트라인": thema_dict[thema]["10프로이상"],
                                "종목코드": code,
                                "종목명": a,
                                "등락률": b,
                                "등락률베이스점수": self.PerRate,
                                "등락률점수": e,
                                "장악률": d,
                                "장악률베이스점수": self.PerPower,
                                "장악률점수": f,
                                "순위": "N",
                                "총점": e + f
                            }
                            sum_save_item.append(save_item)
                            code_rst2.append(code)
                        else:
                            pass
                    except KeyError:
                        self.logging.logger.debug("Code Score Error")
                else:
                    pass
                    # self.logging.logger.debug("테마에 있는 종목이 포트폴리오 안에 없음")

            # 현재 선택된 테마의 가장 높은 등락률
            if len(dup_check_only_rate) == 0:
                dup_check_only_rate.append(0)
                self.logging.logger.debug("기존 중복 테마가 없어서 가장 높은 등락률 0으로 설정")
            else:
                pass
            
            tempCodeRateDupCheck = []
            tempCodeListDupCheck = []
            mongoRateList = self.mongodb.find_items({"$and":[{"테마":thema},{"날짜":save_time.strftime("%Y%m%d")}]},"TodayStrongThema","rawMemeCodeList")
            
            for i in mongoRateList:
                tempCodeRateDupCheck.append(i["등락률"])
                tempCodeListDupCheck.append(i["종목코드"])
            
            if len(tempCodeRateDupCheck) == 0:
                tempCodeRateDupCheck.append(0)

            # tempCodeListDupCheck 리스트의 중복제거
            tempCodeListDupCheck = list(set(tempCodeListDupCheck))
            
            self.logging.logger.debug("최고등락률 비교 : %s vs %s " % (max(tempCodeRateDupCheck), max(dup_check_only_rate)))
            self.logging.logger.debug("최고등락률 비교 : %s " % (max(tempCodeRateDupCheck) <= max(dup_check_only_rate)))
            self.logging.logger.debug("중복선정비교 DB 에 있는 종목 : %s " % tempCodeListDupCheck)
            self.logging.logger.debug("지금 추출된 종목 : %s " % code_rst2)
            self.logging.logger.debug("종목비교 : %s " % (len(set(code_rst2)-set(tempCodeListDupCheck)) > 0))
            
            # 이전보다 상승률이 높거나 같고 중복된 코드리스트가 아닌 경우
            if (max(tempCodeRateDupCheck) <= max(dup_check_only_rate)) and (len(set(code_rst2)-set(tempCodeListDupCheck)) > 0):
                # Contents DataFrame 만들기
                df_contents = pd.DataFrame(thema_contents, columns = ['종목명','등락률','거래대금','장악률'])
                df_contents = df_contents.sort_values("등락률", ascending=False)
                df_contents.insert(0,'순위',df_contents['등락률'].rank(method='min', ascending=False, na_option='bottom'),allow_duplicates=False)
                df_contents.set_index(keys='순위',inplace=True, drop=True)
                
                two_buy_third_condition_mgs.append("☆☆  당일주도주 ☆☆\n%s\n%s\n\n%s" % (kospi_kosdaq_don,df_header,df_contents))
                two_buy_third_condition_code_list.append(code_rst2) # 밖에 있는 변수와 통신이 필요
            else:
                self.logging.logger.debug("종목선정 7번식 중복으로 발송안함")
            
            if (len(two_buy_third_condition_code_list) != 0):
                for i in range(len(two_buy_third_condition_mgs)):
                    self.bot_send_in_cnt(two_buy_third_condition_mgs[i])

                self.logging.logger.debug("☆☆ 당일주도주(종목선정 7번식 ☆☆\n%s\n%s\n\n%s" % (kospi_kosdaq_don,df_header,df_contents))
                for save_item in sum_save_item:
                    self.mongodb.upsert_item({"복합키": save_item["복합키"]}, {"$set": save_item}, "TodayStrongThema", "rawMemeCodeList")
                self.cal_total_score()
            else:
                pass
                # print("중복이거나 걸리는 조건 없음")
        
        sum_save_item = []        
        # 15%↑ 2↑ 이고 장악률 10% 이상의 매수 커트라인(4순위) 종목 (종목명 등락률 거래대금 장악률 종목순위)
        for thema in buy_atleast_condition_list:
            save_time = datetime.today()
            thema_contents = []
            a = thema
            b = thema_dict[thema]["15프로이상"]
            c = thema_dict[thema]["등락률"]
            d = thema_dict[thema]["거래대금"]
            e = round(thema_dict[thema]["장악률"],2)
            thema_jumsu = round(thema_dict[thema]["등락률"] * self.PerRate + ( round(thema_dict[thema]["장악률"],2) * self.PerPower / thema_dict[thema]["10프로이상"] ))
            # 헤더의 출력 값 양식
            df_header = ("%s 점수: %s점 10%%↑: %s개 등락률: %s%% 거래대금: %s조 장악률: %s%%" % (a, thema_jumsu, b, c, d, e))
            self.logging.logger.debug(df_header)
            
            code_rst1 = thema_dict[thema]["코드리스트"]
            code_rst2 = []
            dup_check_only_rate = []
            # 테마에 있는 종목들의 실시간 정보 업데이트
            for code in code_rst1:
                    
                if code in self.portfolio_stock_dict.keys():
                    try:
                        a = self.portfolio_stock_dict[code]["종목명"]
                        b = self.portfolio_stock_dict[code]["등락률"]
                        c = round(self.portfolio_stock_dict[code]["누적거래대금"]/100)
                        d = self.portfolio_stock_dict[code]["장악률"]
                        thema_contents.append((a, b, c, d))
                        dup_check_only_rate.append(b)
                        # 종목 점수 계산에 필요한 변수
                        if b > 10:
                            e = round(b * self.PerRate,0)  # 등락률 점수
                            f = round(d * self.PerPower,0)  # 장악률 점수
                            
                            save_item = {
                                "저장시간": save_time,
                                "복합키": str(thema)+str(code)+str(save_time),
                                "날짜": save_time.strftime("%Y%m%d"),
                                "테마": thema,
                                "테마점수": thema_jumsu,
                                "커트라인": thema_dict[thema]["10프로이상"],
                                "종목코드": code,
                                "종목명": a,
                                "등락률": b,
                                "등락률베이스점수": self.PerRate,
                                "등락률점수": e,
                                "장악률": d,
                                "장악률베이스점수": self.PerPower,
                                "장악률점수": f,
                                "순위": "N",
                                "총점": e + f
                            }
                            sum_save_item.append(save_item)
                            code_rst2.append(code)
                        else:
                            pass
                    except KeyError:
                        self.logging.logger.debug("Code Score Error")
                else:
                    pass
                    # self.logging.logger.debug("테마에 있는 종목이 포트폴리오 안에 없음")

            # 현재 선택된 테마의 가장 높은 등락률
            if len(dup_check_only_rate) == 0:
                dup_check_only_rate.append(0)
                self.logging.logger.debug("기존 중복 테마가 없어서 가장 높은 등락률 0으로 설정")
            else:
                pass
            
            tempCodeRateDupCheck = []
            tempCodeListDupCheck = []
            mongoRateList = self.mongodb.find_items({"$and":[{"테마":thema},{"날짜":save_time.strftime("%Y%m%d")}]},"TodayStrongThema","rawMemeCodeList")
            
            for i in mongoRateList:
                tempCodeRateDupCheck.append(i["등락률"])
                tempCodeListDupCheck.append(i["종목코드"])
            
            if len(tempCodeRateDupCheck) == 0:
                tempCodeRateDupCheck.append(0)
            
            # tempCodeListDupCheck 리스트의 중복제거
            tempCodeListDupCheck = list(set(tempCodeListDupCheck))
            
            self.logging.logger.debug("최고등락률 비교 : %s vs %s " % (max(tempCodeRateDupCheck), max(dup_check_only_rate)))
            self.logging.logger.debug("최고등락률 비교 : %s " % (max(tempCodeRateDupCheck) <= max(dup_check_only_rate)))
            self.logging.logger.debug("중복선정비교 DB 에 있는 종목 : %s " % tempCodeListDupCheck)
            self.logging.logger.debug("지금 추출된 종목 : %s " % code_rst2)
            self.logging.logger.debug("종목비교 : %s " % (len(set(code_rst2)-set(tempCodeListDupCheck)) > 0))
            
            # 이전보다 상승률이 높거나 같고 중복된 코드리스트가 아닌 경우
            if (max(tempCodeRateDupCheck) <= max(dup_check_only_rate)) and (len(set(code_rst2)-set(tempCodeListDupCheck)) > 0):
                # Contents DataFrame 만들기
                df_contents = pd.DataFrame(thema_contents, columns = ['종목명','등락률','거래대금','장악률'])
                df_contents = df_contents.sort_values("등락률", ascending=False)
                df_contents.insert(0,'순위',df_contents['등락률'].rank(method='min', ascending=False, na_option='bottom'),allow_duplicates=False)
                df_contents.set_index(keys='순위',inplace=True, drop=True)
                
                two_buy_atleast_condition_mgs.append("☆☆  당일주도주  ☆☆\n%s\n%s\n\n%s" % (kospi_kosdaq_don,df_header,df_contents))
                two_buy_atleast_condition_code_list.append(code_rst2) # 밖에 있는 변수와 통신이 필요
            else:
                two_buy_atleast_condition_code_list = []
                self.logging.logger.debug("종목선정 8번식 중복으로 발송안함")
            
            if (len(two_buy_atleast_condition_code_list) != 0):
                for i in range(len(two_buy_atleast_condition_mgs)):
                    self.bot_send_in_cnt(two_buy_atleast_condition_mgs[i])
                
                self.logging.logger.debug("☆☆  당일주도주(종목선정 8번식  ☆☆\n%s\n%s\n\n%s" % (kospi_kosdaq_don,df_header,df_contents))
                for save_item in sum_save_item:
                    self.mongodb.upsert_item({"복합키": save_item["복합키"]}, {"$set": save_item}, "TodayStrongThema", "rawMemeCodeList")
                self.cal_total_score()
            else:
                pass
                # print("중복이거나 걸리는 조건 없음")
        
        threading.Timer(6, self.thema_make_check).start()

    # 종목코드를 MongoDB 에 1회 업데이트 하는 함수
    # 개선필요 : 몇 개의 코드만 업데이트가 안됐을 때 잡아낼 수 있도록 수정
    def get_upjong_list(self):
        
        today = datetime.today()
        tomorrow = datetime.today() + timedelta(days=1)
        start = datetime(today.year, today.month, today.day)
        end = datetime(tomorrow.year, tomorrow.month, tomorrow.day)
        date_check = self.mongodb.find_items({"저장시간": {'$gte': start, '$lt' : end}}, "TodayStrongThema", "codeList")
        len_date_check = len(list(date_check))
        
        self.kospi_code_list = self.get_code_list_by_market("0")
        self.kosdaq_code_list = self.get_code_list_by_market("10")
        
        len_sum = len(self.kospi_code_list) + len(self.kosdaq_code_list)
        
        self.logging.logger.debug("DB에 있는 종목수의 합 : %s " % len_date_check)
        self.logging.logger.debug("요청한 종목수의 합 : %s " % len_sum)
        
        # 현재 DB 에 있는 값의 종목수와 요청한 종목수가 같지 않으면 업데이트 한다.
        if len_date_check != len_sum:
            self.logging.logger.debug("Start update to kospi kosdaq upjong list")
            self.mongodb.delete_items({},"TodayStrongThema", "codeList")
            # 이 부분에서 이미 date_check 가 돌아가 있으면 안타니까 문제가 있을 듯

            for code in self.kospi_code_list:
                
                code_nm = self.dynamicCall("GetMasterCodeName(QString)", code)
                kospi_item = {
                    "저장시간" : today,
                    "종목코드" : code,
                    "종목명" : code_nm
                }
                self.mongodb.insert_item(kospi_item, "TodayStrongThema", "codeList")    

            self.logging.logger.debug("Done update to kospi upjong list")
            
            for code in self.kosdaq_code_list:

                code_nm = self.dynamicCall("GetMasterCodeName(QString)", code)
                kosdaq_item = {
                    "저장시간" : today,
                    "종목코드" : code,
                    "종목명" : code_nm
                }
                self.mongodb.insert_item(kosdaq_item, "TodayStrongThema", "codeList")    
                
            self.logging.logger.debug("Done update to kosdaq upjong list")
        else:
            self.logging.logger.debug("Alreay inserted kospi kosdaq upjong list") 

    def get_ocx_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1") # 레지스트리에 저장된 API 모듈 불러오기

    def event_slots(self):
        self.OnEventConnect.connect(self.login_slot) # 로그인 관련 이벤트
        self.OnReceiveTrData.connect(self.trdata_slot) # 트랜잭션 요청 관련 이벤트
        self.OnReceiveMsg.connect(self.msg_slot)

    def real_event_slot(self):
        self.OnReceiveRealData.connect(self.realdata_slot) # 실시간 이벤트 연결
        self.OnReceiveChejanData.connect(self.chejan_slot) # 종목 주문체결 관련한 이벤트

    def signal_login_commConnect(self):
        self.dynamicCall("CommConnect()") # 로그인 요청 시그널
        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_() # 이벤트 루프 실행
        
    def login_slot(self, err_code):
        self.logging.logger.debug(errors(err_code)[1])
        #로그인 처리가 완료됐으면 이벤트 루프를 종료한다.
        self.login_event_loop.exit()

    def get_account_info(self):
        account_list = self.dynamicCall("GetLoginInfo(QString)", "ACCNO") # 계좌번호 반환
        account_num = account_list.split(';')[0] # a;b;c  [a, b, c]

        self.account_num = account_num

        self.logging.logger.debug("계좌번호 : %s" % account_num)
        # self.bot_send_in_cnt("계좌번호 : %s" % account_num)

    def detail_account_info(self, sPrevNext="0"):
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "0000")
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "1")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "예수금상세현황요청", "opw00001", sPrevNext, self.screen_my_info)

        self.detail_account_info_event_loop.exec_()

    def detail_account_mystock(self, sPrevNext="0"):
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "0000")
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "1")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "계좌평가잔고내역요청", "opw00018", sPrevNext, self.screen_my_info)

        self.detail_account_info_event_loop.exec_()

    def not_concluded_account(self, sPrevNext="0"):
        self.logging.logger.debug("미체결 종목 요청")
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(QString, QString)", "체결구분", "1")
        self.dynamicCall("SetInputValue(QString, QString)", "매매구분", "0")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "실시간미체결요청", "opt10075", sPrevNext, self.screen_my_info)

        self.detail_account_info_event_loop.exec_()

    ######### 초기 셋팅 함수들 바로 실행 End ################

    def stop_screen_cancel(self, sScrNo=None):
        self.dynamicCall("DisconnectRealData(QString)", sScrNo) # 스크린 번호 연결 끊기

    def get_code_list_by_market(self, market_code):
        code_list = self.dynamicCall("GetCodeListByMarket(QString)", market_code)
        code_list = code_list.split(';')[:-1]

        return code_list
            
    def update_upjong_gubn(self, code):
        if code in self.kospi_code_list:
            self.portfolio_stock_dict[code].update({"업종구분": "KOSPI"})
            # self.logging.logger.debug("%s 종목 KOSPI 업종구분 업데이트" % code)
        elif code in self.kosdaq_code_list: 
            self.portfolio_stock_dict[code].update({"업종구분": "KOSDAQ"})
            # self.logging.logger.debug("%s 종목 KOSDAQ 업종구분 업데이트" % code)
        else:
            self.logging.logger.debug("%s 종목 업종구분 업데이트 오류" % code)
        
    def calculator_fnc(self):
        kospi_code_list = self.get_code_list_by_market("0")
        kosdaq_code_list = self.get_code_list_by_market("10")
        
        for idx, code in enumerate(kospi_code_list):
            self.dynamicCall("DisconnectRealData(QString)", self.screen_calculation_stock) # 스크린 연결 끊기

            print("%s / %s : KOSPI Stock Code : %s is updating... " % (idx + 1, len(kospi_code_list), code))
            self.day_kiwoom_db(code=code)

        for idx, code in enumerate(kosdaq_code_list):
            self.dynamicCall("DisconnectRealData(QString)", self.screen_calculation_stock) # 스크린 연결 끊기

            print("%s / %s : KOSDAQ Stock Code : %s is updating... 종목분석은 나중에 돌리자. " % (idx + 1, len(kosdaq_code_list), code))
            self.day_kiwoom_db(code=code)
            
    def day_kiwoom_db(self, code=None, date=None, sPrevNext="0"):
        QTest.qWait(3600) #3.6초마다 딜레이를 준다.

        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")

        if date != None:
            self.dynamicCall("SetInputValue(QString, QString)", "기준일자", date)

        # 키움 DB 에서 일봉차트 조회 실행
        # self.dynamicCall("CommRqData(QString, QString, int, QString)", "주식일봉차트조회", "opt10081", sPrevNext, self.screen_calculation_stock)

        self.calculator_event_loop.exec_()
        
    def screen_number_setting(self):
        
        # 포트폴리오에 있는 종목과 없는 종목들 Screen Num Setting
        screen_overwrite = []
            
        # 포트폴리오에 있는 종목들
        for code in self.portfolio_stock_dict.keys():
            if code not in screen_overwrite:
                screen_overwrite.append(code)
        
        # self.logging.logger.debug("Portfolio 종목 수 : %s " % len(screen_overwrite))
        
        for code in screen_overwrite:
            temp_screen = int(self.screen_real_stock)
            meme_screen = int(self.screen_meme_stock)
            
            if (len(screen_overwrite) % 50) == 0:
                self.screen_num_cnt += 1
                temp_screen += 1
                meme_screen += 1
                self.screen_real_stock = str(temp_screen)
                self.screen_meme_stock = str(meme_screen)
            else:
                pass
            
            try:
                self.portfolio_stock_dict[code].update({"스크린번호": str(self.screen_real_stock)})
                self.portfolio_stock_dict[code].update({"주문용스크린번호": str(self.screen_meme_stock)})
            except KeyError:
                pass
            
        # self.logging.logger.debug(self.portfolio_stock_dict)

    # sCode : 6자리 요청한 종목코드, sRealType : 실시간 데이터 타입, sRealData : 실시간 받는 데이터 리스트

    def realdata_slot(self, sCode, sRealType, sRealData):

        if sRealType == "장시작시간":
            fid = self.realType.REALTYPE[sRealType]['장운영구분'] 
            value = self.dynamicCall("GetCommRealData(QString, int)", sCode, fid) # (0:장시작전, 2:장종료전(20분), 3:장시작, 4,8:장종료(30분), 9:장마감)

            if value == '0':
                if self.operation_time_status_value != value:
                    self.logging.logger.debug("장 시작 전")
                    self.bot_send_in_cnt("장 시작 전")
                    self.operation_time_status_value = value
                    # 20분 이상 남았을 때만 수집로직 돌리기
                else:
                    pass

            elif value == '3':
                if self.thema_make_check_oper_num == 0:
                    self.thema_make_check_oper_num = 1
                else:
                    pass
                
                if self.operation_time_status_value != value:
                    self.logging.logger.debug("장 시작")
                    self.bot_send_in_cnt("장 시작")
                    self.operation_time_status_value = value
                else:
                    pass
                
            elif value == "2":
                if self.operation_time_status_value != value:
                    self.logging.logger.debug("장 종료, 동시호가로 넘어감")
                    self.bot_send_in_cnt("장 종료, 동시호가로 넘어감")
                    self.operation_time_status_value = value
                else:
                    pass
                
            elif value == "4" or value == "8":
                if self.operation_time_status_value != value:
                    self.logging.logger.debug("3시30분 장 종료")
                    self.bot_send_in_cnt("3시30분 장 종료")
                    for code in self.portfolio_stock_dict.keys():
                        self.dynamicCall("SetRealRemove(QString, QString)", self.portfolio_stock_dict[code]['스크린번호'], code)
                    self.operation_time_status_value = value
                    
                    QTest.qWait(1000)
                
                    self.bot_send_in_cnt("======== Raorkebot Stop ========")
                    end_pid_parameter = os.getpid()
                    os.system("taskkill /pid %s /f" % end_pid_parameter)
                else:
                    pass
                
                # self.file_delete()
                # self.calculator_fnc()
            elif value == "5":
                if self.operation_time_status_value != value:
                    self.logging.logger.debug("정규장 마감 이후")
                    self.bot_send_in_cnt("정규장 마감 이후")
                    self.operation_time_status_value = value
                    # self.bot_send_in_cnt("Stop Raorke Bot")
                    # end_pid_parameter = os.getpid()
                    # os.system("taskkill /pid %s /f" % end_pid_parameter)
                else:
                    pass
                
            elif value == "9":
                if self.operation_time_status_value != value:
                    self.logging.logger.debug("장마감")
                    self.operation_time_status_value = value
                    # self.bot_send_in_cnt("Stop Raorke Bot")
                    # end_pid_parameter = os.getpid()
                    # os.system("taskkill /pid %s /f" % end_pid_parameter)
                else:
                    pass
                
            else:
                if self.operation_time_status_value != value:
                    self.logging.logger.debug("장마감")
                    self.operation_time_status_value = value
                else:
                    pass

        elif sRealType == "주식체결":
            
            # 테스트 코드 
            # a=b=c=d=e=f=g=h=i=j=k=l=m=n=o=p=""
            
            a = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['체결시간']) # 출력 HHMMSS
            a = a.strip()
            
            b = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['현재가']) # 출력 : +(-)2520
            b = abs(int(b.strip()))

            c = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['전일대비']) # 출력 : +(-)2520
            c = abs(int(c.strip()))

            d = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['등락률']) # 출력 : +(-)12.98
            d = float(d.strip())

            e = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['(최우선)매도호가']) # 출력 : +(-)2520
            e = abs(int(e.strip()))

            f = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['(최우선)매수호가']) # 출력 : +(-)2515
            f = abs(int(f.strip()))

            g = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['거래량']) # 출력 : +240124 매수일때, -2034 매도일 때
            g = abs(int(g.strip()))

            h = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['누적거래량']) # 출력 : 240124
            h = abs(int(h.strip()))
            
            i = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['누적거래대금']) # 출력 : 240124
            i = abs(int(i.strip()))
            
            j = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['고가']) # 출력 : +(-)2530
            j = abs(int(j.strip()))

            k = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['시가']) # 출력 : +(-)2530
            k = abs(int(k.strip()))

            l = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['저가']) # 출력 : +(-)2530
            l = abs(int(l.strip()))
            
            m = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['시가총액(억)']) # 
            m = abs(int(m.strip()))
            
            n = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['상한가발생시간']) # 출력 HHMMSS
            o = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['하한가발생시간']) # 출력 HHMMSS
            p = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['장구분']) # 
            r = b - c
            
            if sCode not in self.portfolio_stock_dict.keys():
                self.portfolio_stock_dict.update({sCode:{}})
                self.screen_number_setting()
                self.logging.logger.debug("==== sRealType 에 이전에 요청하지 않은 종목에 대한 요청이 들어오는 경우로 없어야 맞다 ==== %s " % sCode)
                
            code_nm = self.dynamicCall("GetMasterCodeName(QString)", sCode)
            
            # print("실시간 주식체결 : %s %s %s %s %s %s %s %s %s i: %s %s %s %s %s %s %s %s" % (code_nm,a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p))

            self.portfolio_stock_dict[sCode].update({"종목명": code_nm})
            self.portfolio_stock_dict[sCode].update({"체결시간": a})
            self.portfolio_stock_dict[sCode].update({"현재가": b})
            self.portfolio_stock_dict[sCode].update({"전일대비": c})
            self.portfolio_stock_dict[sCode].update({"등락률": d})
            self.portfolio_stock_dict[sCode].update({"(최우선)매도호가": e})
            self.portfolio_stock_dict[sCode].update({"(최우선)매수호가": f})
            self.portfolio_stock_dict[sCode].update({"거래량": g})
            self.portfolio_stock_dict[sCode].update({"누적거래량": h})
            self.portfolio_stock_dict[sCode].update({"누적거래대금": i})
            self.portfolio_stock_dict[sCode].update({"고가": j})
            self.portfolio_stock_dict[sCode].update({"시가": k})
            self.portfolio_stock_dict[sCode].update({"저가": l})
            self.portfolio_stock_dict[sCode].update({"시가총액(억)": m})
            self.portfolio_stock_dict[sCode].update({"상한가발생시간": n})
            self.portfolio_stock_dict[sCode].update({"하한가발생시간": o})
            self.portfolio_stock_dict[sCode].update({"장구분": p})
            self.portfolio_stock_dict[sCode].update({"전일종가": r})

            # 2022.05.24 상한가 유지 점수 계산식 start #
            try:
                trading_time = a
                high_price = j
                low_price = l
                one_ago_price = r
                item_gubn = self.portfolio_stock_dict[sCode]["업종구분"]
                upper_price = self.calUpperPrice(one_ago_price, item_gubn)
                
                self.portfolio_stock_dict[sCode].update({"상한가": upper_price})
                
                dup_check_time = str(trading_time[0:4]) + "00"
                min_check = ""
                
                if upper_price == b:
                    self.logging.logger.debug("상한가 : %s " % code_nm)
                    try: 
                        # 분봉체크 값이 틀린 경우 값을 넣어준다.
                        min_check = self.portfolio_stock_dict[sCode]["분봉체크"]
                        if dup_check_time != min_check:    
                            self.portfolio_stock_dict[sCode].update({"분봉체크":dup_check_time})

                            standard_time = "090000"
                            standard_time = str(datetime.today().strftime("%Y%m%d"))+standard_time
                            trading_time = str(datetime.today().strftime("%Y%m%d"))+trading_time
                            self.logging.logger.debug("try standard_time: %s, trading_time: %s, upper_price: %s, low_price: %s, 현재가: %s" % (standard_time, trading_time, upper_price, low_price, b))
                            # 상한가 유지 점수를 계산하기 위한 식
                            if (datetime.strptime(trading_time.strip(), '%Y%m%d%H%M%S') >= datetime.strptime(standard_time, '%Y%m%d%H%M%S')):
                                save_item = {
                                    "종목명": code_nm,
                                    "종목코드": sCode,
                                    "저장시간": datetime.today(),
                                    "체결시간": trading_time,
                                    "상한가": upper_price,
                                    "저가": low_price,
                                    "고가": high_price
                                }
                                self.logging.logger.debug(save_item)
                                self.mongodb.insert_item(save_item,'TodayStrongThema','upperCodeOneMinData')
                            else:
                                self.logging.logger.debug("%s try inner pass" % code_nm)
                        else:
                            self.logging.logger.debug("aleady inserted %s upperprice min data" % code_nm)
                            pass
                    except KeyError:
                        # 분봉체크 값이 없는 경우 값을 넣어준다.
                        self.portfolio_stock_dict[sCode].update({"분봉체크":dup_check_time})

                        standard_time = "090000"
                        standard_time = str(datetime.today().strftime("%Y%m%d"))+standard_time
                        trading_time = str(datetime.today().strftime("%Y%m%d"))+trading_time
                        
                        self.logging.logger.debug("KeyError 분봉체크 값 %s, %s, %s" % (code_nm, dup_check_time, min_check))
                        self.logging.logger.debug("KeyError standard_time: %s, trading_time: %s" % (standard_time, trading_time))
                        # 상한가 유지 점수를 계산하기 위한 식
                        if (datetime.strptime(trading_time.strip(), '%Y%m%d%H%M%S') >= datetime.strptime(standard_time, '%Y%m%d%H%M%S')):
                            save_item = {
                                "종목명": code_nm,
                                "종목코드": sCode,
                                "저장시간": datetime.today(),
                                "체결시간": trading_time,
                                "상한가": upper_price,
                                "저가": low_price,
                                "고가": high_price
                            }
                            self.logging.logger.debug(save_item)
                            self.mongodb.insert_item(save_item,'TodayStrongThema','upperCodeOneMinData')
                        else:
                            self.logging.logger.debug("KeyError pass")
                            pass
                else:
                    pass
            except KeyError:
                self.logging.logger.debug("상한가 유지 계산식 %s Key Error" % code_nm)
                pass
            # 2022.05.24 상한가 유지 점수 계산식 end #
            
            # 총 시장거래대금 변수선언
            TotalholdPower = ''
            # 코스피/코스닥 구분 필요
            try:
                if self.portfolio_stock_dict[sCode]["업종구분"] == "KOSPI":
                    try:
                        TotalholdPower = self.upjong_dict["001"]["누적거래대금"]
                        # print("KOSPI TotalholdPower: %s " % TotalholdPower)
                    except KeyError:
                        TotalholdPower = 0
                        # print("아직 KOSPI 실시간 업종지수 업데이트 안됨")
                        
                elif self.portfolio_stock_dict[sCode]["업종구분"] == "KOSDAQ":
                    try:
                        TotalholdPower = self.upjong_dict["101"]["누적거래대금"]
                        # print("KOSDAQ TotalholdPower: %s " % TotalholdPower)
                        
                    except KeyError:
                        TotalholdPower = 0
                        # print("아직 KOSDAQ 실시간 업종지수 업데이트 안됨")
                else:
                    self.logging.logger.debug("%s 종목이 kosdaq, kospi 어디에도 속하지 않음" % self.portfolio_stock_dict[sCode]["종목명"])

            except KeyError:
                TotalholdPower = 0
                pass
            
            if TotalholdPower == 0:
                holdPower = 0
                self.portfolio_stock_dict[sCode].update({"장악률": holdPower})
            else:
                holdPower = round( (i / abs(float(TotalholdPower)) *100 ),2)
                self.portfolio_stock_dict[sCode].update({"장악률": holdPower})

            # # 계좌평가 잔고에 있고 jango_dict 에 없을 때
            # if sCode in self.account_stock_dict.keys() and sCode not in self.jango_dict.keys():
            #     asd = self.account_stock_dict[sCode]
            #     meme_rate = (b - asd['매입가']) / asd['매입가'] * 100

            #     if asd['매매가능수량'] > 0 and (meme_rate > 5 or meme_rate < -5):
            #         order_success = self.dynamicCall(
            #             "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
            #             ["신규매도", self.portfolio_stock_dict[sCode]["주문용스크린번호"], self.account_num, 2, sCode, asd['매매가능수량'], 0, self.realType.SENDTYPE['거래구분']['시장가'], ""]
            #         )

            #         if order_success == 0:
            #             self.logging.logger.debug("매도주문 전달 성공")
            #             del self.account_stock_dict[sCode]
            #         else:
            #             self.logging.logger.debug("매도주문 전달 실패")

            # # jango_dict 에 있는 종목의 수익률이 +, - 5% 면 매도한다.
            # elif sCode in self.jango_dict.keys():
            #     jd = self.jango_dict[sCode]
            #     meme_rate = (b - jd['매입단가']) / jd['매입단가'] * 100

            #     if jd['주문가능수량'] > 0 and (meme_rate > 5 or meme_rate < -5):
            #         order_success = self.dynamicCall(
            #             "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
            #             ["신규매도", self.portfolio_stock_dict[sCode]["주문용스크린번호"], self.account_num, 2, sCode, jd['주문가능수량'], 0, self.realType.SENDTYPE['거래구분']['시장가'], ""]
            #         )

            #         if order_success == 0:
            #             self.logging.logger.debug("매도주문 전달 성공")
            #         else:
            #             self.logging.logger.debug("매도주문 전달 실패")
            
            # # jango_dict 에 없는 종목 중에서 
            # elif d > 2.0 and sCode not in self.jango_dict:
            #     self.logging.logger.debug("매수조건 통과 %s " % sCode)

            #     result = (self.use_money * 0.1) / e
            #     quantity = int(result)

            #     order_success = self.dynamicCall(
            #         "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
            #         ["신규매수", self.portfolio_stock_dict[sCode]["주문용스크린번호"], self.account_num, 1, sCode, quantity, e, self.realType.SENDTYPE['거래구분']['지정가'], ""]
            #     )

            #     if order_success == 0:
            #         self.logging.logger.debug("매수주문 전달 성공")
            #     else:
            #         self.logging.logger.debug("매수주문 전달 실패")

            # not_meme_list = list(self.not_account_stock_dict)
            
            # for order_num in not_meme_list:
            #     code = self.not_account_stock_dict[order_num]["종목코드"]
            #     meme_price = self.not_account_stock_dict[order_num]['주문가격']
            #     not_quantity = self.not_account_stock_dict[order_num]['미체결수량']
            #     order_gubun = self.not_account_stock_dict[order_num]['주문구분']

            #     if order_gubun == "매수" and not_quantity > 0 and e > meme_price:
            #         order_success = self.dynamicCall(
            #             "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
            #             ["매수취소", self.portfolio_stock_dict[sCode]["주문용스크린번호"], self.account_num, 3, code, 0, 0, self.realType.SENDTYPE['거래구분']['지정가'], order_num]
            #         )

            #         if order_success == 0:
            #             self.logging.logger.debug("매수취소 전달 성공")
            #         else:
            #             self.logging.logger.debug("매수취소 전달 실패")

            #     elif not_quantity == 0:
            #         del self.not_account_stock_dict[order_num]
                    
        elif sRealType == "업종지수":
            # self.logging.logger.debug("실시간 업종지수 받아옴")
            # GetCommRealData : 실시간 이벤트인 OnReceiveRealData 가 발생할 때 실시간데이터를 얻어오는 함수
            # 테스트 코드
            # a=b=c=d=e=f=g=h=i=j=""
            a = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['체결시간']) # 출력 HHMMSS
            
            b = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['현재가']) # 출력 : +(-)2520
            b = abs(float(b))
            
            c = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['전일대비']) # 출력 : +(-)2520
            try:
                c = float(c)
            except ValueError:
                c = 0

            d = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['등락률']) # 출력 : +(-)12.98
            d = float(d)

            e = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['거래량']) # 출력 : +240124 매수일때, -2034 매도일 때
            e = abs(int(e))

            f = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['누적거래량']) # 출력 : 240124
            f = abs(int(f))
            
            g = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['누적거래대금']) # 출력 : 240124
            g = abs(int(g))

            h = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['시가']) # 출력 : +(-)2530
            h = abs(float(h))

            i = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['고가']) # 출력 : +(-)2530
            i = abs(float(i))

            j = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['저가']) # 출력 : +(-)2530
            j = abs(float(j))

            if sCode not in self.upjong_dict.keys():
                self.upjong_dict.update({sCode:{}})
            # else: 
            #     self.logging.logger.debug("업종지수 이전에 요청함")
                
            if sCode == "001":
                code_nm = "KOSPI"
            elif sCode == "101":
                code_nm = "KOSDAQ"
            else:
                self.logging.logger.debug("KOSPI KOSDAQ 업종지수 요청이 아님")
                
            self.upjong_dict[sCode].update({"종목명": code_nm})
            self.upjong_dict[sCode].update({"체결시간": a})
            self.upjong_dict[sCode].update({"현재가": b})
            self.upjong_dict[sCode].update({"전일대비": c})
            self.upjong_dict[sCode].update({"등락률": d})
            self.upjong_dict[sCode].update({"거래량": e})
            self.upjong_dict[sCode].update({"누적거래량": f})
            self.upjong_dict[sCode].update({"누적거래대금": g})
            self.upjong_dict[sCode].update({"시가": h})
            self.upjong_dict[sCode].update({"고가": i})
            self.upjong_dict[sCode].update({"저가": j})
            
            self.upjong_dict[sCode].update({"스크린번호": self.upjong_sisae_stock})
            
            # self.logging.logger.debug("실시간 업종지수 : %s %s %s %s %s %s %s %s %s %s %s" % (code_nm, a, b, c, d, e, f, g, h, i, j))
            
    def msg_slot(self, sScrNo, sRQName, sTrCode, msg):
        print("스크린: %s, 요청이름: %s, tr코드: %s --- %s" %(sScrNo, sRQName, sTrCode, msg))

    def file_delete(self):
        if os.path.isfile("C:\\Dev\\onyourside22\\server\\kiwoom\\files\\pass_condition_code.txt"):
            os.remove("C:\\Dev\\onyourside22\\server\\kiwoom\\files\\pass_condition_code.txt")
            
    #조건검색식 이벤트 모음
    def condition_event_slot(self):
        self.OnReceiveConditionVer.connect(self.condition_slot)
        self.OnReceiveTrCondition.connect(self.condition_tr_slot)
        self.OnReceiveRealCondition.connect(self.condition_real_slot)
    
    # 조건식 로딩 하기
    def condition_signal(self):
        self.dynamicCall("GetConditionLoad()")    

    # 어떤 조건식이 있는지 확인
    def condition_slot(self, lRet, sMsg):
        print("호출 성공 여부 %s, 호출결과 메시지 %s" % (lRet, sMsg))

        condition_name_list = self.dynamicCall("GetConditionNameList()")
        condition_name_list = condition_name_list.split(";")[:-1]
        # print("HTS의 조건검색식 이름 가져오기 %s" % condition_name_list)
        
        new_condition_name_list = []
        for x in condition_name_list:
            if "자동" in x:
                new_condition_name_list.append(x)

        for unit_condition in new_condition_name_list:
            QTest.qWait(1000)
            index = unit_condition.split("^")[0]
            index = int(index)
            condition_name = unit_condition.split("^")[1]

            ok  = self.dynamicCall("SendCondition(QString, QString, int, int)", "0156", condition_name, index, 1) #조회요청 + 실시간 조회
            if ok != 1:
                self.logging.logger.debug("%s 조회 실패값: %s " % (condition_name, ok))

    def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):
        # TR 의 기본요청 갯수는 제한이 있다. 
        # 데이터 조회는 1초당 5회 제한으로 3회 가능하게 제한하기
        # CommRqData(데이터 조회요청), SendCondition(조건검색 조회요청), CommKwRqData(복수종목 조회요청)
        if sRQName == "예수금상세현황요청":
            # OnReceiveTRData 이벤트 발생 시 수신한 데이터를 얻어오는 함수 
            deposit = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "예수금")
            self.deposit = int(deposit)

            use_money = float(self.deposit) * self.use_money_percent
            self.use_money = int(use_money)
            self.use_money = self.use_money / 4

            output_deposit = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "출금가능금액")
            self.output_deposit = int(output_deposit)

            self.logging.logger.debug("예수금 : %s" % self.output_deposit)
            self.bot_send_in_cnt("예수금 : %s" % self.output_deposit) # 텔레그램 전송

            self.stop_screen_cancel(self.screen_my_info)

            self.detail_account_info_event_loop.exit()

        elif sRQName == "계좌평가잔고내역요청":
            total_buy_money = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총매입금액") # 출력 : 000000000746100
            self.total_buy_money = int(total_buy_money)
            total_profit_loss_money = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총평가손익금액") # 출력 : 000000000009761
            self.total_profit_loss_money = int(total_profit_loss_money)
            total_profit_loss_rate = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총수익률(%)") # 출력 : 000000001.31
            self.total_profit_loss_rate = float(total_profit_loss_rate)

            self.logging.logger.debug("계좌평가잔고내역요청 싱글데이터 : %s - %s - %s" % (self.total_buy_money, self.total_profit_loss_money, self.total_profit_loss_rate))
            # 텔레그램 전송
            self.bot_send_in_cnt("주식평가액 : %s - 손익금 : %s - 손익률 : %s" % (self.total_buy_money, self.total_profit_loss_money, self.total_profit_loss_rate))

            rows = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            for i in range(rows):
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목번호")
                code = code.strip()[1:]

                code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")
                stock_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "보유수량")
                buy_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매입가")
                learn_rate = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "수익률(%)")
                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")
                total_chegual_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매입금액")
                possible_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매매가능수량")

                self.logging.logger.debug("종목번호: %s - 종목명: %s - 보유수량: %s - 매입가:%s - 수익률: %s - 현재가: %s" % (
                    code, code_nm.strip(), int(stock_quantity.strip()), int(buy_price.strip()), float(learn_rate.strip()), int(current_price.strip())))

                if code in self.account_stock_dict:
                    pass
                else:
                    self.account_stock_dict[code] = {}

                code_nm = code_nm.strip()
                stock_quantity = int(stock_quantity.strip())
                buy_price = int(buy_price.strip())
                learn_rate = float(learn_rate.strip())
                current_price = int(current_price.strip())
                total_chegual_price = int(total_chegual_price.strip())
                possible_quantity = int(possible_quantity.strip())

                self.account_stock_dict[code].update({"종목명": code_nm})
                self.account_stock_dict[code].update({"보유수량": stock_quantity})
                self.account_stock_dict[code].update({"매입가": buy_price})
                self.account_stock_dict[code].update({"수익률(%)": learn_rate})
                self.account_stock_dict[code].update({"현재가": current_price})
                self.account_stock_dict[code].update({"매입금액": total_chegual_price})
                self.account_stock_dict[code].update({"매매가능수량": possible_quantity})

            self.logging.logger.debug("sPreNext : %s" % sPrevNext)
            self.logging.logger.debug("계좌에 가지고 있는 종목은 %s " % rows)

            if sPrevNext == "2":
                self.detail_account_mystock(sPrevNext="2")
            else:
                self.detail_account_info_event_loop.exit()

        elif sRQName == "실시간미체결요청":
            # self.bot_send_in_cnt("미체결 주문 체크")
            rows = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)

            for i in range(rows):
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목코드")

                code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")
                order_no = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문번호")
                order_status = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문상태") # 접수,확인,체결
                order_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문수량")
                order_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문가격")
                order_gubun = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문구분") # -매도, +매수, -매도정정, +매수정정
                not_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "미체결수량")
                ok_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "체결량")

                code = code.strip()
                code_nm = code_nm.strip()
                order_no = int(order_no.strip())
                order_status = order_status.strip()
                order_quantity = int(order_quantity.strip())
                order_price = int(order_price.strip())
                order_gubun = order_gubun.strip().lstrip('+').lstrip('-')
                not_quantity = int(not_quantity.strip())
                ok_quantity = int(ok_quantity.strip())

                if order_no in self.not_account_stock_dict:
                    pass
                else:
                    self.not_account_stock_dict[order_no] = {}

                self.not_account_stock_dict[order_no].update({'종목코드': code})
                self.not_account_stock_dict[order_no].update({'종목명': code_nm})
                self.not_account_stock_dict[order_no].update({'주문번호': order_no})
                self.not_account_stock_dict[order_no].update({'주문상태': order_status})
                self.not_account_stock_dict[order_no].update({'주문수량': order_quantity})
                self.not_account_stock_dict[order_no].update({'주문가격': order_price})
                self.not_account_stock_dict[order_no].update({'주문구분': order_gubun})
                self.not_account_stock_dict[order_no].update({'미체결수량': not_quantity})
                self.not_account_stock_dict[order_no].update({'체결량': ok_quantity})

                self.logging.logger.debug("미체결 종목 : %s " % self.not_account_stock_dict[order_no])
                self.bot_send_in_cnt("미체결 종목 : %s " % self.not_account_stock_dict[order_no])

            self.detail_account_info_event_loop.exit()

        # 분봉 차트 조회
        elif sRQName == "주식분봉차트조회요청":
            code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드")
            code = code.strip()
            
            cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            
            for i in range(cnt):
                data = []

                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")  # 출력 : 000070
                value = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "거래량")  # 출력 : 000070
                trading_time = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "체결시간")  # 출력 : 000070
                start_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "시가")  # 출력 : 000070
                high_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "고가")  # 출력 : 000070
                low_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "저가")  # 출력 : 000070
                
                standard_time = str(datetime.today().strftime("%Y%m%d"))+"090000"
                # 상한가 유지 점수를 계산하기 위한 식
                if datetime.strptime(trading_time.strip(), '%Y%m%d%H%M%S') >= datetime.strptime(standard_time, '%Y%m%d%H%M%S') and (high_price.strip() == low_price.strip()):
                    data.append(current_price.strip())
                    data.append(value.strip())
                    data.append(trading_time.strip())
                    data.append(start_price.strip())
                    data.append(high_price.strip())
                    data.append(low_price.strip())
                    
                    self.one_min_data.append(data.copy())

            self.calculator_event_loop.exit()

        # 주식 시장 끝나고 다음날 매매할 종목 조회하기
        elif sRQName == "주식일봉차트조회":
            code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드")
            code = code.strip()
            # 차트데이터 한 번에 가져올 목적으로 만든 전용함수
            # data = self.dynamicCall("GetCommDataEx(QString, QString)", sTrCode, sRQName)

            cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            self.logging.logger.debug("남은 일자 수 %s" % cnt)

            for i in range(cnt):
                data = []

                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")  # 출력 : 000070
                value = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "거래량")  # 출력 : 000070
                trading_value = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "거래대금")  # 출력 : 000070
                date = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "일자")  # 출력 : 000070
                start_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "시가")  # 출력 : 000070
                high_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "고가")  # 출력 : 000070
                low_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "저가")  # 출력 : 000070

                data.append("")
                data.append(current_price.strip())
                data.append(value.strip())
                data.append(trading_value.strip())
                data.append(date.strip())
                data.append(start_price.strip())
                data.append(high_price.strip())
                data.append(low_price.strip())
                data.append("")

                self.calcul_data.append(data.copy())

            if sPrevNext == "2":
                self.day_kiwoom_db(code=code, sPrevNext=sPrevNext)
            else:
                self.logging.logger.debug("총 일수 %s" % len(self.calcul_data))

                pass_success = False

                # 120일 이평선을 그릴만큼의 데이터가 있는지 체크
                if self.calcul_data == None or len(self.calcul_data) < 120:
                    pass_success = False
                else:
                    # 120일 이평선의 최근 가격 구함
                    total_price = 0
                    for value in self.calcul_data[:120]:
                        total_price += int(value[1])
                    moving_average_price = total_price / 120

                    # 오늘자 주가가 120일 이평선에 걸쳐있는지 확인
                    bottom_stock_price = False
                    check_price = None
                    if int(self.calcul_data[0][7]) <= moving_average_price and moving_average_price <= int(self.calcul_data[0][6]):
                        self.logging.logger.debug("오늘의 주가가 120 이평선에 걸쳐있는지 확인")
                        bottom_stock_price = True
                        check_price = int(self.calcul_data[0][6])

                    # 과거 일봉 데이터를 조회하면서 120일 이동평균선보다 주가가 계속 밑에 존재하는지 확인
                    prev_price = None
                    if bottom_stock_price == True:
                        moving_average_price_prev = 0
                        price_top_moving = False
                        idx = 1

                        while True:
                            if len(self.calcul_data[idx:]) < 120: # 120일 치가 있는지 계속 확인
                                self.logging.logger.debug("120일 치가 없음")
                                break

                            total_price = 0
                            for value in self.calcul_data[idx:120+idx]:
                                total_price += int(value[1])
                            moving_average_price_prev = total_price / 120

                            if moving_average_price_prev <= int(self.calcul_data[idx][6]) and idx <= 20:
                                self.logging.logger.debug("20일 동안 주가가 120일 이평선과 같거나 위에 있으면 조건 통과 못 함")
                                price_top_moving = False
                                break

                            elif int(self.calcul_data[idx][7]) > moving_average_price_prev and idx > 20: # 120일 이평선 위에 있는 구간 존재
                                self.logging.logger.debug("120일치 이평선 위에 있는 구간 확인됨")
                                price_top_moving = True
                                prev_price = int(self.calcul_data[idx][7])
                                break

                            idx += 1

                        # 해당부분 이평선이 가장 최근의 이평선 가격보다 낮은지 확인
                        if price_top_moving == True:
                            if moving_average_price > moving_average_price_prev and check_price > prev_price:
                                self.logging.logger.debug("포착된 이평선의 가격이 오늘자 이평선 가격보다 낮은 것 확인")
                                self.logging.logger.debug("포착된 부분의 일봉 저가가 오늘자 일봉의 고가보다 낮은지 확인")
                                pass_success = True

                if pass_success == True:
                    self.logging.logger.debug("조건부 통과됨")

                    code_nm = self.dynamicCall("GetMasterCodeName(QString)", code)

                    f = open("C:\\Dev\\onyourside22\\server\\kiwoom\\files\\pass_condition_code.txt", "a", encoding="utf8")
                    f.write("%s\t%s\t%s\n" % (code, code_nm, str(self.calcul_data[0][1])))
                    f.close()

                elif pass_success == False:
                    self.logging.logger.debug("조건부 통과 못 함")

                self.calcul_data.clear()
                self.calculator_event_loop.exit()

        elif sRQName == "업종현재가요청":

            stock_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "현재가")
            updown_rate = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "등락률")
            guraedaeguem = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "거래대금")

            stock_price = abs(float(stock_price.strip()))
            updown_rate = float(updown_rate.strip())
            guraedaeguem = int(guraedaeguem.strip())
            
            if code == "001":
                code_nm = "코스피"
            elif code =="101":
                code_nm = "코스닥"
            else: 
                self.logging.logger.debug("업종 코드 네임 업데이트 추가필요")
                
            if code not in self.upjong_dict.keys():
                self.upjong_dict.update({code:{"종목명":code_nm, "현재가": stock_price, "등락률": updown_rate, "거래대금": guraedaeguem}})
            
            self.logging.logger.debug("TR 업종현재가요청 종목코드 : %s, 종목명 : %s, 현재가 : %s, 등락률 : %s, 거래대금 : %s " % (code, code_nm, stock_price, updown_rate, guraedaeguem))
            self.calculator_event_loop.exit()

        elif sRQName == "주식기본정보요청":
            
            code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드")
            code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목명")
            sichong = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "시가총액")
            per = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "PER")
            pbr = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "PBR")
            start_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "시가")  # 출력 : 000070
            high_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "고가")  # 출력 : 000070
            low_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "저가")  # 출력 : 000070
            yesang_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "예상체결가")
            yesang_mount = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "예상체결수량")
            stock_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "현재가")
            guraeryang = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "거래량")  # 출력 : 000070
            yutong_stock = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "유통주식")
            yutong_rate = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "유통비율")
            upper_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "상한가")
            
            code = code.strip()
            code_nm = code_nm.strip()
            sichong = int(sichong.strip()) # 000000
            per = per.strip() 
            pbr = pbr.strip() 
            start_price = abs(int(start_price.strip()))
            high_price = abs(int(high_price.strip()))
            low_price = abs(int(low_price.strip()))
            yesang_price = abs(int(yesang_price.strip()))
            yesang_mount = yesang_mount.strip()
            stock_price = abs(int(stock_price.strip()))
            guraeryang = int(guraeryang.strip())
            yutong_stock = str(yutong_stock.strip())
            yutong_rate = str(yutong_rate.strip())
            upper_price = abs(int(upper_price.strip()))
            
            # # print("유통주식: %s, 유통비율: %s" % (yutong_stock, yutong_rate))
            # # realSichong = sichong * yutong_rate
            
            # if code in self.portfolio_stock_dict.keys():                
            #     self.portfolio_stock_dict[code].update({"상한가": upper_price})
            #     # self.portfolio_stock_dict[code].update({"실제시총": realSichong})
            
            # bokHapKey = self.codePlus
            # if bokHapKey not in self.outTimeUpDownRate.keys():
            #     self.outTimeUpDownRate.update({bokHapKey: {}})
            # self.outTimeUpDownRate[bokHapKey].update({"상한가": upper_price})
            # self.outTimeUpDownRate[bokHapKey].update({"실제시총": realSichong})
            
            # self.logging.logger.debug("TR 주식기본정보요청 : %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s" % (code, code_nm, sichong, per, pbr, start_price, high_price, low_price, yesang_price, yesang_mount, stock_price, guraeryang, yutong_stock, yutong_rate, upper_price))
            self.calculator_event_loop.exit()
        
        # elif sRQName == "시간외단일가요청":
        #     self.logging.logger.debug("시간외 단일가 요청")
        #     outTimeUpDownRate = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "시간외단일가_등락률")
        #     try:
        #         outTimeUpDownRate = float(outTimeUpDownRate.strip())
        #     except ValueError:
        #         self.logging.logger.debug("시간외 단일가 Value Error 로 0으로 세팅")
        #         outTimeUpDownRate = 0
        #     self.TempOutTimeUpDownRate = outTimeUpDownRate
            
        #     self.logging.logger.debug("TR 시간외단일가요청 : %s" % (outTimeUpDownRate))
        #     self.calculator_event_loop.exit()
            
            
        # 상한가 종목 요청 로직추가
            
        
    def chejan_slot(self, sGubun, nItemCnt, sFidList):
        if int(sGubun) == 0: #주문체결
            account_num = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['계좌번호'])
            sCode = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['종목코드'])[1:]
            stock_name = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['종목명'])
            stock_name = stock_name.strip()

            origin_order_number = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['원주문번호']) # 출력 : defaluse : "000000"
            order_number = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문번호']) # 출럭: 0115061 마지막 주문번호

            order_status = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문상태']) # 출력: 접수, 확인, 체결
            order_quan = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문수량']) # 출력 : 3
            order_quan = int(order_quan)

            order_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문가격']) # 출력: 21000
            order_price = int(order_price)

            not_chegual_quan = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['미체결수량']) # 출력: 15, default: 0
            not_chegual_quan = int(not_chegual_quan)

            order_gubun = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문구분']) # 출력: -매도, +매수
            order_gubun = order_gubun.strip().lstrip('+').lstrip('-')

            chegual_time_str = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문/체결시간']) # 출력: '151028'

            chegual_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['체결가']) # 출력: 2110 default : ''
            if chegual_price == '':
                chegual_price = 0
            else:
                chegual_price = int(chegual_price)

            chegual_quantity = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['체결량']) # 출력: 5 default : ''
            if chegual_quantity == '':
                chegual_quantity = 0
            else:
                chegual_quantity = int(chegual_quantity)

            current_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['현재가']) # 출력: -6000
            current_price = abs(int(current_price))

            first_sell_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['(최우선)매도호가']) # 출력: -6010
            first_sell_price = abs(int(first_sell_price))

            first_buy_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['(최우선)매수호가']) # 출력: -6000
            first_buy_price = abs(int(first_buy_price))

            ######## 새로 들어온 주문이면 주문번호 할당
            if order_number not in self.not_account_stock_dict.keys():
                self.not_account_stock_dict.update({order_number: {}})

            self.not_account_stock_dict[order_number].update({"종목코드": sCode})
            self.not_account_stock_dict[order_number].update({"주문번호": order_number})
            self.not_account_stock_dict[order_number].update({"종목명": stock_name})
            self.not_account_stock_dict[order_number].update({"주문상태": order_status})
            self.not_account_stock_dict[order_number].update({"주문수량": order_quan})
            self.not_account_stock_dict[order_number].update({"주문가격": order_price})
            self.not_account_stock_dict[order_number].update({"미체결수량": not_chegual_quan})
            self.not_account_stock_dict[order_number].update({"원주문번호": origin_order_number})
            self.not_account_stock_dict[order_number].update({"주문구분": order_gubun})
            self.not_account_stock_dict[order_number].update({"주문/체결시간": chegual_time_str})
            self.not_account_stock_dict[order_number].update({"체결가": chegual_price})
            self.not_account_stock_dict[order_number].update({"체결량": chegual_quantity})
            self.not_account_stock_dict[order_number].update({"현재가": current_price})
            self.not_account_stock_dict[order_number].update({"(최우선)매도호가": first_sell_price})
            self.not_account_stock_dict[order_number].update({"(최우선)매수호가": first_buy_price})

        elif int(sGubun) == 1: #잔고
            account_num = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['계좌번호'])
            sCode = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['종목코드'])[1:]

            stock_name = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['종목명'])
            stock_name = stock_name.strip()

            current_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['현재가'])
            current_price = abs(int(current_price))

            stock_quan = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['보유수량'])
            stock_quan = int(stock_quan)

            like_quan = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['주문가능수량'])
            like_quan = int(like_quan)

            buy_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['매입단가'])
            buy_price = abs(int(buy_price))

            total_buy_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['총매입가']) # 계좌에 있는 종목의 총매입가
            total_buy_price = int(total_buy_price)

            meme_gubun = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['매도매수구분'])
            meme_gubun = self.realType.REALTYPE['매도수구분'][meme_gubun]

            first_sell_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['(최우선)매도호가'])
            first_sell_price = abs(int(first_sell_price))

            first_buy_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['(최우선)매수호가'])
            first_buy_price = abs(int(first_buy_price))

            if sCode not in self.jango_dict.keys():
                self.jango_dict.update({sCode:{}})

            self.jango_dict[sCode].update({"현재가": current_price})
            self.jango_dict[sCode].update({"종목코드": sCode})
            self.jango_dict[sCode].update({"종목명": stock_name})
            self.jango_dict[sCode].update({"보유수량": stock_quan})
            self.jango_dict[sCode].update({"주문가능수량": like_quan})
            self.jango_dict[sCode].update({"매입단가": buy_price})
            self.jango_dict[sCode].update({"총매입가": total_buy_price})
            self.jango_dict[sCode].update({"매도매수구분": meme_gubun})
            self.jango_dict[sCode].update({"(최우선)매도호가": first_sell_price})
            self.jango_dict[sCode].update({"(최우선)매수호가": first_buy_price})

    # 나의 조건식에 해당하는 종목코드 받기
    def condition_tr_slot(self, sScrNo, strCodeList, strConditionName, index, nNext):
        # self.logging.logger.debug("화면번호: %s, 종목코드 리스트: %s, 조건식 이름: %s, 조건식 인덱스: %s, 연속조회: %s" % (sScrNo, strCodeList, strConditionName, index, nNext))

        code_list = strCodeList.split(";")[:-1]
        if "자동" in strConditionName:
            # 메세지 보낼 타이밍은 자동조건식 마지막 값을 출력한 후 
            self.condition_tr_slot_send_msg_check = self.condition_tr_slot_send_msg_check + 1
            
            for strCode in code_list:
                
                code_nm = self.dynamicCall("GetMasterCodeName(QString)", strCode)
                
                if strCode not in self.portfolio_stock_dict.keys():
                    self.portfolio_stock_dict.update({strCode:{}})
                    self.portfolio_stock_dict[strCode].update({"종목명": code_nm})
                    # 업종구분 업데이트
                    self.update_upjong_gubn(strCode)
                    self.screen_number_setting()
                    # 실시간 시세조회 요청
                    self.set_real_reg_stock_dict(strCode)
                
                if strConditionName == "자동_대장주확인":
                    if strCode not in self.jogun1_dict.keys():
                        self.jogun1_dict.update({strCode:{}})
                    self.jogun1_dict[strCode].update({"종목명": code_nm})
                    self.jogun1_dict[strCode].update({"strType": "I"})
                    self.jogun1_dict[strCode].update({"조건식명": strConditionName})
                elif strConditionName == "자동_장초반_상승률상위":
                    if strCode not in self.jogun2_dict.keys():
                        self.jogun2_dict.update({strCode:{}})
                    self.jogun2_dict[strCode].update({"종목명": code_nm})
                    self.jogun2_dict[strCode].update({"strType": "I"})
                    self.jogun2_dict[strCode].update({"조건식명": strConditionName})
                elif strConditionName == "자동_장중세력봉":
                    if strCode not in self.jogun3_dict.keys():
                        self.jogun3_dict.update({strCode:{}})
                    self.jogun3_dict[strCode].update({"종목명": code_nm})
                    self.jogun3_dict[strCode].update({"strType": "I"})
                    self.jogun3_dict[strCode].update({"조건식명": strConditionName})
                elif strConditionName == "자동_장중매횡":
                    if strCode not in self.jogun4_dict.keys():
                        self.jogun4_dict.update({strCode:{}})
                    self.jogun4_dict[strCode].update({"종목명": code_nm})
                    self.jogun4_dict[strCode].update({"strType": "I"})
                    self.jogun4_dict[strCode].update({"조건식명": strConditionName})
                elif strConditionName == "자동_당일강세테마":
                    if strCode not in self.jogun5_dict.keys():
                        self.jogun5_dict.update({strCode:{}})
                    self.jogun5_dict[strCode].update({"종목명": code_nm})
                    self.jogun5_dict[strCode].update({"strType": "I"})
                    self.jogun5_dict[strCode].update({"조건식명": strConditionName})
                else:
                    pass
                
            print("%s \n %s " % (strConditionName, code_list))
            
            if self.condition_tr_slot_send_msg_check == 5:
                
                # 종목 테마 오늘 입력여부 확인
                today = datetime.today()
                tomorrow = datetime.today() + timedelta(days=1)
                start = datetime(today.year, today.month, today.day) - timedelta(hours=8)
                end = datetime(tomorrow.year, tomorrow.month, tomorrow.day)
                
                thema_dup_check = {}
                self.thema_notyet_input_list = []
                for code in self.portfolio_stock_dict.keys():
                    code_nm2 = self.dynamicCall("GetMasterCodeName(QString)", code)
                    thema_dup_check = self.mongodb.find_items({"$and": [{"종목코드": code}, {"저장시간": {'$gte': start, '$lt' : end}}]}, "TodayStrongThema", "themaUpdate")
                    dup_check_cnt = len(list(thema_dup_check))
                    
                    # 장시작 전 시그널이 아니면 수행한다.(장시작 전 시그널 = 0)
                    if self.operation_time_status_value != 0:
                        # 오늘 날짜의 테마가 입력되지 않은 경우 (thema_dup_check 가 안나오면)
                        if dup_check_cnt == 0:
                            # 아직 테마 업데이트하라고 보내지 않은 리스트에 추가한다. 
                            if code_nm2 not in self.thema_notyet_input_list:
                                self.thema_notyet_input_list.append(code_nm2)
                            pass
                            # self.logging.logger.debug("thema dup check count is 0 in jogun code list update")
                        # 오늘 날짜의 테마가 입력된 경우
                        elif dup_check_cnt > 0:
                            if code_nm2 in self.thema_notyet_input_list:
                                # 점검필요
                                del self.thema_notyet_input_list[self.thema_notyet_input_list.index(code_nm2)]
                            # self.logging.logger.debug("thema dup check count is bigger 1 in jogun code list update")
                        else:
                            # self.logging.logger.debug("thema dup check error in jogun code list update")
                            pass
                    else:
                        # print("장 시작전이므로 조건검색식에 나온 종목들을 테마추가여부 확인 리스트에 추가/삭제하지 않는다.")
                        pass
                
                if len(self.thema_notyet_input_list) > 0:
                    self.logging.logger.debug("테마입력필요 \n %s " % (self.thema_notyet_input_list))
                    self.selfBot.send("테마입력필요 \n %s " % (self.thema_notyet_input_list))
                    # 뉴스를 보낸다.
                    for code_nm in self.thema_notyet_input_list:
                        QTest.qWait(300)
                        crawlRst = newsNLP.crawlNews(code_nm)
                        self.logging.logger.debug("crawlRst : %s " % crawlRst)
                        if crawlRst == "pass":
                            pass
                        else:
                            self.selfBot.send(crawlRst)
                else:
                    pass
                self.condition_tr_slot_send_msg_check = 0
        else:
            self.logging.logger.debug("조건검색식 조회 Error")
            
    # 조건식 실시간으로 받기
    def condition_real_slot(self, strCode, strType, strConditionName, strConditionIndex):
        changeCheck = 0

        if strType == "I":
            code_nm = self.dynamicCall("GetMasterCodeName(QString)", strCode)
            
            if "자동" in strConditionName:

                # 해당 조건 종목들 포트폴리오에 업데이트
                if strCode not in self.portfolio_stock_dict.keys():
                    self.portfolio_stock_dict.update({strCode:{}})
                    self.portfolio_stock_dict[strCode].update({"종목명": code_nm})
                    
                    # 업종구분 업데이트
                    self.update_upjong_gubn(strCode)
                    self.screen_number_setting()
                    # 실시간 시세조회 요청
                    self.set_real_reg_stock_dict(strCode)
                    # self.logging.logger.debug("실시간 업데이트 : %s" % self.portfolio_stock_dict[strCode])
                
                if strConditionName == "자동_대장주확인":
                    if strCode not in self.jogun1_dict.keys():
                        self.logging.logger.info("[편입] %s \n %s" % (strConditionName, code_nm))
                        
                        code_nm = self.dynamicCall("GetMasterCodeName(QString)", strCode)
                        
                        self.jogun1_dict.update({strCode:{}})
                        self.jogun1_dict[strCode].update({"종목명": code_nm})
                        self.jogun1_dict[strCode].update({"strType": "I"})
                        self.jogun1_dict[strCode].update({"조건식명": strConditionName})
                        
                        today = datetime.today()
                        tomorrow = datetime.today() + timedelta(days=1)
                        start = datetime(today.year, today.month, today.day) - timedelta(hours=8)
                        end = datetime(tomorrow.year, tomorrow.month, tomorrow.day)
                        
                        # 테마 입력여부 메세지를 발송하기 위해서 thema_notyet_input_list 에 아직 발송하지 않은 테마 리스트를 추가하는 작업
                        thema_dup_check = self.mongodb.find_items({"$and": [{"종목코드": strCode}, {"저장시간": {'$gte': start, '$lt' : end}}]}, "TodayStrongThema", "themaUpdate")
                        dup_check_cnt = len(list(thema_dup_check))

                        # 오늘 테마 입력이 안 된 상태
                        if dup_check_cnt == 0:
                            if code_nm not in self.thema_notyet_input_list:
                                self.thema_notyet_input_list.append(code_nm)
                                self.logging.logger.debug("Need insert thema")
                                changeCheck = changeCheck + 1
                        # 오늘 테마 입력이 된 상태
                        elif dup_check_cnt > 0:
                            # 테마 입력 안됐다고 알려주는 변수에서 삭제
                            if code_nm in self.thema_notyet_input_list:
                                del self.thema_notyet_input_list[self.thema_notyet_input_list.index(code_nm)]
                            # self.logging.logger.debug("Already inserted thema")
                        else:
                            self.logging.logger.debug("thema dup check error in jogun code list update")
                                
                    elif strCode in self.jogun1_dict.keys() and self.jogun1_dict[strCode]["strType"] == "D":
                        code_nm = self.dynamicCall("GetMasterCodeName(QString)", strCode)
                        
                        self.jogun1_dict[strCode].update({"strType": "I"})
                        # self.logging.logger.debug("[재편입] %s strType D -> I : %s" % (strConditionName, self.jogun1_dict[strCode]["종목명"]))

                    else:
                        self.logging.logger.debug("원래있었어 : %s" % self.jogun1_dict[strCode]["종목명"])
                    
                elif strConditionName == "자동_장초반_상승률상위":

                    if strCode not in self.jogun2_dict.keys():
                        self.logging.logger.info("[편입] %s \n %s" % (strConditionName, code_nm))
                        
                        code_nm = self.dynamicCall("GetMasterCodeName(QString)", strCode)
                        
                        self.jogun2_dict.update({strCode:{}})
                        self.jogun2_dict[strCode].update({"종목명": code_nm})
                        self.jogun2_dict[strCode].update({"strType": "I"})
                        self.jogun2_dict[strCode].update({"조건식명": strConditionName})
                        
                        today = datetime.today()
                        tomorrow = datetime.today() + timedelta(days=1)
                        start = datetime(today.year, today.month, today.day) - timedelta(hours=8)
                        end = datetime(tomorrow.year, tomorrow.month, tomorrow.day)
                        
                        # 테마 입력여부 메세지를 발송하기 위해서 thema_notyet_input_list 에 아직 발송하지 않은 테마 리스트를 추가하는 작업
                        thema_dup_check = self.mongodb.find_items({"$and": [{"종목코드": strCode}, {"저장시간": {'$gte': start, '$lt' : end}}]}, "TodayStrongThema", "themaUpdate")
                        dup_check_cnt = len(list(thema_dup_check))

                        # 오늘 테마 입력이 안 된 상태
                        if dup_check_cnt == 0:
                            if code_nm not in self.thema_notyet_input_list:
                                self.thema_notyet_input_list.append(code_nm)
                                self.logging.logger.debug("Need insert thema")
                                changeCheck = changeCheck + 1
                        # 오늘 테마 입력이 된 상태
                        elif dup_check_cnt > 0:
                            # 테마 입력 안됐다고 알려주는 변수에서 삭제
                            if code_nm in self.thema_notyet_input_list:
                                del self.thema_notyet_input_list[self.thema_notyet_input_list.index(code_nm)]
                            # self.logging.logger.debug("Already inserted thema")
                        else:
                            self.logging.logger.debug("thema dup check error in jogun code list update")
                        
                    elif strCode in self.jogun2_dict.keys() and self.jogun2_dict[strCode]["strType"] == "D":
                        code_nm = self.dynamicCall("GetMasterCodeName(QString)", strCode)
                        
                        self.jogun2_dict[strCode].update({"strType": "I"})
                        # self.logging.logger.debug("[재편입] %s strType D -> I : %s" % (strConditionName, self.jogun2_dict[strCode]["종목명"]))
                                
                    else:
                        self.logging.logger.debug("원래있었어 : %s" % self.jogun2_dict[strCode]["종목명"])
                    
                elif strConditionName == "자동_장중세력봉":
                        
                    if strCode not in self.jogun3_dict.keys():
                        self.logging.logger.info("[편입] %s \n %s" % (strConditionName, code_nm))
                        
                        code_nm = self.dynamicCall("GetMasterCodeName(QString)", strCode)
                        
                        self.jogun3_dict.update({strCode:{}})
                        self.jogun3_dict[strCode].update({"종목명": code_nm})
                        self.jogun3_dict[strCode].update({"strType": "I"})
                        self.jogun3_dict[strCode].update({"조건식명": strConditionName})
                        
                        today = datetime.today()
                        tomorrow = datetime.today() + timedelta(days=1)
                        start = datetime(today.year, today.month, today.day) - timedelta(hours=8)
                        end = datetime(tomorrow.year, tomorrow.month, tomorrow.day)
                        
                        # 테마 입력여부 메세지를 발송하기 위해서 thema_notyet_input_list 에 아직 발송하지 않은 테마 리스트를 추가하는 작업
                        thema_dup_check = self.mongodb.find_items({"$and": [{"종목코드": strCode}, {"저장시간": {'$gte': start, '$lt' : end}}]}, "TodayStrongThema", "themaUpdate")
                        dup_check_cnt = len(list(thema_dup_check))

                        # 오늘 테마 입력이 안 된 상태
                        if dup_check_cnt == 0:
                            if code_nm not in self.thema_notyet_input_list:
                                self.thema_notyet_input_list.append(code_nm)
                                self.logging.logger.debug("Need insert thema")
                                changeCheck = changeCheck + 1
                        # 오늘 테마 입력이 된 상태
                        elif dup_check_cnt > 0:
                            # 테마 입력 안됐다고 알려주는 변수에서 삭제
                            if code_nm in self.thema_notyet_input_list:
                                del self.thema_notyet_input_list[self.thema_notyet_input_list.index(code_nm)]
                            # self.logging.logger.debug("Already inserted thema")
                        else:
                            self.logging.logger.debug("thema dup check error in jogun code list update")

                    elif strCode in self.jogun3_dict.keys() and self.jogun3_dict[strCode]["strType"] == "D":
                        code_nm = self.dynamicCall("GetMasterCodeName(QString)", strCode)
                        
                        self.jogun3_dict[strCode].update({"strType": "I"})
                        # self.logging.logger.debug("[재편입] %s strType D -> I : %s" % (strConditionName, self.jogun3_dict[strCode]["종목명"]))
                        
                    else:
                        self.logging.logger.debug("원래있었어 : %s" % self.jogun3_dict[strCode]["종목명"])       
                    
                elif strConditionName == "자동_장중매횡":
                        
                    if strCode not in self.jogun4_dict.keys():
                        self.logging.logger.info("[편입] %s \n %s" % (strConditionName, code_nm))
                        
                        code_nm = self.dynamicCall("GetMasterCodeName(QString)", strCode)
                        
                        self.jogun4_dict.update({strCode:{}})
                        self.jogun4_dict[strCode].update({"종목명": code_nm})
                        self.jogun4_dict[strCode].update({"strType": "I"})
                        self.jogun4_dict[strCode].update({"조건식명": strConditionName})
                        
                        today = datetime.today()
                        tomorrow = datetime.today() + timedelta(days=1)
                        start = datetime(today.year, today.month, today.day) - timedelta(hours=8)
                        end = datetime(tomorrow.year, tomorrow.month, tomorrow.day)
                        
                        # 테마 입력여부 메세지를 발송하기 위해서 thema_notyet_input_list 에 아직 발송하지 않은 테마 리스트를 추가하는 작업
                        thema_dup_check = self.mongodb.find_items({"$and": [{"종목코드": strCode}, {"저장시간": {'$gte': start, '$lt' : end}}]}, "TodayStrongThema", "themaUpdate")
                        dup_check_cnt = len(list(thema_dup_check))

                        # 오늘 테마 입력이 안 된 상태
                        if dup_check_cnt == 0:
                            if code_nm not in self.thema_notyet_input_list:
                                self.thema_notyet_input_list.append(code_nm)
                                self.logging.logger.debug("Need insert thema")
                                changeCheck = changeCheck + 1
                        # 오늘 테마 입력이 된 상태
                        elif dup_check_cnt > 0:
                            # 테마 입력 안됐다고 알려주는 변수에서 삭제
                            if code_nm in self.thema_notyet_input_list:
                                del self.thema_notyet_input_list[self.thema_notyet_input_list.index(code_nm)]
                            # self.logging.logger.debug("Already inserted thema")
                        else:
                            self.logging.logger.debug("thema dup check error in jogun code list update")
                        
                    elif strCode in self.jogun4_dict.keys() and self.jogun4_dict[strCode]["strType"] == "D":
                        code_nm = self.dynamicCall("GetMasterCodeName(QString)", strCode)
                        
                        self.jogun4_dict[strCode].update({"strType": "I"})
                        # self.logging.logger.debug("[재편입] %s strType D -> I : %s" % (strConditionName, self.jogun4_dict[strCode]["종목명"]))
                        
                    else:
                        self.logging.logger.debug("원래있었어 : %s" % self.jogun4_dict[strCode]["종목명"])

                elif strConditionName == "자동_당일강세테마":
                        
                    if strCode not in self.jogun5_dict.keys():
                        self.logging.logger.info("[편입] %s \n %s" % (strConditionName, code_nm))
                        code_nm = self.dynamicCall("GetMasterCodeName(QString)", strCode)
                        
                        self.jogun5_dict.update({strCode:{}})
                        self.jogun5_dict[strCode].update({"종목명": code_nm})
                        self.jogun5_dict[strCode].update({"strType": "I"})
                        self.jogun5_dict[strCode].update({"조건식명": strConditionName})
                        
                        today = datetime.today()
                        tomorrow = datetime.today() + timedelta(days=1)
                        start = datetime(today.year, today.month, today.day) - timedelta(hours=8)
                        end = datetime(tomorrow.year, tomorrow.month, tomorrow.day)
                        
                        # 테마 입력여부 메세지를 발송하기 위해서 thema_notyet_input_list 에 아직 발송하지 않은 테마 리스트를 추가하는 작업
                        thema_dup_check = self.mongodb.find_items({"$and": [{"종목코드": strCode}, {"저장시간": {'$gte': start, '$lt' : end}}]}, "TodayStrongThema", "themaUpdate")
                        dup_check_cnt = len(list(thema_dup_check))

                        # 오늘 테마 입력이 안 된 상태
                        if dup_check_cnt == 0:
                            if code_nm not in self.thema_notyet_input_list:
                                self.thema_notyet_input_list.append(code_nm)
                                self.logging.logger.debug("Need insert thema")
                                changeCheck = changeCheck + 1
                        # 오늘 테마 입력이 된 상태
                        elif dup_check_cnt > 0:
                            # 테마 입력 안됐다고 알려주는 변수에서 삭제
                            if code_nm in self.thema_notyet_input_list:
                                del self.thema_notyet_input_list[self.thema_notyet_input_list.index(code_nm)]
                            # self.logging.logger.debug("Already inserted thema")
                        else:
                            self.logging.logger.debug("thema dup check error in jogun code list update")
                        
                    elif strCode in self.jogun5_dict.keys() and self.jogun5_dict[strCode]["strType"] == "D":
                        code_nm = self.dynamicCall("GetMasterCodeName(QString)", strCode)
                        
                        self.jogun5_dict[strCode].update({"strType": "I"})
                        # self.logging.logger.debug("[재편입] %s strType D -> I : %s" % (strConditionName, self.jogun5_dict[strCode]["종목명"]))

                    else:
                        self.logging.logger.debug("원래있었어 : %s" % self.jogun5_dict[strCode]["종목명"])
                        
                else:
                    pass
                
                # self.thema_notyet_input_list 변수에 데이터가 있거나 기존과 변동이 있으면(changeCheck > 0) 봇에 메세지를 발송하고 아니면 버린다. 
                temp_bot_mgs = ""
                    
                if len(self.thema_notyet_input_list) > 0 and (changeCheck > 0):
                    today = datetime.today()
                    tomorrow = datetime.today() + timedelta(days=1)
                    start = datetime(today.year, today.month, today.day) - timedelta(hours=8)
                    end = datetime(tomorrow.year, tomorrow.month, tomorrow.day)
                    
                    temp_bot_mgs = temp_bot_mgs + "테마입력필요\n"
                    # DB 에서 한 번 더 있는지 검색한다.
                    for temp_code_nm in self.thema_notyet_input_list:
                        thema_dup_check = self.mongodb.find_items({"$and": [{"종목명": temp_code_nm}, {"저장시간": {'$gte': start, '$lt' : end}}]}, "TodayStrongThema", "themaUpdate")
                        dup_check_cnt = len(list(thema_dup_check))
                        # 오늘 테마 입력이 안 된 상태
                        if dup_check_cnt == 0:
                            self.logging.logger.debug("Need insert thema")
                            temp_bot_mgs = temp_bot_mgs + "%s " % temp_code_nm
                            QTest.qWait(300)
                            crawlRst = newsNLP.crawlNews(temp_code_nm)
                            self.logging.logger.debug("crawlRst : %s " % crawlRst)
                            if crawlRst == "pass":
                                pass
                            else:
                                self.selfBot.send(crawlRst)
                            
                        # 오늘 테마 입력이 된 상태
                        elif dup_check_cnt > 0:
                            # self.logging.logger.debug("Already inserted thema")
                            pass
                else:
                    # self.logging.logger.debug("테마입력 필요없음")
                    pass
            else:
                self.logging.logger.debug("신규 조건식 추가필요")

        elif strType == "D":
            code_nm = self.dynamicCall("GetMasterCodeName(QString)", strCode)
            self.logging.logger.info("[이탈] %s \n 종목명: %s" % (strConditionName, code_nm))
            # 해당 조건 종목들 리프레쉬
            if "자동" in strConditionName:
                if strConditionName == "자동_대장주확인":
                    self.jogun1_dict[strCode].update({"strType": "D"})
                elif strConditionName == "자동_장초반_상승률상위":
                    self.jogun2_dict[strCode].update({"strType": "D"})
                elif strConditionName == "자동_장중세력봉":
                    self.jogun3_dict[strCode].update({"strType": "D"})
                elif strConditionName == "자동_장중매횡":
                    self.jogun4_dict[strCode].update({"strType": "D"})
                elif strConditionName == "자동_당일강세테마":
                    self.jogun5_dict[strCode].update({"strType": "D"})
                else:
                    pass
            else:
                self.logging.logger.debug("신규 조건식 추가필요")
        else:
            self.logging.logger.info("실시간 조건식 strType Error")
            
    def bot_send_in_cnt(self, msg):
        
        telEnd = time.time()
        diffTime = telEnd - self.telStart
        self.telFloodCnt = self.telFloodCnt + 1
        
        if self.telFloodCnt % 18 == 0:
            if diffTime < 60:
                self.telFloodCnt = 1
                self.telStart = time.time()
                if self.telType == 1:
                    self.bot2.send(msg)
                    self.telType = 2
                elif self.telType == 2:
                    self.bot3.send(msg)
                    self.telType = 3
                elif self.telType == 3:
                    self.bot.send(msg)
                    self.telType = 1
                else:
                    QTest.qWait(6000-(diffTime*100))
            else:
                pass
        else:
            if self.telType == 1:
                self.bot2.send(msg)
            elif self.telType == 2:
                self.bot3.send(msg)
            elif self.telType == 3:
                self.bot.send(msg)
            else:
                pass
            
    # def get_outTimeUpDownRate(self):
    #     if "00:00:00" <= datetime.today().strftime("%H:%M:%S") <= "08:30:00":
    #         # 수집일을 오늘 날짜로
    #         collect_time = datetime.today().strftime("%Y%m%d")
    #         self.logging.logger.debug("수집일을 오늘 날짜로 ")
    #         # 수집일을 오늘 날짜로 TR 에서 직접처리 collect_time = ""
    #         codeList = []
    #         for i in self.mongodb.find_items({}, 'TodayStrongThema', 'codeList'):
    #             codeList.append(i["종목코드"])
                
    #         i = 0
    #         for code in codeList:
    #             dup_check = self.mongodb.find_item({"$and":[{"수집날짜": collect_time},{"종목코드": code}]}, "TodayStrongThema", "outTimeUpDownRate")
    #             self.logging.logger.debug("dup_check 수행")
    #             if dup_check == None:
    #                 self.out_time_up_down_rate_info(code)
    #                 outTimeUpDownRate = self.TempOutTimeUpDownRate
    #                 save_item = {
    #                     "수집날짜": collect_time,
    #                     "종목코드": code,
    #                     "시간외단일가": outTimeUpDownRate
    #                 }
    #                 self.mongodb.upsert_item({"종목코드": code},{"$set": save_item},'TodayStrongThema','outTimeUpDownRate')
    #                 QTest.qWait(3600)
    #                 remain_check = len(codeList) - i
    #                 self.logging.logger.debug("시간외 요청함수 수행 %s분 남음" % (remain_check * 3.6 / 60))
    #             else:
    #                 remain_check = len(codeList) - i
    #             i = i + 1

    #     elif "18:01:00" <= datetime.today().strftime("%H:%M:%S") <= "23:59:00":
    #         # 수집일을 내일 날짜로 
    #         collect_time = (datetime.today() + timedelta(days=1)).strftime("%Y%m%d")
    #         self.logging.logger.debug("수집일을 내일 날짜로 ")
    #         # 수집일을 오늘 날짜로 TR 에서 직접처리 collect_time = ""
    #         codeList = []
    #         for i in self.mongodb.find_items({}, 'TodayStrongThema', 'codeList'):
    #             codeList.append(i["종목코드"])
            
    #         i = 0
    #         for code in codeList:    
    #             dup_check = self.mongodb.find_item({"$and":[{"수집날짜": collect_time},{"종목코드": code}]}, "TodayStrongThema", "outTimeUpDownRate")
    #             if dup_check == None:
    #                 self.out_time_up_down_rate_info(code)
    #                 outTimeUpDownRate = self.TempOutTimeUpDownRate
    #                 save_item = {
    #                     "수집날짜": collect_time,
    #                     "종목코드": code,
    #                     "시간외단일가": outTimeUpDownRate
    #                 }
    #                 self.mongodb.upsert_item({"종목코드": code},{"$set": save_item},'TodayStrongThema','outTimeUpDownRate')
    #                 QTest.qWait(3600)
    #                 remain_check = len(codeList) - i
    #                 self.logging.logger.debug("시간외 요청함수 수행 %s분 남음" % (remain_check * 3.6 / 60))
    #             else:
    #                 remain_check = len(codeList) - i
    #             i = i + 1
    #     else:
    #         pass