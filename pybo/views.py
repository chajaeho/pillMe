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

# Create your views here.

def index(request):
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
                return render(request, 'pybo/main.html')
            else:
                response_data['error'] = "비밀번호가 틀립니다."
                return render(request, 'pybo/login.html', response_data)
            
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
        return render(request, 'pybo/main.html', user)
    else:
        return render(request, 'pybo/main.html') 


def friend(request):
    friendlist = Friend.objects.all()

    q = request.session.get('user')

    if q:
        friendlist = friendlist.filter(FriendMaster__icontains=q)
        return render(request, 'pybo/friend.html', {'friendlist': friendlist})

def search(request):
    users = UserMember.objects.all()

    q = request.POST.get('q', '')

    if q:
        users = users.filter(userID__icontains=q)
        friend = users.get(userID=q)        
        friends = Friend()
        friends.FriendMaster = request.session.get('user')
        friends.FriendID= q
        friends.save()

        userId = request.session.get('user')
        friendlist = Friend.objects.all()
        friendlist = friendlist.filter(FriendMaster__icontains=userId)
        return render(request, 'pybo/friend.html', {'friendlist' : friendlist})
    else:
        userId = request.user.userId
        friendlist = Friend.objects.all()
        friendlist = friendlist.filter(userId__icontains=userId)
        return render(request, 'pybo/friend.html', {'friendlist' : friendlist})


def friendpill(request, username):
   # pilllist = PillList.objects.all()
    pillList = PillList.objects.filter(PillMaster__icontains=username)
    userName = {
        'userName': username,
    }
    if pillList:
        return render(request, 'pybo/friendpill.html', {'userName' : userName, 'pillList': pillList})
    else:
        return render(request, 'pybo/friendpill.html')

   # pilllist = pilllist.objects.filter(PillMaster__icontains=userName)
#    render(request, 'pybo/friendpill.html', {'pilllist': pilllist})
def mypill(request):
    pilllist = PillList.objects.all()
    
    q = request.session.get('user')
    if q:
        pilllist = pilllist.filter(PillMaster__icontains=q)        
        return render(request, 'pybo/mypill.html', {'pilllist': pilllist})


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


