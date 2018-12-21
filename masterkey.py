import requests
from bs4 import BeautifulSoup as bs

def master_key_info(cd):
    url = 'http://www.master-key.co.kr/booking/booking_list_new'
    params = {
        'data' :'2018-12-22',
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
        theme_list.append(title)
        for col in li.select('.col'):
            info = '{} - {}'.format(col.select_one('.time').text, col.select_one('.state').text)
            theme = {
                
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

# 사용자로부터 '마스터키 ***'점 이라는 메시지를 받으면

# 해당 지점에 대한 오늘의 정보를 요청하고(크롤링)

# 메시지(예약정보)를 보내준다.
print(master_key_info(21))
for cafe in master_key_list():
    print('{} : {}'.format(cafe['title'], cafe['link'].split('=')[1]))
