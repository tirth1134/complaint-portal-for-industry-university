from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_complaints, name='complaints_list'),
    # New: selection page first
    path('new/', views.select_category, name='select_complaint_category'),
    # Form page for a chosen category
    path('new/<str:category>/', views.create_complaint, name='create_complaint'),
    path('<int:complaint_id>/', views.complaint_detail, name='complaint_detail'),
    path('<int:complaint_id>/validate/', views.validate_complaint, name='validate_complaint'),
    path('<int:complaint_id>/status/', views.update_status, name='update_status'),
]
