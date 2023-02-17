from telegram import Bot
from common.importConfig import *
import time
from util.MongoDBHandler import MongoDBHandler
from datetime import datetime
from telegram import ParseMode

# Push 용
from PyQt5.QtWidgets import *

class TTTelegram3():
    
    importConfig = importConfig()
    # 프로퍼티 파일 읽기
    mongodb = MongoDBHandler()
    token = importConfig.select_section("TELEGRAM")["token3"]
    chat_id = importConfig.select_section("TELEGRAM")["chat_id"]
    bot = Bot(token)
    
    def send(self, msg):

        parts = []
        text = str(msg)

        if len(text) <= 4096:
            self.bot.sendMessage(self.chat_id, text, timeout=30)
        else:
            parts = []
            while len(text) > 0:
                if len(text) > 4080: # '(Continuing...)\n'이 16자임을 고려하여 4096-16=4080을 했습니다.
                    part = text[:4080]
                    first_lnbr = part.rfind('\n')
                    if first_lnbr != -1: # 가능하면 개행문자를 기준으로 자릅니다.
                        parts.append(part[:first_lnbr])
                        text = text[first_lnbr:]
                    else:
                        parts.append(part)
                        text = text[4080:]
                else:
                    parts.append(text)
                    break
            for idx, part in enumerate(parts):
                if idx == 0:
                    self.bot.send_message(self.chat_id, text = part)
                else: # 두번째 메시지부터 '(Continuing...)\n'을 앞에 붙여줍니다.
                    self.bot.send_message(self.chat_id, text = '(Continuing...)\n')
                
    def sendToHTML(self, msg):
        parts = []
        text = str(msg)

        if len(text) <= 4096:
            self.bot.sendMessage(self.chat_id, text, timeout=30, parse_mode=ParseMode.HTML)
        else:
            parts = []
            while len(text) > 0:
                if len(text) > 4080: # '(Continuing...)\n'이 16자임을 고려하여 4096-16=4080을 했습니다.
                    part = text[:4080]
                    first_lnbr = part.rfind('\n')
                    if first_lnbr != -1: # 가능하면 개행문자를 기준으로 자릅니다.
                        parts.append(part[:first_lnbr])
                        text = text[first_lnbr:]
                    else:
                        parts.append(part)
                        text = text[4080:]
                else:
                    parts.append(text)
                    break
            for idx, part in enumerate(parts):
                if idx == 0:
                    self.bot.send_message(self.chat_id, text = part, parse_mode=ParseMode.HTML)      
                else: # 두번째 메시지부터 '(Continuing...)\n'을 앞에 붙여줍니다.
                    self.bot.send_message(self.chat_id, text = '(Continuing...)\n' + part, parse_mode=ParseMode.HTML)

    def sendToMARKDOWN(self, msg):
        parts = []
        text = str(msg)

        if len(text) <= 4096:
            self.bot.sendMessage(self.chat_id, text, timeout=30, parse_mode=ParseMode.MARKDOWN_V2)
        else:
            parts = []
            while len(text) > 0:
                if len(text) > 4080: # '(Continuing...)\n'이 16자임을 고려하여 4096-16=4080을 했습니다.
                    part = text[:4080]
                    first_lnbr = part.rfind('\n')
                    if first_lnbr != -1: # 가능하면 개행문자를 기준으로 자릅니다.
                        parts.append(part[:first_lnbr])
                        text = text[first_lnbr:]
                    else:
                        parts.append(part)
                        text = text[4080:]
                else:
                    parts.append(text)
                    break
            for idx, part in enumerate(parts):
                if idx == 0:
                    self.bot.send_message(self.chat_id, text = part, parse_mode=ParseMode.MARKDOWN_V2)    
                else: # 두번째 메시지부터 '(Continuing...)\n'을 앞에 붙여줍니다.
                    self.bot.send_message(self.chat_id, text = '(Continuing...)\n' + part, parse_mode=ParseMode.MARKDOWN_V2)
    
if __name__ == '__main__':
    print("Telegram class")