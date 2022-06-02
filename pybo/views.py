from django.shortcuts import render
from .models import UserMember
from django.contrib.auth import authenticate, login
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
            user = authenticate(request, userID = login_userID, userPW = login_userPW)
            if user is not None:
                login(request, user)
    return render(request, 'pybo/login.html', response_data)

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