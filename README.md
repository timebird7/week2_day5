# webhook

봇에 메세지 보내면 c9서버에 alert를 줌

텔레그램 서버에는 return 뒤에 있는 200만 보냄

추가적으로 사용자에게 메세지를 전달하기 위해 sendMessage 사용



## 배열을 문자열 하나로

```python
l = ['abc', 'def', 'ghi']
''.join(l)

#''사이에 쓴 글자가 합쳐지는 문자열 사이에 추가됨
```







## 방탈출 챗봇

```python
from flask import Flask, request
import requests
import json
import time
import os
from bs4 import BeautifulSoup as bs
from datetime import date

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_URL = "https://api.hphk.io/telegram"
CAFE_LIST = {
    '전체' : -1,
    '부천점' : 15,
    '안양점' : 13,
    '대구동성로2호점' : 14,
    '대구동성로점' : 9,
    '궁동직영점' : 1,
    '은행직영점' : 2,
    '부산서면점' : 19,
    '홍대상수점' : 20,
    '강남점' : 16,
    '건대점' : 10,
    '홍대점' : 11,
    '신촌점' : 6,
    '잠실점' : 21,
    '부평점' : 17,
    '익산점' : 12,
    '전주고사점' : 8,
    '천안신부점' : 18,
    '천안점' : 3,
    '천안두정점' : 7,
    '청주점' : 4
}

cafe_code = {
    '강남1호점': 3,
    '홍대1호점': 1,
    '부산 서면점': 5,
    '인천 부평점': 4,
    '강남2호점': 11,
    '홍대2호점': 10
}


today = date.today()
def master_key_info(cd):
    url = 'http://www.master-key.co.kr/booking/booking_list_new'
    params = {
        'data' :today,
        'store':cd,
        'room' :''
    }

    response = requests.post(url, params).text
    document = bs(response, 'html.parser')
    ul= document.select('.reserve .escape_view')
    theme_list=[]
    for li in ul:
        title = li.select('p')[0].text
        info = ''
        for col in li.select('.col'):
            info = '{} - {}'.format(col.select_one('.time').text, col.select_one('.state').text)
            theme = {
                'title': title,
                'info': info
            }
        
            theme_list.append(theme)
    return theme_list





def master_key_list():
    url = 'http://www.master-key.co.kr/home/office'
    response = requests.get(url).text
    soup = bs(response, 'html.parser')


    stores=[]
    li = soup.select('.escape_view')

    for item in li:
        title = item.select_one('.escape_text p').text
        if title.endswith('NEW'):
            title = title[:-3]
        store = {
        'title' :title,
        'tel' :item.select('.escape_text dd')[1].text,
        'address' :item.select_one('.escape_text dd').text,
        'link' :'http://www.master-key.co.kr' + item.select_one('a')['href']
        }
        stores.append(store)

    return stores
    
    
def get_total_info():
    url = 'https://www.seoul-escape.com/reservation/change_date/'
    params = {
        'current_date': '2018/12/21'
    }

    response = requests.get(url, params = params).text
    document = json.loads(response)
    total = {}
    game_room_list = document['gameRoomList']
    for cafe in cafe_code:
        total[cafe] = []
        for room in game_room_list:
            if(cafe_code[cafe] == room["branch_id"]):
                total[cafe].append({'title': room['room_name'], 'info':[]})
            

    book_list = document['bookList']

    for cafe in total:
        print(cafe)
        for book in book_list:
            if(cafe == book['branch']):
                for theme in total[cafe]:
                    if(theme['title'] == book['room']):
                        if(book['booked']):
                            booked = '예약완료'
                        else:
                            booked = '예약가능'
                        theme['info'].append('{} - {}'.format(book['hour'], booked))
                    
    return total                    

def seoul_escape_list():
    
    total = get_total_info()
    return total.keys()
    
def seoul_escape_info(cd):
    total = get_total_info()
    cafe = total[cd]
    tmp = []
    for theme in cafe:
        tmp.append('{}\n {}'.format(theme['title'], '\n'.join(theme['info'])))
        
    return tmp    
    
@app.route('/{}'.format(os.getenv('TELEGRAM_TOKEN')), methods=['POST'])
def telegram():
    #텔레그램으로부터 요청이 들어올 경우, 해당 요청을 처리하는 코드
    url = 'https://api.hphk.io/telegram/bot{}/getUpdates'.format(TELEGRAM_TOKEN)
    req = request.get_json()
    chat_id = req["message"]["from"]["id"]
    txt = req["message"]["text"]
    url = 'https://api.hphk.io/telegram/bot{}/sendMessage'.format(TELEGRAM_TOKEN)
    if txt.startswith('마스터키'):
        cafe_name = txt.split(' ')[1]
        cd = CAFE_LIST[cafe_name]
        if cd > 0:
            data = master_key_info(cd)
        else:
            data = master_key_list()
        
        msg = []
        for d in data:
            msg.append('\n'.join(d.values()))
        msg = '\n'.join(msg)
    elif txt.startswith('서이룸'):
        
        cafe_name = txt.split(' ')
        
        if(len(cafe_name) > 2):
            cafe_name = ' '.join(cafe_name[1:3])
        else:
            cafe_name = cafe_name[-1]
        if(cafe_name == '전체'):
            data = seoul_escape_list()
        else:
            data = seoul_escape_info(cafe_name)
        msg = []
        for d in data:
            msg.append(d)
        msg = '\n'.join(msg)
    
    else:
        msg = '등록되지 않은 지점입니다.'
    requests.get(url, params = {"chat_id": chat_id, "text": msg})
    
    
    return '', 200

@app.route('/set_webhook')
def set_webhook():
    url = TELEGRAM_URL + '/bot' + TELEGRAM_TOKEN + '/setWebhook'
    params = {
        'url' : 'https://ssafy-timebird7.c9users.io/{}'.format(TELEGRAM_TOKEN)
    }
    
    response = requests.get(url, params = params).text   
    
    
    print(response)
    
    
    return response
    
```

