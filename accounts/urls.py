from django.urls import path
from .views import accounts, add_doctor

urlpatterns = [
    path('', accounts, name='accounts'),
    path('add_doctor/', add_doctor, name='add_doctor'),
]