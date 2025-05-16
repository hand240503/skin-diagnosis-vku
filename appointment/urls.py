from django.urls import path
from . import views

urlpatterns = [
    path('lich-kham/', views.them_lich_hen, name='them_lich_hen'),
    path('lich-kham-thanh-cong/', views.lich_hen_thanh_cong, name='lich_hen_thanh_cong'),
]
