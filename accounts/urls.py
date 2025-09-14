from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/student/', views.register_student, name='register_student'),
    path('register/staff/', views.register_staff, name='register_staff'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
]