#크롤링시 필요한 라이브러리 불러오기
from bs4 import BeautifulSoup
import requests
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from datetime import datetime, timedelta
from util.MongoDBHandler import MongoDBHandler

#웹드라이버 설정
options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('--disable-gpu')
# options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), chrome_options=options)


class newsNLP():
    
    def crawlNews(code_nm):
        mongodb = MongoDBHandler()
        # 검색어 입력
        today = datetime.today()
        tomorrow = datetime.today() + timedelta(days=1)
        start = datetime(today.year, today.month, today.day) - timedelta(hours=8)
        end = datetime(tomorrow.year, tomorrow.month, tomorrow.day)
        
        search = "특징주 "+ code_nm
        check_code_list = mongodb.find_items({"종목명": code_nm}, 'TodayStrongThema', 'codeList')

        if len(list(check_code_list)) > 0:
            search_url = "https://search.naver.com/search.naver?where=news&sm=tab_pge&query=" + search + "&start=1" + "&nso=" + "so%3Ar%2Cp%3A1d" + "&qdt=0"

            # selenium으로 검색 페이지 불러오기 #

            driver.get(search_url)

            headers = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/98.0.4758.102" }
            original_html = requests.get(search_url,headers=headers)
            html = BeautifulSoup(original_html.text, "html.parser")
            all_titles = html.select('.news_tit')
            titles = ""
            limit_len = 0
            
            if len(all_titles) > 3:
                limit_len = 3
            else:
                limit_len = len(all_titles)
                
            for i in range(limit_len):
                titles = titles + "\n" + (html.select('.news_tit')[i]['title']) + "\n" + html.select('.news_tit')[i]['href']

            # 검색 종목을 오늘 날짜 - 8시간으로 themaUpdate 에서 검색하고 
            thema_dup_check = mongodb.find_items({"$and": [{"종목명": code_nm}, {"저장시간": {'$gte': start, '$lt' : end}}]}, "TodayStrongThema", "themaUpdate")
            dup_check_cnt = len(list(thema_dup_check))
            
            # 오늘 최초 검색 : 메세지를 발송하고 검색을 업데이트 한다.
            if dup_check_cnt == 0:
                
                # 일단 검색을 했으면 무조건 패스라고 DB에 넣는다.
                code_search = mongodb.find_item({"종목명": code_nm}, "TodayStrongThema", "codeList")
                code = str(code_search["종목코드"])
                
                save_item = {
                        "저장시간" : datetime.today(),
                        "종목명" : str(code_nm),
                        "종목코드" : code,
                        "테마" : "패스"
                    }
                mongodb.delete_items({"$and": [{"테마" : "패스"},{"종목명": code_nm}]}, "TodayStrongThema", "themaUpdate")
                mongodb.insert_item(save_item, "TodayStrongThema", "themaUpdate") 
                
                if titles == "":
                    titles = " %s 관련 기사가 없습니다." % code_nm
                else:
                    titles = " %s 관련기사 \n %s" % (code_nm, titles)
                    # 메세지 발송여부를 체크하기 위해 패스를 한 번 더 입력해준다.
                    code_search = mongodb.find_item({"종목명": code_nm}, "TodayStrongThema", "codeList")
                    code = str(code_search["종목코드"])
                    
                    save_item = {
                            "저장시간" : datetime.today(),
                            "종목명" : str(code_nm),
                            "종목코드" : code,
                            "테마" : "패스"
                        }
                    mongodb.insert_item(save_item, "TodayStrongThema", "themaUpdate") 

            # 오늘 이미 검색을 했던 종목
            elif dup_check_cnt == 1:
                if titles == "":
                    # 기사가 없으면 메세지를 발송하지 않는다.
                    titles = "pass"
                else:
                    # 기사가 나오면 메세지를 발송한다.
                    titles = " %s 관련기사 \n %s" % (code_nm, titles)
                    
                    # 메세지 발송여부를 체크하기 위해 패스를 한 번 더 입력해준다.
                    code_search = mongodb.find_item({"종목명": code_nm}, "TodayStrongThema", "codeList")
                    code = str(code_search["종목코드"])
                    
                    save_item = {
                            "저장시간" : datetime.today(),
                            "종목명" : str(code_nm),
                            "종목코드" : code,
                            "테마" : "패스"
                        }
                    mongodb.insert_item(save_item, "TodayStrongThema", "themaUpdate") 

            # 오늘 테마 입력이 된 상태
            elif dup_check_cnt >= 2:
                # 메세지를 발송하지 않는다.
                titles = "pass"
            
            # 기사도 검색
            else:
                titles = "error"

            return titles
        else:
            titles = "%s 는 종목명과 일치하지 않습니다." % code_nm
            return titles
    
    def crawlQuit():
        driver.quit()