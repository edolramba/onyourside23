from common.importConfig import *
from telegram.ext import Updater
from telegram.ext import MessageHandler, Filters
from util.selfTelegram import selfTelegram
from util.MongoDBHandler import MongoDBHandler
from datetime import datetime, timedelta
from util.newsNLP import *

class themaUpdate:

    def __init__(self):
        super().__init__()
        # DB 사용선언
        self.mongodb = MongoDBHandler()
        self.bot = selfTelegram()

        # updater
        updater = Updater(token=self.bot.token, use_context=True)
        dispatcher = updater.dispatcher
        updater.start_polling()

        echo_handler = MessageHandler(Filters.text, self.handler)
        dispatcher.add_handler(echo_handler)
        
    # 테마 업데이트 해주는 로직
    def handler(self, update, context):
        code_nm_search_list = self.mongodb.find_items({}, "TodayStrongThema", "codeList") # 해당 조건으로 검색한 전체 List 를 DB 에서 가져온다.
        code_nm_list = []
        for item in code_nm_search_list:
            code_nm_list.append(str(item["종목명"]))

        user_text = update.message.text # 사용자가 보낸 메세지를 user_text 변수에 저장합니다.

        split_blank = user_text.split() # 사용자가 보낸 메세지를 빈칸으로 나누어 저장한다.
        delete_word = ""

        # 종목명
        if len(split_blank) == 1:
            first_word = user_text
            content_word = ""
            save_time = datetime.today()
            code_nm = "" 

        elif len(split_blank) == 2:
            # 종목(빈칸)명 = 2개
            if split_blank[0] + " " + split_blank[1] in code_nm_list:
                first_word = split_blank[0] + " " + split_blank[1]
                content_word = ""
                save_time = datetime.today()
                code_nm = "" 
            # 종목명 테마 = 2개
            elif split_blank[0] + " " + split_blank[1] not in code_nm_list:
                first_word = split_blank[0]
                content_word = split_blank[1]
                save_time = datetime.today()
                code_nm = "" 
            elif split_blank[0] == "테마":
                first_word = "테마"
                content_word = split_blank[1]
                save_time = datetime.today()
                code_nm = "" 
            elif split_blank[0] == "일괄삭제":
                first_word = "일괄삭제"
                content_word = split_blank[1]
                save_time = datetime.today()
                code_nm = "" 
            else:
                pass

        elif len(split_blank) == 3 and split_blank[0] != "삭제":
            # 종목(빈칸)명 테마 = 3개
            if split_blank[0] + " " + split_blank[1] in code_nm_list:
                first_word = split_blank[0] + " " + split_blank[1]
                content_word = split_blank[2]
                save_time = datetime.today()
                code_nm = ""
            
            # 종(빈칸)목(빈칸)명 = 3개
            elif split_blank[0] + " " + split_blank[1] + " " + split_blank[2] in code_nm_list:
                first_word = split_blank[0] + " " + split_blank[1] + " " + split_blank[2]
                content_word = ""
                save_time = datetime.today()
                code_nm = ""
                
            else:
                pass
            
        # 삭제(빈칸)종목명(빈칸)테마 = 3개
        elif len(split_blank) == 3 and split_blank[0] == "삭제":
            first_word = "삭제"
            content_word = split_blank[2]
            save_time = datetime.today()
            code_nm = ""
            delete_word = split_blank[1]
            
        # 삭제(빈칸)종목(빈칸)명(빈칸)테마 = 4개
        elif len(split_blank) == 4 and split_blank[0] == "삭제":
            first_word = "삭제"
            content_word = split_blank[3]
            save_time = datetime.today()
            code_nm = ""
            delete_word = split_blank[1] + " " + split_blank[2]
        # 종(빈칸)목(빈칸)명(빈칸)테마 = 4개
        elif len(split_blank) == 4 and split_blank[0] != "삭제":
            first_word = split_blank[0] + " " + split_blank[1] + " " + split_blank[2]
            content_word = split_blank[3]
            save_time = datetime.today()
            code_nm = ""
        # 삭제(빈칸)종(빈칸)목(빈칸)명(빈칸)테마 = 5개
        elif len(split_blank) == 5 and split_blank[0] == "삭제":
            first_word = "삭제"
            content_word = split_blank[4]
            save_time = datetime.today()
            delete_word = split_blank[1] + " " + split_blank[2] + " " + split_blank[3]
            code_nm = ""
        else:
            pass

        # 보낸 텍스트에 종목명과 테마가 적혀있으면 DB 에 테마를 업데이트 한다.
        if first_word in code_nm_list:
            # 종목코드, 종목명, 테마, 저장시간을 업데이트 한다. 
            # 같은 종목코드의 같은테마라면 저장시간만 업데이트 한다.
            update_list = self.mongodb.find_item( {"$and": [ {"종목명": first_word, "테마": content_word} ] }, "TodayStrongThema", "themaUpdate") 
            code_nm_search = self.mongodb.find_items({"종목명": first_word}, "TodayStrongThema", "codeList")
            for item in code_nm_search:
                code_nm = str(item["종목코드"])
            if update_list is None:
                save_item = {
                    "저장시간" : save_time,
                    "종목명" : str(first_word),
                    "종목코드" : code_nm,
                    "테마" : str(content_word)
                }
                if len(split_blank) != 1:
                    self.mongodb.insert_item(save_item, "TodayStrongThema", "themaUpdate")
                
            else:
                save_item = {
                    "저장시간" : save_time
                }
                if len(split_blank) != 1:
                    self.mongodb.update_item( {"$and": [ {"종목명": first_word, "테마": content_word} ] }, {"$set": save_item}, "TodayStrongThema", "themaUpdate")
                    
            return_values = self.mongodb.find_items({"종목명": first_word}, "TodayStrongThema", "themaUpdate")
            return_list = []
            for item in return_values:
                return_list.append(item["테마"])
                
            self.bot.send("%s 테마: %s" % (first_word, return_list))

        elif first_word == "일괄삭제":            
            
            self.mongodb.delete_items( {"테마": content_word}, "TodayStrongThema", "themaUpdate")
            
            return_values = self.mongodb.find_items({"테마": content_word}, "TodayStrongThema", "themaUpdate")
            return_list = []
            for item in return_values:
                return_list.append(item["종목명"])
                
            self.bot.send("[일괄삭제완료] %s 테마\n 테마에 속한 종목: %s" % (content_word, return_list))

        elif first_word == "삭제":            
            
            self.bot.send("삭제양식: 삭제 종목명 테마")
            if delete_word in code_nm_list:
                
                self.mongodb.delete_items( {"$and": [ {"종목명": delete_word, "테마": content_word} ] }, "TodayStrongThema", "themaUpdate")
                
                return_values = self.mongodb.find_items({"종목명": delete_word}, "TodayStrongThema", "themaUpdate")
                return_list = []
                for item in return_values:
                    return_list.append(item["테마"])
                    
                self.bot.send("[삭제완료] %s %s 테마\n 현재테마: %s" % (delete_word, content_word, return_list))
            else:
                pass
        # 오늘 테마를 입력하지 않은 종목리스트 추출
        elif first_word == "1111":
            today = datetime.today()
            tomorrow = datetime.today() + timedelta(days=1)
            start = datetime(today.year, today.month, today.day) - timedelta(hours=8)
            end = datetime(tomorrow.year, tomorrow.month, tomorrow.day)

            non_input_list = []
            today_input_list = []
            today_input = self.mongodb.find_items({"$and": [ {"저장시간": {'$gte': start, '$lt' : end}}  ] }, "TodayStrongThema", "themaUpdate")
            for i in today_input:
                today_input_list.append(i["종목명"])
            
            today_input_list = list(set(today_input_list))

            for item in today_input_list:
                # 패스를 입력한 수
                pass_thema = self.mongodb.find_items({"$and": [ {"종목명": item, "테마": "패스", "저장시간": {'$gte': start, '$lt' : end}}  ] }, "TodayStrongThema", "themaUpdate")
                pass_thema_len = len(list(pass_thema))
                # 전체 재료의 수
                item_thema = self.mongodb.find_items({"$and": [ {"종목명": item, "저장시간": {'$gte': start, '$lt' : end}}  ] }, "TodayStrongThema", "themaUpdate")
                item_thema_len = len(list(item_thema))
                # 전체 - 패스 > 0 이면 재료를 입력했고, 0보다 작거나 같으면 재료를 입력하지 않음
                if item_thema_len - pass_thema_len > 0:
                    pass
                else:
                    non_input_list.append(item)
                
            self.bot.send("재료 미입력 테마\n %s" % non_input_list)

        # 오늘 테마를 입력하지 않은 종목들 뉴스 재발송
        elif first_word == "2222":
            today = datetime.today()
            tomorrow = datetime.today() + timedelta(days=1)
            start = datetime(today.year, today.month, today.day) - timedelta(hours=8)
            end = datetime(tomorrow.year, tomorrow.month, tomorrow.day)

            non_input_list = []
            today_input_list = []
            today_input = self.mongodb.find_items({"$and": [ {"저장시간": {'$gte': start, '$lt' : end}}  ] }, "TodayStrongThema", "themaUpdate")
            for i in today_input:
                today_input_list.append(i["종목명"])

            today_input_list = list(set(today_input_list))
            
            for item in today_input_list:
                # 패스를 입력한 수
                pass_thema = self.mongodb.find_items({"$and": [ {"종목명": item, "테마": "패스", "저장시간": {'$gte': start, '$lt' : end}}  ] }, "TodayStrongThema", "themaUpdate")
                pass_thema_len = len(list(pass_thema))
                # 전체 재료의 수
                item_thema = self.mongodb.find_items({"$and": [ {"종목명": item, "저장시간": {'$gte': start, '$lt' : end}}  ] }, "TodayStrongThema", "themaUpdate")
                item_thema_len = len(list(item_thema))
                # 전체 - 패스 > 0 이면 재료를 입력했고, 0보다 작거나 같으면 재료를 입력하지 않음
                if item_thema_len - pass_thema_len > 0:
                    pass
                else:
                    non_input_list.append(item)
            
            # 뉴스를 보낸다.
            if non_input_list:
                for code_nm in non_input_list:
                    crawlRst = newsNLP.crawlNews(code_nm)
                    if crawlRst == "pass":
                        pass
                    else:
                        self.bot.send(crawlRst)
            else:
                pass
            
            self.bot.send("Sending news is done.")

        elif first_word == "헬프":
            
            helpFilePath = "C:\\Dev\\onyourside22\\server\\kiwoom\\files\\themaUpdateHelp.txt"
            startMsg = ""
            startMsgesFile = open(helpFilePath, 'rt', encoding='utf-8')
            startMsg = startMsgesFile.readlines()
            
            sendMgs = ""
            for line in startMsg:
                sendMgs = sendMgs + str(line)
            startMsgesFile.close()
            
            self.bot.send(sendMgs)
            
        elif first_word == "테마" and len(split_blank) > 1:
            thema_code_list = []
            all_themas = self.mongodb.find_items({"테마": content_word}, "TodayStrongThema", "themaUpdate")
            for i in all_themas:
                thema_code_list.append(i["종목명"])
                
            self.bot.send("%s 테마 종목리스트\n %s" % (content_word, thema_code_list))

        else:
            pass

if __name__ == '__main__':
    print("Telegram class")