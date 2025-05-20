from django.db import models
from django.contrib.auth.models import User
from accounts.models import UserProfile

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
        UserProfile,
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
    doctor = models.ForeignKey(UserProfile, on_delete=models.CASCADE, limit_choices_to={'type': 1})
    lich_kham = models.ForeignKey(LichKham, on_delete=models.CASCADE)
    trang_thai = models.IntegerField(choices=TRANG_THAI_CHOICES, default=0)
    ghi_chu = models.TextField(null=True, blank=True)
    class Meta:
        unique_together = ('doctor', 'lich_kham')

    def __str__(self):
        return f"{self.doctor.ten} - Lịch khám {self.lich_kham}"
