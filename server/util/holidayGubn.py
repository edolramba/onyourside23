from datetime import datetime
import sys
sys.path.append("C:\\Dev\\onyourside22\\server")
sys.path.append("C:\\Dev\\onyourside22\\server\\test")
sys.path.append("C:\\Dev\\onyourside22\\server\\util")
from util.MongoDBHandler import MongoDBHandler

mongodb = MongoDBHandler()

def holidayGubn(date):
    holidays_list = []
    holidays_mongo = mongodb.find_items({}, 'TodayStrongThema', 'holiday')
    for i in holidays_mongo:
        holidays_list.append(i["휴장일"])
    
    datetime_date = datetime.strptime(date, '%Y-%m-%d')

    dateDict = {0: '월요일', 1:'화요일', 2:'수요일', 3:'목요일', 4:'금요일', 5:'토요일', 6:'일요일'}
    
    # print(dateDict[datetime_date.weekday()])
    if dateDict[datetime_date.weekday()] in ("토요일","일요일") or date in holidays_list:
        return 0
    else:
        return 1
    
if __name__ == "__main__":
    date = '2022-06-07'
    # print(holidayGubn(date))