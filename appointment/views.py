import random
import uuid
from urllib.parse import urlencode

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, send_mail
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.contrib.auth.models import User

from .models import LichKham
from chuyen_khoa.models import ChuyenKhoa
from accounts.models import UserProfile


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

        activation_token = str(uuid.uuid4())

        lich_hen = LichKham.objects.create(
            ho_ten=ho_ten,
            email=email,
            chuyen_khoa=chuyen_khoa,
            ngay_kham=ngay_kham,
            buoi_kham=buoi_kham,
            trieu_chung=trieu_chung,
            phone=phone,
            activation_token=activation_token,
            type=0
        )

        # Kiểm tra profile theo email
        if not UserProfile.objects.filter(email=email).exists():
            # Nếu chưa có profile, tạo mới và gửi email kích hoạt tài khoản
            profile = UserProfile.objects.create(
                email=email,
                activation_token=activation_token,
                is_activated=False,
                ten=ho_ten,
                phone=phone,
            )
            send_activation_email(email, ho_ten, ten_chuyen_khoa, ngay_kham, buoi_kham, phone, trieu_chung, activation_token,lich_hen.id, request)
        else:
            send_appointment_confirmation_email(email, ho_ten, ten_chuyen_khoa, ngay_kham, buoi_kham, phone, trieu_chung, activation_token, lich_hen.id, request)

        # Lưu email vào session để hiển thị trang thành công
        request.session['dat_lich_email'] = email
        return redirect('lich_hen_thanh_cong')

    return render(request, 'appointment.html', {'chuyen_khoa_list': chuyen_khoa_list})

def lich_hen_thanh_cong(request):
    email = request.session.pop('dat_lich_email', None)
    return render(request, 'lich_hen_thanh_cong.html', {'email': email})




def activate_account(request, email):
    token = request.GET.get('active')
    appointment_id = request.GET.get('id')

    if not token:
        return render(request, 'activation_failed.html', {'message': 'Thiếu mã kích hoạt'})

    try:
        profile = UserProfile.objects.get(email=email)
    except UserProfile.DoesNotExist:
        return render(request, 'activation_failed.html', {'message': 'Không tìm thấy hồ sơ người dùng'})

    if profile.is_activated:
        return render(request, 'activation_success.html', {'message': 'Tài khoản đã được kích hoạt trước đó'})

    # So sánh token, bỏ dấu '-' để tránh lỗi format
    token_profile = str(profile.activation_token).replace('-', '')
    token_request = token.replace('-', '')

    if token_profile != token_request:
        return render(request, 'activation_failed.html', {'message': 'Mã kích hoạt không hợp lệ'})

    # Đánh dấu đã kích hoạt
    profile.is_activated = True
    profile.activation_token = None

    # Tạo mật khẩu ngẫu nhiên gồm 6 số
    random_password = ''.join([str(random.randint(0, 9)) for _ in range(6)])

    # Tạo user mới với username là email
    user = User.objects.create_user(username=email, password=random_password)
    user.save()

    # Gán user vào profile và lưu
    profile.user = user
    profile.save()

    # Nếu có ID lịch hẹn, kiểm tra và kích hoạt luôn lịch
    if appointment_id:
        try:
            appointment = LichKham.objects.get(id=appointment_id)
            token_appointment = str(appointment.activation_token).replace('-', '')
            if token_appointment == token_request:
                appointment.type = 1
                appointment.activation_token = None
                appointment.user = user
                appointment.save()
        except LichKham.DoesNotExist:
            pass

    # Chuẩn bị gửi mail thông báo kích hoạt thành công
    subject = 'Kích hoạt tài khoản thành công'
    from_email = settings.EMAIL_HOST_USER
    to_email = [email]

    context = {
        'ho_ten': profile.ten or '',
        'email': email,
        'password': random_password,
    }

    html_content = render_to_string('email/account_activated.html', context)

    msg = EmailMultiAlternatives(subject, '', from_email, to_email)
    msg.attach_alternative(html_content, "text/html")
    msg.send()

    return render(request, 'activation_success.html', {'message': 'Kích hoạt tài khoản thành công'})





def activate_appointment(request):
    token = request.GET.get('token')
    lich_id = request.GET.get('id')

    if not token or not lich_id:
        message = "Thiếu tham số token hoặc id."
        status = "error"
        return render(request, 'email/activation_result.html', {'message': message, 'status': status})

    try:
        lich = LichKham.objects.get(id=lich_id)
        lich.type = 1
        lich.save()
        message = (
            "Lịch hẹn của bạn đã được xác nhận thành công.<br>"
            "Bạn có thể kiểm tra chi tiết lịch hẹn bằng email hoặc tài khoản đã được cung cấp.<br>"
            f"Email đăng ký: <b>{lich.email}</b>"
        )

        status = "success"
    except LichKham.DoesNotExist:
        message = "Lịch hẹn không tồn tại hoặc đã được xác nhận."
        status = "error"

    return render(request, 'email/activation_result.html', {'message': message, 'status': status})





def send_activation_email(email, ho_ten,ten_chuyen_khoa, ngay_kham, buoi_kham, phone, trieu_chung, activation_token, id, request):
    activation_account_url = request.build_absolute_uri(
        reverse('activate_account', kwargs={'email': email}) + f"?active={activation_token}&id={id}"
    )
    subject = "Kích hoạt tài khoản của bạn"
    from_email = settings.EMAIL_HOST_USER
    to = [email]

    context = {
        'ho_ten': ho_ten,
        'chuyen_khoa': ten_chuyen_khoa,
        'ngay_kham': ngay_kham,
        'buoi_kham': buoi_kham,
        'phone': phone,
        'trieu_chung': trieu_chung,
        'confirm_url': activation_account_url,
    }

    html_content = render_to_string('email/confirm_appointment.html', context)
    email_message = EmailMultiAlternatives(subject=subject, body='', from_email=from_email, to=to)
    email_message.attach_alternative(html_content, "text/html")
    email_message.send()




def send_appointment_confirmation_email(email, ho_ten, ten_chuyen_khoa, ngay_kham, buoi_kham, phone, trieu_chung, activation_token, lich_id, request):
    base_url = reverse('activate_appointment')  # chỉ lấy path không tham số
    query_string = urlencode({'token': activation_token, 'id': lich_id})
    confirm_url = request.build_absolute_uri(f"{base_url}?{query_string}")

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
        'confirm_url': confirm_url,
    }

    html_content = render_to_string('email/confirm_appointment.html', context)
    email_message = EmailMultiAlternatives(subject=subject, body='', from_email=from_email, to=to)
    email_message.attach_alternative(html_content, "text/html")
    email_message.send()
