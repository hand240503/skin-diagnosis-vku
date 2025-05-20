from django import forms
from .models import UserProfile

class DoctorForm(forms.ModelForm):
    is_activated = forms.TypedChoiceField(
        choices=[(True, 'Đã kích hoạt'), (False, 'Chưa kích hoạt')],
        coerce=lambda x: x == 'True',
        widget=forms.Select,
        label='Trạng thái'
    )

    class Meta:
        model = UserProfile
        fields = ['ten', 'email', 'phone', 'chuyen_khoa', 'tuoi', 'hoc_vi', 'kinh_nghiem', 'chuc_vu', 'is_activated', 'avatar']
