from django.urls import path
from . import views

urlpatterns = [
    path('lich-kham/', views.them_lich_hen, name='them_lich_hen'),
    path('lich-kham-thanh-cong/', views.lich_hen_thanh_cong, name='lich_hen_thanh_cong'),
    path('activate-account/<str:email>/', views.activate_account, name='activate_account'),
    path('xac-nhan-lich-hen/', views.activate_appointment, name='activate_appointment'),
    path('lich-kham-nguoi-dung/', views.lich_kham_nguoi_dung, name='lich_kham_nguoi_dung'),
    path('lich-kham/tim-kiem-lich/', views.lich_kham_tim_kiem, name='tim_kiem_lich'),
    path('huy-lich-hen/<int:lich_id>/', views.huy_lich_kham, name='huy_lich_hen'),
    path('benh-an-cua-toi/', views.all_benh_an_view, name='benh_an_cua_toi'),
    path('benh-an-cua-toi/<int:benh_an_id>/', views.chi_tiet_benh_an_view, name='chi_tiet_benh_an_cua_toi'),

]
