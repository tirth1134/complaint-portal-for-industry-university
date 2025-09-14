from django.urls import path
from . import views

urlpatterns = [
    path('new/', views.create_complaint, name='create_complaint'),
    path('<int:complaint_id>/', views.complaint_detail, name='complaint_detail'),
    path('<int:complaint_id>/validate/', views.validate_complaint, name='validate_complaint'),
    path('<int:complaint_id>/status/', views.update_status, name='update_status'),
]