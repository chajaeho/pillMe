from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('login/', views.login_user, name="login"),
    path('signup/', views.signup, name="signup"),
    path('main/', views.main, name="main"),
    path('logout/', views.logout, name="logout"),
    path('friend/', views.friend, name="friend"),
    path('searchFriend/', views.search, name="searchFriend"),
    path('mypill/', views.mypill, name="mypill"),
    path('friend/<str:username>/', views.friendpill, name='friendpill'),
    path('addpill/', views.addpill, name="addpill"),
    path('addpillList/', views.addpillList, name='addpillList'),
    path('find/', views.find, name='find'),
    path('friend/<str:friendID>/delete', views.deleteFriend, name='deleteFriend'),
    path('pillinfo/', views.pillinfo, name='pillinfo'),
    path('mypill/<str:pillName>/', views.editpillList, name='editpillList'),
    path('mypill/<str:pillName>/edit/', views.edit, name='edit'),
    path('searchfriendpill/', views.friendpill, name='searchFriendPill'),

]