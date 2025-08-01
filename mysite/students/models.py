from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    # NOTE: A migration is needed after adding this field.
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='student_profile')

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    student_id = models.CharField(max_length=20, unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(unique=True)
    address = models.TextField(null=True, blank=True)

    major = models.CharField(max_length=100)
    year_enrolled = models.IntegerField()
    graduation_year_estimate = models.IntegerField(null=True, blank=True)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)

    STATUS_CHOICES = [
        ('studying', 'ກຳລັງສຶກສາ'),
        ('graduated', 'ຈົບການສຶກສາ'),
        ('leave', 'ພັກການຮຽນ'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='studying')

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.student_id})"
