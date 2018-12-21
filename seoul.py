import requests
import json


url = 'https://www.seoul-escape.com/reservation/change_date/'
params = {
    'current_date': '2018/12/21'
}

response = requests.get(url, params = params).text
document = json.loads(response)

cafe_code = {
    '강남1호점': 3,
    '홍대1호점': 1,
    '부산 서면점': 5,
    '인천 부평점': 4,
    '강남2호점': 11,
    '홍대2호점': 10
}
def get_total_info():
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
    
print('\n'.join(seoul_escape_info("홍대1호점")))
        