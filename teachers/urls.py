from django.urls import path
from . import views

urlpatterns = [
    path('', views.teacher_home, name="teacher_home"),
    path('signup/', views.teacher_signup, name="teacher_signup"),
    path('signin/', views.teacher_signin, name="teacher_signin"),
    path('signout/', views.teacher_signout, name="teacher_signout"),
    path('dashboard/', views.teacher_dashboard, name="teacher_dashboard"),
    path('student/<int:student_id>/', views.student_detail, name="student_detail"),
]