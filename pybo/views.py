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
# Create your views here.

def index(request):
    user_id = request.session.get('user')

    if user_id:
        user = UserMember.objects.get(userID=user_id)
        return render(request, 'pybo/main.html', {'user' : user})
    else:
        return render(request, 'pybo/main.html') 
    

def login_user(request):
    response_data = {}
    if request.method == "GET":
        return render(request, 'pybo/login.html')
    
    elif request.method == "POST":
        login_userID = request.POST.get('userID', None)
        login_userPW = request.POST.get('userPW', None) 

        if not (login_userID and login_userPW):
            response_data['error']="아이디와 비밀번호를 모두 입력하세요."

        else:
            user = UserMember.objects.get(userID=login_userID)
            if (login_userPW ==user.userPW):
                request.session['user'] = user.userID
                return redirect('/pybo')
            else:
                response_data['error'] = "비밀번호가 틀립니다."
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
        if not(userID and userPW and reuserPW and userNAME and userTEL):
            res_data['error'] = "모든 값을 입력해야 합니다."
        if userPW != reuserPW:
            res_data['error'] = "비밀번호가 다릅니다."
        else:
            user = UserMember(userID=userID, userPW=userPW, userNAME=userNAME, userTEL=userTEL)
            user.save()
        
        return render(request, 'pybo/main.html')

def main(request):
    user_id = request.session.get('user')

    if user_id:
        user = UserMember.objects.get(userID=user_id)
        return render(request, 'pybo/main.html', {'user' : user})
    else:
        return render(request, 'pybo/main.html') 


def friend(request):    
    q = request.session.get('user')
    Friends = Friend.objects.all()
    if q:
        user = UserMember.objects.get(userID=q)
        friendlist = Friends.filter(FriendMaster__icontains=q)
        return render(request, 'pybo/friend.html', {'friendlist': friendlist, 'user': user})

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
        users = users.filter(userID__icontains=q)
        friend = users.get(userID=q)        
        friends = Friend()
        friends.FriendMaster = request.session.get('user')
        friends.FriendID=friend.userID
        friends.save()

        userId = request.session.get('user')
        friendlist = Friend.objects.all()
        friendlist = friendlist.filter(FriendMaster__icontains=userId)
      #  return render(request, 'pybo/friend.html', {'friendlist' : friendlist})
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
            print("success!!")
        except:
            print("failed")
        return render(request, 'pybo/friendpill.html', {'user' : user, 'pillList': pillList})
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


def addpill(request):        
        return render(request, 'pybo/addpill.html')

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
    return render(request, 'pybo/find.html')

def findPassword(request):
    userID = request.POST.get('userID')
    userTEL = request.POST.get('userTEL')

    userMember = UserMember.objects.get(userID=userID)
    SendSMS.send_SMS(userTEL, userMember.userNAME, userMember.userPW)

    return render('pybo/main.html')



def pillinfo(request):
    if request.method == "GET":
        return render(request, 'pybo/pillinfo.html')
    elif request.method == "POST":
        q = request.POST.get('q', '')
        url = 'http://apis.data.go.kr/1471000/HtfsTrgetInfoService01/getHtfsInfoList01'
        # url = 'http://34.64.106.196:8080/getApiData.php'
        serviceKey = '8/bnxiQS+6+cZaLNhKmIRXawXVN8vYxJh23R3gZDCnHi0fzQuzUuY2XeXsibxBc6rt4h9iuZfXkP4/65n1eyrA=='
        params ={'serviceKey' : serviceKey, 'prdlst_nm' : q, 'bssh_nm' : '', 'pageNo' : '1', 'numOfRows' : '3', 'type' : 'json' }
        response = requests.get(url, params=params)
        responsedecoded = response.content.decode('utf-8')
        r_dd = response.json()
        r_data = r_dd["body"]["items"]
       # data = r_data.content.decode('utf-8')
        print(r_data)


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

        return render(request, 'pybo/pillinfo.html', context={'r_data':r_data})

        # 
 # {'data' : data}


