from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('signup',views.signup,name="signup"),
    path('signin',views.signin,name="signin"),
    path('signout',views.signout,name="signout"),
    # path('activate/<uidb64>/<token>',views.activate,name="activate"),
    # path('dashboard',views.upload_timetable,name="dashboard"),
    path('dashboard2',views.upload_acdcalendar,name="dashboard2"),
    path('insights',views.userprofile,name="insights"),
    path('homepage',views.homepage,name="homepage"),
    path('db1',views.userinput,name="db1"),
    path('db2',views.upload_timetable,name="db2"),
    path('db3',views.upload_academiccalendar,name="db3"),
    path('db4',views.calculations,name="db4"),
    path('markattendance',views.update_attendance,name="markattendance"),
    path('continue_tracking',views.continue_tracking,name="continue_tracking"),
    path('updateattendance',views.updateattendance,name="updateattendance"),
    path('updatecalendar',views.updatecalendar,name="updatecalendar"),
    path('impevent',views.important_events,name="impevent"),
]
