from django import forms
from .models import BenhAnChiTiet

class BenhAnDetailForm(forms.ModelForm):
    class Meta:
        model = BenhAnChiTiet
        fields = ['trieu_chung', 'ket_qua_xet_nghiem', 'don_thuoc', 'ghi_chu', 'anh_benh_an']
