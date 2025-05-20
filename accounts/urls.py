from django.urls import path
from . import views  # import views để dùng DoctorUpdateView
from .views import accounts, add_doctor, doctors, doctor_detail, doctor_update

urlpatterns = [
    path('', accounts, name='accounts'),
    path('doctors/', doctors, name='doctors'),
    path('add_doctor/', add_doctor, name='add_doctor'),
    path('doctors/<int:id>/', doctor_detail, name='doctor_detail'),  # dấu phẩy ở cuối
    path('doctors/<int:pk>/update/', doctor_update, name='doctor_update'),
    path('doctors/<int:pk>/cap-tai-khoan/', views.cap_tai_khoan, name='cap_tai_khoan'),
    path('doctors/<int:doctor_id>/reset_password/', views.reset_password, name='reset_password'),
    path('appointments/', views.all_appointments, name='all_appointments'),
    path('appointments/<int:appointment_id>/', views.appointment_detail, name='appointment_detail'),

]
