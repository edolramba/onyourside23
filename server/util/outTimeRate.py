import sys
sys.path.append("C:\\Dev\\onyourside22\\server")
sys.path.append("C:\\Dev\\onyourside22\\server\\test")
sys.path.append("C:\\Dev\\onyourside22\\server\\util")
#크롤링시 필요한 라이브러리 불러오기
from bs4 import BeautifulSoup
import requests
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
from util.MongoDBHandler import MongoDBHandler
import pyperclip
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from util.selfTelegram import selfTelegram
from util.newsNLP import *
from PyQt5.QtTest import *

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('land=ko_KR')

driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()), options=chrome_options)
driver.implicitly_wait(3)
mongodb = MongoDBHandler()
selfBot = selfTelegram()

def getStockInfo(url):
    # DB 에서 종목명과 코드를 추출한다. 
    code_nm_list = []
    code_list = []
    code_dict_data = mongodb.find_items({},"TodayStrongThema", "codeList")
    for i in code_dict_data:
        code_nm_list.append(i["종목명"])
        code_list.append(i["종목코드"])

    if "00:00:00" <= datetime.today().strftime("%H:%M:%S") <= "18:00:00":
        # 수집일을 오늘 날짜로
        collect_time = datetime.today().strftime("%Y%m%d")
    elif "18:00:00" < datetime.today().strftime("%H:%M:%S") <= "23:59:59":
        # 수집일을 내일 날짜로 
        collect_time = (datetime.today() + timedelta(days=1)).strftime("%Y%m%d")
    else:
        pass

    # 상승종목 수집
    driver.get(url) # 시간외 단일가
    
    WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located)
    
    # 마지막 페이지 번호 추출
    last_page_arrow_path = '#boxAfterHours > div.box_contents > div:nth-child(1) > div > a.btnLast'
    last_page = driver.find_element(By.CSS_SELECTOR, last_page_arrow_path).click()
    time.sleep(1)
    
    page_last = driver.find_element(By.CSS_SELECTOR, '#boxAfterHours > div.box_contents > div:nth-child(1) > div').text
    split_blank = page_last.split()
    total_page_num = int(split_blank[-1])
    print(total_page_num)
    
    
    # 상승에 해당하는 페이지 정보 수집
    for i in range(1,total_page_num+1):
        breakVaiable = 0
        print("============= 상승 %s page =============" % i)
        if i == 1:
            # 가장 첫 페이지를 클릭한다. 
            select_page = driver.find_element(By.CSS_SELECTOR, '#boxAfterHours > div.box_contents > div:nth-child(1) > div > a.btnFirst').click()
            time.sleep(1)
        elif (i == 11) or (i == 21) or (i == 31) or (i == 41):
            # 넥스트 페이지를 클릭한다.
            select_page = driver.find_element(By.CSS_SELECTOR, '#boxAfterHours > div.box_contents > div:nth-child(1) > div > a.btnNext').click()
            time.sleep(1)
        elif i >= 12:
            a = divmod(i, 10)
            mok = a[0]  # 몫
            namuji = a[1] # 나머지
            page_num = 0
            
            if (mok + 1) * 10 > total_page_num:
                page_num = (mok + 1) * 10 - total_page_num + 2 + namuji
            else:
                page_num = 2 + namuji
            select_page = driver.find_element(By.CSS_SELECTOR, '#boxAfterHours > div.box_contents > div:nth-child(1) > div > a:nth-child(%s)' % page_num).click()
            time.sleep(1)
        else:
            # 남는 페이지를 클릭한다.
            select_page = driver.find_element(By.CSS_SELECTOR, '#boxAfterHours > div.box_contents > div:nth-child(1) > div > a:nth-child(%s)' % i).click()
            time.sleep(1)
            
        for j in range(1,32):
            try:
                if j == 1:
                    itemName = driver.find_element(By.CSS_SELECTOR, "#boxAfterHours > div.box_contents > div:nth-child(1) > table > tbody > tr.first > td:nth-child(1) > a").text    
                    itemOutTimeRate = driver.find_element(By.CSS_SELECTOR, "#boxAfterHours > div.box_contents > div:nth-child(1) > table > tbody > tr.first > td:nth-child(4) > span").text
                else:
                    itemName = driver.find_element(By.CSS_SELECTOR, "#boxAfterHours > div.box_contents > div:nth-child(1) > table > tbody > tr:nth-child(%s) > td:nth-child(1) > a" % j).text
                    itemOutTimeRate = driver.find_element(By.CSS_SELECTOR, "#boxAfterHours > div.box_contents > div:nth-child(1) > table > tbody > tr:nth-child(%s) > td:nth-child(4) > span" % j).text

                print(itemName, itemOutTimeRate)

                if itemName in code_nm_list:
                    code_dict_data = mongodb.find_item({'종목명': itemName},"TodayStrongThema", "codeList")
                    code = code_dict_data["종목코드"]
                    if(itemOutTimeRate[0] == "+") and float(itemOutTimeRate[1:-1])>=2:
                        itemOutTimeRate = float(itemOutTimeRate[1:-1])
                    elif(itemOutTimeRate[0] == "-") and float(itemOutTimeRate[1:-1])<=-2:
                        itemOutTimeRate = float(itemOutTimeRate[1:-1]) * -1
                    else:
                        breakVaiable = 1
                        break
                    
                    save_item = {
                        "종목코드": code,
                        "종목명": itemName,
                        "수집날짜": collect_time,
                        "시간외단일가": itemOutTimeRate
                    }
                    mongodb.upsert_item({"종목코드": code},{"$set": save_item},'TodayStrongThema','outTimeUpDownRate')
                    
            except StaleElementReferenceException:
                print("상승 row click StaleElementReferenceException")
            except NoSuchElementException:
                print("상승 row click NoSuchElementException")
            except ValueError:
                print("상승 row click ValueError")
        if breakVaiable == 1:
            break

    # 하락 탭 클릭       
    select_page = driver.find_element(By.CSS_SELECTOR, '#boxAfterHours > div.tab > ul > li:nth-child(2) > a').click()
    time.sleep(1)
    
    # 마지막 페이지 번호 추출
    try:
        last_page_arrow_path = '#boxAfterHours > div.box_contents > div:nth-child(2) > div > a.btnLast'
        last_page = driver.find_element(By.CSS_SELECTOR, last_page_arrow_path).click()
        time.sleep(1)
        page_last = driver.find_element(By.CSS_SELECTOR, '#boxAfterHours > div.box_contents > div:nth-child(2) > div').text
        split_blank = page_last.split()
        total_page_num = int(split_blank[-1])
        print(total_page_num)
    except NoSuchElementException:
        print("하락 페이지 번호 추출 NoSuchElementException")
        page_last = driver.find_element(By.CSS_SELECTOR, '#boxAfterHours > div.box_contents > div:nth-child(2) > div').text
        split_blank = page_last.split()
        total_page_num = int(split_blank[-1])
        print(total_page_num)
    except StaleElementReferenceException:
        print("하락 페이지 번호 추출 StaleElementReferenceException")
    except ValueError:
        print("하락 페이지 번호 추출 ValueError")
        
    # 하락에 해당하는 페이지 정보 수집
    for i in range(1,total_page_num+1):
        breakVaiable = 0
        print("============= 하락 %s page =============" % i)
        if i == 1:
            try:
                # 가장 첫 페이지를 클릭한다. 
                select_page = driver.find_element(By.CSS_SELECTOR, '#boxAfterHours > div.box_contents > div:nth-child(2) > div > a.btnFirst').click()
                time.sleep(1)
            except NoSuchElementException:
                pass
        elif (i == 11) or (i == 21) or (i == 31) or (i == 41):
            # 넥스트 페이지를 클릭한다.
            select_page = driver.find_element(By.CSS_SELECTOR, '#boxAfterHours > div.box_contents > div:nth-child(2) > div > a.btnNext').click()
            time.sleep(1)
        elif i >= 12:
            a = divmod(i, 10)
            mok = a[0]  # 몫
            namuji = a[1] # 나머지
            page_num = 0
            
            if (mok + 1) * 10 > total_page_num:
                page_num = (mok + 1) * 10 - total_page_num + 2 + namuji
            else:
                page_num = 2 + namuji
            
            select_page = driver.find_element(By.CSS_SELECTOR, '#boxAfterHours > div.box_contents > div:nth-child(2) > div > a:nth-child(%s)' % page_num).click()
            time.sleep(1)
        else:
            # 남는 페이지를 클릭한다.
            select_page = driver.find_element(By.CSS_SELECTOR, '#boxAfterHours > div.box_contents > div:nth-child(2) > div > a:nth-child(%s)' % i).click()
            time.sleep(1)
            
        for j in range(1,32):
            try:
                if j == 1:
                    itemName = driver.find_element(By.CSS_SELECTOR, "#boxAfterHours > div.box_contents > div:nth-child(2) > table > tbody > tr.first > td:nth-child(1) > a").text    
                    itemOutTimeRate = driver.find_element(By.CSS_SELECTOR, "#boxAfterHours > div.box_contents > div:nth-child(2) > table > tbody > tr.first > td:nth-child(4) > span").text
                else:
                    itemName = driver.find_element(By.CSS_SELECTOR, "#boxAfterHours > div.box_contents > div:nth-child(2) > table > tbody > tr:nth-child(%s) > td:nth-child(1) > a" % j).text
                    itemOutTimeRate = driver.find_element(By.CSS_SELECTOR, "#boxAfterHours > div.box_contents > div:nth-child(2) > table > tbody > tr:nth-child(%s) > td:nth-child(4) > span" % j).text

                print(itemName, itemOutTimeRate)

                if itemName in code_nm_list:
                    code_dict_data = mongodb.find_item({'종목명': itemName},"TodayStrongThema", "codeList")
                    code = code_dict_data["종목코드"]
                    if(itemOutTimeRate[0] == "+") and float(itemOutTimeRate[1:-1])>=2:
                        itemOutTimeRate = float(itemOutTimeRate[1:-1])
                    elif(itemOutTimeRate[0] == "-") and float(itemOutTimeRate[1:-1])<=-2:
                        itemOutTimeRate = float(itemOutTimeRate[1:-1]) * -1
                    else:
                        breakVaiable = 1
                        break
                    
                    save_item = {
                        "종목코드": code,
                        "종목명": itemName,
                        "수집날짜": collect_time,
                        "시간외단일가": itemOutTimeRate
                    }
                    mongodb.upsert_item({"종목코드": code},{"$set": save_item},'TodayStrongThema','outTimeUpDownRate')
            except StaleElementReferenceException:
                print("하락 row click StaleElementReferenceException")
            except NoSuchElementException:
                print("하락 row click NoSuchElementException")
            except ValueError:
                print("하락 row click ValueError")
        if breakVaiable == 1:
            break
        
if __name__ == '__main__':

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
        
    selfBot.send("시간외 단일가 수집 시작 ")

    # codeList DB 에서 전체 종목명과 코드를 추출한다. 
    code_list = []
    code_dict_data = mongodb.find_items({},"TodayStrongThema", "codeList")
    for item in code_dict_data:
        code_list.append(item["종목코드"])
    
    # code_list 에 없는 outTimeUpDownRate 의 종목들을 삭제한다.
    out_time_all_list = []
    out_time_all_mongo_data_len = 0
    out_time_all_mongo_data = mongodb.find_items({},"TodayStrongThema", "outTimeUpDownRate")
    if out_time_all_mongo_data is None:
        pass
    else:  
        for item in out_time_all_mongo_data:
            out_time_all_list.append(item['종목코드'])
        out_time_all_mongo_data_len = len(out_time_all_list)

    delete_item_list = list(set(out_time_all_list) - set(code_list))
    # selfBot.send("삭제할 종목코드 : %s" % delete_item_list)
    
    insert_item_list = list(set(code_list) - set(out_time_all_list))
    # outTimeUpDownRate 에 없는 code_list 종목들을 추가한다. 
    if insert_item_list != []:
        for item in insert_item_list:
            temp_code_nm_mongo = mongodb.find_item({"종목코드": item},"TodayStrongThema", "codeList")
            
            add_item = {
                "종목코드": item,
                "수집날짜": collect_time,
                "시간외단일가": 0,
                "종목명": temp_code_nm_mongo["종목명"]
            }
            mongodb.insert_item(add_item, "TodayStrongThema", "outTimeUpDownRate") 
    else:
        pass
    
    for item in delete_item_list:
        mongodb.delete_items({"종목코드":item},"TodayStrongThema", "outTimeUpDownRate")

    before_items_list = []
    before_items_len = 0
    # 시간외단일가 수집 전 수집이 완료된 데이터를 검색
    before_items = mongodb.find_items({"수집날짜":collect_time},'TodayStrongThema','outTimeUpDownRate')
    if before_items is None:
        before_items_len = 0
    else:  
        for item in before_items:
            before_items_list.append(item['종목코드'])
        before_items_len = len(before_items_list)
    selfBot.send("수집 전 수집완료 데이터 수 : %s " % before_items_len)
    
    if before_items_len != out_time_all_mongo_data_len:
        kospiUrl = 'https://finance.daum.net/domestic/after_hours?market=KOSPI'
        kosdaqUrl = 'https://finance.daum.net/domestic/after_hours?market=KOSDAQ'
        
        getStockInfo(kospiUrl)
        getStockInfo(kosdaqUrl)
        selfBot.send("시간외 단일가 웹 크롤링 완료")
    else:
        selfBot.send("시간외 단일가 업데이트 할 종목 없음")
    
    # outTimeUpDownRate 에 있는 종목중에서 웹 크롤링이 되지 않은 종목의 날짜를 업데이트해서 전체 수집을 완료시킨다.
    not_crawl_items_list = []
    # 시간외단일가 수집일이 다른 데이터를 검색
    not_crawl_items = mongodb.find_items({"수집날짜":{'$ne':collect_time}},'TodayStrongThema','outTimeUpDownRate')
    if not_crawl_items is None:
        pass
    else:
        for item in not_crawl_items:
            not_crawl_items_list.append(item['종목코드'])
    
    # selfBot.send("시간외 수집일이 다른 종목 : %s " % not_crawl_items_list)
    
    # outTimeUpDownRate 에 있는 종목중에서 웹 크롤링이 되지 않은 종목의 날짜, 시간외단일가 를 업데이트해서 전체 수집을 완료시킨다.
    for i in not_crawl_items_list:
        save_item = {
            "시간외단일가":0,
            "수집날짜":collect_time
        }
        mongodb.update_items({"종목코드": i},{"$set":save_item},'TodayStrongThema','outTimeUpDownRate')

    after_items_list = []
    # 시간외단일가 수집이 완료된 데이터를 검색
    after_items = mongodb.find_items({"수집날짜":collect_time},'TodayStrongThema','outTimeUpDownRate')
    if after_items is None:
        after_items_len = 0
    else:
        for item in after_items:
            after_items_list.append(item['종목코드'])
        after_items_len = len(after_items_list)
    
    collect_item_list = list(set(after_items_list) - set(before_items_list))

    selfBot.send("전체 %s 개 중 %s개 종목 업데이트\n 시간외 단일가 수집 완료" % (len(code_list), len(collect_item_list)))
    
    # +2 % 이상인 종목들에 대한 기사검색하여 발송
    tempOutTimeDataList = []
    tempOutTimeData = mongodb.find_items({"$and":[{"수집날짜": collect_time},{"시간외단일가": {'$gte': 2}}]}, "TodayStrongThema", "outTimeUpDownRate")

    if tempOutTimeData is None:
        selfBot.send("시간외 특이 종목 없음")
    else:
        for item in tempOutTimeData:
            tempOutTimeDataList.append(item["종목명"])
    # 테마 업데이트 여부 체크
    minusItemList = []
    minusItem = mongodb.find_items({"저장시간": {'$gte': start, '$lt' : end}}, "TodayStrongThema", "themaUpdate")
    if minusItem is None:
        print("minusItem is None")
    else:
        for item in minusItem:
            # 이미 업데이트 된 테마 리스트
            minusItemList.append(item["종목명"])
        
    need_update_thema_list = list(set(tempOutTimeDataList) - set(minusItemList))
    
    if len(need_update_thema_list) > 0:
        selfBot.send("테마입력필요 \n %s " % (need_update_thema_list))
        # 뉴스를 보낸다.
        for code_nm in need_update_thema_list:
            QTest.qWait(300)
            crawlRst = newsNLP.crawlNews(code_nm)
            if crawlRst == "pass":
                pass
            else:
                selfBot.send(crawlRst)
        selfBot.send("시간외 특징주 뉴스 검색 완료")
    else:
        selfBot.send("시간외 특징주 뉴스 없음")
    selfBot.send("시간외 단일가 수집 완료")
    driver.quit()