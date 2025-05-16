from django.shortcuts import render, redirect
from .models import LichKham
from chuyen_khoa.models import ChuyenKhoa

def them_lich_hen(request):
    chuyen_khoa_list = ChuyenKhoa.objects.all().order_by('ten_chuyen_khoa')

    if request.method == 'POST':
        ho_ten = request.POST.get('ho_ten')
        email = request.POST.get('email')
        chuyen_khoa = request.POST.get('chuyen_khoa')
        ngay_kham = request.POST.get('ngay_kham')
        buoi_kham = request.POST.get('buoi_kham')
        trieu_chung = request.POST.get('trieu_chung')

        lich_hen = LichKham(
            ho_ten=ho_ten,
            email=email,
            chuyen_khoa=chuyen_khoa,
            ngay_kham=ngay_kham,
            buoi_kham=buoi_kham,
            trieu_chung=trieu_chung
        )
        lich_hen.save()

        # Gửi email vào session
        request.session['dat_lich_email'] = email

        # Chuyển sang trang cảm ơn
        return redirect('lich_hen_thanh_cong')

    return render(request, 'appointment.html', {'chuyen_khoa_list': chuyen_khoa_list})

def lich_hen_thanh_cong(request):
    email = request.session.pop('dat_lich_email', None)
    return render(request, 'lich_hen_thanh_cong.html', {'email': email})
