from django.shortcuts import render, redirect, get_object_or_404

from appointment.models import LichKham
from .models import User
from .models import UserProfile
from chuyen_khoa.models import ChuyenKhoa
from .forms import DoctorForm
import random
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, get_object_or_404
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

def all_appointments(request):
    status = request.GET.get('status')

    lich_kham_list = LichKham.objects.all()

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
