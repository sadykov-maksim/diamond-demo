from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('room/<int:pk>/', views.room, name='room'),
    path('check_spin_history/', views.check_spin_history, name='check_spin_history'),
]