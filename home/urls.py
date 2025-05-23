from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('chat/api/', views.chat_api, name='chat_api'),
    path('teams/', views.team, name='teams'),
]
