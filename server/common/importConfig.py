import configparser as parser

# 프로퍼티 파일 읽기
class importConfig:
    
    properties = parser.ConfigParser()
    properties.read('C:\Dev\onyourside22\server\config\config.ini')
    
    ## 반환에 사용할 변수들 ##
    token = ""
    token2 = ""
    token3 = ""
    chat_id = ""
    self_token = ""
    self_chat_id = ""
    host = ""
    port = ""
    ## section 에 넣은 값에 따라 config 파일의 section 을 읽는다.
    def select_section(self, section):
        
        if(section == "TELEGRAM"):
            self.token=self.properties[section]['token']
            self.token2=self.properties[section]['token2']
            self.token3=self.properties[section]['token3']
            self.self_token=self.properties[section]['self_token']
            self.chat_id=self.properties[section]['chat_id']
            self.self_chat_id=self.properties[section]['self_chat_id']
            return {"token": self.token, "token2": self.token2, "token3": self.token3, "self_token": self.self_token, "chat_id": self.chat_id, "self_chat_id": self.self_chat_id}
        
        elif(section == "MONGODB"):
            self.host=self.properties[section]['host']
            self.port=self.properties[section]['port']
            return {"host": self.host, "port": self.port}
            
        else:
            print("not yet setting section")