import uuid
from django.db import models
from django.contrib.auth.models import User
from chuyen_khoa.models import ChuyenKhoa
class UserProfile(models.Model):
    USER_TYPES = (
        (0, 'Quản trị viên'),
        (1, 'Bác sĩ'),
        (2, 'Bệnh nhân'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    type = models.PositiveSmallIntegerField(choices=USER_TYPES, default=2)
    ten = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    activation_token = models.UUIDField(default=uuid.uuid4, null=True, blank=True)
    is_activated = models.BooleanField(default=False)

    chuyen_khoa = models.ForeignKey(
        ChuyenKhoa,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Chuyên khoa"
    )

    tuoi = models.PositiveIntegerField(null=True, blank=True, verbose_name="Tuổi")
    hoc_vi = models.CharField(max_length=100, null=True, blank=True, verbose_name="Học vị")
    kinh_nghiem = models.PositiveIntegerField(null=True, blank=True, verbose_name="Số năm kinh nghiệm")
    chuc_vu = models.CharField(max_length=100, null=True, blank=True, verbose_name="Chức vụ")

    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name="Ảnh đại diện")

    def __str__(self):
        return f"{self.user.username} - {self.get_type_display()}"

    class Meta:
        db_table = 'user_profile'


