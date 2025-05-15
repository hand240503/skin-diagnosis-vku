from django.urls import path
from . import views

urlpatterns = [
    path('', views.diagnosis_form, name='diagnosis_form'),
    path('result/', views.diagnosis_result, name='diagnosis_result'),
]
