from django.db import models
from django.contrib.auth.models import User

class Advisor(models.Model):
    # NOTE: A migration is needed after adding this field.
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='advisor_profile')

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    position = models.CharField(max_length=100, null=True, blank=True)
    department = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(unique=True)

    leading_quota = models.IntegerField(default=0)
    committee_quota = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class AdvisorRole(models.Model):
    ROLE_CHOICES = [
        ('advisor', 'ອາຈານນຳພາ'),
        ('committee', 'ຄະນະກຳມະການ'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, unique=True)

    def __str__(self):
        return self.get_role_display()

# This is a through model for the ManyToMany relationship 
# to allow for more flexibility if needed in the future.
class AdvisorToRole(models.Model):
    advisor = models.ForeignKey(Advisor, on_delete=models.CASCADE)
    role = models.ForeignKey(AdvisorRole, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('advisor', 'role')
