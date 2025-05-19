import uuid
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    USER_TYPES = (
        (0, 'Quản trị viên'),   # admin
        (1, 'Bác sĩ'),          # doctor
        (2, 'Bệnh nhân'),       # patient
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    type = models.PositiveSmallIntegerField(choices=USER_TYPES, default=2)
    ten = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    activation_token = models.UUIDField(default=uuid.uuid4, null=True, blank=True)
    is_activated = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.get_type_display()}"

    class Meta:
        db_table = 'userprofile'
