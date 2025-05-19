from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from .models import LichKham
from chuyen_khoa.models import ChuyenKhoa
from django.conf import settings

def them_lich_hen(request):
    chuyen_khoa_list = ChuyenKhoa.objects.all().order_by('ten_chuyen_khoa')

    if request.method == 'POST':
        ho_ten = request.POST.get('ho_ten')
        email = request.POST.get('email')
        chuyen_khoa = request.POST.get('chuyen_khoa')
        ngay_kham = request.POST.get('ngay_kham')
        buoi_kham = request.POST.get('buoi_kham')
        trieu_chung = request.POST.get('trieu_chung')
        phone = request.POST.get('phone')

        try:
            chuyen_khoa_obj = ChuyenKhoa.objects.get(ma_chuyen_khoa=chuyen_khoa)
            ten_chuyen_khoa = chuyen_khoa_obj.ten_chuyen_khoa
        except ChuyenKhoa.DoesNotExist:
            ten_chuyen_khoa = 'Không xác định'

        lich_hen = LichKham(
            ho_ten=ho_ten,
            email=email,
            chuyen_khoa=chuyen_khoa,
            ngay_kham=ngay_kham,
            buoi_kham=buoi_kham,
            trieu_chung=trieu_chung,
            phone=phone
        )
        lich_hen.save()

        subject = "Xác nhận đặt lịch khám bệnh"
        from_email = settings.EMAIL_HOST_USER
        to = [email]

        context = {
            'ho_ten': ho_ten,
            'chuyen_khoa': ten_chuyen_khoa,
            'ngay_kham': ngay_kham,
            'buoi_kham': buoi_kham,
            'phone': phone,
            'trieu_chung': trieu_chung,
        }

        html_content = render_to_string('email/confirm_appointment.html', context)
        email_message = EmailMultiAlternatives(subject=subject, body='', from_email=from_email, to=to)
        email_message.attach_alternative(html_content, "text/html")
        email_message.send()

        request.session['dat_lich_email'] = email
        return redirect('lich_hen_thanh_cong')

    return render(request, 'appointment.html', {'chuyen_khoa_list': chuyen_khoa_list})


def lich_hen_thanh_cong(request):
    email = request.session.pop('dat_lich_email', None)
    return render(request, 'lich_hen_thanh_cong.html', {'email': email})
