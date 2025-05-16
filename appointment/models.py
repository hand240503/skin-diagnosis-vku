from django.db import models

class LichKham(models.Model):
    ho_ten = models.CharField(max_length=100)
    email = models.EmailField()
    chuyen_khoa = models.CharField(max_length=100)
    ngay_kham = models.DateField()
    buoi_kham = models.CharField(max_length=20)
    trieu_chung = models.TextField()

    def __str__(self):
        return f"{self.ho_ten} - {self.ngay_kham} - {self.buoi_kham}"
    class Meta:
        db_table = 'lich_kham'
