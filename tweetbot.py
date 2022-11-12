#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import tweepy
import time
import random
import re
import gspread
import schedule
import datetime

from tweepy.auth import OAuthHandler

API_KEY = "-"
API_KEY_SECRET = "-"
ACCESS_KEY = "-"
ACCESS_SECRET = "-"

gc = gspread.service_account()
sh = gc.open_by_url('-')

FILE_NAME = 'last_seen_id.txt'

def refresh_auth():
    auth  = OAuthHandler(API_KEY, API_KEY_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    api = tweepy.API(auth, wait_on_rate_limit=True)
    return api

def retrieve_last_seen_id(file_name):
    f_read = open(file_name, 'r')
    last_seen_id = int(f_read.read().strip())
    f_read.close()
    return last_seen_id

def store_last_seen_id(last_seen_id, file_name):
    f_write = open(file_name, 'w')
    f_write.write(str(last_seen_id))
    f_write.close()
    return

def printtime2():
    check2 = "False"
    for i in range(2, 16):
        print(worksheet.cell(i, 10), end=' ')
        worksheet.update_cell(i, 10, check2)
        print(">",worksheet.cell(i, 10), end=' ')


def reply_to_tweets():
    print('트윗 확인 중...', flush=True)
    api = refresh_auth()
    last_seen_id = retrieve_last_seen_id(FILE_NAME)
    mentions = api.mentions_timeline(last_seen_id,tweet_mode='extended')
    for mention in reversed(mentions):
        print(str(mention.id) + ' - ' + mention.full_text, flush=True)
        last_seen_id = mention.id
        store_last_seen_id(last_seen_id, FILE_NAME)


        worksheet = sh.get_worksheet(0)
        cell = worksheet.find("아이디")

        print("%s행 %s열에서 찾았습니다." % (cell.row, cell.col))


        if '[출석]' in mention.full_text.lower():
            worksheet = sh.get_worksheet(0) #맨 첫 번째 시트 내 값 가져오기. 괄호 내 숫자를 1로 바꾸면 2번째 시트, 2로 바꾸면 3번째 시트가 가져와짐
            cell = worksheet.find(mention.user.screen_name)
            print("%s행 %s열에서 찾았습니다." % (cell.row, cell.col))
            check1 = "True"
            check2 = "FALSE"

            if str(worksheet.cell(cell.row, 10).value) == "FALSE" and datetime.datetime.today().hour < 13 and datetime.datetime.today().hour >= 1 :
                gold = int(worksheet.cell(cell.row,5).value)
                worksheet.update_cell(cell.row, 5, gold + 1) #보유중인 골드-금액
                worksheet.update_cell(cell.row, 10, check1)
                worksheet.update_cell(cell.row, 11, check2)
                worksheet.update_cell(cell.row, 12, 0)
                print(">",worksheet.cell(cell.row, 10).value, end=' ')
                new_status = api.update_status("@"+ mention.user.screen_name + "출석이 확인되었습니다." + "\n [" + time.strftime("%Y-%m-%d %H:%M:%S") + "]", mention.id)
            elif str(worksheet.cell(cell.row, 10).value) == "TRUE" and datetime.datetime.today().hour < 13 and datetime.datetime.today().hour >= 1:
                worksheet.update_cell(cell.row, 10, check1)
                print(">",worksheet.cell(cell.row, 10).value, end=' ')
                new_status = api.update_status("@"+ mention.user.screen_name + "이미 출석처리 되었습니다. 내일 다시 시도해주세요." + "\n [" + time.strftime("%Y-%m-%d %H:%M:%S") + "]", mention.id)
            else:
                new_status = api.update_status("@"+ mention.user.screen_name + "출석이 불가한 시간입니다. 출석은 AM 10:00 ~ PM 10:00 사이에 해주세요." + "\n [" + time.strftime("%Y-%m-%d %H:%M:%S") + "]", mention.id)

        elif '[오늘의 식사]' in mention.full_text.lower():
            worksheet = sh.get_worksheet(0) #맨 첫 번째 시트 내 값 가져오기. 괄호 내 숫자를 1로 바꾸면 2번째 시트, 2로 바꾸면 3번째 시트가 가져와짐
            user = api.get_user(mention.user.screen_name)
            name = user.name
            cell = worksheet.find(mention.user.screen_name)
            worksheet1 = sh.get_worksheet(8) #운세시트 (두번째 시트)
            cok = str(worksheet1.cell(random.randint(1, 40), 3).value) #늘어난 만큼 56부분 수정 (열 숫자보고 그대로!)
            print("%s행 %s열에서 찾았습니다." % (cell.row, cell.col))
            check1 = "True"

            if str(worksheet.cell(cell.row, 10).value) == "TRUE" and str(worksheet.cell(cell.row, 11).value) == "FALSE" :
                worksheet.update_cell(cell.row, 11, check1)
                print(">",worksheet.cell(cell.row, 11).value, end=' ')
                new_status = api.update_status("@"+ mention.user.screen_name + " 오늘의 식사는...\n" + cok  +"입니다.\n" +"\n [" + time.strftime("%Y-%m-%d %H:%M:%S") + "]", mention.id)
            elif str(worksheet.cell(cell.row, 10).value) == "TRUE" and str(worksheet.cell(cell.row, 11).value) == "TRUE":
                print(">",worksheet.cell(cell.row, 11).value, end=' ')
                new_status = api.update_status("@"+ mention.user.screen_name + "오늘은 이미 식사를 마쳤습니다. 과식은 금물. 내일 다시 시도해주세요." + "\n [" + time.strftime("%Y-%m-%d %H:%M:%S") + "]", mention.id)
            elif str(worksheet.cell(cell.row, 10).value) == "FALSE" and str(worksheet.cell(cell.row, 11).value) == "TRUE" :
                print(">",worksheet.cell(cell.row, 11).value, end=' ')
                new_status = api.update_status("@"+ mention.user.screen_name + "출석을 아직 하지 않으셨습니다. 출석을 한 후 시도해주세요." + "\n [" + time.strftime("%Y-%m-%d %H:%M:%S") + "]", mention.id)

        elif '[포춘쿠키]' in mention.full_text.lower():
            worksheet0 = sh.get_worksheet(0) #기본시트(첫번째 시트)
            cell0 = worksheet0.find(mention.user.screen_name)
            worksheet1 = sh.get_worksheet(2) #운세시트 (두번째 시트)
            gold = int(worksheet0.cell(cell0.row,5).value)
            user = api.get_user(mention.user.screen_name)
            name = user.name

            if gold >= 1: #보유 금액이 아이템 가격보다 큰 경우
                gold = int(worksheet0.cell(cell0.row,5).value)
                worksheet0.update_cell(cell0.row, 5, gold-1) #보유중인 골드-금액
                str(print("구매완료. 남은 갈레온:",worksheet0.cell(cell0.row, 5).value, end=' ')).format(user.name)
                cok = str(worksheet1.cell(random.randint(1, 56), 3).value)
                new_status = api.update_status("@"+ mention.user.screen_name + " 포춘 쿠키 안에 든 내용은...\n" + cok  +"\n" + "\n보유 갈레온: " + (worksheet0.cell(cell0.row,5).value).format(user.name) +"\n [" + time.strftime("%Y-%m-%d %H:%M:%S") + "]", mention.id)
            elif gold < 1: # 보유 금액이 아이템 가격보다 낮은 경우
                gold = int(worksheet0.cell(cell0.row,5).value)
                print("보유 갈레온:",gold,"\n구매실패")
                new_status = api.update_status("@"+ mention.user.screen_name + " [구매 실패. 갈레온이 부족합니다.] " + "\n보유 갈레온: " + (worksheet0.cell(cell0.row,5).value).format(user.name) + " 갈레온" + "\n [" + time.strftime("%Y-%m-%d %H:%M:%S") + "]", mention.id)

        elif '[랜덤 박스]' in mention.full_text.lower():
            worksheet0 = sh.get_worksheet(0) #기본시트(첫번째 시트)
            cell0 = worksheet0.find(mention.user.screen_name)
            worksheet1 = sh.get_worksheet(3) #운세시트 (두번째 시트)
            gold = int(worksheet0.cell(cell0.row,5).value)
            user = api.get_user(mention.user.screen_name)
            name = user.name

            if gold >= 3: #보유 금액이 아이템 가격보다 큰 경우
                r_num = random.randint(2, 40)  #늘어난 만큼 33부분 수정 (열 숫자보고 그대로!)
                gold = int(worksheet0.cell(cell0.row,5).value)
                worksheet0.update_cell(cell0.row, 5, gold - 3) #보유중인 골드-금액 / 금액 수정하고 싶을 시 3과 elif if 숫자 수정
                str(print("구매완료. 보유 갈레온:",worksheet0.cell(cell0.row, 5).value, end=' ')).format(user.name)
                cok = "상자에서 나온 물건은…!!! " + str(worksheet1.cell(r_num, 3).value) + "!"
                src = str(worksheet1.cell(r_num, 4).value)
                img = str(worksheet1.cell(r_num, 5).value)

                new_status = api.update_status("@"+ mention.user.screen_name + " " + cok + "\n" + src + "\n\n남은 갈레온: " + (worksheet0.cell(cell0.row,5).value).format(user.name) +"\n\n [" + time.strftime("%Y-%m-%d %H:%M:%S") + "] " + img, mention.id)
            elif gold < 3: # 보유 금액이 아이템 가격보다 낮은 경우
                gold = int(worksheet0.cell(cell0.row,5).value)
                print("보유금액:",gold,"\n구매실패")
                new_status = api.update_status("@"+ mention.user.screen_name + " [구매 실패. 갈레온이 부족합니다.] " + "\n보유 갈레온 : " + (worksheet0.cell(cell0.row,5).value).format(user.name) + " 갈레온" + "\n [" + time.strftime("%Y-%m-%d %H:%M:%S") + "]", mention.id)

        elif '[간식 상자]' in mention.full_text.lower():
            worksheet0 = sh.get_worksheet(0) #기본시트(첫번째 시트)
            cell0 = worksheet0.find(mention.user.screen_name)
            worksheet1 = sh.get_worksheet(4) #간식시트 (다섯번째 시트)
            gold = int(worksheet0.cell(cell0.row,5).value)
            user = api.get_user(mention.user.screen_name)
            name = user.name

            if gold >= 1: #보유 금액이 아이템 가격보다 큰 경우
                r_num = random.randint(1, 10) #행의 시작번호부터 끝을 입력하면 됨
                gold = int(worksheet0.cell(cell0.row,5).value)
                worksheet0.update_cell(cell0.row, 5, gold - 1) #보유중인 골드-금액 / 금액을 수정하고 싶으면 if 와 elif숫자 수정 그리고 gold - 여기에 들어가는 숫자 수
                str(print("구매완료. 남은 갈레온:",worksheet0.cell(cell0.row, 5).value, end=' ')).format(user.name)
                cok = "[" + str(worksheet1.cell(r_num, 3).value) + "]을(를) 획득했습니다."

                new_status = api.update_status("@"+ mention.user.screen_name + " " + cok  + "\n 남은 갈레온: " + (worksheet0.cell(cell0.row,5).value).format(user.name) +"\n [" + time.strftime("%Y-%m-%d %H:%M:%S") + "] ", mention.id)
            elif gold < 1: # 보유 금액이 아이템 가격보다 낮은 경우
                gold = int(worksheet0.cell(cell0.row,5).value)
                print("남은 갈레온:",gold,"\n구매실패")
                new_status = api.update_status("@"+ mention.user.screen_name + " [구매 실패. 갈레온이 부족합니다.] " + "\n보유 갈레온: " + (worksheet0.cell(cell0.row,5).value).format(user.name) + " 갈레온" + "\n [" + time.strftime("%Y-%m-%d %H:%M:%S") + "]", mention.id)

        elif '[갈레온 주머니]' in mention.full_text.lower():
            worksheet0 = sh.get_worksheet(0) #기본시트(첫번째 시트)
            cell0 = worksheet0.find(mention.user.screen_name)
            gold = int(worksheet0.cell(cell0.row,5).value)
            cnt_g = int(worksheet0.cell(cell0.row,12).value)
            user = api.get_user(mention.user.screen_name)
            name = user.name

            if cnt_g > 2: #갈레온 주머니 하고싶은 횟수 -1 한 값을 숫자에 넣어주기
                str(print("구매실패. 횟수 초과 남은 갈레온: ",worksheet0.cell(cell0.row, 5).value, end=' ')).format(user.name)
                new_status = api.update_status("@"+ mention.user.screen_name + " 오늘은 더이상 갈레온 주머니를 뽑을 수 없습니다. 내일 출석 후 이용해주세요." + "\n [" + time.strftime("%Y-%m-%d %H:%M:%S") + "]", mention.id)
            elif gold >= 5 and cnt_g <= 2: #보유 금액이 아이템 가격보다 큰 경우 / #갈레온 주머니 하고싶은 횟수 -1 한 값을 숫자에 넣어주기
                r_num = random.randint(0, 4)
                gold_rand = ["0", "3", "5", "7", "10"]
                gold = int(worksheet0.cell(cell0.row,5).value)
                worksheet0.update_cell(cell0.row, 5, gold - 5 + int(gold_rand[r_num])) #보유중인 골드-금액
                worksheet0.update_cell(cell0.row, 12, cnt_g + 1)
                str(print("구매완료. 남은 갈레온:",worksheet0.cell(cell0.row, 5).value, end=' ')).format(user.name)
                new_status = api.update_status("@"+ mention.user.screen_name + " 갈레온 주머니에는... [" + gold_rand[r_num]  + "갈레온]이 들어있었습니다.\n 남은 갈레온: " + (worksheet0.cell(cell0.row,5).value).format(user.name) + " 갈레온" + "\n [" + time.strftime("%Y-%m-%d %H:%M:%S") + "]", mention.id)
            elif gold < 5: # 보유 금액이 아이템 가격보다 낮은 경우
                gold = int(worksheet0.cell(cell0.row,5).value)
                print("보유 갈레온:",gold,"\n구매실패")
                new_status = api.update_status("@"+ mention.user.screen_name + " [구매 실패. 갈레온이 부족합니다.] " + "\n보유 갈레온: " + (worksheet0.cell(cell0.row,5).value).format(user.name) + " 갈레온" + "\n [" + time.strftime("%Y-%m-%d %H:%M:%S") + "]", mention.id)

        elif '[소문]' in mention.full_text.lower():
            worksheet0 = sh.get_worksheet(6) #소문(일곱번째 시트)
            user = api.get_user(mention.user.screen_name)
            name = user.name
            voice = ["남학생들이 수런거리는 소리", "여학생들의 웃음기 담긴 목소리", "성별을 알 수 없는 이의 수상한 목소리", "교수님들끼리 수군거리는 소리"]

            cok = str(worksheet0.cell(random.randint(1, 20), 3).value)   #늘어난 만큼 15부분 수정 (열 숫자보고 그대로!)
            new_status = api.update_status("@"+ mention.user.screen_name + " 호그와트 어딘가에서 " + voice[random.randint(0, 3)]+ "가 들려옵니다...\n" + cok + "\n [" + time.strftime("%Y-%m-%d %H:%M:%S") + "]", mention.id)
        				#아이템 구매
        elif '[사용' in mention.full_text.lower():

            object = ['보급 상자', '상급 보급 상자'] # 아이템 전부 넣기 입력 방식은 '아이템 이름' 그리고 ,로 구분
            user = api.get_user(mention.user.screen_name)
            name = user.name

            worksheet0 = sh.get_worksheet(9) #기본시트(첫번째 시트)
            cell0 = worksheet0.find(mention.user.screen_name)
            worksheet1 = sh.get_worksheet(1) #상점시트 (세번째 시트)
            worksheet2 = sh.get_worksheet(7) #기본시트(첫번째 시트)
            r_num = random.randint(1,10)

            count = str(worksheet0.cell(cell0.row, 9).value)
            item = count.split(",")

            for obj in object:
                if obj in mention.full_text.lower():
                    if '상급 보급 상자' in item:
                        cell1 = worksheet1.find('상급 보급 상자')
                        print("%s행 %s열에서 찾았습니다." % (cell1.row, cell1.col))
                        print(cell1)
                        src = str(worksheet1.cell(cell1.row, 4).value) #상점시트 - 아이템 설
                        item.remove('상급 보급 상자')
                        item_list = ','.join(item)
                        randitem = worksheet2.cell(r_num, 3).value
                        #인벤토리 시트에 제거
                        cell4 = worksheet.find(mention.user.screen_name)
                        worksheet0.update_cell(cell4.row, 9, item_list)
                        print("%s행 %s열에서 찾았습니다." % (cell4.row, 9))
                        new_status = api.update_status("@"+ mention.user.screen_name + " 획득한 아이템: " + randitem + "입니다. 정산 요청 @Summer_occult \n [" + time.strftime("%Y-%m-%d %H:%M:%S") + "]", mention.id)
                    elif '보급 상자' in item:
                        cell1 = worksheet1.find('보급 상자')
                        print("%s행 %s열에서 찾았습니다." % (cell1.row, cell1.col))
                        print(cell1)
                        src = str(worksheet1.cell(cell1.row, 4).value) #상점시트 - 아이템 설
                        item.remove('보급 상자')
                        item_list = ','.join(item)
                        randitem = worksheet2.cell(r_num, 3).value
                        #인벤토리 시트에 제거
                        cell4 = worksheet.find(mention.user.screen_name)
                        worksheet0.update_cell(cell4.row, 9, item_list)
                        print("%s행 %s열에서 찾았습니다." % (cell4.row, 9))
                        new_status = api.update_status("@"+ mention.user.screen_name + " 획득한 아이템: " + randitem + "입니다. 정산 요청 @Summer_occult \n [" + time.strftime("%Y-%m-%d %H:%M:%S") + "]", mention.id)
                    else:
                        new_status = api.update_status("@"+ mention.user.screen_name + " [" + obj +"이(는) 소지하고 있는 아이템이 아닙니다. 다시 한번 확인 후 사용해주시길 바랍니다."+"\n [" + time.strftime("%Y-%m-%d %H:%M:%S") + "]", mention.id)

        elif '[구매' in mention.full_text.lower():

            object = ['사탕', '오르골', '출석 도장'] # 아이템 전부 넣기 입력 방식은 '아이템 이름' 그리고 ,로 구분
            user = api.get_user(mention.user.screen_name)
            name = user.name

            worksheet0 = sh.get_worksheet(0) #기본시트(첫번째 시트)
            cell0 = worksheet0.find(mention.user.screen_name)
            worksheet1 = sh.get_worksheet(1) #상점시트 (세번째 시트)

            for obj in object:
                if obj in mention.full_text.lower():
                    cell1 = worksheet1.find(obj)
                    print("%s행 %s열에서 찾았습니다." % (cell1.row, cell1.col))
                    print(cell1)
                    delta = int(worksheet1.cell(cell1.row, 3).value) #상점시트 - 아이템 가격
                    str(print(delta))
                    src = str(worksheet1.cell(cell1.row, 4).value) #상점시트 - 아이템 설
                    gold = int(worksheet0.cell(cell0.row,5).value)

                    #인벤토리 시트에 추가
                    cell4 = worksheet.find(mention.user.screen_name)
                    print("%s행 %s열에서 찾았습니다." % (cell4.row, 9))

                    if gold >= delta:
                        count  = ""
                        if(str(worksheet0.cell(cell4.row, 9).value) == None):
                            count = obj #멘션한 아이디가 적힌 행의 3번째 열
                        else:
                            count = str(worksheet0.cell(cell4.row, 9).value) + ", " + obj #멘션한 아이디가 적힌 행의 3번째 열
                        worksheet0.update_cell(cell4.row, 9, count) #멘션한 아이디가 적힌 행의 3번째 열 내용+1


                    if gold >= delta: #보유 금액이 아이템 가격보다 큰 경우
                        gold = int(worksheet0.cell(cell0.row,5).value)
                        worksheet0.update_cell(cell0.row, 5, gold-delta) #보유중인 골드-금액
                        str(print("구매완료. \n남은 갈레온:",worksheet0.cell(cell0.row, 5).value, end=' ')).format(user.name)
                        new_status = api.update_status("@"+ mention.user.screen_name + " " + obj +" 구매가 완료되었습니다.\n남은 갈레온: " + (worksheet0.cell(cell0.row,5).value).format(user.name) + "갈레온\n" + src +"\n [" + time.strftime("%Y-%m-%d %H:%M:%S") + "]", mention.id)


                    elif gold < delta: # 보유 금액이 아이템 가격보다 낮은 경우
                        gold = int(worksheet0.cell(cell0.row,5).value)
                        print("보유금액:",gold,"\n구매실패")
                        new_status = api.update_status("@"+ mention.user.screen_name + " [구매 실패. 보유 금액이 부족합니다.] " + "\n보유 금액 : " + (worksheet0.cell(cell0.row,5).value).format(user.name) + "갈레온" + "\n [" + time.strftime("%Y-%m-%d %H:%M:%S") + "]", mention.id)


        elif '/보급 상자]' in mention.full_text.lower():
            worksheet0 = sh.get_worksheet(7) #소문(일곱번째 시트)
            user = api.get_user(mention.user.screen_name)
            name = user.name

            cok = str(worksheet0.cell(random.randint(1, 10), 3).value)   #늘어난 만큼 15부분 수정 (열 숫자보고 그대로!)
            new_status = api.update_status("@"+ mention.user.screen_name + " 획득한 아이템: " + cok + "입니다. 정산 요청 @Summer_occult \n [" + time.strftime("%Y-%m-%d %H:%M:%S") + "]", mention.id)
        				#아이템 구매


        elif '/상급 보급 상자]' in mention.full_text.lower():
            worksheet0 = sh.get_worksheet(7) #소문(일곱번째 시트)
            user = api.get_user(mention.user.screen_name)
            name = user.name

            cok = str(worksheet0.cell(random.randint(1, 2), 3).value)   #늘어난 만큼 15부분 수정 (열 숫자보고 그대로!)
            new_status = api.update_status("@"+ mention.user.screen_name + " 획득한 아이템: " + cok + "입니다. 정산 요청 @Summer_occult \n [" + time.strftime("%Y-%m-%d %H:%M:%S") + "]", mention.id)
        				#아이템 구매

while True:
    reply_to_tweets()
    time.sleep(40)
