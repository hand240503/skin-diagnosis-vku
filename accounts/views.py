from django.conf import settings
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from appointment.forms import BenhAnDetailForm
from appointment.models import BenhAn, BenhAnChiTiet, DoctorAppointment, LichKham
from .models import User
from .models import UserProfile
from chuyen_khoa.models import ChuyenKhoa
from .forms import DoctorForm, AssignDoctorForm
import random
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, get_object_or_404
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
@login_required(login_url='/login/')
def accounts(request):
    users = UserProfile.objects.filter(type=2)
    return render(request, 'accounts.html', {'users': users})

@login_required(login_url='/login/')
def doctors(request):
    doctors = UserProfile.objects.filter(type=1)
    return render(request, 'doctors.html', {'doctors': doctors})


@login_required(login_url='/login/')
def doctor_detail(request, id):
    doctor = get_object_or_404(UserProfile, id=id,type=1)
    context = {'doctor': doctor}
    return render(request, 'doctor_detail.html', context)


@login_required(login_url='/login/')
def add_doctor(request):
    chuyen_khoa_list = ChuyenKhoa.objects.all()

    if request.method == "POST":
        ten = request.POST.get('ten')
        tuoi = request.POST.get('tuoi')
        chuyen_khoa_id = request.POST.get('chuyen_khoa')
        hoc_vi = request.POST.get('hoc_vi')
        kinh_nghiem = request.POST.get('kinh_nghiem')
        chuc_vu = request.POST.get('chuc_vu')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        avatar = request.FILES.get('avatar')

        chuyen_khoa = None
        if chuyen_khoa_id:
            try:
                chuyen_khoa = ChuyenKhoa.objects.get(id=chuyen_khoa_id)
            except ChuyenKhoa.DoesNotExist:
                chuyen_khoa = None  # hoặc bạn có thể thêm thông báo lỗi

        # Tạo UserProfile mới
        doctor = UserProfile.objects.create(
            ten=ten,
            tuoi=int(tuoi) if tuoi else None,
            chuyen_khoa=chuyen_khoa,
            hoc_vi=hoc_vi,
            kinh_nghiem=int(kinh_nghiem) if kinh_nghiem else None,
            chuc_vu=chuc_vu,
            email=email,
            phone=phone,
            avatar=avatar,
            type=1,
            is_activated=True,
            activation_token=None,
        )

        return redirect('doctors')

    return render(request, 'add_doctor.html', {'chuyen_khoa_list': chuyen_khoa_list})


@login_required(login_url='/login/')
def doctor_update(request, pk):
    doctor = get_object_or_404(UserProfile, pk=pk)
    chuyen_khoa_list = ChuyenKhoa.objects.all()
    if request.method == 'POST':
        form = DoctorForm(request.POST, request.FILES, instance=doctor)
        if form.is_valid():
            doctor = form.save(commit=False)

            if doctor.user:
                doctor.user.is_active = doctor.is_activated
                doctor.user.save()

            doctor.save()
            return redirect('doctor_detail', id=doctor.pk)
    else:
        form = DoctorForm(instance=doctor)
    return render(request, 'doctor_update.html', {
        'form': form,
        'doctor': doctor,
        'chuyen_khoa_list': chuyen_khoa_list,
    })

@login_required(login_url='/login/')
def cap_tai_khoan(request, pk):
    doctor = get_object_or_404(UserProfile, pk=pk)

    # Kiểm tra nếu đã có tài khoản
    if User.objects.filter(username=doctor.email).exists():
        messages.warning(request, "Tài khoản đã tồn tại cho bác sĩ này.")
        return redirect('doctor_detail', id=pk)

    # Tạo mật khẩu 6 số
    password = ''.join([str(random.randint(0, 9)) for _ in range(6)])

    # Tạo người dùng
    user = User.objects.create_user(
        username=doctor.email,
        email=doctor.email,
        password=password,
        is_active=True
    )

    # Có thể liên kết doctor với user (nếu bạn có quan hệ OneToOneField)
    doctor.user = user
    doctor.is_activated = True
    doctor.save()

    messages.success(request, f"Tài khoản đã được tạo. Mật khẩu: {password}")
    return redirect('doctor_detail', id=pk)
@login_required(login_url='/login/')
def reset_password(request, doctor_id):
    # Lấy doctor hoặc trả về 404 nếu không tồn tại
    doctor = get_object_or_404(UserProfile, id=doctor_id)

    if not doctor.user:
        messages.error(request, 'Bác sĩ chưa có tài khoản.')
        return redirect('doctors')  # hoặc trang phù hợp

    user = doctor.user

    new_password = ''.join(random.choices('0123456789', k=6))
    user.password = make_password(new_password)
    user.save()

    messages.success(request, f'Mật khẩu mới đã được cấp cho bác sĩ {doctor.ten}: {new_password}')
    return redirect('doctor_detail', id=doctor_id)

@login_required
def all_appointments(request):
    status = request.GET.get('status')
    user = request.user

    if user.is_superuser:
        # Superuser lấy tất cả lịch khám
        lich_kham_list = LichKham.objects.all()
    else:
        try:
            profile = user.userprofile
        except:
            profile = None

        if profile:
            doctor_appointments = DoctorAppointment.objects.filter(doctor=profile).select_related('lich_kham')
            lich_kham_list = LichKham.objects.filter(id__in=[da.lich_kham.id for da in doctor_appointments])
        else:
            lich_kham_list = LichKham.objects.none()

    if status in ['0', '1', '2']:
        lich_kham_list = lich_kham_list.filter(type=status)

    lich_kham_list = lich_kham_list.order_by('ngay_kham').distinct()

    return render(request, 'all_appointments.html', {
        'lich_kham_list': lich_kham_list,
        'request': request
    })
def appointment_detail(request, appointment_id):
    lich_kham = get_object_or_404(LichKham, id=appointment_id)

    return render(request, 'appointment_detail.html', {
        'lich_kham': lich_kham
    })

def update_appointment_status(request, appointment_id):
    lich_kham = get_object_or_404(LichKham, id=appointment_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['0', '1', '2']:
            lich_kham.type = int(new_status)
            lich_kham.save()
            messages.success(request, 'Cập nhật trạng thái thành công.')
        else:
            messages.error(request, 'Trạng thái không hợp lệ.')
    return redirect('appointment_detail', appointment_id=appointment_id)


def assign_doctor(request, appointment_id):
    lich_kham = get_object_or_404(LichKham, id=appointment_id)

    if request.method == 'POST':
        form = AssignDoctorForm(request.POST)
        if form.is_valid():
            selected_doctors = form.cleaned_data['doctors']
            # Xóa các phân công cũ
            DoctorAppointment.objects.filter(lich_kham=lich_kham).delete()
            # Tạo lại phân công mới
            for doctor in selected_doctors:
                DoctorAppointment.objects.create(doctor=doctor, lich_kham=lich_kham)
            messages.success(request, 'Phân công bác sĩ thành công.')
            return redirect('appointment_detail', appointment_id=appointment_id)
    else:
        # Lấy các bác sĩ đã được phân công
        assigned_doctors = UserProfile.objects.filter(
            doctorappointment__lich_kham=lich_kham
        )
        form = AssignDoctorForm(initial={'doctors': assigned_doctors})

    return render(request, 'assign_doctor.html', {'form': form, 'lich_kham': lich_kham})

def create_user_account_view(request):
    email = request.GET.get('email')
    if not email:
        return JsonResponse({'success': False, 'message': 'Thiếu email'})

    try:
        profile = UserProfile.objects.get(email=email)
    except UserProfile.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Không tìm thấy hồ sơ người dùng'})

    if profile.user is not None:
        return JsonResponse({'success': False, 'message': 'Tài khoản đã được tạo trước đó'})

    random_password = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    user = User.objects.create_user(username=email, email=email, password=random_password)
    user.save()

    profile.user = user
    profile.is_activated = True
    profile.activation_token = None
    profile.save()

    appointments = LichKham.objects.filter(email=email)

    for appt in appointments:
        appt.user = user
        appt.type = 1
        appt.save()

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

    return JsonResponse({
        'success': True,
        'message': 'Tạo tài khoản thành công',
        'email': email,
        'username': user.username,
        'password': random_password
    })

from datetime import date

@login_required
def tao_benh_an_view(request, lich_kham_id):
    user = request.user

    # Kiểm tra bác sĩ
    if not hasattr(user, 'userprofile') or user.userprofile.type != 1:
        return HttpResponseForbidden("Bạn không có quyền thực hiện thao tác này.")

    # Lấy lịch khám
    lich_kham = get_object_or_404(LichKham, id=lich_kham_id)

    # Kiểm tra lịch này có liên kết với bác sĩ hiện tại không
    if not DoctorAppointment.objects.filter(lich_kham=lich_kham, doctor=user.userprofile).exists():
        return HttpResponseForbidden("Bạn không được phân công lịch khám này.")

    if request.method == 'POST':
        chuan_doan = request.POST.get('chuan_doan')
        ghi_chu = request.POST.get('ghi_chu')
        trieu_chung = request.POST.get('trieu_chung')
        ket_qua_xet_nghiem = request.POST.get('ket_qua_xet_nghiem')
        don_thuoc = request.POST.get('don_thuoc')
        chi_tiet_ghi_chu = request.POST.get('chi_tiet_ghi_chu')
        anh_benh_an = request.FILES.get('anh_benh_an')

        benh_an = BenhAn.objects.create(
            benh_nhan=lich_kham.user,
            bac_si=user.userprofile,
            chuan_doan=chuan_doan,
            ghi_chu=ghi_chu,
            lich_kham=lich_kham,
        )

        BenhAnChiTiet.objects.create(
            benh_an=benh_an,
            trieu_chung=trieu_chung,
            ket_qua_xet_nghiem=ket_qua_xet_nghiem,
            don_thuoc=don_thuoc,
            ghi_chu=chi_tiet_ghi_chu,
            anh_benh_an=anh_benh_an
        )

        return redirect('danh_sach_benh_an')

    list_user_profile_bacsi = UserProfile.objects.filter(type=1)
    today = date.today().isoformat()  # định dạng 'YYYY-MM-DD'

    return render(request, 'tao_benh_an.html', {
        'lich_kham': lich_kham,
        'bac_si_userprofile': user.userprofile,
        'bac_si_auth_user': user,
        'benh_nhan_auth_user': lich_kham.user,
        'benh_nhan_userprofile': getattr(lich_kham.user, 'userprofile', None),
        'list_user_profile_bacsi': list_user_profile_bacsi,
        'today': today,
    })


@login_required
def benh_an_detail_view(request, benh_an_id):
    user = request.user

    # Lấy bệnh án hoặc 404
    benh_an = get_object_or_404(
        BenhAn.objects.select_related("benh_nhan", "bac_si", "bac_si__user"),
        id=benh_an_id
    )

    # Kiểm tra quyền:
    is_bac_si = hasattr(user, 'userprofile') and user.userprofile == benh_an.bac_si
    is_benh_nhan = (user == benh_an.benh_nhan)
    if not (user.is_superuser or is_bac_si or is_benh_nhan):
        return HttpResponseForbidden("Bạn không có quyền xem bệnh án này.")


    # Lấy chi tiết bệnh án
    chi_tiet_benh_an_list = benh_an.chi_tiet.all()

    # Gắn profile bệnh nhân và bác sĩ
    benh_an.benh_nhan_profile = getattr(benh_an.benh_nhan, "userprofile", None)
    benh_an.bac_si_profile = benh_an.bac_si

    # Tên hiển thị bệnh nhân
    benh_an.bn_display_name = (
        benh_an.benh_nhan_profile.ten
        if benh_an.benh_nhan_profile and benh_an.benh_nhan_profile.ten
        else benh_an.benh_nhan.get_full_name() or benh_an.benh_nhan.username
    )

    # Tên hiển thị bác sĩ
    benh_an.bs_display_name = (
        benh_an.bac_si_profile.ten
        if benh_an.bac_si_profile and benh_an.bac_si_profile.ten
        else benh_an.bac_si_profile.user.get_full_name() or benh_an.bac_si_profile.user.username
    )

    return render(request, 'benh_an_detail.html', {
        'benh_an': benh_an,
        'chi_tiet_benh_an_list': chi_tiet_benh_an_list,
    })

@login_required
def all_benh_an_view(request):

    user = request.user

    if user.is_superuser or (hasattr(user, "userprofile") and user.userprofile.type == 1):
        qs = BenhAn.objects.all()
    else:
        qs = BenhAn.objects.filter(benh_nhan=user)

    qs = (
        qs.select_related("benh_nhan")
          .select_related("bac_si", "bac_si__user")
          .order_by("-id")
    )

    # --- Gắn profile & display_name cho từng bệnh án ------------------------
    for ba in qs:
        # profile bệnh nhân
        ba.benh_nhan_profile = getattr(ba.benh_nhan, "userprofile", None)

        # profile bác sĩ đã có sẵn trong ba.bac_si (cũng là UserProfile)
        ba.bac_si_profile = ba.bac_si

        # tên hiển thị bệnh nhân
        ba.bn_display_name = (
            ba.benh_nhan_profile.ten
            if ba.benh_nhan_profile and ba.benh_nhan_profile.ten
            else ba.benh_nhan.get_full_name() or ba.benh_nhan.username
        )

        # tên hiển thị bác sĩ
        ba.bs_display_name = (
            ba.bac_si_profile.ten
            if ba.bac_si_profile and ba.bac_si_profile.ten
            else ba.bac_si_profile.user.get_full_name() or ba.bac_si_profile.user.username
        )

    return render(
        request,
        "all_benh_an.html",
        {"benh_an_list": qs},
    )

def add_benh_an_detail(request, benh_an_id):
    benh_an = get_object_or_404(BenhAn, id=benh_an_id)

    if request.method == 'POST':
        form = BenhAnDetailForm(request.POST, request.FILES)
        if form.is_valid():
            benh_an_detail = form.save(commit=False)
            benh_an_detail.benh_an = benh_an
            benh_an_detail.save()
            return redirect('benh_an_detail', benh_an_id=benh_an.id)  # chuyển về trang chi tiết bệnh án
    else:
        form = BenhAnDetailForm()

    return render(request, 'add_benh_an_detail.html', {'form': form, 'benh_an': benh_an})
