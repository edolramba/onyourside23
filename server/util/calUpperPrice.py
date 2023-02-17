import sys
sys.path.append("C:\\Dev\\onyourside22\\server")
sys.path.append("C:\\Dev\\onyourside22\\server\\test")
sys.path.append("C:\\Dev\\onyourside22\\server\\util")

from PyQt5.QtTest import *

def calUpperPrice(price, market):
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
            pass
        
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
        pass
    
    return quote

        
if __name__ == '__main__':
    
    for i in [
        ['아스타', 5570, -5.57, 'KOSPI'],
        ['카카오', 82900, -2.77, 'KOSPI']
    ]:
        
        b = calUpperPrice(i[1], i[3])
        print(f'{i[0]}, 상한가 {b:,}')
