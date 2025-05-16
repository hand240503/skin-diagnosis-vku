from django.db import models

class ChuyenKhoa(models.Model):
    ma_chuyen_khoa = models.CharField(max_length=10, unique=True, verbose_name="Mã chuyên khoa")
    ten_chuyen_khoa = models.CharField(max_length=100, verbose_name="Tên chuyên khoa")
    mo_ta = models.TextField(blank=True, null=True, verbose_name="Mô tả chuyên khoa")

    class Meta:
        verbose_name = "Chuyên khoa"
        verbose_name_plural = "Các chuyên khoa"
        ordering = ['ten_chuyen_khoa']
        db_table = 'chuyen_khoa'

    def __str__(self):
        return self.ten_chuyen_khoa
