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
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from util.newsNLP import *

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('land=ko_KR')

driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()), options=chrome_options)
driver.implicitly_wait(3)
mongodb = MongoDBHandler()
selfBot = selfTelegram()

def simpleTest():
    
    if "00:00:00" <= datetime.today().strftime("%H:%M:%S") <= "18:00:00":
        # 수집일을 오늘 날짜로
        collect_time = datetime.today().strftime("%Y%m%d")
        
        # 시간외단일가 테마 오늘 입력여부 확인
        today = datetime.today()
        tomorrow = datetime.today() + timedelta(days=1)
        start = datetime(today.year, today.month, today.day) - timedelta(hours=8)
        end = datetime(tomorrow.year, tomorrow.month, tomorrow.day)
          
    elif "18:00:00" < datetime.today().strftime("%H:%M:%S") <= "23:59:59":
        # 수집일을 내일 날짜로 
        collect_time = (datetime.today() + timedelta(days=1)).strftime("%Y%m%d")
        
        # 시간외단일가 테마 오늘 입력여부 확인
        today = datetime.today()
        tomorrow = datetime.today() + timedelta(days=1)
        start = datetime(today.year, today.month, today.day) + timedelta(hours=16)
        end = datetime(tomorrow.year, tomorrow.month, tomorrow.day)
    else:
        pass
    
    # outTimeUpDownRate 에 있는 종목중에서 웹 크롤링이 되지 않은 종목의 날짜를 업데이트해서 전체 수집을 완료시킨다.
    not_crawl_items_list = []
    # 시간외단일가 수집일이 다른 데이터를 검색
    not_crawl_items = mongodb.find_items({"수집날짜":{'$ne':collect_time}},'TodayStrongThema','outTimeUpDownRate')
    if not_crawl_items is None:
        pass
    else:
        for item in not_crawl_items:
            not_crawl_items_list.append(item['종목코드'])
            not_crawl_items_list.append(item['종목명'])
    
    print(not_crawl_items_list)

        
if __name__ == "__main__":
    simpleTest()
    driver.quit()