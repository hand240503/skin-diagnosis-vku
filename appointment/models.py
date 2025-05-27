from django.db import models
from django.contrib.auth.models import User


class LichKham(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lich_kham', null=True, blank=True)

    ho_ten = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, null=True, blank=True)
    chuyen_khoa = models.CharField(max_length=100)
    ngay_kham = models.DateField()
    buoi_kham = models.CharField(max_length=20)
    trieu_chung = models.TextField()

    activation_token = models.CharField(max_length=128, null=True, blank=True)
    TYPE_CHOICES = (
        (0, 'Chưa xác nhận'),
        (1, 'Đã xác nhận'),
        (2, 'Đã hủy'),
    )
    type = models.IntegerField(choices=TYPE_CHOICES, default=0)
    doctors = models.ManyToManyField(
        'accounts.UserProfile',
        through='DoctorAppointment',
        related_name='appointments'
    )
    def __str__(self):
        return f"{self.ho_ten} - {self.ngay_kham} - {self.buoi_kham}"

    class Meta:
        db_table = 'lich_kham'

TRANG_THAI_CHOICES = (
    (0, 'Chưa xử lý'),
    (1, 'Đã xác nhận'),
    (2, 'Đã từ chối'),
)

class DoctorAppointment(models.Model):
    doctor = models.ForeignKey('accounts.UserProfile', on_delete=models.CASCADE, limit_choices_to={'type': 1})
    lich_kham = models.ForeignKey(LichKham, on_delete=models.CASCADE)
    trang_thai = models.IntegerField(choices=TRANG_THAI_CHOICES, default=0)
    ghi_chu = models.TextField(null=True, blank=True)
    class Meta:
        unique_together = ('doctor', 'lich_kham')
        db_table = 'doctor_appointments'

    def __str__(self):
        return f"{self.doctor.ten} - Lịch khám {self.lich_kham}"
    class Meta:
        db_table = 'doctor_appointments'

class BenhAn(models.Model):
    benh_nhan = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'type': 2},  # Chỉ bệnh nhân
        related_name='benh_an_benh_nhan'
    )
    bac_si = models.ForeignKey(
         'accounts.UserProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'type': 1},  # Chỉ bác sĩ
        related_name='benh_an_bac_si'
    )
    lich_kham = models.ForeignKey(
        'appointment.LichKham',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='benh_an_lich_kham'
    )
    ngay_kham = models.DateField(auto_now_add=True)
    chuan_doan = models.TextField()
    ghi_chu = models.TextField(blank=True, null=True)

    def __str__(self):
        user_profile = getattr(self.benh_nhan, 'userprofile', None)
        ten = user_profile.ten if user_profile else self.benh_nhan.get_full_name() or self.benh_nhan.username
        return f"Bệnh án của {ten} - {self.ngay_kham}"



    class Meta:
        db_table = 'benh_an'  # Tên bảng rõ ràng
        verbose_name = 'Bệnh án'
        verbose_name_plural = 'Danh sách bệnh án'

class BenhAnChiTiet(models.Model):
    benh_an = models.ForeignKey(
        BenhAn,
        on_delete=models.CASCADE,
        related_name='chi_tiet'
    )
    trieu_chung = models.TextField()
    ket_qua_xet_nghiem = models.TextField(blank=True, null=True)
    don_thuoc = models.TextField(blank=True, null=True)
    ghi_chu = models.TextField(blank=True, null=True)
    anh_benh_an = models.ImageField(upload_to='benh_an_images/', blank=True, null=True, verbose_name="Ảnh bệnh án")
    def __str__(self):
        return f"Chi tiết bệnh án #{self.id} - {self.benh_an}"

    class Meta:
        db_table = 'benh_an_detail'
        verbose_name = 'Chi tiết bệnh án'
        verbose_name_plural = 'Chi tiết bệnh án'

