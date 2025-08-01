from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('staff', 'Staff/ພະນັກງານ'),
        ('lecturer', 'Lecturer/ອາຈານ'),
        ('student', 'Student/ນັກສຶກສາ'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')

    def __str__(self):
        return self.user.username
