#-*- coding:UTF-8 -*-
from django.shortcuts import render, redirect
from .models import UserMember
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from .models import Friend
from .models import PillList
from .models import PillTake
from .models import PillTime
import hashlib
import hmac
import base64
import time, json
from .sendSMS import SendSMS
from django.db.models import F
from urllib.parse import urlencode, unquote, quote_plus
import xmltodict
from bs4 import BeautifulSoup
from .searchPill import search 
import requests
from django.db import connection
import datetime
# Create your views here.

def pillreminder(pillmaster):
    now = datetime.datetime.now()
    nowTime = now.strftime('%H:%M')
    print(nowTime)
    try:
        nowTime = now.strftime('%H:%M')
        print(nowTime)
        cursor = connection.cursor()
        strSql = "SELECT * FROM PillMe.PillTime as A WHERE (TIME_TO_SEC('"+nowTime+"') - TIME_TO_SEC(EatTime))/60 <= 30 AND PillMaster = '"+pillmaster+"'  AND NOT EXISTS ( SELECT *, DATE_FORMAT(PillTakeTime, '%H:%I'), (TIME_TO_SEC(DATE_FORMAT(PillTakeTime, '%H:%I')) - TIME_TO_SEC(A.EatTime))/60 FROM PillMe.PillTake WHERE DATE_FORMAT(PillTakeTime, '%Y-%m-%d') = DATE_FORMAT(now(), '%Y-%m-%d') AND ModuleNum = A.ModuleNum AND (TIME_TO_SEC(DATE_FORMAT(PillTakeTime, '%H:%I')) - TIME_TO_SEC(A.EatTime))/60 <= 30 AND (TIME_TO_SEC(DATE_FORMAT(PillTakeTime, '%H:%I')) - TIME_TO_SEC(A.EatTime))/60 >= 0) ORDER BY EatTime ASC"
        result = cursor.execute(strSql)
        pillReminder = cursor.fetchall()

        print(pillReminder)
        print(pillReminder[0])
        pillReminder = pillReminder[0]
        connection.commit()
        connection.close()
        print("success!!")

        print(pillReminder[2])
        pillReminder = pillReminder[2]+' - '+pillReminder[4]
        return pillReminder
    except:
        print("failed")


    return '알림이 없습니다.'


def index(request):
    user_id = request.session.get('user')

    if user_id:
        user = UserMember.objects.get(userID=user_id)
        pillReminder = pillreminder(user_id)
        return render(request, 'pybo/main.html', {'user' : user, 'pillReminder':pillReminder})
    else:
        return render(request, 'pybo/main.html') 
    

def login_user(request):
    response_data = {}
    if request.method == "GET":
        return render(request, 'pybo/login.html')
    
    elif request.method == "POST":
        login_userID = request.POST.get('userID', None)
        login_userPW = request.POST.get('userPW', None) 
        user = UserMember.objects.filter(userID=login_userID)

        if user.exists():
            if not (login_userID and login_userPW):
                response_data['error']="아이디와 비밀번호를 모두 입력하세요."
                return render(request, 'pybo/login.html', response_data)

            else:
                user = UserMember.objects.get(userID=login_userID)
                if (login_userPW==user.userPW):
                    request.session['user'] = user.userID
                    return redirect('/pybo')
                elif (login_userPW!=user.userPW):
                    response_data['error'] = "비밀번호가 틀립니다."
                    return render(request, 'pybo/login.html', response_data)
        else:
            response_data['error'] = "존재하지 않는 아이디입니다."
            return render(request, 'pybo/login.html', response_data)
 
def logout(request):
    request.session.pop('user')
    return redirect('/pybo')

def signup(request):
    if request.method == "GET":
        return render(request, 'pybo/signup.html')
    
    elif request.method == "POST":
        userID = request.POST.get('userID')
        userPW = request.POST.get('userPW')
        reuserPW = request.POST.get('userPW', None)
        userNAME = request.POST.get('userNAME', None)
        userTEL = request.POST.get('userTEL', None)
        res_data = {}

        user = UserMember.objects.filter(userID=userID)
        if user.exists():
            res_data['error'] = "이미 존재하는 아이디입니다."
            return render(request, 'pybo/signup.html', res_data)
        else:
            if not(userID and userPW and reuserPW and userNAME and userTEL):
                res_data['error'] = "모든 값을 입력해야 합니다."
                return render(request, 'pybo/signup.html', res_data)

            if userPW != reuserPW:
                res_data['error'] = "비밀번호가 다릅니다."
                return render(request, 'pybo/signup.html', res_data)

            else:
                user = UserMember(userID=userID, userPW=userPW, userNAME=userNAME, userTEL=userTEL)
                user.save()
                return render(request, 'pybo/main.html')
               

def main(request):
    user_id = request.session.get('user')

    if user_id:
        user = UserMember.objects.get(userID=user_idj)
        pillReminder = pillreminder(user_id)
        return render(request, 'pybo/main.html', {'user' : user, 'pillReminder':pillReminder})
    else:
        return render(request, 'pybo/main.html') 

def friend(request):    
    q = request.session.get('user')
    Friends = Friend.objects.all()
    if q:
        pillReminder = pillreminder(q)
        user = UserMember.objects.get(userID=q)
        friendlist = Friends.filter(FriendMaster__icontains=q)
        return render(request, 'pybo/friend.html', {'friendlist': friendlist, 'user': user, 'pillReminder':pillReminder})

def deleteFriend(request, friendID):
     FriendMaster = request.session.get('user')
     friendID= friendID
     friend = Friend.objects.get(FriendMaster=FriendMaster, FriendID=friendID)
     friend.delete()
     return redirect('/pybo/friend')

def search(request):
    users = UserMember.objects.all()

    q = request.POST.get('q', '')

    if q:
        users = users.filter(userID=q)

        if users.exists():
            friend = users.get(userID=q)        
            friends = Friend()
            friends.FriendMaster = request.session.get('user')
            friends.FriendID=friend.userID
            friends.save()

            userId = request.session.get('user')
            friendlist = Friend.objects.all()
            friendlist = friendlist.filter(FriendMaster__icontains=userId)
            return redirect('/pybo/friend')
        else:
            return redirect('/pybo/friend')
    else:
        userId = request.user.userId
        friendlist = Friend.objects.all()
        friendlist = friendlist.filter(userId__icontains=userId)
        return render(request, 'pybo/friend.html', {'friendlist' : friendlist})


def friendpill(request, username):
   # pilllist = PillList.objects.all()
    pillList = PillList.objects.filter(PillMaster__icontains=username)
    user = UserMember.objects.get(userID__icontains=username)
    if pillList:
        try:
            cursor = connection.cursor()
            strSql = "with recursive D as (select last_day(now() - interval 1 month) + interval 1 day as startDate union all select startDate + interval 1 day from D where startDate < last_day(now())) SELECT count(T.PillTakeTime) AS cnt, P.startDate FROM PillMe.PillTake AS T, ( SELECT C.ModuleNum as ModuleNum, C.PromTime as PromTime, D.startDate as startDate FROM D, (SELECT ModuleNum, CONCAT(CONCAT(D.startDate, ' ')  , EatTime) AS PromTime FROM PillMe.PillTime, D WHERE PillMaster = '"+user.userID+"') C WHERE C.PromTime = D.startDate) P WHERE T.ModuleNum = P.ModuleNum AND TIMESTAMPDIFF(minute, P.PromTime, T.PillTakeTime) <= 30 AND  T.PillTakeTime >= P.PromTime group by P.startDate"
            result = cursor.execute(strSql)
            pillcalendar = cursor.fetchall()

            connection.commit()
            connection.close()

            cnt = []
            startDate = []
            for value in pillcalendar :
                cnt.append(value[0])
                startDate.append(value[1])
            i = 0

            pillcalDict = {}

            for value in pillcalendar :
                pillcalDict[int(str(startDate[i])[8:])] = cnt[i]
                i = i + 1

            print(pillcalDict)
            print("success!!")
        except:
            print("failed")
        return render(request, 'pybo/friendpill.html', {'user' : user, 'pillList' : pillList, 'pillcalDict' :  pillcalDict})
    else:
        return render(request, 'pybo/friendpill.html')

   # pilllist = pilllist.objects.filter(PillMaster__icontains=userName)
#    render(request, 'pybo/friendpill.html', {'pilllist': pilllist})
def mypill(request):
    pilllist = PillList.objects.all()
    
    q = request.session.get('user')
    if q:            
        user = UserMember.objects.get(userID = q)
        pilllist = pilllist.filter(PillMaster__icontains=q)        
        return render(request, 'pybo/mypill.html', {'pilllist': pilllist, 'user': user})

def mypill(request):
    pilllist = PillList.objects.all()
    
    q = request.session.get('user')
    if q: 
        pillReminder = pillreminder(q)   
        user = UserMember.objects.get(userID = q)
        pilllist = pilllist.filter(PillMaster__icontains=q)        
        return render(request, 'pybo/mypill.html', {'pilllist': pilllist, 'user': user, 'pillReminder':pillReminder})


def addpill(request):   
    q = request.session.get('user')
    if q:            
        user = UserMember.objects.get(userID = q) 
        return render(request, 'pybo/addpill.html', {'user':user})

def addpillList(request):

    smartpill = PillList()
    smartpill.ModuleNum = request.POST.get('ModuleNum')
    smartpill.PillMaster = request.session.get('user')
    smartpill.PillName = request.POST.get('PillName')
    smartpill.PillAmount = '0'
    PillEat = request.POST.get('PillEat') 
    pillTime = request.POST.get('PillTime')

    if PillEat == 'before':
        smartpill.PillEat = '0'
    else:
        smartpill.PillEat = '1'

    if pillTime == '1':
        smartpill.PillTime = '0'
    elif pillTime == '2':
        smartpill.PillTime = '1'
    else:
        smartpill.PillTime = '2'

    smartpill.save()

    pilltime = PillTime()
    pilltime.ModuleNum = request.POST.get('ModuleNum')
    pilltime.PillName =  request.POST.get('PillName') 
    pilltime.PillMaster = request.session.get('user')
    pilltime.EatTime = request.POST.get('EatTime')
    pilltime.save()
    
    return render(request, 'pybo/addpill.html')


def find(request):
    if request.method == "GET":
        return render(request, 'pybo/find.html')


    elif request.method == "POST":
        userID = request.POST.get('userID')
        userTEL = request.POST.get('userTEL')
        user = UserMember.objects.filter(userID=userID)
        res_data = {}

        if user.exists():
            userMember = UserMember.objects.get(userID=userID)

            if (userMember.userTEL==userTEL):
                res_data['error'] = "전화번호가 다릅니다."
                return render(request, 'pybo/find.html', res_data)
            else:
                return render(request, 'pybo/find.html', {'userMember': userMember})
        else:
            res_data['error'] = "존재하지 않는 아이디입니다."
            return render(request, 'pybo/find.html', res_data)

def pillinfo(request):

    q = request.session.get('user') 
    user = UserMember.objects.get(userID=q)
    pillReminder = pillreminder(q)

    if request.method == "GET":
        return render(request, 'pybo/pillinfo.html', {'user': user, 'pillReminder':pillReminder})
    elif request.method == "POST":
        q = request.POST.get('q', '')
        url = 'http://apis.data.go.kr/1471000/HtfsTrgetInfoService01/getHtfsInfoList01'
        # url = 'http://34.64.106.196:8080/getApiData.php'
        serviceKey = '8/bnxiQS+6+cZaLNhKmIRXawXVN8vYxJh23R3gZDCnHi0fzQuzUuY2XeXsibxBc6rt4h9iuZfXkP4/65n1eyrA=='
        params ={'serviceKey' : serviceKey, 'prdlst_nm' : q, 'bssh_nm' : '', 'pageNo' : '1', 'numOfRows' : '3', 'type' : 'json' }        
        response = requests.get(url, params=params)
        responsedecoded = response.content.decode('utf-8')
        res_data={}
        r_dd = response.json()
        
        try:
            r_data = r_dd["body"]["items"]
            return render(request, 'pybo/pillinfo.html', context={'r_data':r_data, 'user': user, 'pillReminder':pillReminder})
        except:
            pass
        res_data['error'] = "결과가 없습니다."
        

        return render(request, 'pybo/pillinfo.html',  {'res_data':res_data, 'user':user, 'pillReminder':pillReminder})
        
        #try:
        #    r_data = r_dd["body"]["items"]
        #    return render(request, 'pybo/pillinfo.html', context={'r_data':r_data, 'user': user})
       # except KeyError:
        #    print("error")
       #     res_data['error'] = "결과가 존재하지 않습니다."
           # return redirect('/pybo/pillinfo')
           
        #    return render(request, 'pybo/pillinfo.html', res_data, {'user':user})
      # data = r_data.content.decode('utf-8')
       # print(r_data)


        # dataJson = response.json()

#        for item in response.content['header']['body']['items']['item']:
 #           print(item)
       # data = r_item.decode('utf-8')
       # data = response.content.decode('utf-8')

        #data = response.content.decode('utf-8')

     #   dataJson = json.loads(response.content)
      #  dataJson['PRDLST_NM']
       # data = response.content.decode('utf-8')
        # result_data = response.content.json()
      #  print(dataJson)

        #return render(request, 'pybo/pillinfo.html', context={'r_data':r_data, 'user': user})

        # 
 # {'data' : data}


def mypillinfo(request, pillName):
    q = request.session.get('user')
    pillReminder = pillreminder(q)

    user = UserMember.objects.get(userID=q)


    return render(request, 'pybo/mypillinfo.html', {'user':user, 'pillReminder':pillReminder})
